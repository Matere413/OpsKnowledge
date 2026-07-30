"""Safe report adapter: allowlisted serialization and atomic baseline retention.

Serializes only safe fields: IDs, enums, versions, timestamps, booleans, counts,
rates, profile, and duration. Never emits question/answer/citation content,
claim text, or provider payloads.

Baseline retention is atomic: ``current/`` holds the latest reviewed baseline;
``previous/`` is created only when a later replacement exists. Incomplete
promotions (empty payload) are rejected with no baseline written.
"""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from backend.features.evaluation.application import RunSummary

_FILES = ("summary.json", "records.jsonl", "report.txt")
_SUMMARY_KEYS = frozenset(
    [
        "schema_version",
        "contract_version",
        "population_version",
        "population_digest",
        "replaces_population_version",
        "manifest_digest",
        "mapping_digest",
        "run_id",
        "profile",
        "provider_mode",
        "timestamp",
        "duration_seconds",
        "total_cases",
        "exclusions",
        "metrics",
        "contract_metrics",
    ]
)  # noqa: E501, SIM905
_METRICS = frozenset(
    [
        "outcome_classification",
        "citation_exact_match",
        "language_routing",
        "sensitive_block",
        "contradiction_detection",
    ]
)  # noqa: E501, SIM905
_CONTRACT_METRICS = frozenset(
    ["language_accuracy", "correct_abstention", "unsupported_claim_escape"]
)  # noqa: E501, SIM905
_RECORD_KEYS = frozenset(
    [
        "case_id",
        "language",
        "routed_language",
        "expected_outcome",
        "expected_reason_code",
        "observed_outcome",
        "reason_code",
        "escalation",
        "citation_ids",
        "citations_match",
        "language_eligible",
        "abstention_eligible",
        "escape_required",
        "provider_failure",
    ]
)  # noqa: E501, SIM905
_os_replace = os.replace


def _metric_dict(signal: object) -> dict[str, int]:
    return {"numerator": signal.numerator, "denominator": signal.denominator}  # type: ignore[attr-defined]


def _summary_data(summary: RunSummary) -> dict[str, Any]:
    if summary.contract_metrics is None:
        raise ValueError("contract-metrics-missing")
    population = summary.population
    data = {
        "schema_version": "1",
        "contract_version": "1",
        "population_version": getattr(population, "version", None),
        "population_digest": getattr(population, "digest", None),
        "replaces_population_version": getattr(summary, "replaces_population_version", None),
        "manifest_digest": getattr(summary, "manifest_digest", None),
        "mapping_digest": getattr(summary, "mapping_digest", None),
        "run_id": summary.identity.run_id,
        "profile": "development",
        "provider_mode": "fake",
        "timestamp": getattr(summary, "timestamp", None),
        "duration_seconds": getattr(summary, "duration_seconds", None),
        "total_cases": len(summary.results),
        "exclusions": {
            "language_routing": sum(not c.language_eligible for c in summary.cases),
            "sensitive": sum(c.safety_classification == "sensitive" for c in summary.cases),
        },
        "metrics": {
            name: _metric_dict(getattr(summary.metrics, name)) for name in sorted(_METRICS)
        },
        "contract_metrics": {
            name: _metric_dict(getattr(summary.contract_metrics, name))
            for name in sorted(_CONTRACT_METRICS)
        },
    }
    return data


def serialize_summary(summary: RunSummary) -> str:
    return json.dumps(_summary_data(summary), sort_keys=True, separators=(",", ":"))


def serialize_records(summary: RunSummary) -> str:
    cases = {case.scenario_id: case for case in summary.cases}
    population = {case.case_id: case for case in getattr(summary.population, "cases", ())}
    lines = []
    for result in sorted(summary.results, key=lambda item: item.case_id):
        case = cases.get(result.case_id)
        if case is None:
            raise ValueError("record-case-mismatch")
        record = {
            "case_id": result.case_id,
            "language": case.language,
            "routed_language": result.language,
            "expected_outcome": case.expected_outcome,
            "expected_reason_code": case.expected_reason_code,
            "observed_outcome": result.observed_outcome,
            "reason_code": result.reason_code,
            "escalation": result.escalation,
            "citation_ids": sorted(result.citation_ids),
            "citations_match": result.citations_match,
            "language_eligible": case.language_eligible,
            "abstention_eligible": case.abstention_eligible,
            "escape_required": case.escape_required,
            "provider_failure": bool(
                getattr(population.get(result.case_id), "provider_failure", False)
            ),
        }
        lines.append(json.dumps(record, sort_keys=True, separators=(",", ":")))
    return "\n".join(lines)


