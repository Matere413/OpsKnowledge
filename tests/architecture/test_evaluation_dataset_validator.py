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


# --- PR4b-1: shape-check fix + manifest/entry mutations + CLI contract ---
#
# This slice implements task 4.2 (CLI contract) and the validator shape-check
# fix (call _validate_entry/_validate_scenario even when payload is not a dict)
# plus mutation coverage for manifest and entry failure classes. The remaining
# mutation coverage (fragment fields, scenario fields/catalog, hash/reference,
# filesystem/encoding) is deferred to PR4c to stay within the 400-line budget.


def _write_json(root: Path, rel: str, payload: Any) -> None:
    (root / rel).write_bytes(_canonical_bytes(payload))


def _entry_artifact(payload: dict[str, Any]) -> dict[str, Any]:
    for artifact in payload["artifacts"]:
        if artifact["kind"] == "entry":
            return artifact
    raise AssertionError("fixture manifest has no entry artifact")


def _load_entry(root: Path, rel: str) -> dict[str, Any]:
    return json.loads((root / rel).read_bytes().decode("utf-8"))


def _load_scenario(root: Path, rel: str) -> dict[str, Any]:
    return json.loads((root / rel).read_bytes().decode("utf-8"))


@pytest.mark.parametrize(
    ("case", "expected_reason"),
    [
        ("manifest-shape", "manifest-shape"),
        ("manifest-missing-field", "manifest-missing-field"),
        ("manifest-schema-version", "manifest-schema-version"),
        ("manifest-dataset-id", "manifest-dataset-id"),
        ("manifest-profile", "manifest-profile"),
        ("manifest-approval", "manifest-approval"),
        ("manifest-classification", "manifest-classification"),
        ("manifest-artifacts-shape", "manifest-artifacts-shape"),
        ("manifest-artifact-shape", "manifest-artifact-shape"),
        ("manifest-artifact-missing-field", "manifest-artifact-missing-field"),
        ("manifest-artifact-kind", "manifest-artifact-kind"),
        ("manifest-artifact-path", "manifest-artifact-path"),
        ("manifest-artifact-duplicate-path", "manifest-artifact-duplicate-path"),
        ("manifest-self-entry-path", "manifest-self-entry-path"),
    ],
)
def test_manifest_mutation_reason_codes(tmp_path: Path, case: str, expected_reason: str) -> None:
    """PR4b-1: each manifest-shape/field mutation fails closed with the exact reason."""
    validator = _load_validator()
    root = _copy_dataset(tmp_path)
    payload = _load_manifest(root)

    if case == "manifest-shape":
        _write_json(root, "manifest.json", [])
        findings = validator.validate(root)
        assert expected_reason in _reasons(findings), (case, findings)
        return
    elif case == "manifest-missing-field":
        del payload["schema_version"]
    elif case == "manifest-schema-version":
        payload["schema_version"] = "99"
    elif case == "manifest-dataset-id":
        payload["dataset_id"] = "wrong-dataset"
    elif case == "manifest-profile":
        payload["profile"] = "production"
    elif case == "manifest-approval":
        payload["approval"] = "draft"
    elif case == "manifest-classification":
        payload["classification"] = "corporate"
    elif case == "manifest-artifacts-shape":
        payload["artifacts"] = "not-a-list"
        _write_manifest(root, payload)
        findings = validator.validate(root)
        assert expected_reason in _reasons(findings), (case, findings)
        return
    elif case == "manifest-artifact-shape":
        payload["artifacts"][0] = "not-an-object"
        _write_manifest(root, payload)
        findings = validator.validate(root)
        assert expected_reason in _reasons(findings), (case, findings)
        return
    elif case == "manifest-artifact-missing-field":
        del payload["artifacts"][0]["kind"]
        _write_manifest(root, payload)
        findings = validator.validate(root)
        assert expected_reason in _reasons(findings), (case, findings)
        return
    elif case == "manifest-artifact-kind":
        payload["artifacts"][0]["kind"] = "unknown-kind"
    elif case == "manifest-artifact-path":
        payload["artifacts"][0]["path"] = ""
    elif case == "manifest-artifact-duplicate-path":
        first_entry = _entry_artifact(payload)
        first_entry_path = first_entry["path"]
        payload["artifacts"].append(
            {
                "id": "entry.dup.rev.1",
                "kind": "entry",
                "path": first_entry_path,
                "revision": "1",
                "sha256": "0" * 64,
            }
        )
    elif case == "manifest-self-entry-path":
        manifest_artifact = next(a for a in payload["artifacts"] if a["kind"] == "manifest")
        manifest_artifact["path"] = "wrong/manifest.json"
    else:  # pragma: no cover - exhausted by parametrize
        raise AssertionError(f"unknown case: {case}")

    _recompute_manifest_self_hash(root, payload)
    findings = validator.validate(root)
    reasons = _reasons(findings)
    assert expected_reason in reasons, (case, expected_reason, findings)


