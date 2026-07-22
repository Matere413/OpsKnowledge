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

import importlib.util
import json
import os
import shutil
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
