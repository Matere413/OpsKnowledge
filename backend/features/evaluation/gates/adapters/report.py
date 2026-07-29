"""Gate report adapter: allowlisted serialization and atomic promotion.

Serializes only safe fields: IDs, enums, versions, thresholds, observations
(citation IDs only, never content), decisions, reason codes, timestamps, and
durations. Never emits question/answer/claim/citation-content/provider-payload
text.

Atomic promotion is journaled: a staged directory is validated and written
before any committed path moves. ``current/`` holds the latest reviewed gate
report; ``previous/`` is created only on replacement and holds the prior
``current``. A failure during the rename transaction rolls back so prior
committed evidence remains unchanged; the next invocation recovers cleanly.

Distinct from the harness ``ReportAdapter``: the gate owns its own store so
harness multi-file writes cannot move gate ``current`` before a later failure.
"""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from backend.features.evaluation.application import RunSummary
from backend.features.evaluation.gates.domain import (
    CRITICAL_EXPECTATIONS,
    FLOORS,
    METRIC_NAMES,
    GateDecision,
    GateMetrics,
    GateSignal,
)

SCHEMA_VERSION: Final[str] = "1"
GATE_VERSION: Final[str] = "1"

_ALLOWED_REPORT_KEYS: Final[frozenset[str]] = frozenset(
    {
        "schema_version",
        "gate_version",
        "run_id",
        "profile",
        "provider_mode",
        "status",
        "reason_codes",
        "baseline_metrics",
        "observed_metrics",
        "floors",
        "critical_observations",
        "timestamp",
        "duration_seconds",
    }
)
_ALLOWED_OBSERVATION_KEYS: Final[frozenset[str]] = frozenset(
    {"case_id", "observed_outcome", "reason_code", "citation_ids", "citations_match"}
)


def _signal_dict(signal: GateSignal) -> dict[str, int]:
    return {"numerator": signal.numerator, "denominator": signal.denominator}


def _metrics_dict(metrics: GateMetrics) -> dict[str, dict[str, int]]:
    return {name: _signal_dict(metrics.by_name(name)) for name in METRIC_NAMES}


def _floors_dict() -> dict[str, dict[str, Any]]:
    return {
        name: {
            "numerator": floor.numerator,
            "denominator": floor.denominator,
            "regression": floor.regression,
        }
        for name, floor in FLOORS.items()
    }


def _critical_observations(summary: RunSummary) -> list[dict[str, Any]]:
    """Allowlisted critical observations: IDs, enums, citation IDs, booleans only.

    Selects exactly the critical case IDs from CRITICAL_EXPECTATIONS. Never
    emits citation content — only opaque citation IDs.
    """
    critical_ids = {exp.case_id for exp in CRITICAL_EXPECTATIONS}
    observations: list[dict[str, Any]] = []
    for result in summary.results:
        if result.case_id not in critical_ids:
            continue
        observations.append(
            {
                "case_id": result.case_id,
                "observed_outcome": result.observed_outcome,
                "reason_code": result.reason_code,
                "citation_ids": list(result.citation_ids),
                "citations_match": result.citations_match,
            }
        )
    return observations


def serialize_gate_report(
    *,
    decision: GateDecision,
    summary: RunSummary,
    baseline: GateMetrics,
    profile: str,
    provider_mode: str,
    timestamp: float,
    duration_seconds: float,
) -> bytes:
    """Serialize a content-free gate report to canonical JSON bytes.

    The allowlist is exact: only the keys in ``_ALLOWED_REPORT_KEYS`` appear.
    Sort keys for byte-stable output under a frozen clock.
    """
    data: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "gate_version": GATE_VERSION,
        "run_id": summary.identity.run_id,
        "profile": profile,
        "provider_mode": provider_mode,
        "status": decision.status,
        "reason_codes": list(decision.reason_codes),
        "baseline_metrics": _metrics_dict(baseline),
        "observed_metrics": _metrics_dict(_to_gate_metrics_from_summary(summary)),
        "floors": _floors_dict(),
        "critical_observations": _critical_observations(summary),
        "timestamp": timestamp,
        "duration_seconds": duration_seconds,
    }
    # Defensive: the dict above is the allowlist; assert no drift.
    assert set(data.keys()) == _ALLOWED_REPORT_KEYS
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _to_gate_metrics_from_summary(summary: RunSummary) -> GateMetrics:
    """Adapt harness Metrics to GateMetrics for serialization (observed)."""
    from backend.features.evaluation.gates.application import _to_gate_metrics

    return _to_gate_metrics(summary.metrics)


