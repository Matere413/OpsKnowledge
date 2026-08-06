"""Local development outbound adapter for the approved source inventory.

This adapter is the only component that touches the filesystem for approved
source discovery. It runs ONLY in the ``development`` profile against a
manifest-controlled synthetic fixture kept separate from ``evaluation-dataset/``.
It uses the standard library only and never parses PDF bytes, interprets OCR,
persists state, publishes, rolls back, synchronizes, or calls a provider.

Authority model (Spec R2): the canonical manifest authorizes approval,
classification, collection, path, and expected hash. A filename NEVER proves
approval; a hash mismatch or manifest disagreement rejects the whole snapshot.

Data-flow order (from ``design.md``):

1. profile denial (non-development -> ``profile-not-development``);
2. evaluation-dataset separation guard (root MUST NOT be or live inside it);
3. root and manifest path/link/non-regular checks;
4. manifest read and schema validation;
5. manifest record shape validation (declared-path coverage set);
6. sorted enumeration of on-disk payload files with path/link/non-regular checks;
7. for each declared path (sorted): filename grammar, manifest authority,
   duplicate-identity, read bytes, and hash agreement;
8. final exact coverage and completion gate.

Whole-snapshot fail-closed (Spec R6): any invalid name, duplicate identity,
missing record, unreadable artifact, unsafe path, hash mismatch, invalid
manifest record, or incomplete scan rejects the ENTIRE snapshot. No partial
valid subset is ever returned.

Completeness (Spec R5): a completed zero-artifact scan yields a valid immutable
empty :class:`CompleteSnapshot`; an incomplete scan yields ``scan-incomplete``
and never appears empty.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from backend.features.indexing.domain import (
    ALLOWED_APPROVALS,
    ALLOWED_CLASSIFICATIONS,
    ALLOWED_COLLECTIONS,
    Approval,
    Classification,
    Collection,
    CompleteSnapshot,
    Diagnostic,
    EntryId,
    Language,
    RejectedSnapshot,
    RepositoryRelativePath,
    Revision,
    Sha256,
    SourceArtifact,
    SourceIdentity,
)
from backend.features.indexing.ports import InventoryResult

# Local constants for the manifest schema. They mirror the controlled
# vocabularies in ``domain`` (frozensets) but are pinned here as exact values
# the manifest authority gate checks against.
MANIFEST_FILENAME: Final[str] = "manifest.json"
SCHEMA_VERSION: Final[str] = "1"
SOURCE_ID: Final[str] = "opsknowledge-approved-source-fixture"
APPROVED_APPROVAL: Final[str] = "approved"
SYNTHETIC_CLASSIFICATION: Final[str] = "synthetic"
DEVELOPMENT_PROFILE: Final[str] = "development"
MAX_MANIFEST_BYTES: Final[int] = 1024 * 1024
MAX_FILE_BYTES: Final[int] = 64 * 1024 * 1024
SHA256_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")

# Filename grammar: ``<entry-id>_ESP_REV_<revision>.pdf`` or
# ``<entry-id>_EN_REV_<revision>.pdf``. Tokens are non-empty, unnormalized, and
# contain no path separators, control chars, or whitespace. The entry-id and
# revision tokens are captured; the language suffix maps to the controlled
# vocabulary (ESP -> es, EN -> en).
_FILENAME_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^(?P<entry>[^/\\\x00-\x1f\x7f\s]+)_ESP_REV_(?P<rev>[^/\\\x00-\x1f\x7f\s]+)\.pdf$"
    r"|^(?P<entry_en>[^/\\\x00-\x1f\x7f\s]+)_EN_REV_(?P<rev_en>[^/\\\x00-\x1f\x7f\s]+)\.pdf$"
)

# Map the filename language suffix to the controlled vocabulary value.
_LANGUAGE_BY_SUFFIX: Final[dict[str, str]] = {"ESP": "es", "EN": "en"}


def _diag(code: str, reference: str) -> Diagnostic:
    return Diagnostic(code=code, reference=reference)


def _reject(*diagnostics: Diagnostic) -> RejectedSnapshot:
    return RejectedSnapshot(diagnostics=tuple(diagnostics))


def _sorted_diagnostics(diagnostics: tuple[Diagnostic, ...]) -> tuple[Diagnostic, ...]:
    return tuple(sorted(diagnostics, key=lambda d: (d.reference, d.code)))


@dataclass(frozen=True, slots=True)
class _ParsedFilename:
    """Identity triple parsed from the filename grammar."""

    entry: str
    language: str
    revision: str


@dataclass(frozen=True, slots=True)
class _RecordAuthority:
    """Manifest authority values for one artifact record."""

    collection: str
    approval: str
    classification: str


@dataclass(frozen=True, slots=True)
class _HashOutcome:
    """Result of reading and hashing one artifact against the manifest.

    Exactly one of ``sha256`` (success) or ``failure`` (a diagnostic code) is
    set. Using a small typed result avoids overloading ``None``/sentinel strings
    to discriminate the distinct failure modes (Spec R6 fail-closed).
    """

    sha256: str | None
    failure: str | None


class LocalApprovedSourceRepository:
    """Development-only local filesystem adapter for a complete source snapshot.

    Attributes:
        root: Directory containing ``manifest.json`` and the synthetic source
            artifacts. MUST NOT be ``evaluation-dataset/``.
        profile: Active runtime profile. Only ``development`` is permitted.
    """

    def __init__(self, root: Path, *, profile: str = DEVELOPMENT_PROFILE) -> None:
        self._root = Path(root)
        self._profile = profile

    def inventory(self) -> InventoryResult:
        """Return a complete current snapshot or a whole-snapshot rejection.

        See the module docstring for the explicit data-flow order and the
        fail-closed semantics. This method never returns a partial subset and
        never masks an incomplete or invalid scan as empty.
        """
        # Step 1: profile denial (development-only wiring).
        if self._profile != DEVELOPMENT_PROFILE:
            return _reject(_diag("profile-not-development", ""))

        # Step 2: evaluation-dataset separation guard (by resolved path so
        # symlinks/relatives cannot smuggle it in).
        try:
            resolved_root = self._root.resolve()
        except OSError:
            return _reject(_diag("scan-incomplete", ""))
        if _is_inside_evaluation_dataset(resolved_root):
            return _reject(_diag("unsafe-path", ""))

        # Step 3: root and manifest path/link/non-regular checks.
        root_diag = _check_root_safe(self._root, resolved_root)
        if root_diag is not None:
            return _reject(root_diag)
        manifest_path = self._root / MANIFEST_FILENAME
        manifest_diag = _check_path_safe(
            manifest_path, resolved_root, MANIFEST_FILENAME, link_code="unsafe-link"
        )
        if manifest_diag is not None:
            return _reject(manifest_diag)

        # Step 4: manifest read and schema validation.
        manifest_payload = _read_manifest(manifest_path, MANIFEST_FILENAME)
        if isinstance(manifest_payload, RejectedSnapshot):
            return manifest_payload
        schema_diag = _validate_manifest_schema(manifest_payload, MANIFEST_FILENAME)
        if schema_diag is not None:
            return _reject(schema_diag)

        # Step 5: manifest record shape validation -> declared-path coverage set.
        records_by_path, record_diagnostics = _build_record_index(manifest_payload["artifacts"])
        if record_diagnostics:
            return _reject(*_sorted_diagnostics(tuple(record_diagnostics)))

        # Step 6: sorted enumeration of on-disk payload files.
        on_disk_relpaths: list[str] = []
        enum_diag = _enumerate_payload_files(
            self._root, resolved_root, on_disk_relpaths, MANIFEST_FILENAME
        )
        if enum_diag is not None:
            # Enumeration uncertainty -> scan-incomplete, never empty.
            return _reject(enum_diag)

        # Step 7: for each declared path (sorted), validate filename grammar,
        # manifest authority, duplicate identity, read bytes, and hash.
        artifacts, diagnostics = _scan_declared_artifacts(
            self._root, resolved_root, records_by_path
        )

        # Step 8: exact coverage and completion gate.
        coverage_diag = _check_exact_coverage(on_disk_relpaths, set(records_by_path))
        if coverage_diag is not None:
            diagnostics.append(coverage_diag)

        if diagnostics:
            return _reject(*_sorted_diagnostics(tuple(diagnostics)))

        # Deterministic ascending order by repository-relative path.
        artifacts.sort(key=lambda a: a.path.value)
        return CompleteSnapshot(artifacts=tuple(artifacts))


# ---------------------------------------------------------------------------
# Evaluation-dataset separation guard.
# ---------------------------------------------------------------------------


def _is_inside_evaluation_dataset(resolved_root: Path) -> bool:
    """True when ``resolved_root`` is or lives inside ``evaluation-dataset/``.

    The marker is anchored deterministically from this module's committed
    location (the project root that owns ``evaluation-dataset/``), not from the
    process working directory, so the guard stays correct after ``chdir`` away
    from the project root while a same-named external directory elsewhere
    resolves to a different path and remains allowed (Spec R7).
    """
    marker = Path(__file__).resolve().parent.parent.parent.parent.parent / "evaluation-dataset"
    try:
        resolved_marker = marker.resolve()
    except OSError:
        return False
    try:
        resolved_root.relative_to(resolved_marker)
    except ValueError:
        try:
            resolved_marker.relative_to(resolved_root)
        except ValueError:
            return False
        return True
    return True


# ---------------------------------------------------------------------------
# Step 3: root and per-path safety (no absolute, traversal, symlink, non-regular).
# ---------------------------------------------------------------------------


def _check_root_safe(root: Path, resolved_root: Path) -> Diagnostic | None:
    rel = ""
    try:
        root_stat = os.lstat(root)
    except OSError:
        return _diag("scan-incomplete", rel)
    if stat.S_ISLNK(root_stat.st_mode):
        return _diag("unsafe-link", rel)
    if not stat.S_ISDIR(root_stat.st_mode):
        return _diag("source-non-regular", rel)
    return None


def _check_path_safe(
    path: Path, resolved_root: Path, rel: str, *, link_code: str
) -> Diagnostic | None:
    """Reject absolute, traversal, symlink, and non-regular targets before reads."""
    if rel.startswith("/"):
        return _diag("unsafe-path", rel)
    if ".." in Path(rel).parts:
        return _diag("unsafe-path", rel)
    candidate = resolved_root / rel
    try:
        metadata = os.lstat(candidate)
    except FileNotFoundError:
        return _diag("coverage-missing", rel)
    except OSError:
        return _diag("source-unreadable", rel)
    if stat.S_ISLNK(metadata.st_mode):
        return _diag(link_code, rel)
    if not stat.S_ISREG(metadata.st_mode):
        return _diag("source-non-regular", rel)
    # Resolve and confirm it stays inside the root (no traversal escape).
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError):
        return _diag("unsafe-path", rel)
    return None


# ---------------------------------------------------------------------------
# Step 4: manifest read (canonical JSON, no BOM) and schema validation.
# ---------------------------------------------------------------------------


def _read_manifest(path: Path, rel: str) -> RejectedSnapshot | dict[str, Any]:
    try:
        raw = path.read_bytes()
    except OSError:
        return _reject(_diag("source-unreadable", rel))
    if len(raw) > MAX_MANIFEST_BYTES:
        return _reject(_diag("manifest-invalid", rel))
    if raw.startswith(b"\xef\xbb\xbf"):
        return _reject(_diag("manifest-invalid", rel))
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return _reject(_diag("manifest-invalid", rel))
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return _reject(_diag("manifest-invalid", rel))
    return payload


def _validate_manifest_schema(payload: object, rel: str) -> Diagnostic | None:
    if not isinstance(payload, dict):
        return _diag("manifest-invalid", rel)
    for key in (
        "schema_version",
        "source_id",
        "profile",
        "approval",
        "classification",
        "artifacts",
    ):
        if key not in payload:
            return _diag("manifest-invalid", rel)
    if payload.get("schema_version") != SCHEMA_VERSION:
        return _diag("manifest-invalid", rel)
    if payload.get("source_id") != SOURCE_ID:
        return _diag("manifest-invalid", rel)
    if payload.get("profile") != DEVELOPMENT_PROFILE:
        return _diag("manifest-invalid", rel)
    if payload.get("approval") != APPROVED_APPROVAL:
        return _diag("manifest-invalid", rel)
    if payload.get("classification") != SYNTHETIC_CLASSIFICATION:
        return _diag("manifest-invalid", rel)
    if not isinstance(payload.get("artifacts"), list):
        return _diag("manifest-invalid", rel)
    return None


# ---------------------------------------------------------------------------
# Step 5: manifest record shape validation -> declared-path coverage set.
# ---------------------------------------------------------------------------


def _build_record_index(
    artifacts_field: object,
) -> tuple[dict[str, dict[str, Any]], list[Diagnostic]]:
    """Build a declared-path -> record index and collect shape diagnostics.

    A duplicate declared path is a ``manifest-invalid`` rejection. Record
    authority (collection/approval/classification) is validated later, when the
    on-disk file is known to exist and be safe.
    """
    records_by_path: dict[str, dict[str, Any]] = {}
    diagnostics: list[Diagnostic] = []
    manifest_rel = MANIFEST_FILENAME
    for record in artifacts_field:  # type: ignore[union-attr]
        if not isinstance(record, dict):
            diagnostics.append(_diag("manifest-invalid", manifest_rel))
            continue
        path = record.get("path")
        if not isinstance(path, str) or not path:
            diagnostics.append(_diag("manifest-invalid", manifest_rel))
            continue
        if path in records_by_path:
            diagnostics.append(_diag("manifest-invalid", path))
            continue
        records_by_path[path] = record
    return records_by_path, diagnostics


# ---------------------------------------------------------------------------
# Step 6: sorted enumeration of on-disk payload files.
# ---------------------------------------------------------------------------


def _enumerate_payload_files(
    root: Path,
    resolved_root: Path,
    out_relpaths: list[str],
    manifest_rel: str,
) -> Diagnostic | None:
    """Walk the fixture root and collect safe regular PDF files, sorted.

    Returns a ``scan-incomplete`` diagnostic on any traversal/stat uncertainty
    so an incomplete scan never appears empty. An undeclared symlinked or
    non-regular PDF rejects the whole snapshot with ``unsafe-link`` or
    ``source-non-regular``; a silent skip would let an unsafe payload masquerade
    as a completed scan (Spec R6 whole-snapshot fail-closed).
    """
    traversal_errors: list[OSError] = []

    def _on_walk_error(error: OSError) -> None:
        traversal_errors.append(error)

    for dirpath, dirnames, filenames in os.walk(root, onerror=_on_walk_error):
        # Skip cache/hidden directories deterministically.
        dirnames[:] = sorted(d for d in dirnames if not d.startswith(".") and d != "__pycache__")
        for filename in sorted(filenames):
            if filename.startswith("."):
                continue
            full = Path(dirpath) / filename
            try:
                rel = full.resolve().relative_to(resolved_root).as_posix()
            except (OSError, ValueError):
                return _diag("unsafe-path", "")
            if rel == manifest_rel:
                continue
            # Only PDF payload files are in scope for the source fixture.
            if not filename.endswith(".pdf"):
                # Non-PDF files are not source artifacts; ignore them so a
                # completed zero-PDF scan can still be a valid empty snapshot.
                continue
            try:
                metadata = os.lstat(full)
            except OSError:
                return _diag("scan-incomplete", rel)
            if stat.S_ISLNK(metadata.st_mode):
                # An undeclared symlinked PDF is unsafe; reject the whole
                # snapshot rather than silently skipping it.
                return _diag("unsafe-link", rel)
            if not stat.S_ISREG(metadata.st_mode):
                # An undeclared non-regular PDF is unsafe; reject the whole
                # snapshot rather than silently skipping it.
                return _diag("source-non-regular", rel)
            out_relpaths.append(rel)
    if traversal_errors:
        # A directory traversal failure (e.g. permission denied) would otherwise
        # look like a completed scan; surface it as scan-incomplete instead.
        return _diag("scan-incomplete", "")
    return None


# ---------------------------------------------------------------------------
# Step 7: scan each declared artifact (filename, authority, dup, read, hash).
# ---------------------------------------------------------------------------


def _scan_declared_artifacts(
    root: Path,
    resolved_root: Path,
    records_by_path: dict[str, dict[str, Any]],
) -> tuple[list[SourceArtifact], list[Diagnostic]]:
    """Validate and read each declared artifact, collecting diagnostics.

    A failing artifact appends a diagnostic and is skipped; because the coverage
    gate runs after, any failure triggers a whole-snapshot rejection.
    """
    artifacts: list[SourceArtifact] = []
    diagnostics: list[Diagnostic] = []
    seen_identities: set[tuple[str, str, str, str]] = set()
    for rel in sorted(records_by_path):
        record = records_by_path[rel]
        artifact_path = root / rel
        # Path safety for the artifact target (the manifest path may be unsafe
        # even if the manifest itself was safe).
        path_diag = _check_path_safe(artifact_path, resolved_root, rel, link_code="unsafe-link")
        if path_diag is not None:
            diagnostics.append(path_diag)
            continue
        parsed = _parse_filename(rel)
        if parsed is None:
            diagnostics.append(_diag("filename-invalid", rel))
            continue
        authority = _check_record_authority(record, rel)
        if authority is None:
            diagnostics.append(_diag("manifest-invalid", rel))
            continue
        identity_key = (authority.collection, parsed.entry, parsed.language, parsed.revision)
        if identity_key in seen_identities:
            diagnostics.append(_diag("identity-duplicate", rel))
            continue
        read_outcome = _read_and_hash(artifact_path, rel, record)
        if read_outcome.failure is not None:
            diagnostics.append(_diag(read_outcome.failure, rel))
            continue
        verified_hash = read_outcome.sha256
        assert verified_hash is not None  # invariant: sha256 set when failure is None
        # Build the immutable artifact and record the identity.
        seen_identities.add(identity_key)
        artifacts.append(
            SourceArtifact(
                path=RepositoryRelativePath(value=rel),
                identity=SourceIdentity(
                    collection=Collection(value=authority.collection),
                    entry=EntryId(value=parsed.entry),
                    language=Language(value=parsed.language),
                    revision=Revision(value=parsed.revision),
                ),
                approval=Approval(value=authority.approval),
                classification=Classification(value=authority.classification),
                sha256=Sha256(value=verified_hash),
            )
        )
    return artifacts, diagnostics


def _parse_filename(rel: str) -> _ParsedFilename | None:
    """Parse the basename into (entry, language, revision) or return None.

    The filename supplies identity only; it never proves approval (Spec R3).
    """
    basename = Path(rel).name
    match = _FILENAME_PATTERN.match(basename)
    if match is None:
        return None
    if match.group("entry") is not None:
        return _ParsedFilename(
            entry=match.group("entry"),
            language=_LANGUAGE_BY_SUFFIX["ESP"],
            revision=match.group("rev"),
        )
    return _ParsedFilename(
        entry=match.group("entry_en"),
        language=_LANGUAGE_BY_SUFFIX["EN"],
        revision=match.group("rev_en"),
    )


def _check_record_authority(record: dict[str, Any], rel: str) -> _RecordAuthority | None:
    """Validate manifest authority for collection/approval/classification.

    Returns the authority triple on success or ``None`` (the caller emits a
    ``manifest-invalid`` diagnostic). The manifest is the policy authority; the
    filename does not override it (Spec R2).
    """
    collection = record.get("collection")
    approval = record.get("approval")
    classification = record.get("classification")
    if not isinstance(collection, str) or collection not in ALLOWED_COLLECTIONS:
        return None
    if not isinstance(approval, str) or approval not in ALLOWED_APPROVALS:
        return None
    if not isinstance(classification, str) or classification not in ALLOWED_CLASSIFICATIONS:
        return None
    return _RecordAuthority(collection=collection, approval=approval, classification=classification)


def _read_and_hash(path: Path, rel: str, record: dict[str, Any]) -> _HashOutcome:
    """Read bytes and compare SHA-256 against the manifest hash.

    Returns a :class:`_HashOutcome` whose ``sha256`` is the verified hash on
    success or whose ``failure`` carries the diagnostic code on failure
    (``manifest-invalid``, ``source-unreadable``, or ``hash-mismatch``).
    """
    declared = record.get("sha256")
    if not isinstance(declared, str) or not SHA256_PATTERN.match(declared):
        return _HashOutcome(sha256=None, failure="manifest-invalid")
    try:
        raw = path.read_bytes()
    except OSError:
        return _HashOutcome(sha256=None, failure="source-unreadable")
    if len(raw) > MAX_FILE_BYTES:
        return _HashOutcome(sha256=None, failure="source-unreadable")
    actual = hashlib.sha256(raw).hexdigest()
    if actual != declared:
        return _HashOutcome(sha256=None, failure="hash-mismatch")
    return _HashOutcome(sha256=actual, failure=None)


# ---------------------------------------------------------------------------
# Step 8: exact coverage and completion gate.
# ---------------------------------------------------------------------------


def _check_exact_coverage(
    on_disk_relpaths: list[str], declared_paths: set[str]
) -> Diagnostic | None:
    on_disk = set(on_disk_relpaths)
    missing = declared_paths - on_disk
    if missing:
        # A declared artifact is not present/readable on disk.
        return _diag("coverage-missing", sorted(missing)[0])
    unlisted = on_disk - declared_paths
    if unlisted:
        # A disk artifact is not declared in the manifest.
        return _diag("coverage-unlisted", sorted(unlisted)[0])
    return None


__all__ = [
    "LocalApprovedSourceRepository",
]
