"""Gate report serializer: allowlisted, content-free JSON serialization.

Serializes only safe fields: IDs, enums, versions, thresholds, observations
(citation IDs only, never content), decisions, reason codes, timestamps, and
durations. Never emits question/answer/claim/citation-content/provider-payload
text.

This module owns the serializer core for the gate report. Atomic promotion
(``GateReportAdapter``) and baseline bootstrap belong to later stacked slices
and live in this same module once those slices land.
"""

from __future__ import annotations

import json
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


__all__ = [
    "GATE_VERSION",
    "SCHEMA_VERSION",
    "serialize_gate_report",
]
