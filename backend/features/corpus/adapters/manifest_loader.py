"""Manifest adapter: the corpus outbound port that reads the dataset from disk.

This adapter is the only component that touches the filesystem for corpus
loading. It resolves manifest artifact paths safely (no absolute, escaping,
symlinked, or non-regular targets), reads canonical JSON, verifies sha256
integrity, and delegates boundary validation to the application layer.

It consumes the development-only synthetic corpus from ``evaluation-dataset/``
by default. The loader fails closed on:

- non-development active profile or manifest-declared profile,
- non-synthetic or unapproved entries/fragments,
- invalid parents (fragment references a missing or unapproved entry),
- mixed languages (fragment language != parent entry language),
- unlisted paths (a payload file present on disk but absent from the manifest),
- unsupported controlled vocabularies (language, collection, provenance, OCR quality),
- unsafe artifact paths (absolute, out-of-root, symlink, non-regular, dangling),
- sha256 mismatches, and manifest/payload id mismatches.

All errors are raised as :class:`CorpusLoadError` with a safe ``reason_code``;
no content ever appears in errors or logs.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
from pathlib import Path
from typing import Any, Final

from backend.features.corpus.application import (
    APPROVED_APPROVAL,
    DEVELOPMENT_PROFILE,
    SYNTHETIC_CLASSIFICATION,
    Corpus,
    CorpusLoadError,
    assert_profile_allowed,
    validate_entry_payload,
    validate_fragment_payload,
)
from backend.features.corpus.domain import Entry, Fragment

MANIFEST_FILENAME: Final[str] = "manifest.json"
SCHEMA_VERSION: Final[str] = "1"
DATASET_ID: Final[str] = "opsknowledge-evaluation-dataset"
MAX_FILE_BYTES: Final[int] = 1024 * 1024


def load_corpus(manifest_path: Path, *, profile: str) -> Corpus:
    """Load and validate the development-only synthetic corpus.

    Args:
        manifest_path: Path to the dataset ``manifest.json`` (the dataset root
            is its parent directory).
        profile: Active runtime profile. Must be ``development``.

    Returns:
        An immutable :class:`Corpus` of approved, synthetic, development-only
        fragments ordered by stable ascending identifier.

    Raises:
        CorpusLoadError: with a safe ``reason_code`` on any boundary violation.
    """
    assert_profile_allowed(profile)

    root = manifest_path.resolve().parent
    _assert_manifest_safe(manifest_path, root)
    manifest_payload = _read_canonical_json(manifest_path, root, "manifest.json")
    if not isinstance(manifest_payload, dict):
        raise CorpusLoadError("manifest-shape", "manifest.json")

    _validate_manifest_top_level(manifest_payload)

    artifacts = manifest_payload.get("artifacts")
    if not isinstance(artifacts, list):
        raise CorpusLoadError("manifest-artifacts-shape", "manifest.json")

    index_by_path: dict[str, dict[str, Any]] = {}
    declared_paths: set[str] = set()
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            raise CorpusLoadError("manifest-artifact-shape", "manifest.json")
        artifact_path = artifact.get("path")
        if not isinstance(artifact_path, str) or not artifact_path:
            raise CorpusLoadError("manifest-artifact-path", "manifest.json")
        if artifact_path in declared_paths:
            raise CorpusLoadError("manifest-artifact-duplicate-path", artifact_path)
        declared_paths.add(artifact_path)
        index_by_path[artifact_path] = artifact

    # Load entries first so fragments can resolve parent references.
    entries_by_id: dict[str, Entry] = {}
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        if artifact.get("kind") == "entry":
            entry = _load_entry(artifact, root, index_by_path)
            entries_by_id[entry.identifier] = entry

    # Load fragments and validate against their parent entries.
    fragments: list[Fragment] = []
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        if artifact.get("kind") == "fragment":
            fragment = _load_fragment(artifact, root, index_by_path, entries_by_id)
            fragments.append(fragment)

    fragments.sort(key=lambda f: f.identifier)
    # Detect unlisted payload files only after declared artifacts have been
    # loaded and their path-safety/shape/hash checks have surfaced their own
    # reason codes. This ordering ensures the most specific failure surfaces
    # first: a malformed manifest artifact path reports its own reason code
    # rather than being masked by the unlisted-payload scan.
    _assert_no_unlisted_payloads(root, declared_paths)
    return Corpus(fragments=tuple(fragments))


# ---------------------------------------------------------------------------
# Manifest-level validation.
# ---------------------------------------------------------------------------


def _validate_manifest_top_level(payload: dict) -> None:
    for key in (
        "schema_version",
        "dataset_id",
        "profile",
        "approval",
        "classification",
        "artifacts",
    ):
        if key not in payload:
            raise CorpusLoadError("manifest-missing-field", f"manifest.json:{key}")
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise CorpusLoadError("manifest-schema-version", "manifest.json")
    if payload.get("dataset_id") != DATASET_ID:
        raise CorpusLoadError("manifest-dataset-id", "manifest.json")
    if payload.get("profile") != DEVELOPMENT_PROFILE:
        raise CorpusLoadError("manifest-profile-not-development", "manifest.json")
    if payload.get("approval") != APPROVED_APPROVAL:
        raise CorpusLoadError("manifest-approval-not-approved", "manifest.json")
    if payload.get("classification") != SYNTHETIC_CLASSIFICATION:
        raise CorpusLoadError("manifest-classification-not-synthetic", "manifest.json")


def _assert_manifest_safe(manifest_path: Path, root: Path) -> None:
    rel = "manifest.json"
    try:
        metadata = os.lstat(manifest_path)
    except FileNotFoundError:
        raise CorpusLoadError("manifest-missing", rel) from None
    except OSError:
        raise CorpusLoadError("manifest-stat-error", rel) from None
    if stat.S_ISLNK(metadata.st_mode):
        raise CorpusLoadError("manifest-symlink", rel)
    if not stat.S_ISREG(metadata.st_mode):
        raise CorpusLoadError("manifest-non-regular", rel)
    try:
        manifest_path.resolve().relative_to(root.resolve())
    except (OSError, ValueError):
        raise CorpusLoadError("manifest-out-of-root", rel) from None


# ---------------------------------------------------------------------------
# Safe path resolution and JSON reading.
# ---------------------------------------------------------------------------


def _safe_artifact_target(root: Path, artifact_path: str) -> Path:
    """Resolve an artifact path to a safe in-root regular file or fail closed."""
    rel = artifact_path
    if artifact_path.startswith("/"):
        raise CorpusLoadError("manifest-artifact-absolute-path", rel)
    candidate = root / artifact_path
    try:
        resolved = candidate.resolve()
        resolved.relative_to(root.resolve())
    except (OSError, ValueError):
        raise CorpusLoadError("manifest-artifact-out-of-root", rel) from None
    try:
        metadata = os.lstat(candidate)
    except FileNotFoundError:
        raise CorpusLoadError("manifest-dangling-reference", rel) from None
    except OSError:
        raise CorpusLoadError("manifest-artifact-stat-error", rel) from None
    if stat.S_ISLNK(metadata.st_mode):
        raise CorpusLoadError("manifest-artifact-symlink", rel)
    if not stat.S_ISREG(metadata.st_mode):
        raise CorpusLoadError("manifest-artifact-non-regular", rel)
    return resolved


def _read_canonical_json(path: Path, root: Path, rel: str) -> Any:
    try:
        raw = path.read_bytes()
    except OSError:
        raise CorpusLoadError("read-error", rel) from None
    if len(raw) > MAX_FILE_BYTES:
        raise CorpusLoadError("resource-limit-file", rel)
    if raw.startswith(b"\xef\xbb\xbf"):
        raise CorpusLoadError("bom-not-allowed", rel)
    if not raw.endswith(b"\n"):
        raise CorpusLoadError("missing-trailing-lf", rel)
    if raw.endswith(b"\n\n"):
        raise CorpusLoadError("extra-trailing-lf", rel)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise CorpusLoadError("decode-error", rel) from None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise CorpusLoadError("json-syntax-error", rel) from None


def _canonical_sha256(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256((encoded + "\n").encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Entry and fragment loading.
# ---------------------------------------------------------------------------


def _load_entry(artifact: dict, root: Path, index_by_path: dict[str, dict[str, Any]]) -> Entry:
    artifact_path = artifact["path"]
    rel = artifact_path
    target = _safe_artifact_target(root, artifact_path)
    payload = _read_canonical_json(target, root, rel)
    if not isinstance(payload, dict):
        raise CorpusLoadError("entry-shape", rel)

    # Manifest <-> payload id consistency.
    manifest_id = artifact.get("id")
    payload_id = payload.get("id")
    if manifest_id != payload_id:
        raise CorpusLoadError("entry-id-mismatch", rel)

    # sha256 integrity: manifest-declared hash must match the canonical file hash.
    declared_sha = artifact.get("sha256")
    actual_sha = _canonical_sha256(payload)
    if not isinstance(declared_sha, str) or declared_sha != actual_sha:
        raise CorpusLoadError("entry-hash-mismatch", rel)

    return validate_entry_payload(payload, rel)


def _load_fragment(
    artifact: dict,
    root: Path,
    index_by_path: dict[str, dict[str, Any]],
    entries_by_id: dict[str, Entry],
) -> Fragment:
    artifact_path = artifact["path"]
    rel = artifact_path
    target = _safe_artifact_target(root, artifact_path)
    payload = _read_canonical_json(target, root, rel)
    if not isinstance(payload, dict):
        raise CorpusLoadError("fragment-shape", rel)

    manifest_id = artifact.get("id")
    payload_id = payload.get("id")
    if manifest_id != payload_id:
        raise CorpusLoadError("fragment-id-mismatch", rel)

    declared_sha = artifact.get("sha256")
    actual_sha = _canonical_sha256(payload)
    if not isinstance(declared_sha, str) or declared_sha != actual_sha:
        raise CorpusLoadError("fragment-hash-mismatch", rel)

    return validate_fragment_payload(payload, rel, entries_by_id)


# ---------------------------------------------------------------------------
# Unlisted payload detection.
# ---------------------------------------------------------------------------


def _assert_no_unlisted_payloads(root: Path, declared_paths: set[str]) -> None:
    """Fail closed when a JSON payload file exists on disk but is not declared."""
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip cache/hidden directories.
        dirnames[:] = sorted(
            d for d in dirnames if d not in {"__pycache__"} and not d.startswith(".")
        )
        for filename in sorted(filenames):
            if filename.startswith("."):
                continue
            if not filename.endswith(".json"):
                # Non-JSON files in the dataset root are out of scope for the
                # corpus loader; the CI validator governs them. Skip here.
                continue
            full = Path(dirpath) / filename
            try:
                rel = full.resolve().relative_to(root.resolve()).as_posix()
            except (OSError, ValueError):
                continue
            if rel == MANIFEST_FILENAME:
                continue
            if rel not in declared_paths:
                raise CorpusLoadError("payload-not-in-manifest", rel)
