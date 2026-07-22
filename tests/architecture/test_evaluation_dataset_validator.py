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


def _valid_scenario_payload(
    pair_id: str = "eval-01",
    language: str = "es",
    case_type: str = "grounded",
    expected_outcome: str = "supported",
    safety_classification: str = "safe",
    claim_expectation: str = "claim-grounded-01",
    abstention_reason: str = "none",
    evidence: list[str] | None = None,
    scenario_id: str | None = None,
) -> dict[str, Any]:
    if evidence is None:
        evidence = ["fragment.runbook-001.rev.1.es.original"] if language == "es" else []
    if scenario_id is None:
        scenario_id = f"scenario.{pair_id}.{language}"
    return {
        "id": scenario_id,
        "pair_id": pair_id,
        "language": language,
        "case_type": case_type,
        "expected_outcome": expected_outcome,
        "safety_classification": safety_classification,
        "claim_expectation": claim_expectation,
        "abstention_reason": abstention_reason,
        "evidence": evidence,
        "approval": "approved",
        "classification": "synthetic",
        "profile": "development",
    }


def _write_scenario(root: Path, pair_id: str, language: str, payload: dict[str, Any]) -> None:
    (root / "scenarios" / f"{pair_id}.{language}.json").write_bytes(_canonical_bytes(payload))


def _scenario_artifact(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": payload["id"],
        "kind": "scenario",
        "path": f"scenarios/{payload['pair_id']}.{payload['language']}.json",
        "sha256": _sha256(_canonical_bytes(payload)),
    }


def _replace_scenario_in_manifest(
    payload: dict[str, Any], manifest: dict[str, Any], pair_id: str, language: str
) -> None:
    target = f"scenarios/{pair_id}.{language}.json"
    manifest["artifacts"] = [
        a
        for a in manifest["artifacts"]
        if not (a.get("kind") == "scenario" and a.get("path") == target)
    ]
    manifest["artifacts"].append(_scenario_artifact(payload))


