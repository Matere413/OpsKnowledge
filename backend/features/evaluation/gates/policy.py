"""Technical grounding safety gate policy: floors, validation, precedence.

Pure functions over immutable domain values. Compares observed signals against
reviewed temporary floors AND an immutable baseline using integer cross
multiplication (no floating-point rates). Fails closed on invalid evidence.
Block outranks escalate. The policy MUST NOT import the harness application,
kernel, dataset, or query feature.
"""

from __future__ import annotations

from backend.features.evaluation.gates.domain import (
    GATE_REASON_CODES,
    METRIC_NAMES,
    GateDecision,
    GateFloor,
    GateMetrics,
    GateSignal,
)

_INVALID_EVIDENCE: tuple[str, ...] = ("invalid_evidence",)


def _is_valid_signal(signal: object) -> bool:
    """A valid signal is a GateSignal with int (not bool) numerator/denominator,
    non-negative values, numerator <= denominator, and non-zero denominator."""
    if not isinstance(signal, GateSignal):
        return False
    num = signal.numerator
    den = signal.denominator
    # bool is a subclass of int; reject it explicitly.
    if isinstance(num, bool) or isinstance(den, bool):
        return False
    if not isinstance(num, int) or not isinstance(den, int):
        return False
    if num < 0 or den < 0:
        return False
    if den == 0:
        return False
    return not num > den


def _metrics_valid(metrics: GateMetrics) -> bool:
    """All five signals must be present and valid."""
    for name in METRIC_NAMES:
        signal = getattr(metrics, name, None)
        if not _is_valid_signal(signal):
            return False
    return True


def _meets_floor(observed: GateSignal, floor: GateFloor) -> bool:
    """Cross-multiplication: observed_num * floor_den >= floor_num * observed_den.

    Integer arithmetic avoids floating-point instability at boundaries.
    """
    return observed.numerator * floor.denominator >= floor.numerator * observed.denominator


def _meets_baseline(observed: GateSignal, baseline: GateSignal) -> bool:
    """Observed must be >= baseline (cross-multiplication, integer arithmetic)."""
    return observed.numerator * baseline.denominator >= baseline.numerator * observed.denominator


def evaluate_floor_policy(
    *,
    observed: GateMetrics,
    baseline: GateMetrics,
) -> GateDecision:
    """Evaluate reviewed floors and immutable baseline; return a fail-closed decision.

    Precedence (fail-closed):
    1. Invalid evidence (malformed/missing/zero-denominator) => block, no floor checks.
    2. Outcome/citation/contradiction regression => block.
    3. Language/sensitive regression => escalate.
    4. Otherwise => pass.

    Block outranks escalate: if any block-regression and any escalate-regression
    both fire, the decision is block with all reason codes aggregated.
    """
    # 1. Fail closed on invalid evidence before any comparison.
    if not _metrics_valid(observed) or not _metrics_valid(baseline):
        return GateDecision(status="block", reason_codes=_INVALID_EVIDENCE)

    block_reasons: list[str] = []
    escalate_reasons: list[str] = []

    for name in METRIC_NAMES:
        floor = _floor_for(name)
        obs = observed.by_name(name)
        base = baseline.by_name(name)

        # Floor check (reviewed temporary floor).
        if not _meets_floor(obs, floor):
            reason = _regression_reason_for(name)
            if floor.regression == "escalate":
                escalate_reasons.append(reason)
            else:
                block_reasons.append(reason)
            continue

        # Baseline check (immutable: observed must not fall below baseline).
        if not _meets_baseline(obs, base):
            reason = _regression_reason_for(name)
            if floor.regression == "escalate":
                escalate_reasons.append(reason)
            else:
                block_reasons.append(reason)

    # Block outranks escalate in STATUS, but all regression reason codes are
    # aggregated so reviewers see every failing signal.
    if block_reasons:
        return GateDecision(status="block", reason_codes=tuple(block_reasons + escalate_reasons))
    if escalate_reasons:
        return GateDecision(status="escalate", reason_codes=tuple(escalate_reasons))
    return GateDecision(status="pass", reason_codes=("pass",))


def _floor_for(name: str) -> GateFloor:
    from backend.features.evaluation.gates.domain import FLOORS

    return FLOORS[name]


def _regression_reason_for(name: str) -> str:
    return {
        "language_routing": "language_regression",
        "sensitive_block": "sensitive_regression",
        "outcome_classification": "outcome_regression",
        "citation_exact_match": "citation_regression",
        "contradiction_detection": "contradiction_regression",
    }[name]


__all__ = [
    "evaluate_floor_policy",
]


# Suppress unused-import lint while keeping GATE_REASON_CODES importable for
# future reason-code validation extensions.
_ = GATE_REASON_CODES