def _validate_report_payload(payload: bytes) -> None:
    """Reject empty, malformed, or non-allowlisted payloads before any I/O."""
    if not payload:
        raise ValueError("incomplete-promotion: empty payload")
    try:
        data = json.loads(payload.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("malformed gate report payload") from exc
    if not isinstance(data, dict):
        raise ValueError("malformed gate report payload: not an object")
    if set(data.keys()) != _ALLOWED_REPORT_KEYS:
        raise ValueError("gate report payload keys do not match allowlist")
    # Minimal structural checks for safe fields.
    if data.get("status") not in {"pass", "block", "escalate"}:
        raise ValueError("gate report payload has invalid status")


# os.replace is module-level so tests can monkeypatch it to inject failures.
_os_replace = os.replace


@dataclass(frozen=True, slots=True)
class GateReportAdapter:
    """Atomic gate evidence store: at most current + previous.

    Validates the staged payload before touching any committed path. On a
    rename failure, rolls back so prior committed evidence is unchanged.
    """

    base_dir: Path

    def promote(self, run_id: str, payload: bytes) -> None:
        _validate_report_payload(payload)
        current = self.base_dir / "current"
        previous = self.base_dir / "previous"
        staged = self.base_dir / f".staging-{run_id}"
        # Clean any stale staging from a prior failed run.
        if staged.exists():
            shutil.rmtree(staged)
        staged.mkdir(parents=True, exist_ok=True)
        (staged / "report.json").write_bytes(payload)

        if current.exists():
            # Move current -> previous first; if that fails, current is untouched
            # but staging must be cleaned so the next run starts fresh.
            # Preserve a pre-existing previous as a backup so a failed final
            # rename can restore BOTH prior committed snapshots unchanged.
            backup_previous = self.base_dir / f".previous-backup-{run_id}"
            prior_previous_existed = previous.exists()
            if prior_previous_existed:
                # Acquire the backup inside a cleanup guard: os.replace is atomic,
                # so a failure here leaves current AND previous untouched; only
                # staging must be removed so the next run starts fresh.
                try:
                    _os_replace(previous, backup_previous)
                except OSError:
                    shutil.rmtree(staged, ignore_errors=True)
                    raise
            try:
                _os_replace(current, previous)
                try:
                    _os_replace(staged, current)
                except OSError:
                    # Rollback: restore prior current from previous, then
                    # restore the pre-existing previous from its backup.
                    _os_replace(previous, current)
                    if prior_previous_existed:
                        _os_replace(backup_previous, previous)
                    shutil.rmtree(staged, ignore_errors=True)
                    raise
                # Success: remove the backup of the old previous (now replaced).
                if prior_previous_existed:
                    shutil.rmtree(backup_previous, ignore_errors=True)
            except OSError:
                # current->previous failed; restore the pre-existing previous.
                if prior_previous_existed:
                    _os_replace(backup_previous, previous)
                shutil.rmtree(staged, ignore_errors=True)
                raise
        else:
            _os_replace(staged, current)


def _signal_from_dict(raw: dict[str, Any]) -> GateSignal:
    num = raw["numerator"]
    den = raw["denominator"]
    if not isinstance(num, int) or isinstance(num, bool):
        raise ValueError("invalid signal numerator")
    if not isinstance(den, int) or isinstance(den, bool):
        raise ValueError("invalid signal denominator")
    if num < 0 or den < 0:
        raise ValueError("negative signal value")
    if den == 0:
        raise ValueError("zero denominator")
    if num > den:
        raise ValueError("numerator exceeds denominator")
    return GateSignal(numerator=num, denominator=den)


def _metrics_from_dict(raw: dict[str, Any]) -> GateMetrics:
    expected = set(METRIC_NAMES)
    if set(raw.keys()) != expected:
        raise ValueError("metrics keys do not match expected signals")
    return GateMetrics(
        language_routing=_signal_from_dict(raw["language_routing"]),
        sensitive_block=_signal_from_dict(raw["sensitive_block"]),
        outcome_classification=_signal_from_dict(raw["outcome_classification"]),
        citation_exact_match=_signal_from_dict(raw["citation_exact_match"]),
        contradiction_detection=_signal_from_dict(raw["contradiction_detection"]),
    )


def bootstrap_baseline(*, gate_dir: Path, harness_current: Path) -> GateMetrics:
    """Resolve the immutable baseline for the current run.

    On the first gate run (no gate ``current/``), bootstraps from the validated
    harness ``evaluation-runs/current/summary.json``. On later runs, reads the
    gate snapshot ``gate_dir/current/report.json`` so the baseline is the prior
    reviewed gate result. Missing or malformed sources block (raise).
    """
    gate_report = gate_dir / "current" / "report.json"
    if gate_report.exists():
        try:
            data = json.loads(gate_report.read_bytes().decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
            raise ValueError("malformed gate baseline report") from exc
        if not isinstance(data, dict):
            raise ValueError("malformed gate baseline report: not an object")
        metrics = data.get("observed_metrics")
        if not isinstance(metrics, dict):
            raise ValueError("gate baseline report missing observed_metrics")
        return _metrics_from_dict(metrics)

    harness_summary = harness_current / "summary.json"
    if not harness_summary.exists():
        raise ValueError("no baseline source: gate and harness snapshots both missing")
    try:
        data = json.loads(harness_summary.read_bytes().decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
        raise ValueError("malformed harness summary") from exc
    if not isinstance(data, dict):
        raise ValueError("malformed harness summary: not an object")
    metrics = data.get("metrics")
    if not isinstance(metrics, dict):
        raise ValueError("harness summary missing metrics")
    return _metrics_from_dict(metrics)


__all__ = [
    "GATE_VERSION",
    "SCHEMA_VERSION",
    "GateReportAdapter",
    "bootstrap_baseline",
    "serialize_gate_report",
]