@pytest.mark.parametrize(
    ("case", "expected_reasons"),
    [
        ("count", ["scenario-count"]),
        ("language-split", ["scenario-language-split"]),
        ("pair-shape", ["scenario-pair-shape"]),
        ("parity", ["scenario-parity"]),
        ("balance-grounded", ["scenario-balance-grounded"]),
        ("evidence-language-mismatch", ["scenario-evidence-language-mismatch"]),
        ("supported-no-evidence", ["scenario-supported-no-evidence"]),
        ("empty-evidence-required", ["scenario-empty-evidence-required"]),
        ("unanswerable-outcome", ["scenario-unanswerable-outcome"]),
        ("contradiction-revisions", ["scenario-contradiction-revisions"]),
        ("outcome-allowlist", ["scenario-outcome"]),
        ("case-type-allowlist", ["scenario-case-type"]),
        ("prohibited-field", ["scenario-prohibited-field"]),
        ("safety-allowlist", ["scenario-safety"]),
        ("abstention-reason-allowlist", ["scenario-abstention-reason"]),
        ("evidence-missing", ["scenario-evidence-missing"]),
    ],
)
def test_scenario_contract_violations_fail_closed(
    tmp_path: Path, case: str, expected_reasons: list[str]
) -> None:
    """PR3 scenario contracts: each documented violation fails closed with the
    matching stable reason code(s). Covers count, language split, pair shape,
    parity, balance, evidence language isolation, supported-evidence requirement,
    empty-evidence case types, unanswerable outcome, contradiction paired
    revisions, and the outcome/case-type/safety/reason/prohibited-field allowlists."""
    validator = _load_validator()
    root = _copy_dataset(tmp_path)
    manifest = _load_manifest(root)

    if case == "count":
        # Remove all scenarios to drop below 32.
        for art in list(manifest["artifacts"]):
            if art.get("kind") == "scenario":
                (root / art["path"]).unlink()
        manifest["artifacts"] = [a for a in manifest["artifacts"] if a.get("kind") != "scenario"]
    elif case == "language-split":
        # Convert one es scenario to en to break the 16/16 split (17 en / 15 es).
        target = root / "scenarios" / "eval-01.es.json"
        payload = json.loads(target.read_bytes().decode("utf-8"))
        payload["language"] = "en"
        payload["id"] = "scenario.eval-01.en"
        target.unlink()
        _write_scenario(root, "eval-01", "en", payload)
        _replace_scenario_in_manifest(payload, manifest, "eval-01", "en")
        # Remove the original en to avoid a duplicate pair-language finding masking this.
        (root / "scenarios" / "eval-01.en.json").unlink()
        manifest["artifacts"] = [
            a for a in manifest["artifacts"] if a.get("path") != "scenarios/eval-01.en.json"
        ]
    elif case == "pair-shape":
        # Add a third scenario to eval-01 via a distinct file path so the pair
        # contains three members (two es, one en). The manifest gets a new
        # scenario artifact with a unique path; no duplicate-path masking.
        extra = _valid_scenario_payload(
            pair_id="eval-01",
            language="es",
            scenario_id="scenario.eval-01.es.dup",
            evidence=["fragment.runbook-001.rev.1.es.original"],
        )
        dup_path = "scenarios/eval-01.es.dup.json"
        (root / dup_path).write_bytes(_canonical_bytes(extra))
        manifest["artifacts"].append(
            {
                "id": "scenario.eval-01.es.dup",
                "kind": "scenario",
                "path": dup_path,
                "sha256": _sha256(_canonical_bytes(extra)),
            }
        )
    elif case == "parity":
        # Flip eval-01.en case_type to break parity with eval-01.es.
        target = root / "scenarios" / "eval-01.en.json"
        payload = json.loads(target.read_bytes().decode("utf-8"))
        payload["case_type"] = "contradictory"
        _write_scenario(root, "eval-01", "en", payload)
        _replace_scenario_in_manifest(payload, manifest, "eval-01", "en")
    elif case == "balance-grounded":
        # Flip a supported scenario to an abstention outcome (15 grounded / 17 abstention).
        target = root / "scenarios" / "eval-01.es.json"
        payload = json.loads(target.read_bytes().decode("utf-8"))
        payload["expected_outcome"] = "out_of_scope"
        payload["case_type"] = "out-of-scope"
        payload["abstention_reason"] = "out-of-scope"
        payload["evidence"] = []
        _write_scenario(root, "eval-01", "es", payload)
        _replace_scenario_in_manifest(payload, manifest, "eval-01", "es")
        # Also flip the en counterpart to preserve parity (so only balance fires).
        t2 = root / "scenarios" / "eval-01.en.json"
        p2 = json.loads(t2.read_bytes().decode("utf-8"))
        p2["expected_outcome"] = "out_of_scope"
        p2["case_type"] = "out-of-scope"
        p2["abstention_reason"] = "out-of-scope"
        p2["evidence"] = []
        _write_scenario(root, "eval-01", "en", p2)
        _replace_scenario_in_manifest(p2, manifest, "eval-01", "en")
    elif case == "evidence-language-mismatch":
        # An es scenario references an en fragment.
        target = root / "scenarios" / "eval-01.es.json"
        payload = json.loads(target.read_bytes().decode("utf-8"))
        payload["evidence"] = ["fragment.adr-002.rev.1.en.original"]
        _write_scenario(root, "eval-01", "es", payload)
        _replace_scenario_in_manifest(payload, manifest, "eval-01", "es")
    elif case == "supported-no-evidence":
        # A supported scenario with empty evidence.
        target = root / "scenarios" / "eval-01.es.json"
        payload = json.loads(target.read_bytes().decode("utf-8"))
        payload["evidence"] = []
        _write_scenario(root, "eval-01", "es", payload)
        _replace_scenario_in_manifest(payload, manifest, "eval-01", "es")
    elif case == "empty-evidence-required":
        # An out-of-scope scenario that carries evidence.
        target = root / "scenarios" / "eval-13.es.json"
        payload = json.loads(target.read_bytes().decode("utf-8"))
        payload["evidence"] = ["fragment.runbook-001.rev.1.es.original"]
        _write_scenario(root, "eval-13", "es", payload)
        _replace_scenario_in_manifest(payload, manifest, "eval-13", "es")
    elif case == "unanswerable-outcome":
        # An unanswerable scenario that declares a supported outcome.
        target = root / "scenarios" / "eval-14.es.json"
        payload = json.loads(target.read_bytes().decode("utf-8"))
        payload["expected_outcome"] = "supported"
        _write_scenario(root, "eval-14", "es", payload)
        _replace_scenario_in_manifest(payload, manifest, "eval-14", "es")
    elif case == "contradiction-revisions":
        # A contradiction scenario that references only a single revision.
        target = root / "scenarios" / "eval-11.es.json"
        payload = json.loads(target.read_bytes().decode("utf-8"))
        payload["evidence"] = ["fragment.runbook-001.rev.1.es.original"]
        _write_scenario(root, "eval-11", "es", payload)
        _replace_scenario_in_manifest(payload, manifest, "eval-11", "es")
    elif case == "outcome-allowlist":
        target = root / "scenarios" / "eval-01.es.json"
        payload = json.loads(target.read_bytes().decode("utf-8"))
        payload["expected_outcome"] = "definitely-supported"
        _write_scenario(root, "eval-01", "es", payload)
        _replace_scenario_in_manifest(payload, manifest, "eval-01", "es")
    elif case == "case-type-allowlist":
        target = root / "scenarios" / "eval-01.es.json"
        payload = json.loads(target.read_bytes().decode("utf-8"))
        payload["case_type"] = "hallucination"
        _write_scenario(root, "eval-01", "es", payload)
        _replace_scenario_in_manifest(payload, manifest, "eval-01", "es")
    elif case == "prohibited-field":
        target = root / "scenarios" / "eval-01.es.json"
        payload = json.loads(target.read_bytes().decode("utf-8"))
        payload["answer"] = "synthetic answer prose must be rejected"
        _write_scenario(root, "eval-01", "es", payload)
        _replace_scenario_in_manifest(payload, manifest, "eval-01", "es")
    elif case == "safety-allowlist":
        target = root / "scenarios" / "eval-01.es.json"
        payload = json.loads(target.read_bytes().decode("utf-8"))
        payload["safety_classification"] = "dangerous"
        _write_scenario(root, "eval-01", "es", payload)
        _replace_scenario_in_manifest(payload, manifest, "eval-01", "es")
    elif case == "abstention-reason-allowlist":
        target = root / "scenarios" / "eval-01.es.json"
        payload = json.loads(target.read_bytes().decode("utf-8"))
        payload["abstention_reason"] = "made-up-reason"
        _write_scenario(root, "eval-01", "es", payload)
        _replace_scenario_in_manifest(payload, manifest, "eval-01", "es")
    elif case == "evidence-missing":
        target = root / "scenarios" / "eval-01.es.json"
        payload = json.loads(target.read_bytes().decode("utf-8"))
        payload["evidence"] = ["fragment.does-not-exist"]
        _write_scenario(root, "eval-01", "es", payload)
        _replace_scenario_in_manifest(payload, manifest, "eval-01", "es")
    else:  # pragma: no cover - exhausted by parametrize
        raise AssertionError(f"unknown PR3 case: {case}")

    _recompute_manifest_self_hash(root, manifest)
    findings = validator.validate(root)
    reasons = _reasons(findings)
    for expected in expected_reasons:
        assert expected in reasons, (case, expected, findings)


def test_valid_scenarios_load_with_zero_findings(tmp_path: Path) -> None:
    """Baseline: the committed dataset (entries + fragments + 32 scenarios)
    validates cleanly with zero findings."""
    validator = _load_validator()
    root = _copy_dataset(tmp_path)
    findings = validator.validate(root)
    assert findings == [], findings


def test_scenario_catalog_contract_holds(tmp_path: Path) -> None:
    """The committed dataset meets the exact 32-scenario / 16-pair / 16-16
    balance / 16-16 language-split contract deterministically."""
    validator = _load_validator()
    root = _copy_dataset(tmp_path)
    findings = validator.validate(root)
    # No count/split/pair/parity/balance findings means the contract holds.
    contract_reasons = {
        "scenario-count",
        "scenario-language-split",
        "scenario-pair-count",
        "scenario-pair-shape",
        "scenario-pair-language",
        "scenario-parity",
        "scenario-parity-evidence-shape",
        "scenario-balance-grounded",
        "scenario-balance-abstention",
    }
    present = {f[1] for f in findings}
    assert not (contract_reasons & present), findings
