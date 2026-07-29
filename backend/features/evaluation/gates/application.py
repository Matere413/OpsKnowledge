"""Technical grounding safety gate application: runner and critical contracts.

Consumes harness ``RunSummary.metrics`` and ``CaseResult`` observations as a
separate capability. Selects critical observations by case ID, asserts their
expected outcome/reason/citation rules WITHOUT reimplementing kernel or metric
logic, evaluates the floor policy, and emits a single safe ``GateDecision``.

Precedence (fail-closed):
1. Critical contract mismatch => block (outranks everything).
2. Floor policy: invalid evidence => block; block regressions => block;
   escalate regressions => escalate; otherwise pass.

The runner MUST NOT import the kernel, query feature, or dataset adapter.
"""

from __future__ import annotations

from backend.features.evaluation.application import RunSummary
from backend.features.evaluation.domain import Metrics as HarnessMetrics
from backend.features.evaluation.domain import MetricSignal
from backend.features.evaluation.gates.domain import (
    ALLOWED_REASON_CODES,
    CRITICAL_EXPECTATIONS,
    GateDecision,
    GateMetrics,
    GateSignal,
)
from backend.features.evaluation.gates.policy import evaluate_floor_policy


def _to_gate_metrics(harness_metrics: HarnessMetrics) -> GateMetrics:
    """Adapt harness ``Metrics`` (five ``MetricSignal``) to ``GateMetrics``.

    The harness ``MetricSignal`` and gate ``GateSignal`` both expose
    ``numerator``/``denominator`` ints; this adapter reads them by attribute
    without importing the harness domain, preserving the separation contract.
    """
    return GateMetrics(
        language_routing=_to_gate_signal(harness_metrics.language_routing),
        sensitive_block=_to_gate_signal(harness_metrics.sensitive_block),
        outcome_classification=_to_gate_signal(harness_metrics.outcome_classification),
        citation_exact_match=_to_gate_signal(harness_metrics.citation_exact_match),
        contradiction_detection=_to_gate_signal(harness_metrics.contradiction_detection),
    )


def _to_gate_signal(signal: MetricSignal) -> GateSignal:
    return GateSignal(
        numerator=signal.numerator,
        denominator=signal.denominator,
    )


def _evaluate_critical_contracts(
    results: tuple[object, ...],
) -> tuple[bool, list[str]]:
    """Assert critical whole-answer contracts.

    Returns (all_passed, reason_codes). When any selected case has an
    unexpected outcome, reason code, or non-empty citations, returns
    (False, ["critical_contract_mismatch"]).
    """
    by_id = {r.case_id: r for r in results}  # type: ignore[attr-defined]
    mismatches: list[str] = []
    for expectation in CRITICAL_EXPECTATIONS:
        result = by_id.get(expectation.case_id)
        if result is None:
            mismatches.append("critical_contract_mismatch")
            continue
        # Unknown reason code => fail closed.
        if result.reason_code not in ALLOWED_REASON_CODES:  # type: ignore[attr-defined]
            mismatches.append("critical_contract_mismatch")
            continue
        if result.observed_outcome != expectation.expected_outcome:  # type: ignore[attr-defined]
            mismatches.append("critical_contract_mismatch")
            continue
        if result.reason_code != expectation.expected_reason_code:  # type: ignore[attr-defined]
            mismatches.append("critical_contract_mismatch")
            continue
        if expectation.requires_empty_citations and result.citation_ids:  # type: ignore[attr-defined]
            mismatches.append("critical_contract_mismatch")
            continue
    return (len(mismatches) == 0, mismatches)


def _validate_reason_codes(results: tuple[object, ...]) -> list[str]:
    """Validate ALL result reason codes (non-critical included); fail-closed."""
    for result in results:
        if getattr(result, "reason_code", None) not in ALLOWED_REASON_CODES:
            return ["unknown_reason_code"]
    return []


def evaluate_gate(
    *,
    summary: RunSummary,
    baseline: GateMetrics,
) -> GateDecision:
    """Evaluate the full gate: critical contracts + floor policy.

    Consumes ``summary.metrics`` directly (no recomputation) and selects
    ``summary.results`` by critical case ID. Returns a single safe
    ``GateDecision`` with fail-closed precedence.
    """
    # 1. Critical contracts (outrank floor regressions).
    critical_ok, critical_reasons = _evaluate_critical_contracts(summary.results)

    # 1b. Validate ALL result reason codes (non-critical included); fail-closed.
    unknown_reasons = _validate_reason_codes(summary.results)

    # 2. Floor policy.
    observed = _to_gate_metrics(summary.metrics)
    floor_decision = evaluate_floor_policy(observed=observed, baseline=baseline)

    # 3. Combine with precedence: critical mismatch => block (outranks all).
    if not critical_ok or unknown_reasons:
        # Block outranks escalate: if floor policy escalated, critical mismatch
        # still blocks. Aggregate critical mismatch with floor reasons.
        combined = (
            tuple(critical_reasons)
            + tuple(unknown_reasons)
            + tuple(r for r in floor_decision.reason_codes if r != "pass")
        )
        # Deduplicate while preserving order.
        seen: set[str] = set()
        ordered: list[str] = []
        for code in combined:
            if code not in seen:
                seen.add(code)
                ordered.append(code)
        return GateDecision(status="block", reason_codes=tuple(ordered))

    return floor_decision


__all__ = ["evaluate_gate"]
