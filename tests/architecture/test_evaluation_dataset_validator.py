"""Severe-finding regression coverage for the OpsKnowledge evaluation dataset.

PR1a (Foundation, recovery slice) keeps only the regression tests that prove
the two severe behavioral contracts introduced by the escalated review lineage
`review-795cdaffea9a85e8` stay closed:

- R4-001: unsafe artifact paths (absolute, out-of-root, symlink, non-regular)
  are never opened; the validator fails closed with a stable reason code.
- R3-001: an empty manifest `artifacts` list or a missing manifest self-entry
  fails closed instead of certifying a corpus without governed coverage.

Redundant CLI/edge coverage (orphan, single-document, canonical-hash, CLI
exit codes) is deferred to PR1b. These tests use only the validator and a
deterministic copy of the committed dataset; no network, database, provider,
or out-of-root filesystem access.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

REPO_ROOT = Path(__file__).parents[2]
VALIDATOR_PATH = REPO_ROOT / "scripts/ci/validate_evaluation_dataset.py"
DATASET_ROOT = REPO_ROOT / "evaluation-dataset"


def _load_validator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("evaluation_dataset_validator", VALIDATOR_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _copy_dataset(tmp_path: Path) -> Path:
    target = tmp_path / "evaluation-dataset"
    shutil.copytree(DATASET_ROOT, target)
    return target


def _canonical_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
            "utf-8"
        )
        + b"\n"
    )


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_manifest(root: Path) -> dict[str, Any]:
    return json.loads((root / "manifest.json").read_bytes().decode("utf-8"))


def _write_manifest(root: Path, payload: dict[str, Any]) -> None:
    (root / "manifest.json").write_bytes(_canonical_bytes(payload))


def _first_entry_artifact(payload: dict[str, Any]) -> dict[str, Any]:
    for artifact in payload["artifacts"]:
        if artifact["kind"] == "entry":
            return artifact
    raise AssertionError("fixture manifest has no entry artifact")


def _reasons(findings: list[tuple[str, str, str]]) -> list[str]:
    return [reason for _, reason, _ in findings]


def _apply_r4_case(root: Path, payload: dict[str, Any], case: str) -> None:
    """Mutate the manifest and filesystem for the named R4-001 unsafe-path case."""
    artifact = _first_entry_artifact(payload)
    if case == "absolute":
        artifact["path"] = "/etc/passwd"
    elif case == "out-of-root":
        artifact["path"] = "../escape.json"
    elif case == "symlink":
        (root / "entries" / "link.rev.1.json").symlink_to(
            root / "entries" / "runbook-001.rev.1.json"
        )
        artifact["path"] = "entries/link.rev.1.json"
        artifact["id"] = "entry.link.rev.1"
    elif case == "non-regular":
        os.mkfifo(root / "entries" / "fifo.rev.1.json")
        artifact["path"] = "entries/fifo.rev.1.json"
        artifact["id"] = "entry.fifo.rev.1"
    else:  # pragma: no cover - exhausted by parametrize
        raise AssertionError(f"unknown R4 case: {case}")


def _apply_r3_case(payload: dict[str, Any], case: str) -> None:
    """Mutate the manifest for the named R3-001 manifest-coverage case."""
    if case == "empty-artifacts":
        payload["artifacts"] = []
    elif case == "missing-self-entry":
        payload["artifacts"] = [a for a in payload["artifacts"] if a.get("kind") != "manifest"]
    else:  # pragma: no cover - exhausted by parametrize
        raise AssertionError(f"unknown R3 case: {case}")


@pytest.mark.parametrize(
    ("case", "expected_reason"),
    [
        ("absolute", "manifest-artifact-absolute-path"),
        ("out-of-root", "manifest-artifact-out-of-root"),
        ("symlink", "manifest-artifact-symlink"),
        ("non-regular", "manifest-artifact-non-regular"),
    ],
)
def test_r4_001_unsafe_artifact_path_never_opened(
    tmp_path: Path, case: str, expected_reason: str
) -> None:
    """R4-001: an unsafe/escaping artifact path fails closed and is never reopened."""
    validator = _load_validator()
    root = _copy_dataset(tmp_path)
    payload = _load_manifest(root)
    _apply_r4_case(root, payload, case)
    _write_manifest(root, payload)
    findings = validator.validate(root)
    reasons = _reasons(findings)
    assert expected_reason in reasons, findings
    # Fail closed: no read attempt surfaces as a read-error for the unsafe path.
    assert "read-error" not in reasons, findings


@pytest.mark.parametrize(
    ("case", "expected_reason"),
    [
        ("symlink", "manifest-symlink"),
        ("non-regular", "manifest-non-regular"),
    ],
)
def test_r1_r2_r3_001_unsafe_manifest_never_read(
    tmp_path: Path, case: str, expected_reason: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """R1-001/R2-001/R3-001: a symlinked or FIFO manifest.json fails closed
    before any read attempt, with no read-error and no blocking I/O."""
    validator = _load_validator()
    root = _copy_dataset(tmp_path)
    manifest = root / "manifest.json"
    manifest.unlink()
    if case == "symlink":
        target = tmp_path / "external-manifest.json"
        target.write_bytes(b"{}\n")
        manifest.symlink_to(target)
    else:  # non-regular (FIFO)
        os.mkfifo(manifest)

    original_read_bytes = Path.read_bytes

    def _guarded_read_bytes(self: Path, *args: object, **kwargs: object) -> bytes:
        if self.resolve() == manifest.resolve():
            raise AssertionError("manifest.json read_bytes called despite unsafe type")
        return original_read_bytes(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_bytes", _guarded_read_bytes)

    findings = validator.validate(root)
    reasons = _reasons(findings)
    assert expected_reason in reasons, findings
    assert "read-error" not in reasons, findings


@pytest.mark.parametrize(
    ("case", "expected_reason"),
    [
        ("empty-artifacts", "manifest-artifacts-empty"),
        ("missing-self-entry", "manifest-self-entry-missing"),
    ],
)
def test_r3_001_empty_or_missing_manifest_coverage_fails_closed(
    tmp_path: Path, case: str, expected_reason: str
) -> None:
    """R3-001: empty artifacts or missing manifest self-entry fail closed."""
    validator = _load_validator()
    root = _copy_dataset(tmp_path)
    payload = _load_manifest(root)
    _apply_r3_case(payload, case)
    _write_manifest(root, payload)
    findings = validator.validate(root)
    assert expected_reason in _reasons(findings), findings


# --- PR1b: deferred CLI/edge coverage (no production behavior change) ---


def test_valid_manifest_loads_with_zero_findings(tmp_path: Path) -> None:
    """Baseline: a valid copy of the committed dataset loads with zero findings."""
    validator = _load_validator()
    root = _copy_dataset(tmp_path)
    findings = validator.validate(root)
    assert findings == [], findings


def test_manifest_hash_matches_canonical_bytes(tmp_path: Path) -> None:
    """The manifest self-referential sha256 is recomputed over canonical bytes
    with the manifest artifact's sha256 field set to the empty string."""
    validator = _load_validator()
    root = _copy_dataset(tmp_path)
    payload = _load_manifest(root)
    manifest_artifact = next(
        artifact for artifact in payload["artifacts"] if artifact["kind"] == "manifest"
    )
    manifest_artifact["sha256"] = ""
    expected = _sha256(_canonical_bytes(payload))
    manifest_artifact["sha256"] = expected
    _write_manifest(root, payload)
    findings = validator.validate(root)
    assert findings == [], findings


