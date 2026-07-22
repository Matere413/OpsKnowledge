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

ARTIFACT_KINDS = frozenset({"manifest", "entry", "fragment", "scenario"})
MANIFEST_PATH = "manifest.json"
MAX_FILES = 10_000
MAX_FILE_BYTES = 1024 * 1024


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

    # Per-entry structural checks. Fragments and scenarios are validated in later slices.
    if manifest is not None and isinstance(manifest.get("artifacts"), list):
        index_by_path: dict[str, dict[str, Any]] = {
            artifact["path"]: artifact
            for artifact in manifest["artifacts"]
            if isinstance(artifact, dict) and isinstance(artifact.get("path"), str)
        }
        for path in files:
            rel = _relative(path, resolved)
            if rel == MANIFEST_PATH:
                continue
            artifact_meta = index_by_path.get(rel)
            kind = artifact_meta.get("kind") if artifact_meta else None
            if kind == "entry":
                payload, entry_read_findings = _safe_read_json(path, resolved)
                findings.extend(entry_read_findings)
                if payload is not None:
                    findings.extend(_validate_entry(path, resolved, payload, artifact_meta))

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