def serialize_human(summary: RunSummary) -> str:
    data = _summary_data(summary)
    metadata = (
        "run_id",
        "schema_version",
        "contract_version",
        "population_version",
        "replaces_population_version",
        "profile",
        "provider_mode",
        "timestamp",
        "duration_seconds",
        "total_cases",
        "exclusions",
    )  # noqa: E501
    lines = ["OpsKnowledge quality evaluation"]
    lines += [
        f"{key}: {json.dumps(data[key], sort_keys=True, separators=(',', ':'))}" for key in metadata
    ]
    lines += [
        f"{key}: {data['metrics'][key]['numerator']}/{data['metrics'][key]['denominator']}"
        for key in sorted(_METRICS)
    ]
    lines += [
        f"{key}: {data['contract_metrics'][key]['numerator']}/"
        f"{data['contract_metrics'][key]['denominator']}"
        for key in sorted(_CONTRACT_METRICS)
    ]
    return "\n".join(lines) + "\n"


@dataclass(frozen=True, slots=True)
class ReportAdapter:
    """Stage and rotate the three reviewed files without losing evidence."""

    base_dir: Path

    def promote(
        self,
        run_id: str,
        payload: bytes,
        records: bytes | str | None = None,
        report: bytes | str | None = None,
    ) -> None:
        if records is None and report is None:
            bundle = {"summary.json": payload}
        elif records is not None and report is not None:
            bundle = {
                "summary.json": payload,
                "records.jsonl": self._bytes(records),
                "report.txt": self._bytes(report),
            }
        else:
            raise ValueError("incomplete-promotion: expected three files")
        if set(bundle) not in ({"summary.json"}, set(_FILES)) or any(
            not value for value in bundle.values()
        ):
            raise ValueError("incomplete-promotion: expected three files")
        if set(bundle) == set(_FILES):
            _validate_bundle(run_id, bundle)
        self._rotate(run_id, bundle)

    @staticmethod
    def _bytes(value: bytes | str) -> bytes:
        return value if isinstance(value, bytes) else value.encode("utf-8")

    def _rotate(self, run_id: str, bundle: dict[str, bytes]) -> None:
        if not run_id or Path(run_id).name != run_id:
            raise ValueError("invalid-run-id")
        current, previous = self.base_dir / "current", self.base_dir / "previous"
        staged = self.base_dir / f".staging-{run_id}"
        history = self.base_dir / "history" / run_id
        if history.exists():
            if _read_bundle(history / "staged") != bundle or _read_bundle(current) != bundle:
                raise ValueError("history-run-id-reuse")
            return
        if staged.exists():
            shutil.rmtree(staged)
        staged.mkdir(parents=True, exist_ok=True)
        for name, value in bundle.items():
            (staged / name).write_bytes(value)
        _snapshot(current, history / "current")
        _snapshot(previous, history / "previous")
        _snapshot(staged, history / "staged")
        backup = self.base_dir / f".previous-backup-{run_id}"
        had_previous, moved_current = previous.exists(), False
        try:
            if had_previous:
                _os_replace(previous, backup)
            if current.exists():
                _os_replace(current, previous)
                moved_current = True
            _os_replace(staged, current)
        except OSError:
            if moved_current:
                _os_replace(previous, current)
            if had_previous and backup.exists():
                _os_replace(backup, previous)
            shutil.rmtree(staged, ignore_errors=True)
            raise
        if had_previous:
            shutil.rmtree(backup, ignore_errors=True)


def _read_bundle(path: Path) -> dict[str, bytes]:
    return (
        {name: (path / name).read_bytes() for name in _FILES if (path / name).is_file()}
        if path.is_dir()
        else {}
    )  # noqa: E501


def _snapshot(source: Path, destination: Path) -> None:
    if not source.exists():
        return
    incoming = _read_bundle(source)
    if destination.exists() and _read_bundle(destination) != incoming:
        raise ValueError("history-snapshot-conflict")
    if destination.exists():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)


def _validate_bundle(run_id: str, bundle: dict[str, bytes]) -> None:
    try:
        summary = json.loads(bundle["summary.json"].decode())
        rows = [json.loads(line) for line in bundle["records.jsonl"].decode().splitlines() if line]
        bundle["report.txt"].decode()
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("malformed-report-bundle") from exc
    if (
        not isinstance(summary, dict)
        or set(summary) != _SUMMARY_KEYS
        or summary.get("run_id") != run_id
    ):  # noqa: E501
        raise ValueError("summary-allowlist-mismatch")
    if (
        set(summary.get("metrics", ())) != _METRICS
        or set(summary.get("contract_metrics", ())) != _CONTRACT_METRICS
        or any(not isinstance(row, dict) or set(row) != _RECORD_KEYS for row in rows)
    ):  # noqa: E501
        raise ValueError("bundle-allowlist-mismatch")
    raw = b"".join(bundle.values()).lower()
    if any(token in raw for token in (b"question", b"answer", b"payload", b"internal_text")):
        raise ValueError("protected-content-in-report")