def test_manifest_must_be_single_document(tmp_path: Path) -> None:
    """An appended second JSON object yields json-syntax-error (not silent acceptance)."""
    validator = _load_validator()
    root = _copy_dataset(tmp_path)
    manifest_path = root / "manifest.json"
    original = manifest_path.read_bytes()
    manifest_path.write_bytes(original + b'{"second": true}\n')
    findings = validator.validate(root)
    assert "json-syntax-error" in _reasons(findings), findings


def test_orphan_file_outside_manifest_fails_closed(tmp_path: Path) -> None:
    """A JSON file under the dataset root that is not declared in the manifest
    fails closed with the stable reason code orphan-file-not-in-manifest."""
    validator = _load_validator()
    root = _copy_dataset(tmp_path)
    orphan = root / "entries" / "orphan.rev.1.json"
    orphan.write_bytes(
        _canonical_bytes(
            {
                "id": "entry.orphan.rev.1",
                "logical_entry_id": "orphan",
                "revision": "1",
                "collection": "runbooks",
                "language": "es",
                "approval": "approved",
                "classification": "synthetic",
                "profile": "development",
                "content": "orphan entry not in manifest.",
                "content_sha256": "deadbeef",
            }
        )
    )
    findings = validator.validate(root)
    orphan_findings = [finding for finding in findings if finding[0] == "entries/orphan.rev.1.json"]
    assert orphan_findings, findings
    reason = orphan_findings[0][1]
    assert reason == "orphan-file-not-in-manifest", orphan_findings
    remediation = orphan_findings[0][2]
    assert remediation, "remediation hint must be non-empty"