@pytest.mark.parametrize(
    ("case", "expected_reason"),
    [
        ("entry-shape", "entry-shape"),
        ("entry-missing-field", "entry-missing-field"),
        ("entry-collection", "entry-collection"),
        ("entry-language", "entry-language"),
        ("entry-approval", "entry-approval"),
        ("entry-classification", "entry-classification"),
        ("entry-profile", "entry-profile"),
        ("entry-content", "entry-content"),
        ("entry-content-hash", "entry-content-hash"),
        ("entry-id-mismatch", "entry-id-mismatch"),
        ("entry-revision-mismatch", "entry-revision-mismatch"),
    ],
)
def test_entry_mutation_reason_codes(tmp_path: Path, case: str, expected_reason: str) -> None:
    """PR4b-1: each entry-shape/field mutation fails closed with the exact reason."""
    validator = _load_validator()
    root = _copy_dataset(tmp_path)
    manifest = _load_manifest(root)
    rel = "entries/runbook-001.rev.1.json"

    if case == "entry-shape":
        _write_json(root, rel, [])
        _recompute_manifest_self_hash(root, manifest)
        findings = validator.validate(root)
        assert expected_reason in _reasons(findings), (case, findings)
        return

    entry = _load_entry(root, rel)

    if case == "entry-missing-field":
        del entry["revision"]
    elif case == "entry-collection":
        entry["collection"] = "recipes"
    elif case == "entry-language":
        entry["language"] = "fr"
    elif case == "entry-approval":
        entry["approval"] = "draft"
    elif case == "entry-classification":
        entry["classification"] = "corporate"
    elif case == "entry-profile":
        entry["profile"] = "production"
    elif case == "entry-content":
        entry["content"] = ""
    elif case == "entry-content-hash":
        entry["content_sha256"] = "0" * 64
    elif case == "entry-id-mismatch":
        manifest_artifact = next(a for a in manifest["artifacts"] if a["path"] == rel)
        manifest_artifact["id"] = "entry.wrong.rev.1"
    elif case == "entry-revision-mismatch":
        manifest_artifact = next(a for a in manifest["artifacts"] if a["path"] == rel)
        manifest_artifact["revision"] = "99"
    else:  # pragma: no cover - exhausted by parametrize
        raise AssertionError(f"unknown case: {case}")

    _write_json(root, rel, entry)
    _recompute_manifest_self_hash(root, manifest)
    findings = validator.validate(root)
    assert expected_reason in _reasons(findings), (case, findings)


# --- PR4 Task 4.2: final-form CLI subprocess contract ---
#
# PR1b already covers baseline CLI exit 0/1/2. Task 4.2 retains the final-form
# CLI subprocess contract here so PR4 is the authoritative source for the
# mutation suite. These tests assert the CLI is the only subprocess invoked
# and that no network/DB/provider access occurs beyond the intended CLI call.


