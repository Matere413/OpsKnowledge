"""Behavior-first tests for the local approved source scanner.

Work Unit 2 (PR 2) proves the development-only local adapter against the spec
requirements the contracts unit (PR 1) intentionally did not cover:

* Manifest authority — a filename cannot override policy (R2 / Scenario: Filename
  cannot override policy).
* Safe paths and deterministic output — escaping/changed-order paths are
  rejected and valid output ordering stays byte-stable (R4 / Scenario: Unsafe
  paths fail consistently).
* Explicit complete-scan semantics — a completed zero-artifact scan returns a
  valid empty snapshot while an incomplete scan never appears empty (R5 /
  Scenario: Empty success differs from partial failure).
* Whole-snapshot fail-closed validation — one bad artifact rejects all and no
  partial subset is returned (R6 / Scenario: One bad artifact rejects all).

These tests build temporary fixtures programmatically with ``tmp_path`` and the
standard library only. They never touch the real ``approved-source-fixture/``
except the committed-fixture golden test, and they never call a provider,
database, OCR, or network.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import fields
from pathlib import Path
from typing import Any

from backend.features.indexing.adapters.local_repository import (
    LocalApprovedSourceRepository,
)
from backend.features.indexing.domain import (
    CompleteSnapshot,
    Diagnostic,
    RejectedSnapshot,
    SourceArtifact,
)

# ---------------------------------------------------------------------------
# Fixture/manifest builders (deterministic, standard library only).
# ---------------------------------------------------------------------------

SCHEMA_VERSION = "1"
SOURCE_ID = "opsknowledge-approved-source-fixture"
MANIFEST_NAME = "manifest.json"
RUNBOOKS_DIR = "runbooks"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _synthetic_pdf(body: str = "opsknowledge synthetic source artifact") -> bytes:
    """Opaque synthetic PDF-shaped bytes (never parsed by the adapter)."""
    return b"%PDF-1.4\n%" + body.encode("utf-8") + b"\n%%EOF\n"


def _write_pdf(root: Path, rel: str, body: str = "opsknowledge synthetic source artifact") -> str:
    """Write a synthetic PDF at ``root/rel`` and return its SHA-256."""
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = _synthetic_pdf(body)
    path.write_bytes(raw)
    return _sha256(raw)


def _manifest_record(rel: str, sha: str, collection: str = "runbooks") -> dict[str, Any]:
    return {
        "path": rel,
        "collection": collection,
        "approval": "approved",
        "classification": "synthetic",
        "sha256": sha,
    }


def _manifest(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "source_id": SOURCE_ID,
        "profile": "development",
        "approval": "approved",
        "classification": "synthetic",
        "artifacts": records,
    }


def _write_manifest(root: Path, payload: dict[str, Any]) -> None:
    (root / MANIFEST_NAME).write_text(json.dumps(payload), encoding="utf-8")


def _bilingual_fixture(root: Path) -> dict[str, Any]:
    """Build the canonical bilingual fixture and return its manifest payload."""
    esp_rel = f"{RUNBOOKS_DIR}/runbook-1_ESP_REV_2.pdf"
    en_rel = f"{RUNBOOKS_DIR}/runbook-1_EN_REV_7.pdf"
    esp_sha = _write_pdf(root, esp_rel, "spanish revision 2")
    en_sha = _write_pdf(root, en_rel, "english revision 7")
    payload = _manifest([_manifest_record(esp_rel, esp_sha), _manifest_record(en_rel, en_sha)])
    _write_manifest(root, payload)
    return payload


def _repo(root: Path, *, profile: str = "development") -> LocalApprovedSourceRepository:
    return LocalApprovedSourceRepository(root, profile=profile)


def _codes(result: object) -> list[str]:
    if isinstance(result, RejectedSnapshot):
        return [d.code for d in result.diagnostics]
    return []


class _ExpectRaise:
    """Plain context manager asserting a callable body raises (not pytest.raises).

    The repo focused-test guard forbids ``pytest.raises``; this helper provides
    equivalent semantics: ``with _ExpectRaise(SomeError): body`` asserts the body
    raises the expected exception type(s). See the convention in
    ``test_technical_grounding_gates_report.py``.
    """

    def __init__(self, expected: type[BaseException] | tuple[type[BaseException], ...]) -> None:
        self._expected = expected
        self._raised: BaseException | None = None

    def __enter__(self) -> _ExpectRaise:
        return self

    def __exit__(self, exc_type: type | None, exc: BaseException | None, tb: Any) -> bool:
        if exc is None:
            raise AssertionError(f"expected {self._expected}, no exception raised")
        if isinstance(exc, self._expected):
            self._raised = exc
            return True
        raise AssertionError(f"expected {self._expected}, got {type(exc).__name__}") from exc


# ---------------------------------------------------------------------------
# Committed-fixture golden: the real synthetic fixture scans to a complete
# bilingual snapshot (anchors the temporary-fixture tests to a real artifact).
# ---------------------------------------------------------------------------


def test_committed_fixture_scans_to_complete_bilingual_snapshot(project_root: Path) -> None:
    """The committed ``approved-source-fixture`` yields a complete snapshot."""
    repo = _repo(project_root / "approved-source-fixture")
    result = repo.inventory()
    assert isinstance(result, CompleteSnapshot)
    assert len(result.artifacts) == 2
    identities = {
        (a.identity.entry.value, a.identity.language.value, a.identity.revision.value)
        for a in result.artifacts
    }
    assert identities == {("runbook-1", "es", "2"), ("runbook-1", "en", "7")}
    # Stably ordered by ascending repository-relative path.
    paths = [a.path.value for a in result.artifacts]
    assert paths == sorted(paths)
    # Hashes match the manifest exactly.
    manifest = json.loads((project_root / "approved-source-fixture" / MANIFEST_NAME).read_bytes())
    by_path = {r["path"]: r["sha256"] for r in manifest["artifacts"]}
    for artifact in result.artifacts:
        assert artifact.sha256.value == by_path[artifact.path.value]


# ---------------------------------------------------------------------------
# R2 / Scenario: Filename cannot override policy — manifest authority.
# ---------------------------------------------------------------------------


def test_manifest_authority_rejects_unapproved_record(tmp_path: Path) -> None:
    """A validly named artifact with an unapproved manifest record is rejected."""
    root = tmp_path / "source"
    root.mkdir()
    esp_rel = f"{RUNBOOKS_DIR}/runbook-1_ESP_REV_2.pdf"
    sha = _write_pdf(root, esp_rel)
    payload = _manifest([_manifest_record(esp_rel, sha)])
    payload["artifacts"][0]["approval"] = "draft"  # not approved
    _write_manifest(root, payload)
    result = _repo(root).inventory()
    assert isinstance(result, RejectedSnapshot)
    assert "manifest-invalid" in _codes(result)
    assert not isinstance(result, CompleteSnapshot)


def test_manifest_authority_rejects_wrong_classification(tmp_path: Path) -> None:
    """A non-synthetic classification in the manifest record is rejected."""
    root = tmp_path / "source"
    root.mkdir()
    esp_rel = f"{RUNBOOKS_DIR}/runbook-1_ESP_REV_2.pdf"
    sha = _write_pdf(root, esp_rel)
    payload = _manifest([_manifest_record(esp_rel, sha)])
    payload["artifacts"][0]["classification"] = "corporate"  # not synthetic
    _write_manifest(root, payload)
    result = _repo(root).inventory()
    assert isinstance(result, RejectedSnapshot)
    assert "manifest-invalid" in _codes(result)


def test_hash_mismatch_rejects_whole_snapshot(tmp_path: Path) -> None:
    """A declared hash that disagrees with the file bytes rejects everything."""
    root = tmp_path / "source"
    root.mkdir()
    esp_rel = f"{RUNBOOKS_DIR}/runbook-1_ESP_REV_2.pdf"
    _write_pdf(root, esp_rel, "actual body")
    payload = _manifest([_manifest_record(esp_rel, "0" * 64)])  # wrong hash
    _write_manifest(root, payload)
    result = _repo(root).inventory()
    assert isinstance(result, RejectedSnapshot)
    assert "hash-mismatch" in _codes(result)


def test_manifest_profile_must_be_development(tmp_path: Path) -> None:
    """A manifest declaring a non-development profile is rejected."""
    root = tmp_path / "source"
    root.mkdir()
    payload = _manifest([])
    payload["profile"] = "production"
    _write_manifest(root, payload)
    result = _repo(root).inventory()
    assert isinstance(result, RejectedSnapshot)
    assert "manifest-invalid" in _codes(result)


def test_non_development_profile_denies_before_filesystem(tmp_path: Path) -> None:
    """A non-development profile is denied before any filesystem scan."""
    root = tmp_path / "source"
    root.mkdir()
    _bilingual_fixture(root)
    result = _repo(root, profile="production").inventory()
    assert isinstance(result, RejectedSnapshot)
    assert result.diagnostics[0].code == "profile-not-development"


# ---------------------------------------------------------------------------
# R3 (via adapter): bilingual revisions remain distinct.
# ---------------------------------------------------------------------------


def test_bilingual_revisions_are_distinct_in_one_snapshot(tmp_path: Path) -> None:
    """ES revision 2 and EN revision 7 are both accepted as distinct identities."""
    root = tmp_path / "source"
    root.mkdir()
    _bilingual_fixture(root)
    result = _repo(root).inventory()
    assert isinstance(result, CompleteSnapshot)
    assert len(result.artifacts) == 2
    assert {a.identity.language.value for a in result.artifacts} == {"es", "en"}


# ---------------------------------------------------------------------------
# R4 / Scenario: Unsafe paths fail consistently + deterministic ordering.
# ---------------------------------------------------------------------------


def test_absolute_path_in_manifest_is_rejected(tmp_path: Path) -> None:
    """An absolute path in the manifest is rejected as unsafe."""
    root = tmp_path / "source"
    root.mkdir()
    payload = _manifest([_manifest_record("/etc/passwd", "0" * 64)])
    _write_manifest(root, payload)
    result = _repo(root).inventory()
    assert isinstance(result, RejectedSnapshot)
    assert "unsafe-path" in _codes(result)


def test_traversal_path_in_manifest_is_rejected(tmp_path: Path) -> None:
    """A ``..`` traversal path in the manifest is rejected as unsafe."""
    root = tmp_path / "source"
    root.mkdir()
    payload = _manifest([_manifest_record("../escape.pdf", "0" * 64)])
    _write_manifest(root, payload)
    result = _repo(root).inventory()
    assert isinstance(result, RejectedSnapshot)
    assert "unsafe-path" in _codes(result)


def test_output_is_deterministic_across_scans(tmp_path: Path) -> None:
    """Two scans of the same fixture produce byte-stable artifact ordering."""
    root = tmp_path / "source"
    root.mkdir()
    _bilingual_fixture(root)
    first = _repo(root).inventory()
    second = _repo(root).inventory()
    assert isinstance(first, CompleteSnapshot)
    assert isinstance(second, CompleteSnapshot)
    assert [a.path.value for a in first.artifacts] == [a.path.value for a in second.artifacts]
    assert first == second


def test_diagnostics_are_sorted_by_reference_then_code(tmp_path: Path) -> None:
    """Diagnostics are stably sorted by reference then code (R4)."""
    root = tmp_path / "source"
    root.mkdir()
    # Two declared artifacts that both fail (wrong hashes) so two diagnostics.
    esp_rel = f"{RUNBOOKS_DIR}/runbook-1_ESP_REV_2.pdf"
    en_rel = f"{RUNBOOKS_DIR}/runbook-1_EN_REV_7.pdf"
    _write_pdf(root, esp_rel, "body a")
    _write_pdf(root, en_rel, "body b")
    payload = _manifest([_manifest_record(esp_rel, "0" * 64), _manifest_record(en_rel, "1" * 64)])
    _write_manifest(root, payload)
    result = _repo(root).inventory()
    assert isinstance(result, RejectedSnapshot)
    refs = [d.reference for d in result.diagnostics]
    assert refs == sorted(refs)


def test_diagnostics_omit_unsafe_content(tmp_path: Path) -> None:
    """No diagnostic carries an absolute path, bytes, or content."""
    root = tmp_path / "source"
    root.mkdir()
    esp_rel = f"{RUNBOOKS_DIR}/runbook-1_ESP_REV_2.pdf"
    _write_pdf(root, esp_rel, "secret body")
    payload = _manifest([_manifest_record(esp_rel, "0" * 64)])
    _write_manifest(root, payload)
    result = _repo(root).inventory()
    assert isinstance(result, RejectedSnapshot)
    for d in result.diagnostics:
        assert isinstance(d, Diagnostic)
        assert str(tmp_path) not in d.reference
        assert "secret" not in d.reference
        assert "secret" not in d.code


def test_rejection_returns_only_safe_diagnostics_and_no_partial_snapshot(tmp_path: Path) -> None:
    """Rejected results expose no partial artifact or sensitive source payload."""
    root = tmp_path / "source"
    root.mkdir()
    rel = f"{RUNBOOKS_DIR}/runbook-1_ESP_REV_2.pdf"
    document_text = "SECRET-DOCUMENT-TEXT"
    provider_payload = "provider-payload credential-value password-value"
    raw = _synthetic_pdf(f"{document_text} {provider_payload}")
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    _write_manifest(root, _manifest([_manifest_record(rel, "0" * 64)]))

    result = _repo(root).inventory()

    assert isinstance(result, RejectedSnapshot)
    assert not isinstance(result, CompleteSnapshot)
    assert not hasattr(result, "artifacts")
    assert tuple(field.name for field in fields(result)) == ("diagnostics",)
    assert all(
        tuple(field.name for field in fields(d)) == ("code", "reference")
        for d in result.diagnostics
    )
    rendered = repr(result)
    for forbidden in (
        document_text,
        provider_payload,
        "b'%PDF",
        str(tmp_path),
        "absolute_path",
        "bytes",
    ):
        assert forbidden not in rendered


# ---------------------------------------------------------------------------
# R5 / Scenario: Empty success differs from partial failure.
# ---------------------------------------------------------------------------


def test_completed_empty_fixture_returns_valid_empty_snapshot(tmp_path: Path) -> None:
    """A completed scan of a zero-artifact fixture yields a valid empty snapshot."""
    root = tmp_path / "source"
    root.mkdir()
    _write_manifest(root, _manifest([]))
    result = _repo(root).inventory()
    assert isinstance(result, CompleteSnapshot)
    assert result.artifacts == ()


def test_unlisted_on_disk_artifact_rejects_whole_snapshot(tmp_path: Path) -> None:
    """An on-disk PDF not declared in the manifest rejects the whole snapshot."""
    root = tmp_path / "source"
    root.mkdir()
    _write_manifest(root, _manifest([]))
    # An undeclared PDF on disk.
    _write_pdf(root, f"{RUNBOOKS_DIR}/runbook-1_ESP_REV_2.pdf", "orphan")
    result = _repo(root).inventory()
    assert isinstance(result, RejectedSnapshot)
    assert "coverage-unlisted" in _codes(result)


def test_declared_artifact_missing_on_disk_rejects(tmp_path: Path) -> None:
    """A declared artifact absent from disk is rejected as coverage-missing."""
    root = tmp_path / "source"
    root.mkdir()
    payload = _manifest([_manifest_record(f"{RUNBOOKS_DIR}/runbook-1_ESP_REV_2.pdf", "0" * 64)])
    _write_manifest(root, payload)
    result = _repo(root).inventory()
    assert isinstance(result, RejectedSnapshot)
    assert "coverage-missing" in _codes(result)


def test_incomplete_scan_never_appears_empty(tmp_path: Path) -> None:
    """A scan blocked by enumeration uncertainty returns no empty snapshot."""
    root = tmp_path / "source"
    root.mkdir()
    _write_manifest(root, _manifest([]))
    # A dangling symlink in the payload path makes enumeration skip it, but the
    # coverage gate still runs; here the fixture is genuinely empty so it stays
    # a valid empty snapshot. The real incompleteness case is a declared-but-
    # missing file (coverage-missing), proven above. This test asserts that an
    # empty completed scan is NOT produced when a declared artifact is missing.
    payload = _manifest([_manifest_record(f"{RUNBOOKS_DIR}/runbook-1_ESP_REV_2.pdf", "0" * 64)])
    _write_manifest(root, payload)
    result = _repo(root).inventory()
    assert not isinstance(result, CompleteSnapshot)
    assert isinstance(result, RejectedSnapshot)


# ---------------------------------------------------------------------------
# R6 / Scenario: One bad artifact rejects all — whole-snapshot fail-closed.
# ---------------------------------------------------------------------------


def test_one_bad_artifact_rejects_all_and_returns_no_partial(tmp_path: Path) -> None:
    """One unreadable artifact among valid ones rejects the whole snapshot."""
    root = tmp_path / "source"
    root.mkdir()
    good_rel = f"{RUNBOOKS_DIR}/runbook-1_ESP_REV_2.pdf"
    bad_rel = f"{RUNBOOKS_DIR}/runbook-1_EN_REV_7.pdf"
    good_sha = _write_pdf(root, good_rel, "good")
    # Bad artifact: declared hash that won't match.
    payload = _manifest([_manifest_record(good_rel, good_sha), _manifest_record(bad_rel, "9" * 64)])
    _write_pdf(root, bad_rel, "different body")
    _write_manifest(root, payload)
    result = _repo(root).inventory()
    assert isinstance(result, RejectedSnapshot)
    assert "hash-mismatch" in _codes(result)
    # No partial subset is returned.
    assert not isinstance(result, CompleteSnapshot)


def test_duplicate_identity_rejects_whole_snapshot(tmp_path: Path) -> None:
    """Two records with the same identity reject the whole snapshot."""
    root = tmp_path / "source"
    root.mkdir()
    rel = f"{RUNBOOKS_DIR}/runbook-1_ESP_REV_2.pdf"
    sha = _write_pdf(root, rel, "body")
    # Two records declare the same path/identity — shape validation rejects.
    payload = _manifest([_manifest_record(rel, sha), _manifest_record(rel, sha)])
    _write_manifest(root, payload)
    result = _repo(root).inventory()
    assert isinstance(result, RejectedSnapshot)
    assert "manifest-invalid" in _codes(result)


def test_duplicate_identity_across_paths_rejects_whole_snapshot(tmp_path: Path) -> None:
    """The same collection/entry/language/revision cannot occur twice."""
    root = tmp_path / "source"
    root.mkdir()
    primary_rel = f"{RUNBOOKS_DIR}/primary/runbook-1_ESP_REV_2.pdf"
    archive_rel = f"{RUNBOOKS_DIR}/archive/runbook-1_ESP_REV_2.pdf"
    primary_sha = _write_pdf(root, primary_rel, "primary body")
    archive_sha = _write_pdf(root, archive_rel, "archive body")
    _write_manifest(
        root,
        _manifest(
            [
                _manifest_record(primary_rel, primary_sha),
                _manifest_record(archive_rel, archive_sha),
            ]
        ),
    )

    result = _repo(root).inventory()

    assert isinstance(result, RejectedSnapshot)
    assert "identity-duplicate" in _codes(result)
    assert not isinstance(result, CompleteSnapshot)


def test_invalid_filename_rejects_whole_snapshot(tmp_path: Path) -> None:
    """A file whose name breaks the grammar rejects the whole snapshot."""
    root = tmp_path / "source"
    root.mkdir()
    rel = f"{RUNBOOKS_DIR}/not-a-valid-name.pdf"
    sha = _write_pdf(root, rel, "body")
    payload = _manifest([_manifest_record(rel, sha)])
    _write_manifest(root, payload)
    result = _repo(root).inventory()
    assert isinstance(result, RejectedSnapshot)
    assert "filename-invalid" in _codes(result)


def test_symlink_artifact_is_rejected(tmp_path: Path) -> None:
    """A symlinked declared artifact is rejected as unsafe-link."""
    root = tmp_path / "source"
    root.mkdir()
    target_rel = f"{RUNBOOKS_DIR}/runbook-1_ESP_REV_2.pdf"
    link_rel = f"{RUNBOOKS_DIR}/runbook-1_EN_REV_7.pdf"
    sha = _write_pdf(root, target_rel, "real body")
    (root / link_rel).parent.mkdir(parents=True, exist_ok=True)
    (root / link_rel).symlink_to(root / target_rel)
    payload = _manifest([_manifest_record(link_rel, sha)])
    _write_manifest(root, payload)
    result = _repo(root).inventory()
    assert isinstance(result, RejectedSnapshot)
    assert "unsafe-link" in _codes(result)


def test_non_regular_artifact_is_rejected(tmp_path: Path) -> None:
    """A non-regular declared artifact (FIFO) is rejected."""
    root = tmp_path / "source"
    root.mkdir()
    rel = f"{RUNBOOKS_DIR}/runbook-1_ESP_REV_2.pdf"
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    os.mkfifo(root / rel)
    payload = _manifest([_manifest_record(rel, "0" * 64)])
    _write_manifest(root, payload)
    result = _repo(root).inventory()
    assert isinstance(result, RejectedSnapshot)
    assert "source-non-regular" in _codes(result)


def test_unreadable_artifact_rejects_whole_snapshot(tmp_path: Path) -> None:
    """An artifact that cannot be read rejects the whole snapshot."""
    root = tmp_path / "source"
    root.mkdir()
    rel = f"{RUNBOOKS_DIR}/runbook-1_ESP_REV_2.pdf"
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = _synthetic_pdf("body")
    path.write_bytes(raw)
    sha = _sha256(raw)
    # Remove read permission to force a read failure.
    path.chmod(0o000)
    payload = _manifest([_manifest_record(rel, sha)])
    _write_manifest(root, payload)
    try:
        result = _repo(root).inventory()
    finally:
        path.chmod(0o600)
    assert isinstance(result, RejectedSnapshot)
    assert "source-unreadable" in _codes(result)


def test_malformed_manifest_json_rejects(tmp_path: Path) -> None:
    """A manifest that is not valid JSON rejects as manifest-invalid."""
    root = tmp_path / "source"
    root.mkdir()
    (root / MANIFEST_NAME).write_text("{not valid json", encoding="utf-8")
    result = _repo(root).inventory()
    assert isinstance(result, RejectedSnapshot)
    assert "manifest-invalid" in _codes(result)


def test_missing_manifest_rejects(tmp_path: Path) -> None:
    """A missing manifest is rejected (coverage-missing for the manifest path)."""
    root = tmp_path / "source"
    root.mkdir()
    result = _repo(root).inventory()
    assert isinstance(result, RejectedSnapshot)
    assert "coverage-missing" in _codes(result)


def test_result_artifacts_are_immutable(tmp_path: Path) -> None:
    """Returned artifacts are immutable metadata (frozen value objects)."""
    root = tmp_path / "source"
    root.mkdir()
    _bilingual_fixture(root)
    result = _repo(root).inventory()
    assert isinstance(result, CompleteSnapshot)
    artifact = result.artifacts[0]
    assert isinstance(artifact, SourceArtifact)
    # Frozen dataclasses raise FrozenInstanceError on direct mutation (R1).
    with _ExpectRaise(Exception):
        artifact.path = artifact.path  # type: ignore[misc]


def test_non_pdf_files_are_ignored_in_empty_scan(tmp_path: Path) -> None:
    """Non-PDF files do not break a completed empty scan."""
    root = tmp_path / "source"
    root.mkdir()
    _write_manifest(root, _manifest([]))
    (root / "README.txt").write_text("not a source artifact", encoding="utf-8")
    result = _repo(root).inventory()
    assert isinstance(result, CompleteSnapshot)
    assert result.artifacts == ()


# ---------------------------------------------------------------------------
# R7 (adapter side): evaluation-dataset separation guard.
# ---------------------------------------------------------------------------


def test_real_evaluation_dataset_root_is_rejected(project_root: Path) -> None:
    """The project's real ``evaluation-dataset/`` root is rejected as unsafe.

    The guard protects the committed evaluation corpus from being scanned as an
    approved-source fixture; it anchors the marker to this module's committed
    location (the project root that owns ``evaluation-dataset/``) so it always
    points at the real corpus regardless of the working directory (Spec R7).
    """
    repo = _repo(project_root / "evaluation-dataset")
    result = repo.inventory()
    assert isinstance(result, RejectedSnapshot)
    assert "unsafe-path" in _codes(result)


def test_same_named_directory_elsewhere_is_allowed(tmp_path: Path) -> None:
    """A directory merely named ``evaluation-dataset`` elsewhere is not rejected.

    The guard protects the real corpus by resolved path, not any same-named
    directory on disk; this confirms the guard is not over-strict.
    """
    root = tmp_path / "evaluation-dataset" / "approved-source-fixture"
    root.mkdir(parents=True)
    _write_manifest(root, _manifest([]))
    result = _repo(root).inventory()
    assert isinstance(result, CompleteSnapshot)
    assert result.artifacts == ()


def test_symlinked_root_is_rejected(tmp_path: Path) -> None:
    """A symlinked fixture root is rejected as unsafe-link."""
    real = tmp_path / "real-source"
    real.mkdir()
    _write_manifest(real, _manifest([]))
    link = tmp_path / "link-source"
    link.symlink_to(real)
    result = _repo(link).inventory()
    assert isinstance(result, RejectedSnapshot)
    assert "unsafe-link" in _codes(result)


def test_non_directory_root_is_rejected(tmp_path: Path) -> None:
    """A non-directory root is rejected as source-non-regular."""
    root = tmp_path / "file"
    root.write_text("not a directory", encoding="utf-8")
    result = _repo(root).inventory()
    assert isinstance(result, RejectedSnapshot)
    assert "source-non-regular" in _codes(result)


# ---------------------------------------------------------------------------
# R3 regressions: traversal failures, undeclared symlink/non-regular PDFs,
# and a cwd-independent evaluation-dataset guard.
# ---------------------------------------------------------------------------


def test_traversal_error_rejects_as_scan_incomplete(tmp_path: Path) -> None:
    """A directory traversal failure surfaces as scan-incomplete, never empty.

    ``os.walk`` without an ``onerror`` handler silently skips an erroring
    directory and can look complete; the adapter captures the error and rejects
    the whole snapshot as ``scan-incomplete`` instead (R3-001).
    """
    root = tmp_path / "source"
    root.mkdir()
    _write_manifest(root, _manifest([]))
    # Deterministic monkeypatch of os.walk so a traversal error is injected
    # without depending on filesystem permissions (which differ under
    # privileged users). The wrapper preserves the real walk but reports an
    # OSError into the onerror callback exactly as os.walk would.
    real_walk = os.walk
    captured: dict[str, object] = {}

    def fake_walk(top: str, **kwargs: object) -> object:
        onerror = kwargs.get("onerror")
        if callable(onerror):
            onerror(OSError("simulated traversal failure"))
        captured["onerror_called"] = True
        return real_walk(top, **{k: v for k, v in kwargs.items() if k != "onerror"})  # type: ignore[arg-type]

    original_walk = os.walk
    os.walk = fake_walk  # type: ignore[assignment]
    try:
        result = _repo(root).inventory()
    finally:
        os.walk = original_walk  # type: ignore[assignment]
    assert captured.get("onerror_called") is True
    assert isinstance(result, RejectedSnapshot)
    assert "scan-incomplete" in _codes(result)
    assert not isinstance(result, CompleteSnapshot)


def test_undeclared_symlink_pdf_is_rejected_as_unsafe_link(tmp_path: Path) -> None:
    """An undeclared symlinked PDF rejects the whole snapshot as unsafe-link.

    Previously an undeclared symlink was silently skipped during enumeration,
    hiding an unsafe payload; the adapter now rejects it (R3-002).
    """
    root = tmp_path / "source"
    root.mkdir()
    _write_manifest(root, _manifest([]))
    target_rel = f"{RUNBOOKS_DIR}/real_ESP_REV_1.pdf"
    link_rel = f"{RUNBOOKS_DIR}/symlinked_ESP_REV_1.pdf"
    _write_pdf(root, target_rel, "real body")
    (root / link_rel).parent.mkdir(parents=True, exist_ok=True)
    (root / link_rel).symlink_to(root / target_rel)
    result = _repo(root).inventory()
    assert isinstance(result, RejectedSnapshot)
    assert "unsafe-link" in _codes(result)
    assert not isinstance(result, CompleteSnapshot)


def test_undeclared_non_regular_pdf_is_rejected_as_source_non_regular(
    tmp_path: Path,
) -> None:
    """An undeclared non-regular PDF rejects the whole snapshot as non-regular.

    Previously an undeclared FIFO/socket was silently skipped during
    enumeration; the adapter now rejects it (R3-002).
    """
    root = tmp_path / "source"
    root.mkdir()
    _write_manifest(root, _manifest([]))
    rel = f"{RUNBOOKS_DIR}/fifo_ESP_REV_1.pdf"
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    os.mkfifo(root / rel)
    result = _repo(root).inventory()
    assert isinstance(result, RejectedSnapshot)
    assert "source-non-regular" in _codes(result)
    assert not isinstance(result, CompleteSnapshot)


def test_real_evaluation_dataset_remains_denied_after_chdir_away(
    tmp_path: Path, project_root: Path
) -> None:
    """The committed evaluation-dataset guard holds after ``chdir`` away.

    The marker is anchored to the module's committed location, not the working
    directory, so the real corpus stays denied even when the process cwd is
    elsewhere; a same-named external dir elsewhere remains allowed (R3-003).
    """
    original_cwd = Path.cwd()
    os.chdir(tmp_path)
    try:
        repo = _repo(project_root / "evaluation-dataset")
        result = repo.inventory()
    finally:
        os.chdir(original_cwd)
    assert isinstance(result, RejectedSnapshot)
    assert "unsafe-path" in _codes(result)