def test_cli_returns_zero_on_valid_dataset(tmp_path: Path) -> None:
    """CLI subprocess exit 0 on a valid dataset copy; stderr is empty."""
    root = _copy_dataset(tmp_path)
    result = subprocess.run(
        [sys.executable, str(VALIDATOR_PATH), str(root)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (result.stdout, result.stderr)
    assert result.stderr == ""


def test_cli_returns_two_on_bad_argv() -> None:
    """CLI subprocess exit 2 on invalid argv (too many args); safe usage to stderr."""
    result = subprocess.run(
        [sys.executable, str(VALIDATOR_PATH), "a", "b"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2, (result.stdout, result.stderr)
    assert "usage" in result.stderr, result.stderr


def test_cli_returns_one_on_findings(tmp_path: Path) -> None:
    """CLI subprocess exit 1 when findings exist; safe path+reason to stderr, no content."""
    root = _copy_dataset(tmp_path)
    orphan = root / "entries" / "orphan.rev.1.json"
    orphan.write_bytes(
        _canonical_bytes(
            {
                "id": "entry.orphan.rev.1",
                "logical_entry_id": "orphan",
                "revision": "1",
                "collection": "runbooks",
                "language": "es",
                "approval": "approved",
                "classification": "synthetic",
                "profile": "development",
                "content": "orphan.",
                "content_sha256": "deadbeef",
            }
        )
    )
    result = subprocess.run(
        [sys.executable, str(VALIDATOR_PATH), str(root)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1, (result.stdout, result.stderr)
    assert "orphan-file-not-in-manifest" in result.stderr, result.stderr
    assert "entries/orphan.rev.1.json" in result.stderr, result.stderr


# --- PR2: Fragments + OCR + Sensitive (RED first, then GREEN coverage) ---


def _write_fragment(root: Path, rel: str, payload: dict[str, Any]) -> None:
    (root / rel).write_bytes(_canonical_bytes(payload))


def _recompute_manifest_self_hash(root: Path, payload: dict[str, Any]) -> None:
    manifest_artifact = next(
        artifact for artifact in payload["artifacts"] if artifact["kind"] == "manifest"
    )
    manifest_artifact["sha256"] = ""
    expected = _sha256(_canonical_bytes(payload))
    manifest_artifact["sha256"] = expected
    _write_manifest(root, payload)


def _valid_fragment_payload(
    fragment_id: str = "fragment.runbook-001.rev.1.es.original",
    entry_id: str = "entry.runbook-001.rev.1",
    language: str = "es",
    provenance: str = "original",
    source_reference: str = "",
    quality: str = "",
    content: str = "Fragmento synthetic RB-001 rev 1 es original.",
    fictitious: bool | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": fragment_id,
        "entry_id": entry_id,
        "language": language,
        "provenance": provenance,
        "source_reference": source_reference,
        "quality": quality,
        "approval": "approved",
        "classification": "synthetic",
        "profile": "development",
        "content": content,
        "content_sha256": _sha256(content.encode("utf-8")),
    }
    if fictitious is not None:
        payload["fictitious"] = fictitious
    return payload


def _mutate_fragment(root: Path, payload: dict[str, Any], case: str) -> tuple[str, dict[str, Any]]:
    """Return (fragment_rel, mutated_payload) for a named PR2 contract violation."""
    if case == "language-mismatch":
        rel = "fragments/runbook-001.rev.1.es.original.json"
        bad = _valid_fragment_payload(language="en")
    elif case == "ocr-missing-source-quality":
        rel = "fragments/runbook-001.rev.1.es.ocr.json"
        bad = _valid_fragment_payload(
            fragment_id="fragment.runbook-001.rev.1.es.ocr",
            provenance="ocr",
            source_reference="",
            quality="",
        )
    elif case == "ocr-quality-allowlist":
        rel = "fragments/runbook-001.rev.1.es.ocr.json"
        bad = _valid_fragment_payload(
            fragment_id="fragment.runbook-001.rev.1.es.ocr",
            provenance="ocr",
            source_reference="synthetic-ocr/runbook-001-page-3.txt",
            quality="probably-ok",
        )
    elif case == "ocr-cross-language":
        rel = "fragments/adr-002.rev.1.en.ocr.json"
        bad = _valid_fragment_payload(
            fragment_id="fragment.adr-002.rev.1.en.ocr",
            entry_id="entry.adr-002.rev.1",
            language="es",
            provenance="ocr",
            source_reference="synthetic-ocr/adr-002-page-1.txt",
            quality="medium",
        )
    elif case == "fictitious-not-true":
        rel = "fragments/policy-003.rev.1.es.sensitive.json"
        bad = _valid_fragment_payload(
            fragment_id="fragment.policy-003.rev.1.es.sensitive",
            entry_id="entry.policy-003.rev.1",
            fictitious=False,
        )
    elif case == "image-field":
        rel = "fragments/runbook-001.rev.1.es.original.json"
        bad = _valid_fragment_payload()
        bad["image"] = "synthetic-ocr/runbook-001-page-3.png"
    elif case == "parent-missing":
        rel = "fragments/runbook-001.rev.1.es.original.json"
        bad = _valid_fragment_payload(entry_id="entry.does-not-exist.rev.1")
    elif case == "content-hash":
        rel = "fragments/runbook-001.rev.1.es.original.json"
        bad = _valid_fragment_payload()
        bad["content_sha256"] = "deadbeef" * 8
    elif case == "non-ocr-metadata":
        rel = "fragments/runbook-001.rev.1.es.original.json"
        bad = _valid_fragment_payload(
            provenance="original",
            source_reference="synthetic-ocr/runbook-001-page-3.txt",
            quality="low",
        )
    elif case == "provenance-allowlist":
        rel = "fragments/runbook-001.rev.1.es.original.json"
        bad = _valid_fragment_payload(provenance="scrape")
    else:  # pragma: no cover - exhausted by parametrize
        raise AssertionError(f"unknown PR2 case: {case}")
    return rel, bad


@pytest.mark.parametrize(
    ("case", "expected_reasons"),
    [
        ("language-mismatch", ["fragment-language-mismatch"]),
        ("ocr-missing-source-quality", ["fragment-ocr-source", "fragment-ocr-quality"]),
        ("ocr-quality-allowlist", ["fragment-ocr-quality"]),
        ("ocr-cross-language", ["fragment-language-mismatch"]),
        ("fictitious-not-true", ["fragment-fictitious-marker"]),
        ("image-field", ["fragment-image-field"]),
        ("parent-missing", ["fragment-parent-missing"]),
        ("content-hash", ["fragment-content-hash"]),
        (
            "non-ocr-metadata",
            ["fragment-source-not-ocr", "fragment-quality-not-ocr"],
        ),
        ("provenance-allowlist", ["fragment-provenance"]),
    ],
)
def test_fragment_contract_violations_fail_closed(
    tmp_path: Path, case: str, expected_reasons: list[str]
) -> None:
    """PR2 fragment contracts: each documented violation fails closed with the
    matching stable reason code(s). Covers language match, OCR provenance +
    source + quality allowlist, cross-language OCR, fictitious marker, image
    field prohibition, parent resolution, content hash, non-OCR metadata, and
    provenance allowlist."""
    validator = _load_validator()
    root = _copy_dataset(tmp_path)
    payload = _load_manifest(root)
    rel, bad = _mutate_fragment(root, payload, case)
    _write_fragment(root, rel, bad)
    _recompute_manifest_self_hash(root, payload)
    findings = validator.validate(root)
    reasons = _reasons(findings)
    for expected in expected_reasons:
        assert expected in reasons, (case, expected, findings)


def test_valid_fragments_load_with_zero_findings(tmp_path: Path) -> None:
    """Baseline: the committed dataset (entries + fragments) validates cleanly."""
    validator = _load_validator()
    root = _copy_dataset(tmp_path)
    findings = validator.validate(root)
    assert findings == [], findings


# --- PR3: Scenarios + Parity + Balance (RED first, then GREEN coverage) ---


def test_valid_scenarios_load_with_zero_findings(tmp_path: Path) -> None:
    """Baseline: the committed dataset (entries + fragments + 32 scenarios)
    validates cleanly with zero findings."""
    validator = _load_validator()
    root = _copy_dataset(tmp_path)
    findings = validator.validate(root)
    assert findings == [], findings