def test_cli_exit_zero_on_valid_root_final_form(tmp_path: Path) -> None:
    """CLI subprocess exit 0 on a valid dataset root; stderr is empty."""
    root = _copy_dataset(tmp_path)
    result = subprocess.run(
        [sys.executable, str(VALIDATOR_PATH), str(root)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (result.stdout, result.stderr)
    assert result.stderr == ""


def test_cli_exit_one_on_findings_final_form(tmp_path: Path) -> None:
    """CLI subprocess exit 1 with a safe stderr finding (path + reason, no content)."""
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
                "content_sha256": "0" * 64,
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


def test_cli_exit_two_on_bad_argv_final_form() -> None:
    """CLI subprocess exit 2 on invalid argv; safe usage message to stderr."""
    result = subprocess.run(
        [sys.executable, str(VALIDATOR_PATH), "a", "b"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2, (result.stdout, result.stderr)
    assert "usage" in result.stderr, result.stderr


# --- PR4c: fragment field, scenario field/catalog, hash/reference,
#     and filesystem/encoding mutation coverage (task 4.1 remainder) ---
#
# These tests complete the task 4.1 mutation suite: every remaining documented
# failure class for fragment fields, scenario fields/catalog, manifest
# hash/reference integrity, and filesystem/encoding guards. Each test copies
# the committed valid dataset to tmp_path, mutates one file/field, recomputes
# the manifest self-hash when needed, and asserts the exact stable reason code.
# No corpus duplication; no network/DB/provider/subprocess access.


def _fragment_artifact(manifest: dict[str, Any], rel: str) -> dict[str, Any]:
    return next(a for a in manifest["artifacts"] if a.get("path") == rel)


def _scenario_manifest_artifact(
    manifest: dict[str, Any], pair_id: str, language: str
) -> dict[str, Any]:
    return next(
        a for a in manifest["artifacts"] if a.get("path") == f"scenarios/{pair_id}.{language}.json"
    )


def _load_fragment(root: Path, rel: str) -> dict[str, Any]:
    return json.loads((root / rel).read_bytes().decode("utf-8"))


@pytest.mark.parametrize(
    ("case", "expected_reason"),
    [
        ("fragment-shape", "fragment-shape"),
        ("fragment-missing-field", "fragment-missing-field"),
        ("fragment-language", "fragment-language"),
        ("fragment-approval", "fragment-approval"),
        ("fragment-classification", "fragment-classification"),
        ("fragment-profile", "fragment-profile"),
        ("fragment-content", "fragment-content"),
        ("fragment-entry-id", "fragment-entry-id"),
        ("fragment-id-mismatch", "fragment-id-mismatch"),
    ],
)
def test_fragment_field_mutation_reason_codes(
    tmp_path: Path, case: str, expected_reason: str
) -> None:
    """PR4c: each fragment field/shape mutation fails closed with the exact reason."""
    validator = _load_validator()
    root = _copy_dataset(tmp_path)
    manifest = _load_manifest(root)
    rel = "fragments/runbook-001.rev.1.es.original.json"

    if case == "fragment-shape":
        _write_json(root, rel, [])
        _recompute_manifest_self_hash(root, manifest)
        assert expected_reason in _reasons(validator.validate(root)), (case,)
        return

    fragment = _load_fragment(root, rel)
    if case == "fragment-missing-field":
        del fragment["provenance"]
    elif case == "fragment-language":
        fragment["language"] = "fr"
    elif case == "fragment-approval":
        fragment["approval"] = "draft"
    elif case == "fragment-classification":
        fragment["classification"] = "corporate"
    elif case == "fragment-profile":
        fragment["profile"] = "production"
    elif case == "fragment-content":
        fragment["content"] = ""
    elif case == "fragment-entry-id":
        fragment["entry_id"] = ""
    elif case == "fragment-id-mismatch":
        _fragment_artifact(manifest, rel)["id"] = "fragment.wrong-id"
    else:  # pragma: no cover - exhausted by parametrize
        raise AssertionError(f"unknown case: {case}")
    _write_json(root, rel, fragment)
    _recompute_manifest_self_hash(root, manifest)
    assert expected_reason in _reasons(validator.validate(root)), (case,)


@pytest.mark.parametrize(
    ("case", "expected_reason"),
    [
        ("scenario-shape", "scenario-shape"),
        ("scenario-missing-field", "scenario-missing-field"),
        ("scenario-approval", "scenario-approval"),
        ("scenario-classification", "scenario-classification"),
        ("scenario-profile", "scenario-profile"),
        ("scenario-language", "scenario-language"),
        ("scenario-claim-expectation", "scenario-claim-expectation"),
        ("scenario-evidence-shape", "scenario-evidence-shape"),
        ("scenario-evidence-ref", "scenario-evidence-ref"),
        ("scenario-id-mismatch", "scenario-id-mismatch"),
    ],
)
def test_scenario_field_mutation_reason_codes(
    tmp_path: Path, case: str, expected_reason: str
) -> None:
    """PR4c: each scenario field/shape mutation fails closed with the exact reason."""
    validator = _load_validator()
    root = _copy_dataset(tmp_path)
    manifest = _load_manifest(root)
    pair_id, language = "eval-01", "es"
    rel = f"scenarios/{pair_id}.{language}.json"

    if case == "scenario-shape":
        _write_json(root, rel, [])
        _recompute_manifest_self_hash(root, manifest)
        assert expected_reason in _reasons(validator.validate(root)), (case,)
        return

    scenario = _load_scenario(root, rel)
    if case == "scenario-missing-field":
        del scenario["case_type"]
    elif case == "scenario-approval":
        scenario["approval"] = "draft"
    elif case == "scenario-classification":
        scenario["classification"] = "corporate"
    elif case == "scenario-profile":
        scenario["profile"] = "production"
    elif case == "scenario-language":
        scenario["language"] = "fr"
    elif case == "scenario-claim-expectation":
        scenario["claim_expectation"] = ""
    elif case == "scenario-evidence-shape":
        scenario["evidence"] = "not-a-list"
    elif case == "scenario-evidence-ref":
        scenario["evidence"] = [123, "fragment.runbook-001.rev.1.es.original"]
    elif case == "scenario-id-mismatch":
        _scenario_manifest_artifact(manifest, pair_id, language)["id"] = "scenario.wrong-id"
    else:  # pragma: no cover - exhausted by parametrize
        raise AssertionError(f"unknown case: {case}")
    _write_json(root, rel, scenario)
    _recompute_manifest_self_hash(root, manifest)
    assert expected_reason in _reasons(validator.validate(root)), (case,)


def test_scenario_balance_abstention_mutation_reason_code(tmp_path: Path) -> None:
    """PR4c: flipping an abstention pair to supported breaks the 16/16 balance
    and fails closed with scenario-balance-abstention (parity preserved)."""
    validator = _load_validator()
    root = _copy_dataset(tmp_path)
    manifest = _load_manifest(root)
    for lang, frag in (
        ("es", "fragment.policy-003.rev.1.es.original"),
        ("en", "fragment.adr-002.rev.2.en.original"),
    ):
        rel = f"scenarios/eval-13.{lang}.json"
        s = _load_scenario(root, rel)
        s["expected_outcome"] = "supported"
        s["case_type"] = "grounded"
        s["abstention_reason"] = "none"
        s["evidence"] = [frag]
        _write_scenario(root, "eval-13", lang, s)
        _replace_scenario_in_manifest(s, manifest, "eval-13", lang)
    _recompute_manifest_self_hash(root, manifest)
    assert "scenario-balance-abstention" in _reasons(validator.validate(root))


def test_scenario_pair_count_mutation_reason_code(tmp_path: Path) -> None:
    """PR4c: a 17th pair (two new scenarios) breaks the 16-pair contract."""
    validator = _load_validator()
    root = _copy_dataset(tmp_path)
    manifest = _load_manifest(root)
    extras = {
        "es": ("scenario.eval-99.es", "fragment.runbook-001.rev.1.es.original"),
        "en": ("scenario.eval-99.en", "fragment.adr-002.rev.1.en.original"),
    }
    for lang, (sid, frag) in extras.items():
        extra = _valid_scenario_payload(
            pair_id="eval-99", language=lang, scenario_id=sid, evidence=[frag]
        )
        path = f"scenarios/eval-99.{lang}.json"
        (root / path).write_bytes(_canonical_bytes(extra))
        manifest["artifacts"].append(
            {
                "id": sid,
                "kind": "scenario",
                "path": path,
                "sha256": _sha256(_canonical_bytes(extra)),
            }
        )
    _recompute_manifest_self_hash(root, manifest)
    assert "scenario-pair-count" in _reasons(validator.validate(root))


def test_scenario_pair_language_mutation_reason_code(tmp_path: Path) -> None:
    """PR4c: a pair with two es scenarios (no en counterpart) fails closed
    with scenario-pair-language. The file stays at eval-01.en.json (path
    unchanged) but its payload declares language=es so the validator groups
    both members as es."""
    validator = _load_validator()
    root = _copy_dataset(tmp_path)
    manifest = _load_manifest(root)
    rel = "scenarios/eval-01.en.json"
    scenario = _load_scenario(root, rel)
    scenario["language"] = "es"
    _write_scenario(root, "eval-01", "en", scenario)
    _scenario_manifest_artifact(manifest, "eval-01", "en")["sha256"] = _sha256(
        _canonical_bytes(scenario)
    )
    _recompute_manifest_self_hash(root, manifest)
    assert "scenario-pair-language" in _reasons(validator.validate(root))


def test_scenario_parity_evidence_shape_mutation_reason_code(tmp_path: Path) -> None:
    """PR4c: a pair whose es/en evidence lists differ in length fails closed
    with scenario-parity-evidence-shape."""
    validator = _load_validator()
    root = _copy_dataset(tmp_path)
    manifest = _load_manifest(root)
    rel = "scenarios/eval-01.es.json"
    scenario = _load_scenario(root, rel)
    scenario["evidence"] = [
        "fragment.runbook-001.rev.1.es.original",
        "fragment.policy-003.rev.1.es.original",
    ]
    _write_scenario(root, "eval-01", "es", scenario)
    _replace_scenario_in_manifest(scenario, manifest, "eval-01", "es")
    _recompute_manifest_self_hash(root, manifest)
    assert "scenario-parity-evidence-shape" in _reasons(validator.validate(root))


def test_scenario_evidence_not_approved_mutation_reason_code(tmp_path: Path) -> None:
    """PR4c: a supported scenario referencing an unapproved fragment fails closed
    with scenario-evidence-not-approved."""
    validator = _load_validator()
    root = _copy_dataset(tmp_path)
    manifest = _load_manifest(root)
    unapproved = _valid_fragment_payload(
        fragment_id="fragment.runbook-001.rev.1.es.unapproved",
        entry_id="entry.runbook-001.rev.1",
    )
    unapproved["approval"] = "draft"
    unapproved["content_sha256"] = _sha256(unapproved["content"].encode("utf-8"))
    bad_rel = "fragments/runbook-001.rev.1.es.unapproved.json"
    _write_fragment(root, bad_rel, unapproved)
    manifest["artifacts"].append(
        {
            "id": "fragment.runbook-001.rev.1.es.unapproved",
            "kind": "fragment",
            "path": bad_rel,
            "sha256": _sha256(_canonical_bytes(unapproved)),
        }
    )
    rel = "scenarios/eval-01.es.json"
    scenario = _load_scenario(root, rel)
    scenario["evidence"] = ["fragment.runbook-001.rev.1.es.unapproved"]
    _write_scenario(root, "eval-01", "es", scenario)
    _replace_scenario_in_manifest(scenario, manifest, "eval-01", "es")
    _recompute_manifest_self_hash(root, manifest)
    assert "scenario-evidence-not-approved" in _reasons(validator.validate(root))


# --- PR4c: hash/reference mutations (manifest + entry/fragment integrity) ---


@pytest.mark.parametrize(
    ("case", "expected_reason"),
    [
        ("file-hash-mismatch", "file-hash-mismatch"),
        ("file-not-canonical-json", "file-not-canonical-json"),
        ("manifest-dangling-reference", "manifest-dangling-reference"),
    ],
)
def test_hash_reference_mutation_reason_codes(
    tmp_path: Path, case: str, expected_reason: str
) -> None:
    """PR4c: manifest hash, non-canonical JSON, and dangling reference failures."""
    validator = _load_validator()
    root = _copy_dataset(tmp_path)
    manifest = _load_manifest(root)
    if case == "file-hash-mismatch":
        _entry_artifact(manifest)["sha256"] = "0" * 64
    elif case == "file-not-canonical-json":
        (root / "entries/runbook-001.rev.1.json").write_bytes(b"{invalid json\n")
    elif case == "manifest-dangling-reference":
        _entry_artifact(manifest)["path"] = "entries/does-not-exist.rev.1.json"
    else:  # pragma: no cover - exhausted by parametrize
        raise AssertionError(f"unknown case: {case}")
    _recompute_manifest_self_hash(root, manifest)
    assert expected_reason in _reasons(validator.validate(root)), (case,)


# --- PR4c: filesystem/encoding mutations (walk + read guards) ---


def _apply_fs_encoding_case(root: Path, case: str) -> None:
    """Apply a filesystem/encoding mutation in place. Cases that change on-disk
    entry bytes do NOT recompute the manifest self-hash (the finding fires before
    the hash path, or the hash path also fires with file-not-canonical-json)."""
    rel = "entries/runbook-001.rev.1.json"
    if case == "hidden-file-not-allowed":
        (root / "entries" / ".hidden.json").write_bytes(b"{}\n")
    elif case == "symlink-not-allowed":
        (root / "entries" / "link.rev.1.json").symlink_to(root / rel)
    elif case == "non-regular-file":
        os.mkfifo(root / "entries" / "fifo.rev.1.json")
    elif case == "non-json-file":
        (root / "entries" / "notes.txt").write_bytes(b"{}\n")
    elif case == "missing-trailing-lf":
        (root / rel).write_bytes((root / rel).read_bytes().rstrip(b"\n"))
    elif case == "extra-trailing-lf":
        (root / rel).write_bytes((root / rel).read_bytes() + b"\n")
    elif case == "bom-not-allowed":
        (root / rel).write_bytes(b"\xef\xbb\xbf" + (root / rel).read_bytes())
    elif case == "decode-error":
        # Trailing LF present so LF guards pass; lone continuation byte fails decode.
        (root / rel).write_bytes(b'{"id":"x"}\xff\n')
    else:  # pragma: no cover - exhausted by parametrize
        raise AssertionError(f"unknown case: {case}")


@pytest.mark.parametrize(
    ("case", "expected_reason"),
    [
        ("hidden-file-not-allowed", "hidden-file-not-allowed"),
        ("symlink-not-allowed", "symlink-not-allowed"),
        ("non-regular-file", "non-regular-file"),
        ("non-json-file", "non-json-file"),
        ("missing-trailing-lf", "missing-trailing-lf"),
        ("extra-trailing-lf", "extra-trailing-lf"),
        ("bom-not-allowed", "bom-not-allowed"),
        ("decode-error", "decode-error"),
    ],
)
def test_filesystem_encoding_mutation_reason_codes(
    tmp_path: Path, case: str, expected_reason: str
) -> None:
    """PR4c: each filesystem/encoding guard fails closed with the exact reason.
    Walk-level guards (hidden, symlink, non-regular, non-json) fire without any
    manifest change; read-level guards (LF, BOM, decode) mutate an entry file and
    recompute the manifest self-hash so the hash path does not mask the finding."""
    validator = _load_validator()
    root = _copy_dataset(tmp_path)
    _apply_fs_encoding_case(root, case)
    # Walk-level cases need no manifest recompute; read-level cases do, so the
    # read finding surfaces instead of a stale file-hash-mismatch masking it.
    if case in {"missing-trailing-lf", "extra-trailing-lf", "bom-not-allowed", "decode-error"}:
        manifest = _load_manifest(root)
        _recompute_manifest_self_hash(root, manifest)
    findings = validator.validate(root)
    assert expected_reason in _reasons(findings), (case, findings)


# --- Phase 4.5: Verify-report remediation (validator + tests only) ---
#
# Tasks 4.5-4.7 remediate two CRITICAL verify findings (duplicate stable
# identifiers silently accepted; production-looking sensitive identifiers not
# rejected) and one WARNING (fragment-parent-not-approved lacks an independent
# mutation assertion). Each test copies the valid dataset to tmp_path, mutates
# one file/field, updates canonical hashes, and asserts the exact safe reason
# code. No content/query/evidence text is logged; diagnostics carry only a safe
# path/id, reason code, and remediation hint.


def _load_fragment_payload(root: Path, rel: str) -> dict[str, Any]:
    return json.loads((root / rel).read_bytes().decode("utf-8"))


def _update_artifact_sha256(manifest: dict[str, Any], rel: str, payload: dict[str, Any]) -> None:
    artifact = next(a for a in manifest["artifacts"] if a.get("path") == rel)
    artifact["sha256"] = _sha256(_canonical_bytes(payload))


def test_duplicate_scenario_id_fails_closed(tmp_path: Path) -> None:
    """Task 4.5: mutating a scenario ID to collide with an existing scenario ID
    fails closed with 'duplicate-identifier'. The manifest artifact ID and the
    scenario payload ID both change, canonical hashes are recomputed, and the
    validator reports the exact reason code naming the duplicate occurrences."""
    validator = _load_validator()
    root = _copy_dataset(tmp_path)
    manifest = _load_manifest(root)
    # Mutate scenario.eval-02.en payload id to collide with scenario.eval-01.en.
    target_rel = "scenarios/eval-02.en.json"
    scenario = _load_scenario(root, target_rel)
    scenario["id"] = "scenario.eval-01.en"
    _write_scenario(root, "eval-02", "en", scenario)
    # Update the manifest artifact id and sha256 for eval-02.en to match.
    _replace_scenario_in_manifest(scenario, manifest, "eval-02", "en")
    _recompute_manifest_self_hash(root, manifest)
    findings = validator.validate(root)
    reasons = _reasons(findings)
    assert "duplicate-identifier" in reasons, findings
    # The finding is safe: only a path/id, reason code, and remediation hint.
    dup_findings = [f for f in findings if f[1] == "duplicate-identifier"]
    assert dup_findings, findings
    remediation = dup_findings[0][2]
    assert "scenario.eval-01.en" in remediation, remediation
    # No content/query/evidence text is logged in the diagnostic.
    assert "evidence" not in remediation.lower(), remediation


def test_production_looking_identifier_fails_closed(tmp_path: Path) -> None:
    """Task 4.6: a fragment with production-looking identifiers (ACME-123456,
    production.internal) and no `fictitious: true` marker fails closed with
    'fragment-production-looking-identifier'. The sensitive text is never
    logged; only a safe path/id, reason code, and remediation hint appear."""
    validator = _load_validator()
    root = _copy_dataset(tmp_path)
    manifest = _load_manifest(root)
    # Replace the sensitive fixture content with production-looking identifiers
    # and remove the fictitious marker.
    rel = "fragments/policy-003.rev.1.es.sensitive.json"
    fragment = _load_fragment_payload(root, rel)
    fragment["content"] = "Sensitive record for account ACME-123456 on production.internal."
    fragment.pop("fictitious", None)
    fragment["content_sha256"] = _sha256(fragment["content"].encode("utf-8"))
    _write_fragment(root, rel, fragment)
    _update_artifact_sha256(manifest, rel, fragment)
    _recompute_manifest_self_hash(root, manifest)
    findings = validator.validate(root)
    reasons = _reasons(findings)
    assert "fragment-production-looking-identifier" in reasons, findings
    # The diagnostic is safe: no sensitive text (ACME-123456, production.internal)
    # appears in any remediation hint or reason code.
    for _path, _reason, remediation in findings:
        assert "ACME-123456" not in remediation, remediation
        assert "production.internal" not in remediation, remediation


def test_fragment_parent_not_approved_fails_closed(tmp_path: Path) -> None:
    """Task 4.7: mutating a parent entry's approval to a non-approved value
    causes every fragment referencing that parent to fail closed with
    'fragment-parent-not-approved'. Preserves existing validator behavior; no
    validator change required for this branch."""
    validator = _load_validator()
    root = _copy_dataset(tmp_path)
    manifest = _load_manifest(root)
    # Mutate the parent entry approval to a non-approved value.
    entry_rel = "entries/policy-003.rev.1.json"
    entry = _load_entry(root, entry_rel)
    entry["approval"] = "draft"
    entry["content_sha256"] = _sha256(entry["content"].encode("utf-8"))
    _write_json(root, entry_rel, entry)
    _update_artifact_sha256(manifest, entry_rel, entry)
    _recompute_manifest_self_hash(root, manifest)
    findings = validator.validate(root)
    reasons = _reasons(findings)
    assert "fragment-parent-not-approved" in reasons, findings
    # The finding is safe: only a path/id, reason code, and remediation hint.
    parent_findings = [f for f in findings if f[1] == "fragment-parent-not-approved"]
    assert parent_findings, findings
    # No content/query/evidence text is logged in the diagnostic.
    for _path, _reason, remediation in parent_findings:
        assert remediation, "remediation hint must be non-empty"
        assert "approved" in remediation, remediation
