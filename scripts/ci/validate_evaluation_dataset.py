"""Dependency-free structural validator for the OpsKnowledge evaluation dataset.

This module is a repository guard, not a corpus loader or runtime feature.
It performs no network, database, provider, or out-of-root filesystem access.

Public API:
    validate(root: Path) -> list[Diagnostic]
    main(argv: list[str]) -> int

Exit codes:
    0 -> valid dataset, no findings
    1 -> one or more findings reported
    2 -> invalid CLI usage
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
import sys
from pathlib import Path
from typing import Any

Diagnostic = tuple[str, str, str]

SCHEMA_VERSION = "1"
DATASET_ID = "opsknowledge-evaluation-dataset"
ALLOWED_LANGUAGES = frozenset({"es", "en"})
ALLOWED_COLLECTIONS = frozenset({"runbooks", "adrs", "operational-policies"})
ALLOWED_PROVENANCE = frozenset({"original", "ocr"})
ALLOWED_APPROVALS = frozenset({"approved"})
ALLOWED_CLASSIFICATIONS = frozenset({"synthetic"})
ALLOWED_PROFILES = frozenset({"development"})
# OCR fragments must declare a non-empty source reference and a quality indicator.
# Quality is a controlled vocabulary so consumers can distinguish OCR confidence
# without interpreting free-form text.
ALLOWED_OCR_QUALITY = frozenset({"low", "medium", "high"})
# Sensitive-identifier allowlist: fragments that carry identifiers MUST mark
# `fictitious: true` and use obviously non-corporate patterns. A fragment is
# considered to carry sensitive identifiers when it declares `fictitious: true`
# OR its content/source mentions one of the reserved patterns. The validator
# rejects a `fictitious` marker that is not strictly true, and rejects content
# that looks like a sensitive identifier without the marker.
SENSITIVE_FICTITIOUS_VALUES = frozenset({True})
SENSITIVE_PATTERNS = ("example.test", "TEST-", "INVALID")
# No entry, fragment, or scenario may reference image content. The dataset is
# text-only; OCR cases carry extracted text plus provenance, never images.
PROHIBITED_IMAGE_FIELDS = frozenset(
    {"image", "images", "screenshot", "photograph", "photo", "picture", "visual"}
)

ARTIFACT_KINDS = frozenset({"manifest", "entry", "fragment", "scenario"})
MANIFEST_PATH = "manifest.json"
MAX_FILES = 10_000
MAX_FILE_BYTES = 1024 * 1024

# Scenario contracts. The six-state outcome taxonomy is canonical per the
# OpsKnowledge domain contract; no seventh outcome is permitted.
ALLOWED_OUTCOMES = frozenset(
    {
        "supported",
        "insufficient_information",
        "contradictory_information",
        "out_of_scope",
        "unavailable",
        "session_expired",
    }
)
# Grounded outcomes count toward the 16 supported scenarios; every other
# outcome counts toward the 16 abstention/safety scenarios.
GROUNDED_OUTCOMES = frozenset({"supported"})
# Case types covered by the scenario catalog. The validator allowlists these
# so an unknown case type fails closed rather than silently certifying novelty.
ALLOWED_CASE_TYPES = frozenset(
    {
        "grounded",
        "ambiguous-incomplete",
        "contradictory",
        "out-of-scope",
        "unanswerable",
        "prompt-override",
        "OCR-uncertainty",
        "sensitive-identifier",
    }
)
# Safety classifications. "safe" is the default; "sensitive" marks a sensitive
# screening case; "override" marks a prompt-override case.
ALLOWED_SAFETY = frozenset({"safe", "sensitive", "override"})
# Abstention reason codes are controlled so consumers can distinguish cases
# without reading content. "none" is the allowed value for supported scenarios.
ALLOWED_ABSTENTION_REASONS = frozenset(
    {
        "none",
        "insufficient-evidence",
        "contradiction-detected",
        "out-of-scope",
        "provider-unavailable",
        "prompt-override-blocked",
        "sensitive-blocked",
    }
)
# Unanswerable case outcomes must be one of these abstention states.
UNANSWERABLE_OUTCOMES = frozenset({"insufficient_information", "out_of_scope", "unavailable"})
# Case types that MUST declare an empty evidence set.
EMPTY_EVIDENCE_CASE_TYPES = frozenset(
    {"out-of-scope", "prompt-override", "unanswerable", "sensitive-identifier"}
)
# Prohibited scenario field names: any field that could carry answer-like prose
# or query text fails closed. The dataset defines outcome, evidence references,
# claim expectation IDs, and abstention reason codes only.
PROHIBITED_SCENARIO_FIELDS = frozenset(
    {"answer", "gold_answer", "response", "completion", "query", "question", "text"}
)
# Required scenario catalog contract: exactly 32 scenarios, 16 es / 16 en,
# 16 bilingual pairs, 16 supported / 16 abstention.
REQUIRED_SCENARIO_COUNT = 32
REQUIRED_LANGUAGE_SPLIT = 16
REQUIRED_GROUNDED_COUNT = 16
REQUIRED_ABSTENTION_COUNT = 16
REQUIRED_PAIR_COUNT = 16


def _relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return "."


def _canonical_bytes(payload: Any) -> bytes:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )
    return encoded + b"\n"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_artifact_target(
    root: Path, rel: str, artifact_path: str
) -> tuple[Path | None, list[Diagnostic]]:
    """Resolve an artifact path to a safe in-root regular file or fail closed.

    Never open escaping, absolute, symlinked, or non-regular targets. Returns
    the resolved on-disk path with no findings on success, or None plus stable
    safe reason codes so callers can skip opening the file.
    """
    if artifact_path.startswith("/"):
        return None, [
            (rel, "manifest-artifact-absolute-path", "use a relative path inside the dataset root")
        ]
    candidate = root / artifact_path
    try:
        resolved = candidate.resolve()
        resolved.relative_to(root.resolve())
    except (OSError, ValueError):
        return None, [
            (rel, "manifest-artifact-out-of-root", "keep artifact paths inside the dataset root")
        ]
    try:
        metadata = os.lstat(candidate)
    except FileNotFoundError:
        return None, [
            (rel, "manifest-dangling-reference", f"create the referenced file '{artifact_path}'")
        ]
    except OSError:
        return None, [(rel, "manifest-artifact-stat-error", "restore readable filesystem metadata")]
    if stat.S_ISLNK(metadata.st_mode):
        return None, [(rel, "manifest-artifact-symlink", "replace the symlink with a regular file")]
    if not stat.S_ISREG(metadata.st_mode):
        return None, [(rel, "manifest-artifact-non-regular", "remove the special file")]
    return resolved, []


def _safe_read_json(path: Path, root: Path) -> tuple[Any, list[Diagnostic]]:
    rel = _relative(path, root)
    try:
        raw = path.read_bytes()
    except OSError:
        return None, [(rel, "read-error", "restore a readable UTF-8 JSON file")]
    if len(raw) > MAX_FILE_BYTES:
        return None, [(rel, "resource-limit-file", "reduce the JSON file to at most 1 MiB")]
    if raw.startswith(b"\xef\xbb\xbf"):
        return None, [(rel, "bom-not-allowed", "strip the UTF-8 BOM from the JSON file")]
    if not raw.endswith(b"\n"):
        return None, [(rel, "missing-trailing-lf", "add exactly one trailing LF to the JSON file")]
    if raw.endswith(b"\n\n"):
        return None, [(rel, "extra-trailing-lf", "keep exactly one trailing LF at end of file")]
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None, [(rel, "decode-error", "restore UTF-8 encoded JSON")]
    try:
        return json.loads(text), []
    except json.JSONDecodeError:
        return None, [(rel, "json-syntax-error", "fix the JSON syntax")]


def _walk_dataset(root: Path) -> tuple[list[Path], list[Diagnostic]]:
    files: list[Path] = []
    findings: list[Diagnostic] = []
    seen = 0
    worklist: list[Path] = [root]
    while worklist:
        directory = worklist.pop()
        try:
            with os.scandir(directory) as entries:
                batch = sorted(entries, key=lambda entry: entry.name)
        except OSError:
            findings.append(
                (
                    _relative(directory, root),
                    "traversal-error",
                    "restore readable directory traversal",
                )
            )
            continue
        for entry in batch:
            seen += 1
            path = Path(entry.path)
            rel = _relative(path, root)
            if entry.name.startswith("."):
                findings.append(
                    (rel, "hidden-file-not-allowed", "remove the hidden file or directory")
                )
                continue
            try:
                metadata = os.lstat(path)
            except OSError:
                findings.append((rel, "stat-error", "restore readable filesystem metadata"))
                continue
            if stat.S_ISLNK(metadata.st_mode):
                findings.append(
                    (rel, "symlink-not-allowed", "replace the symlink with a regular file")
                )
                continue
            if stat.S_ISDIR(metadata.st_mode):
                if entry.name in {"__pycache__"}:
                    continue
                worklist.append(path)
                continue
            if not stat.S_ISREG(metadata.st_mode):
                findings.append((rel, "non-regular-file", "remove the special file"))
                continue
            if path.suffix != ".json":
                findings.append((rel, "non-json-file", "remove the non-JSON file"))
                continue
            seen_files = len(files)
            if seen_files >= MAX_FILES:
                findings.append((rel, "resource-limit-files", "reduce files to at most 10,000"))
                continue
            files.append(path)
    files.sort(key=lambda p: _relative(p, root))
    return files, findings


def _validate_manifest(
    root: Path, manifest_path: Path, files: list[Path]
) -> tuple[dict[str, Any] | None, list[Diagnostic]]:
    rel = _relative(manifest_path, root)
    # Manifest must be a regular, in-root file before any read/open. Reuse the
    # safe path/stat discipline from _safe_artifact_target so a symlinked or
    # non-regular manifest.json fails closed without reaching read_bytes.
    try:
        metadata = os.lstat(manifest_path)
    except FileNotFoundError:
        return None, [(rel, "manifest-missing", "create manifest.json at the dataset root")]
    except OSError:
        return None, [(rel, "manifest-stat-error", "restore readable filesystem metadata")]
    if stat.S_ISLNK(metadata.st_mode):
        return None, [(rel, "manifest-symlink", "replace the symlink with a regular file")]
    if not stat.S_ISREG(metadata.st_mode):
        return None, [(rel, "manifest-non-regular", "remove the special file")]
    try:
        manifest_path.resolve().relative_to(root.resolve())
    except (OSError, ValueError):
        return None, [(rel, "manifest-out-of-root", "keep manifest.json inside the dataset root")]
    payload, findings = _safe_read_json(manifest_path, root)
    if payload is None:
        return None, findings
    if not isinstance(payload, dict):
        findings.append((rel, "manifest-shape", "manifest must be a JSON object"))
        return None, findings
    for key in (
        "schema_version",
        "dataset_id",
        "profile",
        "approval",
        "classification",
        "artifacts",
    ):
        if key not in payload:
            findings.append(
                (rel, "manifest-missing-field", f"add required field '{key}' to manifest")
            )
    if payload.get("schema_version") != SCHEMA_VERSION:
        findings.append(
            (rel, "manifest-schema-version", f"set schema_version to '{SCHEMA_VERSION}'")
        )
    if payload.get("dataset_id") != DATASET_ID:
        findings.append((rel, "manifest-dataset-id", f"set dataset_id to '{DATASET_ID}'"))
    if payload.get("profile") not in ALLOWED_PROFILES:
        findings.append(
            (rel, "manifest-profile", f"set profile to one of {sorted(ALLOWED_PROFILES)}")
        )
    if payload.get("approval") not in ALLOWED_APPROVALS:
        findings.append(
            (rel, "manifest-approval", f"set approval to one of {sorted(ALLOWED_APPROVALS)}")
        )
    if payload.get("classification") not in ALLOWED_CLASSIFICATIONS:
        findings.append(
            (
                rel,
                "manifest-classification",
                f"set classification to one of {sorted(ALLOWED_CLASSIFICATIONS)}",
            )
        )
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, list):
        findings.append((rel, "manifest-artifacts-shape", "manifest 'artifacts' must be a list"))
        return payload, findings
    if len(artifacts) == 0:
        findings.append(
            (rel, "manifest-artifacts-empty", "manifest 'artifacts' must list at least one entry")
        )
        return payload, findings
    seen_paths: list[str] = []
    has_manifest_self_entry = False
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            findings.append(
                (rel, "manifest-artifact-shape", "each manifest artifact must be an object")
            )
            continue
        for key in ("path", "kind", "id", "sha256"):
            if key not in artifact:
                findings.append(
                    (
                        rel,
                        "manifest-artifact-missing-field",
                        f"add required field '{key}' to artifact",
                    )
                )
        kind = artifact.get("kind")
        if kind not in ARTIFACT_KINDS:
            findings.append(
                (rel, "manifest-artifact-kind", f"set kind to one of {sorted(ARTIFACT_KINDS)}")
            )
        artifact_path = artifact.get("path")
        if not isinstance(artifact_path, str) or not artifact_path:
            findings.append((rel, "manifest-artifact-path", "set a non-empty artifact path"))
            continue
        if artifact_path in seen_paths:
            findings.append(
                (
                    rel,
                    "manifest-artifact-duplicate-path",
                    f"remove the duplicate manifest entry for '{artifact_path}'",
                )
            )
            continue
        seen_paths.append(artifact_path)
        if kind == "manifest":
            has_manifest_self_entry = True
            if artifact_path != MANIFEST_PATH:
                findings.append(
                    (
                        rel,
                        "manifest-self-entry-path",
                        f"set the manifest artifact path to '{MANIFEST_PATH}'",
                    )
                )
            continue
        target, target_findings = _safe_artifact_target(root, rel, artifact_path)
        findings.extend(target_findings)
        if target is None:
            continue
        if not target.exists():
            findings.append(
                (
                    rel,
                    "manifest-dangling-reference",
                    f"create the referenced file '{artifact_path}'",
                )
            )
    if not has_manifest_self_entry:
        findings.append(
            (
                rel,
                "manifest-self-entry-missing",
                "add a manifest artifact entry to manifest 'artifacts'",
            )
        )
    return payload, findings


def _validate_entry(
    path: Path, root: Path, payload: Any, manifest_entry: dict[str, Any] | None
) -> list[Diagnostic]:
    rel = _relative(path, root)
    findings: list[Diagnostic] = []
    if not isinstance(payload, dict):
        return [(rel, "entry-shape", "entry must be a JSON object")]
    for key in (
        "id",
        "logical_entry_id",
        "revision",
        "collection",
        "language",
        "approval",
        "classification",
        "profile",
        "content",
        "content_sha256",
    ):
        if key not in payload:
            findings.append((rel, "entry-missing-field", f"add required field '{key}' to entry"))
    collection = payload.get("collection")
    if collection not in ALLOWED_COLLECTIONS:
        findings.append(
            (rel, "entry-collection", f"set collection to one of {sorted(ALLOWED_COLLECTIONS)}")
        )
    language = payload.get("language")
    if language not in ALLOWED_LANGUAGES:
        findings.append(
            (rel, "entry-language", f"set language to one of {sorted(ALLOWED_LANGUAGES)}")
        )
    if payload.get("approval") not in ALLOWED_APPROVALS:
        findings.append(
            (rel, "entry-approval", f"set approval to one of {sorted(ALLOWED_APPROVALS)}")
        )
    if payload.get("classification") not in ALLOWED_CLASSIFICATIONS:
        findings.append(
            (
                rel,
                "entry-classification",
                f"set classification to one of {sorted(ALLOWED_CLASSIFICATIONS)}",
            )
        )
    if payload.get("profile") not in ALLOWED_PROFILES:
        findings.append((rel, "entry-profile", f"set profile to one of {sorted(ALLOWED_PROFILES)}"))
    content = payload.get("content")
    if not isinstance(content, str) or not content:
        findings.append((rel, "entry-content", "set 'content' to a non-empty string"))
    else:
        declared_hash = payload.get("content_sha256")
        actual_hash = _sha256(content.encode("utf-8"))
        if declared_hash != actual_hash:
            findings.append(
                (
                    rel,
                    "entry-content-hash",
                    "recompute content_sha256 over the entry 'content' bytes",
                )
            )
    if manifest_entry is not None:
        if manifest_entry.get("id") != payload.get("id"):
            findings.append((rel, "entry-id-mismatch", "align manifest 'id' with the entry 'id'"))
        revision = payload.get("revision")
        if (
            manifest_entry.get("revision") is not None
            and manifest_entry.get("revision") != revision
        ):
            findings.append(
                (
                    rel,
                    "entry-revision-mismatch",
                    "align manifest 'revision' with the entry 'revision'",
                )
            )
    return findings


def _validate_fragment(
    path: Path,
    root: Path,
    payload: Any,
    manifest_entry: dict[str, Any] | None,
    entries_by_id: dict[str, dict[str, Any]],
) -> list[Diagnostic]:
    rel = _relative(path, root)
    findings: list[Diagnostic] = []
    if not isinstance(payload, dict):
        return [(rel, "fragment-shape", "fragment must be a JSON object")]
    # Prohibited image fields: the dataset is text-only.
    for field in PROHIBITED_IMAGE_FIELDS:
        if field in payload:
            findings.append(
                (
                    rel,
                    "fragment-image-field",
                    f"remove the '{field}' field; OCR text only, no images",
                )
            )
    for key in (
        "id",
        "entry_id",
        "language",
        "provenance",
        "source_reference",
        "quality",
        "approval",
        "classification",
        "profile",
        "content",
        "content_sha256",
    ):
        if key not in payload:
            findings.append(
                (rel, "fragment-missing-field", f"add required field '{key}' to fragment")
            )
    language = payload.get("language")
    if language not in ALLOWED_LANGUAGES:
        findings.append(
            (rel, "fragment-language", f"set language to one of {sorted(ALLOWED_LANGUAGES)}")
        )
    provenance = payload.get("provenance")
    if provenance not in ALLOWED_PROVENANCE:
        findings.append(
            (rel, "fragment-provenance", f"set provenance to one of {sorted(ALLOWED_PROVENANCE)}")
        )
    if payload.get("approval") not in ALLOWED_APPROVALS:
        findings.append(
            (rel, "fragment-approval", f"set approval to one of {sorted(ALLOWED_APPROVALS)}")
        )
    if payload.get("classification") not in ALLOWED_CLASSIFICATIONS:
        findings.append(
            (
                rel,
                "fragment-classification",
                f"set classification to one of {sorted(ALLOWED_CLASSIFICATIONS)}",
            )
        )
    if payload.get("profile") not in ALLOWED_PROFILES:
        findings.append(
            (rel, "fragment-profile", f"set profile to one of {sorted(ALLOWED_PROFILES)}")
        )
    # OCR provenance requires a non-empty source reference and a quality indicator.
    source_reference = payload.get("source_reference")
    quality = payload.get("quality")
    if provenance == "ocr":
        if not isinstance(source_reference, str) or not source_reference:
            findings.append(
                (
                    rel,
                    "fragment-ocr-source",
                    "set a non-empty synthetic 'source_reference' for OCR fragments",
                )
            )
        if quality not in ALLOWED_OCR_QUALITY:
            findings.append(
                (
                    rel,
                    "fragment-ocr-quality",
                    f"set 'quality' to one of {sorted(ALLOWED_OCR_QUALITY)} for OCR fragments",
                )
            )
    else:
        # Non-OCR fragments do not carry OCR metadata; an explicit non-empty
        # source_reference or quality on a non-OCR fragment is a shape error.
        if isinstance(source_reference, str) and source_reference:
            findings.append(
                (rel, "fragment-source-not-ocr", "clear 'source_reference' for non-OCR fragments")
            )
        if isinstance(quality, str) and quality:
            findings.append(
                (rel, "fragment-quality-not-ocr", "clear 'quality' for non-OCR fragments")
            )
    content = payload.get("content")
    if not isinstance(content, str) or not content:
        findings.append((rel, "fragment-content", "set 'content' to a non-empty string"))
    else:
        declared_hash = payload.get("content_sha256")
        actual_hash = _sha256(content.encode("utf-8"))
        if declared_hash != actual_hash:
            findings.append(
                (
                    rel,
                    "fragment-content-hash",
                    "recompute content_sha256 over the fragment 'content' bytes",
                )
            )
    # Sensitive-identifier marker: if present, must be strictly true.
    if "fictitious" in payload and payload.get("fictitious") not in SENSITIVE_FICTITIOUS_VALUES:
        findings.append(
            (rel, "fragment-fictitious-marker", "set 'fictitious' to true or remove the marker")
        )
    # Parent entry resolution and language match.
    entry_id = payload.get("entry_id")
    if not isinstance(entry_id, str) or not entry_id:
        findings.append((rel, "fragment-entry-id", "set 'entry_id' to a declared entry id"))
    else:
        parent = entries_by_id.get(entry_id)
        if parent is None:
            findings.append(
                (rel, "fragment-parent-missing", f"reference a declared entry id '{entry_id}'")
            )
        else:
            parent_language = parent.get("language")
            if parent_language in ALLOWED_LANGUAGES and language != parent_language:
                findings.append(
                    (
                        rel,
                        "fragment-language-mismatch",
                        f"set fragment language to parent entry language '{parent_language}'",
                    )
                )
            if parent.get("approval") not in ALLOWED_APPROVALS:
                findings.append(
                    (rel, "fragment-parent-not-approved", "reference an approved parent entry")
                )
    if manifest_entry is not None and manifest_entry.get("id") != payload.get("id"):
        findings.append((rel, "fragment-id-mismatch", "align manifest 'id' with the fragment 'id'"))
    return findings


def _validate_scenario(
    path: Path,
    root: Path,
    payload: Any,
    manifest_entry: dict[str, Any] | None,
    fragments_by_id: dict[str, dict[str, Any]],
    entries_by_logical_id: dict[str, list[dict[str, Any]]],
) -> list[Diagnostic]:
    rel = _relative(path, root)
    findings: list[Diagnostic] = []
    if not isinstance(payload, dict):
        return [(rel, "scenario-shape", "scenario must be a JSON object")]
    # Prohibited fields: no answer-like or query text may appear on a scenario.
    for field in PROHIBITED_SCENARIO_FIELDS:
        if field in payload:
            findings.append(
                (
                    rel,
                    "scenario-prohibited-field",
                    f"remove the '{field}' field; scenarios carry no answer or query text",
                )
            )
    for key in (
        "id",
        "pair_id",
        "language",
        "case_type",
        "expected_outcome",
        "safety_classification",
        "claim_expectation",
        "abstention_reason",
        "evidence",
        "approval",
        "classification",
        "profile",
    ):
        if key not in payload:
            findings.append(
                (rel, "scenario-missing-field", f"add required field '{key}' to scenario")
            )
    if payload.get("approval") not in ALLOWED_APPROVALS:
        findings.append(
            (rel, "scenario-approval", f"set approval to one of {sorted(ALLOWED_APPROVALS)}")
        )
    if payload.get("classification") not in ALLOWED_CLASSIFICATIONS:
        findings.append(
            (
                rel,
                "scenario-classification",
                f"set classification to one of {sorted(ALLOWED_CLASSIFICATIONS)}",
            )
        )
    if payload.get("profile") not in ALLOWED_PROFILES:
        findings.append(
            (rel, "scenario-profile", f"set profile to one of {sorted(ALLOWED_PROFILES)}")
        )
    language = payload.get("language")
    if language not in ALLOWED_LANGUAGES:
        findings.append(
            (rel, "scenario-language", f"set language to one of {sorted(ALLOWED_LANGUAGES)}")
        )
    case_type = payload.get("case_type")
    if case_type not in ALLOWED_CASE_TYPES:
        findings.append(
            (
                rel,
                "scenario-case-type",
                f"set case_type to one of {sorted(ALLOWED_CASE_TYPES)}",
            )
        )
    outcome = payload.get("expected_outcome")
    if outcome not in ALLOWED_OUTCOMES:
        findings.append(
            (
                rel,
                "scenario-outcome",
                f"set expected_outcome to one of {sorted(ALLOWED_OUTCOMES)}",
            )
        )
    safety = payload.get("safety_classification")
    if safety not in ALLOWED_SAFETY:
        findings.append(
            (
                rel,
                "scenario-safety",
                f"set safety_classification to one of {sorted(ALLOWED_SAFETY)}",
            )
        )
    reason = payload.get("abstention_reason")
    if reason not in ALLOWED_ABSTENTION_REASONS:
        findings.append(
            (
                rel,
                "scenario-abstention-reason",
                f"set abstention_reason to one of {sorted(ALLOWED_ABSTENTION_REASONS)}",
            )
        )
    claim = payload.get("claim_expectation")
    if not isinstance(claim, str) or not claim:
        findings.append(
            (rel, "scenario-claim-expectation", "set 'claim_expectation' to a non-empty claim ID")
        )
    evidence = payload.get("evidence")
    if not isinstance(evidence, list):
        findings.append(
            (rel, "scenario-evidence-shape", "set 'evidence' to a list of fragment IDs")
        )
        evidence = []
    # Evidence language isolation: every referenced fragment must exist and
    # match the scenario language; mixed-language evidence fails closed.
    resolved_fragments: list[dict[str, Any]] = []
    for ref in evidence:
        if not isinstance(ref, str) or not ref:
            findings.append(
                (rel, "scenario-evidence-ref", "reference a declared fragment id in 'evidence'")
            )
            continue
        fragment = fragments_by_id.get(ref)
        if fragment is None:
            findings.append(
                (rel, "scenario-evidence-missing", f"reference a declared fragment id '{ref}'")
            )
            continue
        resolved_fragments.append(fragment)
        frag_lang = fragment.get("language")
        if (
            frag_lang in ALLOWED_LANGUAGES
            and language in ALLOWED_LANGUAGES
            and frag_lang != language
        ):
            findings.append(
                (
                    rel,
                    "scenario-evidence-language-mismatch",
                    f"reference only {language} fragments in the evidence set",
                )
            )
    # Supported scenarios MUST declare at least one approved language-matched
    # fragment whose parent entry is approved.
    if outcome in GROUNDED_OUTCOMES:
        if not resolved_fragments:
            findings.append(
                (
                    rel,
                    "scenario-supported-no-evidence",
                    "a supported scenario must reference at least one approved "
                    "language-matched fragment",
                )
            )
        else:
            for fragment in resolved_fragments:
                if fragment.get("approval") not in ALLOWED_APPROVALS:
                    findings.append(
                        (
                            rel,
                            "scenario-evidence-not-approved",
                            "reference only approved fragments in a supported scenario",
                        )
                    )
    # Empty-evidence case types: out-of-scope, prompt-override, unanswerable,
    # and sensitive-identifier MUST NOT carry resolvable evidence.
    if case_type in EMPTY_EVIDENCE_CASE_TYPES and evidence:
        findings.append(
            (
                rel,
                "scenario-empty-evidence-required",
                f"a {case_type} scenario must declare an empty evidence set",
            )
        )
    # Unanswerable case outcomes must abstain (never supported).
    if case_type == "unanswerable" and outcome not in UNANSWERABLE_OUTCOMES:
        findings.append(
            (
                rel,
                "scenario-unanswerable-outcome",
                "set expected_outcome to one of "
                f"{sorted(UNANSWERABLE_OUTCOMES)} for unanswerable cases",
            )
        )
    # Contradiction scenarios: exactly two approved revisions of the same
    # logical entry, both language-matched and synthetic. The evidence set
    # must contain fragments referencing two distinct revisions of one parent.
    if case_type == "contradictory" and outcome == "contradictory_information":
        parent_logical_ids: set[str] = set()
        revision_pairs: dict[str, set[str]] = {}
        for fragment in resolved_fragments:
            entry_id = fragment.get("entry_id")
            if not isinstance(entry_id, str):
                continue
            parent = None
            for _logical_id, revs in entries_by_logical_id.items():
                for entry in revs:
                    if entry.get("id") == entry_id:
                        parent = entry
                        break
                if parent is not None:
                    break
            if parent is None:
                continue
            parent_logical_ids.add(parent.get("logical_entry_id", ""))
            revision_pairs.setdefault(parent.get("logical_entry_id", ""), set()).add(
                parent.get("revision", "")
            )
        # Must reference exactly one logical entry with at least two revisions.
        valid_pairs = [logical_id for logical_id, revs in revision_pairs.items() if len(revs) >= 2]
        if len(parent_logical_ids) != 1 or len(valid_pairs) != 1:
            findings.append(
                (
                    rel,
                    "scenario-contradiction-revisions",
                    "reference exactly two approved revisions of one logical entry",
                )
            )
    if manifest_entry is not None and manifest_entry.get("id") != payload.get("id"):
        findings.append((rel, "scenario-id-mismatch", "align manifest 'id' with the scenario 'id'"))
    return findings


def _validate_manifest_artifact_hashes(root: Path, manifest: dict[str, Any]) -> list[Diagnostic]:
    findings: list[Diagnostic] = []
    rel = _relative(root / MANIFEST_PATH, root)
    for artifact in manifest.get("artifacts", []):
        if not isinstance(artifact, dict):
            continue
        declared = artifact.get("sha256")
        artifact_path = artifact.get("path")
        if not isinstance(artifact_path, str) or not artifact_path:
            continue
        if artifact.get("kind") == "manifest":
            on_disk = root / MANIFEST_PATH
            if not on_disk.exists():
                continue
            try:
                raw = on_disk.read_bytes()
            except OSError:
                findings.append((rel, "read-error", "restore a readable file"))
                continue
            try:
                payload = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                findings.append((rel, "file-not-canonical-json", "restore canonical JSON"))
                continue
            # Manifest is self-referential: its sha256 field changes its own canonical bytes.
            # The stable manifest hash is computed over canonical bytes with the manifest
            # artifact entry's sha256 set to the empty string.
            artifacts = payload.get("artifacts", [])
            manifest_artifact: dict[str, Any] | None = None
            if isinstance(artifacts, list):
                for item in artifacts:
                    if isinstance(item, dict) and item.get("kind") == "manifest":
                        manifest_artifact = item
                        break
            if manifest_artifact is None:
                findings.append(
                    (
                        rel,
                        "manifest-self-reference-missing",
                        "add a manifest artifact entry to manifest 'artifacts'",
                    )
                )
                continue
            original_hash = manifest_artifact.get("sha256")
            manifest_artifact["sha256"] = ""
            canonical = _canonical_bytes(payload)
            manifest_artifact["sha256"] = original_hash
            actual = _sha256(canonical)
            if declared != actual:
                findings.append(
                    (
                        rel,
                        "file-hash-mismatch",
                        "recompute manifest sha256 over canonical bytes "
                        "with manifest.sha256 set to empty",
                    )
                )
            continue
        target, target_findings = _safe_artifact_target(root, rel, artifact_path)
        findings.extend(target_findings)
        if target is None:
            continue
        if not target.exists():
            continue
        try:
            raw = target.read_bytes()
        except OSError:
            findings.append((rel, "read-error", "restore a readable file"))
            continue
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            findings.append(
                (
                    rel,
                    "file-not-canonical-json",
                    "restore canonical JSON (sorted keys, one trailing LF)",
                )
            )
            continue
        canonical = _canonical_bytes(payload)
        actual = _sha256(canonical)
        if declared != actual:
            findings.append(
                (
                    rel,
                    "file-hash-mismatch",
                    "recompute sha256 over canonical JSON bytes (sorted keys, one trailing LF)",
                )
            )
    return findings


def validate(root: Path) -> list[Diagnostic]:
    """Run the structural validator over the dataset root and return sorted diagnostics."""
    findings: list[Diagnostic] = []
    resolved = root.absolute()
    try:
        stat_result = os.lstat(resolved)
    except OSError:
        return [(".", "root-stat-error", "restore the dataset root directory")]
    if stat.S_ISLNK(stat_result.st_mode):
        return [(".", "root-symlink-not-allowed", "point the validator at a real directory")]
    if not stat.S_ISDIR(stat_result.st_mode):
        return [(".", "root-not-directory", "point the validator at a directory")]

    files, walk_findings = _walk_dataset(resolved)
    findings.extend(walk_findings)

    manifest_path = resolved / MANIFEST_PATH
    manifest, manifest_findings = _validate_manifest(resolved, manifest_path, files)
    findings.extend(manifest_findings)

    # Orphan coverage: every JSON file under root (except manifest) must be in manifest artifacts.
    if manifest is not None and isinstance(manifest.get("artifacts"), list):
        declared_paths = {
            artifact.get("path")
            for artifact in manifest["artifacts"]
            if isinstance(artifact, dict) and isinstance(artifact.get("path"), str)
        }
        for path in files:
            rel = _relative(path, resolved)
            if rel == MANIFEST_PATH:
                continue
            if rel not in declared_paths:
                findings.append(
                    (
                        rel,
                        "orphan-file-not-in-manifest",
                        "add the file to manifest 'artifacts' or remove it",
                    )
                )

    # Per-entry and per-fragment structural checks. Scenarios are validated in
    # a later slice. Entries are loaded first so fragments can resolve parent
    # references and language against a complete entry index.
    if manifest is not None and isinstance(manifest.get("artifacts"), list):
        index_by_path: dict[str, dict[str, Any]] = {
            artifact["path"]: artifact
            for artifact in manifest["artifacts"]
            if isinstance(artifact, dict) and isinstance(artifact.get("path"), str)
        }
        entries_by_id: dict[str, dict[str, Any]] = {}
        entry_payloads: dict[str, Any] = {}
        for path in files:
            rel = _relative(path, resolved)
            if rel == MANIFEST_PATH:
                continue
            artifact_meta = index_by_path.get(rel)
            kind = artifact_meta.get("kind") if artifact_meta else None
            if kind == "entry":
                payload, entry_read_findings = _safe_read_json(path, resolved)
                findings.extend(entry_read_findings)
                if payload is not None and isinstance(payload, dict):
                    entry_payloads[rel] = payload
                    entry_id = payload.get("id")
                    if isinstance(entry_id, str):
                        entries_by_id[entry_id] = payload
                    findings.extend(_validate_entry(path, resolved, payload, artifact_meta))
        for path in files:
            rel = _relative(path, resolved)
            if rel == MANIFEST_PATH:
                continue
            artifact_meta = index_by_path.get(rel)
            kind = artifact_meta.get("kind") if artifact_meta else None
            if kind == "fragment":
                payload, fragment_read_findings = _safe_read_json(path, resolved)
                findings.extend(fragment_read_findings)
                if payload is not None:
                    findings.extend(
                        _validate_fragment(path, resolved, payload, artifact_meta, entries_by_id)
                    )
        # Build a fragment index for scenario evidence resolution. Scenarios
        # resolve evidence references against this index; an evidence ID that
        # does not resolve to a declared fragment fails closed.
        fragments_by_id: dict[str, dict[str, Any]] = {}
        for path in files:
            rel = _relative(path, resolved)
            if rel == MANIFEST_PATH:
                continue
            artifact_meta = index_by_path.get(rel)
            kind = artifact_meta.get("kind") if artifact_meta else None
            if kind == "fragment":
                payload, _fragment_read = _safe_read_json(path, resolved)
                if payload is not None and isinstance(payload, dict):
                    fragment_id = payload.get("id")
                    if isinstance(fragment_id, str):
                        fragments_by_id[fragment_id] = payload
        # Index entries by logical_entry_id so contradiction scenarios can
        # verify two approved revisions of the same logical entry.
        entries_by_logical_id: dict[str, list[dict[str, Any]]] = {}
        for entry_payload in entries_by_id.values():
            logical_id = entry_payload.get("logical_entry_id")
            if isinstance(logical_id, str):
                entries_by_logical_id.setdefault(logical_id, []).append(entry_payload)
        scenario_payloads: list[dict[str, Any]] = []
        for path in files:
            rel = _relative(path, resolved)
            if rel == MANIFEST_PATH:
                continue
            artifact_meta = index_by_path.get(rel)
            kind = artifact_meta.get("kind") if artifact_meta else None
            if kind == "scenario":
                payload, scenario_read_findings = _safe_read_json(path, resolved)
                findings.extend(scenario_read_findings)
                if payload is not None and isinstance(payload, dict):
                    scenario_payloads.append(payload)
                    findings.extend(
                        _validate_scenario(
                            path,
                            resolved,
                            payload,
                            artifact_meta,
                            fragments_by_id,
                            entries_by_logical_id,
                        )
                    )

    if manifest is not None:
        findings.extend(_validate_manifest_artifact_hashes(resolved, manifest))

    return sorted(findings)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(
            "usage: validate_evaluation_dataset.py <dataset-root>",
            file=sys.stderr,
        )
        return 2
    root = Path(argv[1])
    findings = validate(root)
    for rel, reason, remediation in findings:
        print(f"{rel}: {reason}: {remediation}", file=sys.stderr)
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
