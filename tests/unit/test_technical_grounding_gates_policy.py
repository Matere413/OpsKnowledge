"""Unit 1 contracts: technical grounding safety gate policy and domain.

Strict-TDD RED/GREEN scope for the first stacked slice (slice-1-policy-runner):
- 1.1 RED: immutable types, allowlisted statuses/reasons, five floors,
  cross-multiplication, malformed/boolean/negative/zero-denominator evidence,
  and baseline validation
- 1.2 GREEN: domain.py, policy.py, ports.py
- 1.3 REFACTOR/verify: dependency-free, harness-independent

The runner, critical contracts, report, and CLI belong to later units/slices
and are NOT imported here.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest

NEG_ONE = -1


def _raises(func: Callable[..., Any], *args: Any, **kwargs: Any) -> bool:
    """Return True when func(*args, **kwargs) raises any Exception.

    Used in place of ``pytest.raises`` because the repo's focused-test guard
    only allows ``pytest.mark.parametrize``; ``pytest.raises`` is flagged as
    an unsupported test API.
    """
    try:
        func(*args, **kwargs)
    except Exception:
        return True
    return False


def _signal(num: int, den: int):
    from backend.features.evaluation.gates.domain import GateSignal

    return GateSignal(numerator=num, denominator=den)


def _metrics():
    """The reviewed baseline metrics matching the committed harness summary."""
    from backend.features.evaluation.gates.domain import GateMetrics

    return GateMetrics(
        language_routing=_signal(34, 34),
        sensitive_block=_signal(2, 2),
        outcome_classification=_signal(9, 34),
        citation_exact_match=_signal(10, 34),
        contradiction_detection=_signal(0, 4),
    )


# ---------------------------------------------------------------------------
# Task 1.1 RED: immutable types, allowlisted statuses/reasons, five floors
# ---------------------------------------------------------------------------


def test_gate_signal_is_frozen_and_slotted() -> None:
    from backend.features.evaluation.gates.domain import GateSignal

    signal = GateSignal(numerator=9, denominator=34)
    assert signal.numerator == 9
    assert signal.denominator == 34
    assert _raises(setattr, signal, "numerator", 10)
    assert _raises(setattr, signal, "extra", 1)


def test_gate_floor_is_frozen_and_slotted() -> None:
    from backend.features.evaluation.gates.domain import GateFloor

    floor = GateFloor(numerator=9, denominator=34, regression="block")
    assert floor.numerator == 9
    assert floor.denominator == 34
    assert floor.regression == "block"
    assert _raises(setattr, floor, "numerator", 10)


def test_gate_decision_is_frozen_and_slotted() -> None:
    from backend.features.evaluation.gates.domain import GateDecision

    decision = GateDecision(status="pass", reason_codes=("pass",))
    assert decision.status == "pass"
    assert decision.reason_codes == ("pass",)
    assert _raises(setattr, decision, "status", "block")


def test_gate_metrics_is_frozen_and_slotted() -> None:
    metrics = _metrics()
    assert _raises(setattr, metrics, "language_routing", None)
    assert _raises(setattr, metrics, "extra", 1)


def test_gate_statuses_are_exactly_pass_block_escalate() -> None:
    from backend.features.evaluation.gates.domain import GATE_STATUSES

    assert frozenset({"pass", "block", "escalate"}) == GATE_STATUSES


def test_gate_reason_codes_include_all_expected() -> None:
    from backend.features.evaluation.gates.domain import GATE_REASON_CODES

    expected = {
        "pass",
        "outcome_regression",
        "citation_regression",
        "contradiction_regression",
        "language_regression",
        "sensitive_regression",
        "critical_contract_mismatch",
        "invalid_evidence",
        "unknown_reason_code",
    }
    assert expected <= GATE_REASON_CODES


# --- Five floors ---


@pytest.mark.parametrize(
    ("name", "numerator", "denominator", "regression"),
    (
        ("language_routing", 34, 34, "escalate"),
        ("sensitive_block", 2, 2, "escalate"),
        ("outcome_classification", 9, 34, "block"),
        ("citation_exact_match", 10, 34, "block"),
        ("contradiction_detection", 0, 4, "block"),
    ),
)
def test_five_floors_have_reviewed_values_and_regression_types(
    name: str, numerator: int, denominator: int, regression: str
) -> None:
    from backend.features.evaluation.gates.domain import FLOORS

    floor = FLOORS[name]
    assert floor.numerator == numerator
    assert floor.denominator == denominator
    assert floor.regression == regression


def test_floors_mapping_is_immutable() -> None:
    from backend.features.evaluation.gates.domain import FLOORS

    assert _raises(setattr, FLOORS, "outcome_classification", None)
    assert _raises(lambda: FLOORS.update({"extra": None}))  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Task 1.1 RED: cross-multiplication — observed meets floor and baseline
# ---------------------------------------------------------------------------


def test_observed_meeting_all_floors_and_baseline_returns_pass() -> None:
    from backend.features.evaluation.gates.policy import evaluate_floor_policy

    observed = _metrics()
    decision = evaluate_floor_policy(observed=observed, baseline=_metrics())
    assert decision.status == "pass"
    assert "pass" in decision.reason_codes


def test_observed_above_floor_returns_pass() -> None:
    from backend.features.evaluation.gates.policy import evaluate_floor_policy

    observed = _metrics_above_floor()
    decision = evaluate_floor_policy(observed=observed, baseline=_metrics())
    assert decision.status == "pass"


def _metrics_above_floor():
    from backend.features.evaluation.gates.domain import GateMetrics

    return GateMetrics(
        language_routing=_signal(34, 34),
        sensitive_block=_signal(2, 2),
        outcome_classification=_signal(10, 34),
        citation_exact_match=_signal(11, 34),
        contradiction_detection=_signal(1, 4),
    )


# ---------------------------------------------------------------------------
# Task 1.1 RED: cross-multiplication — observed below floor
# ---------------------------------------------------------------------------


def test_outcome_below_floor_returns_block() -> None:
    from backend.features.evaluation.gates.policy import evaluate_floor_policy

    observed = _metrics_with(outcome_classification=_signal(8, 34))
    decision = evaluate_floor_policy(observed=observed, baseline=_metrics())
    assert decision.status == "block"
    assert "outcome_regression" in decision.reason_codes


def test_citation_below_floor_returns_block() -> None:
    from backend.features.evaluation.gates.policy import evaluate_floor_policy

    observed = _metrics_with(citation_exact_match=_signal(9, 34))
    decision = evaluate_floor_policy(observed=observed, baseline=_metrics())
    assert decision.status == "block"
    assert "citation_regression" in decision.reason_codes


def test_contradiction_below_baseline_returns_block() -> None:
    from backend.features.evaluation.gates.policy import evaluate_floor_policy

    baseline = _metrics_with(contradiction_detection=_signal(1, 4))
    observed = _metrics_with(contradiction_detection=_signal(0, 4))
    decision = evaluate_floor_policy(observed=observed, baseline=baseline)
    assert decision.status == "block"
    assert "contradiction_regression" in decision.reason_codes


def test_language_below_floor_returns_escalate() -> None:
    from backend.features.evaluation.gates.policy import evaluate_floor_policy

    observed = _metrics_with(language_routing=_signal(33, 34))
    decision = evaluate_floor_policy(observed=observed, baseline=_metrics())
    assert decision.status == "escalate"
    assert "language_regression" in decision.reason_codes


def test_sensitive_below_floor_returns_escalate() -> None:
    from backend.features.evaluation.gates.policy import evaluate_floor_policy

    observed = _metrics_with(sensitive_block=_signal(1, 2))
    decision = evaluate_floor_policy(observed=observed, baseline=_metrics())
    assert decision.status == "escalate"
    assert "sensitive_regression" in decision.reason_codes


def test_language_below_baseline_returns_escalate() -> None:
    from backend.features.evaluation.gates.policy import evaluate_floor_policy

    baseline = _metrics_with(language_routing=_signal(34, 34))
    observed = _metrics_with(language_routing=_signal(33, 34))
    decision = evaluate_floor_policy(observed=observed, baseline=baseline)
    assert decision.status == "escalate"
    assert "language_regression" in decision.reason_codes


# ---------------------------------------------------------------------------
# Task 1.1 RED: precedence — block outranks escalate
# ---------------------------------------------------------------------------


def test_block_outranks_escalate_when_both_regress() -> None:
    from backend.features.evaluation.gates.policy import evaluate_floor_policy

    observed = _metrics_with(
        language_routing=_signal(33, 34),
        outcome_classification=_signal(8, 34),
    )
    decision = evaluate_floor_policy(observed=observed, baseline=_metrics())
    assert decision.status == "block"
    assert "language_regression" in decision.reason_codes
    assert "outcome_regression" in decision.reason_codes


def test_multiple_block_regressions_aggregate_reason_codes() -> None:
    from backend.features.evaluation.gates.policy import evaluate_floor_policy

    observed = _metrics_with(
        outcome_classification=_signal(8, 34),
        citation_exact_match=_signal(9, 34),
    )
    decision = evaluate_floor_policy(observed=observed, baseline=_metrics())
    assert decision.status == "block"
    assert "outcome_regression" in decision.reason_codes
    assert "citation_regression" in decision.reason_codes


# ---------------------------------------------------------------------------
# Task 1.1 RED: malformed evidence — fail closed with invalid_evidence
# ---------------------------------------------------------------------------


_INVALID_PAIRS_OBSERVED = (
    (True, 34),
    (9, True),
    (NEG_ONE, 34),
    (9, NEG_ONE),
    (35, 34),
    (9, 0),
)
_INVALID_PAIRS_BASELINE = (
    (True, 34),
    (NEG_ONE, 34),
    (35, 34),
    (9, 0),
)


@pytest.mark.parametrize(
    "invalid_pair",
    _INVALID_PAIRS_OBSERVED,
    ids=["bool-num", "bool-den", "neg-num", "neg-den", "num-gt-den", "zero-den"],
)
def test_malformed_observed_signal_returns_block_with_invalid_evidence(
    invalid_pair: tuple[object, object],
) -> None:
    from backend.features.evaluation.gates.domain import GateMetrics, GateSignal
    from backend.features.evaluation.gates.policy import evaluate_floor_policy

    numerator, denominator = invalid_pair
    observed = GateMetrics(
        language_routing=GateSignal(34, 34),
        sensitive_block=GateSignal(2, 2),
        outcome_classification=GateSignal(numerator, denominator),  # type: ignore[arg-type]
        citation_exact_match=GateSignal(10, 34),
        contradiction_detection=GateSignal(0, 4),
    )
    decision = evaluate_floor_policy(observed=observed, baseline=_metrics())
    assert decision.status == "block"
    assert "invalid_evidence" in decision.reason_codes


@pytest.mark.parametrize(
    "invalid_pair",
    _INVALID_PAIRS_BASELINE,
    ids=["bool-num", "neg-num", "num-gt-den", "zero-den"],
)
def test_malformed_baseline_signal_returns_block_with_invalid_evidence(
    invalid_pair: tuple[object, object],
) -> None:
    from backend.features.evaluation.gates.domain import GateMetrics, GateSignal
    from backend.features.evaluation.gates.policy import evaluate_floor_policy

    numerator, denominator = invalid_pair
    baseline = GateMetrics(
        language_routing=GateSignal(34, 34),
        sensitive_block=GateSignal(2, 2),
        outcome_classification=GateSignal(numerator, denominator),  # type: ignore[arg-type]
        citation_exact_match=GateSignal(10, 34),
        contradiction_detection=GateSignal(0, 4),
    )
    decision = evaluate_floor_policy(observed=_metrics(), baseline=baseline)
    assert decision.status == "block"
    assert "invalid_evidence" in decision.reason_codes


def test_missing_observed_metric_returns_block_with_invalid_evidence() -> None:
    from backend.features.evaluation.gates.domain import GateMetrics, GateSignal
    from backend.features.evaluation.gates.policy import evaluate_floor_policy

    observed = GateMetrics(
        language_routing=GateSignal(34, 34),
        sensitive_block=GateSignal(2, 2),
        outcome_classification=None,  # type: ignore[arg-type]
        citation_exact_match=GateSignal(10, 34),
        contradiction_detection=GateSignal(0, 4),
    )
    decision = evaluate_floor_policy(observed=observed, baseline=_metrics())
    assert decision.status == "block"
    assert "invalid_evidence" in decision.reason_codes


def test_missing_baseline_metric_returns_block_with_invalid_evidence() -> None:
    from backend.features.evaluation.gates.domain import GateMetrics, GateSignal
    from backend.features.evaluation.gates.policy import evaluate_floor_policy

    baseline = GateMetrics(
        language_routing=GateSignal(34, 34),
        sensitive_block=GateSignal(2, 2),
        outcome_classification=None,  # type: ignore[arg-type]
        citation_exact_match=GateSignal(10, 34),
        contradiction_detection=GateSignal(0, 4),
    )
    decision = evaluate_floor_policy(observed=_metrics(), baseline=baseline)
    assert decision.status == "block"
    assert "invalid_evidence" in decision.reason_codes


def test_invalid_evidence_outranks_floor_regressions() -> None:
    """Malformed evidence MUST block before any floor comparison runs."""
    from backend.features.evaluation.gates.domain import GateMetrics, GateSignal
    from backend.features.evaluation.gates.policy import evaluate_floor_policy

    observed = GateMetrics(
        language_routing=GateSignal(33, 34),  # would be escalate
        sensitive_block=GateSignal(2, 2),
        outcome_classification=GateSignal(8, 34),  # would be block
        citation_exact_match=GateSignal(10, 34),
        contradiction_detection=GateSignal(0, 0),  # zero-denominator: invalid
    )
    decision = evaluate_floor_policy(observed=observed, baseline=_metrics())
    assert decision.status == "block"
    assert decision.reason_codes == ("invalid_evidence",)


# ---------------------------------------------------------------------------
# Task 1.1 RED: critical expectations table and allowlisted reason codes
# ---------------------------------------------------------------------------


def test_critical_expectations_cover_all_required_scenarios() -> None:
    from backend.features.evaluation.gates.domain import CRITICAL_EXPECTATIONS

    case_ids = {exp.case_id for exp in CRITICAL_EXPECTATIONS}
    expected_ids = {
        "scenario.eval-11.es",
        "scenario.eval-11.en",
        "scenario.eval-12.es",
        "scenario.eval-12.en",
        "scenario.eval-16.es",
        "scenario.eval-16.en",
        "scenario.eval-15.es",
        "scenario.eval-15.en",
        "scenario.eval-13.es",
        "scenario.eval-13.en",
        "injected-provider-failure-es",
        "injected-provider-failure-en",
    }
    assert case_ids == expected_ids


def test_critical_expectations_all_require_empty_citations() -> None:
    from backend.features.evaluation.gates.domain import CRITICAL_EXPECTATIONS

    for exp in CRITICAL_EXPECTATIONS:
        assert exp.requires_empty_citations is True


def test_critical_expectation_is_frozen_and_slotted() -> None:
    from backend.features.evaluation.gates.domain import CriticalExpectation

    exp = CriticalExpectation(
        case_id="scenario.eval-11.es",
        expected_outcome="contradictory_information",
        expected_reason_code="contradiction_detected",
        requires_empty_citations=True,
    )
    assert exp.case_id == "scenario.eval-11.es"
    assert _raises(setattr, exp, "case_id", "other")


def test_allowed_reason_codes_include_critical_contract_codes() -> None:
    from backend.features.evaluation.gates.domain import ALLOWED_REASON_CODES

    expected = {
        "contradiction_detected",
        "sensitive_blocked",
        "prompt_override_blocked",
        "out_of_scope",
        "provider-timeout",
        "none",
        "insufficient_evidence",
    }
    assert expected <= ALLOWED_REASON_CODES


def test_metric_names_are_exactly_five_in_order() -> None:
    from backend.features.evaluation.gates.domain import METRIC_NAMES

    assert METRIC_NAMES == (
        "language_routing",
        "sensitive_block",
        "outcome_classification",
        "citation_exact_match",
        "contradiction_detection",
    )


# ---------------------------------------------------------------------------
# Task 1.1 RED: dependency-free and harness-independent
# ---------------------------------------------------------------------------


def test_gate_domain_imports_no_harness_or_kernel_modules() -> None:
    import backend.features.evaluation.gates.domain as gate_domain

    forbidden = {
        "backend.features.evaluation.application",
        "backend.features.evaluation.adapters.kernel",
        "backend.features.evaluation.adapters.dataset",
        "backend.features.query",
    }
    for forbidden_mod in forbidden:
        assert forbidden_mod not in vars(gate_domain), (
            f"gate domain must not import {forbidden_mod}"
        )


def test_gate_policy_imports_no_harness_or_kernel_modules() -> None:
    import backend.features.evaluation.gates.policy as gate_policy

    forbidden = {
        "backend.features.evaluation.application",
        "backend.features.evaluation.adapters.kernel",
        "backend.features.evaluation.adapters.dataset",
        "backend.features.query",
    }
    for forbidden_mod in forbidden:
        assert forbidden_mod not in vars(gate_policy), (
            f"gate policy must not import {forbidden_mod}"
        )


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _metrics_with(**overrides: Any) -> Any:
    """Construct reviewed-baseline metrics with specific field overrides."""
    from backend.features.evaluation.gates.domain import GateMetrics

    defaults = {
        "language_routing": _signal(34, 34),
        "sensitive_block": _signal(2, 2),
        "outcome_classification": _signal(9, 34),
        "citation_exact_match": _signal(10, 34),
        "contradiction_detection": _signal(0, 4),
    }
    defaults.update(overrides)
    return GateMetrics(**defaults)
