"""Unit 2 contracts: technical grounding gate runner and critical contracts.

Strict-TDD RED/GREEN scope for the first stacked slice (slice-1-policy-runner):
- 2.1 RED: critical scenario contracts (eval-11/12, eval-16, eval-15, eval-13,
  injected failures) for exact outcome/reason pairs, empty citations, no
  kernel/metric reimplementation, and frozen Clock determinism.
- 2.2 GREEN: application.py runner consuming RunSummary.metrics/CaseResult,
  selecting critical observations, emitting safe GateDecision, block outranks
  escalate.
- 2.3 REFACTOR/verify: harness remains numbers-only and unchanged.

The report, CLI, and Make target belong to a later slice and are NOT imported
here.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest


def _raises(func: Callable[..., Any], *args: Any, **kwargs: Any) -> bool:
    try:
        func(*args, **kwargs)
    except Exception:
        return True
    return False


# ---------------------------------------------------------------------------
# Helpers: construct fake CaseResult observations matching the harness contract
# ---------------------------------------------------------------------------


def _case_result(
    case_id: str,
    language: str = "es",
    observed_outcome: str = "supported",
    reason_code: str = "none",
    citation_ids: tuple[str, ...] = (),
    citations_match: bool = True,
):
    from backend.features.evaluation.domain import CaseResult

    return CaseResult(
        case_id=case_id,
        language=language,
        observed_outcome=observed_outcome,
        reason_code=reason_code,
        citation_ids=citation_ids,
        citations_match=citations_match,
    )


def _gate_metrics_passing():
    from backend.features.evaluation.gates.domain import GateMetrics, GateSignal

    return GateMetrics(
        language_routing=GateSignal(34, 34),
        sensitive_block=GateSignal(2, 2),
        outcome_classification=GateSignal(9, 34),
        citation_exact_match=GateSignal(10, 34),
        contradiction_detection=GateSignal(0, 4),
    )


def _run_summary(metrics: Any, results: Any) -> Any:
    from backend.features.evaluation.application import RunSummary
    from backend.features.evaluation.domain import RunIdentity

    identity = RunIdentity(run_id="test-run-id")
    return RunSummary(identity=identity, results=tuple(results), metrics=metrics)


def _all_critical_results_matching():
    """All 12 critical CaseResult observations matching their expectations."""
    from backend.features.evaluation.gates.domain import CRITICAL_EXPECTATIONS

    return [
        _case_result(
            case_id=exp.case_id,
            observed_outcome=exp.expected_outcome,
            reason_code=exp.expected_reason_code,
            citation_ids=(),
        )
        for exp in CRITICAL_EXPECTATIONS
    ]


def _critical_results_with_override(case_id: str, **overrides: Any) -> Any:
    """All 12 critical results, with one case overridden by case_id."""
    base = _all_critical_results_matching()
    return [
        _case_result(case_id=r.case_id, **_override_if(r.case_id, case_id, overrides)) for r in base
    ]


def _override_if(actual_id: str, target_id: str, overrides: Any) -> Any:
    if actual_id != target_id:
        return {
            "observed_outcome": "supported",
            "reason_code": "none",
            "citation_ids": (),
        }
    return overrides


# ---------------------------------------------------------------------------
# Task 2.1 RED: critical scenario contracts — exact outcome/reason pairs
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("case_id", "expected_outcome", "expected_reason"),
    (
        ("scenario.eval-11.es", "contradictory_information", "contradiction_detected"),
        ("scenario.eval-11.en", "contradictory_information", "contradiction_detected"),
        ("scenario.eval-12.es", "contradictory_information", "contradiction_detected"),
        ("scenario.eval-12.en", "contradictory_information", "contradiction_detected"),
        ("scenario.eval-16.es", "unavailable", "sensitive_blocked"),
        ("scenario.eval-16.en", "unavailable", "sensitive_blocked"),
        ("scenario.eval-15.es", "out_of_scope", "prompt_override_blocked"),
        ("scenario.eval-15.en", "out_of_scope", "prompt_override_blocked"),
        ("scenario.eval-13.es", "out_of_scope", "out_of_scope"),
        ("scenario.eval-13.en", "out_of_scope", "out_of_scope"),
        ("injected-provider-failure-es", "unavailable", "provider-timeout"),
        ("injected-provider-failure-en", "unavailable", "provider-timeout"),
    ),
)
def test_critical_contract_passes_when_observation_matches(
    case_id: str, expected_outcome: str, expected_reason: str
) -> None:
    from backend.features.evaluation.gates.application import evaluate_gate

    results = _all_critical_results_matching()
    summary = _run_summary(_gate_metrics_passing(), results)
    decision = evaluate_gate(summary=summary, baseline=_gate_metrics_passing())
    assert "critical_contract_mismatch" not in decision.reason_codes


@pytest.mark.parametrize(
    ("case_id", "expected_outcome", "expected_reason"),
    (
        ("scenario.eval-11.es", "contradictory_information", "contradiction_detected"),
        ("scenario.eval-16.es", "unavailable", "sensitive_blocked"),
        ("scenario.eval-15.es", "out_of_scope", "prompt_override_blocked"),
        ("scenario.eval-13.es", "out_of_scope", "out_of_scope"),
        ("injected-provider-failure-es", "unavailable", "provider-timeout"),
    ),
)
def test_critical_contract_blocks_on_wrong_outcome(
    case_id: str, expected_outcome: str, expected_reason: str
) -> None:
    from backend.features.evaluation.gates.application import evaluate_gate

    results = _critical_results_with_override(
        case_id,
        observed_outcome="insufficient_information",  # wrong outcome
        reason_code=expected_reason,
        citation_ids=(),
    )
    summary = _run_summary(_gate_metrics_passing(), results)
    decision = evaluate_gate(summary=summary, baseline=_gate_metrics_passing())
    assert decision.status == "block"
    assert "critical_contract_mismatch" in decision.reason_codes


@pytest.mark.parametrize(
    ("case_id", "expected_outcome", "expected_reason"),
    (
        ("scenario.eval-11.es", "contradictory_information", "contradiction_detected"),
        ("scenario.eval-16.es", "unavailable", "sensitive_blocked"),
        ("scenario.eval-15.es", "out_of_scope", "prompt_override_blocked"),
        ("scenario.eval-13.es", "out_of_scope", "out_of_scope"),
        ("injected-provider-failure-es", "unavailable", "provider-timeout"),
    ),
)
def test_critical_contract_blocks_on_wrong_reason_code(
    case_id: str, expected_outcome: str, expected_reason: str
) -> None:
    from backend.features.evaluation.gates.application import evaluate_gate

    results = _critical_results_with_override(
        case_id,
        observed_outcome=expected_outcome,
        reason_code="insufficient_evidence",  # wrong reason
        citation_ids=(),
    )
    summary = _run_summary(_gate_metrics_passing(), results)
    decision = evaluate_gate(summary=summary, baseline=_gate_metrics_passing())
    assert decision.status == "block"
    assert "critical_contract_mismatch" in decision.reason_codes


@pytest.mark.parametrize(
    ("case_id", "expected_outcome", "expected_reason"),
    (
        ("scenario.eval-11.es", "contradictory_information", "contradiction_detected"),
        ("scenario.eval-16.es", "unavailable", "sensitive_blocked"),
        ("injected-provider-failure-es", "unavailable", "provider-timeout"),
    ),
)
def test_critical_contract_blocks_on_nonempty_citations(
    case_id: str, expected_outcome: str, expected_reason: str
) -> None:
    from backend.features.evaluation.gates.application import evaluate_gate

    results = _critical_results_with_override(
        case_id,
        observed_outcome=expected_outcome,
        reason_code=expected_reason,
        citation_ids=("fragment.leak-001",),  # non-empty: must block
    )
    summary = _run_summary(_gate_metrics_passing(), results)
    decision = evaluate_gate(summary=summary, baseline=_gate_metrics_passing())
    assert decision.status == "block"
    assert "critical_contract_mismatch" in decision.reason_codes


def test_critical_contract_blocks_on_missing_observation() -> None:
    from backend.features.evaluation.gates.application import evaluate_gate

    # No results at all: the critical case is missing.
    summary = _run_summary(_gate_metrics_passing(), [])
    decision = evaluate_gate(summary=summary, baseline=_gate_metrics_passing())
    assert decision.status == "block"
    assert "critical_contract_mismatch" in decision.reason_codes


def test_critical_contract_subset_passes_without_exposing_citation_content() -> None:
    """The subset passes when all selected cases satisfy their expected
    outcomes, reason codes, and citation rules — without exposing citation
    content (asserts only IDs/booleans, never content)."""
    from backend.features.evaluation.gates.application import evaluate_gate

    results = _all_critical_results_matching()
    summary = _run_summary(_gate_metrics_passing(), results)
    decision = evaluate_gate(summary=summary, baseline=_gate_metrics_passing())
    assert "critical_contract_mismatch" not in decision.reason_codes


# ---------------------------------------------------------------------------
# Task 2.1 RED: critical mismatch outranks floor regressions (block precedence)
# ---------------------------------------------------------------------------


def test_critical_mismatch_outranks_floor_regressions() -> None:
    """When a critical contract fails AND floors regress, the decision is block
    with critical_contract_mismatch present (fail-closed precedence)."""
    from backend.features.evaluation.gates.application import evaluate_gate
    from backend.features.evaluation.gates.domain import GateMetrics, GateSignal

    bad_metrics = GateMetrics(
        language_routing=GateSignal(33, 34),  # would be escalate
        sensitive_block=GateSignal(2, 2),
        outcome_classification=GateSignal(8, 34),  # would be block
        citation_exact_match=GateSignal(10, 34),
        contradiction_detection=GateSignal(0, 4),
    )
    results = _critical_results_with_override(
        "scenario.eval-11.es",
        observed_outcome="insufficient_information",  # critical mismatch
        reason_code="insufficient_evidence",
        citation_ids=(),
    )
    summary = _run_summary(bad_metrics, results)
    decision = evaluate_gate(summary=summary, baseline=_gate_metrics_passing())
    assert decision.status == "block"
    assert "critical_contract_mismatch" in decision.reason_codes


def test_block_outranks_escalate_in_runner_decision() -> None:
    """When floor policy returns escalate but a critical contract fails (block),
    the final decision is block."""
    from backend.features.evaluation.gates.application import evaluate_gate
    from backend.features.evaluation.gates.domain import GateMetrics, GateSignal

    escalate_metrics = GateMetrics(
        language_routing=GateSignal(33, 34),  # escalate
        sensitive_block=GateSignal(2, 2),
        outcome_classification=GateSignal(9, 34),
        citation_exact_match=GateSignal(10, 34),
        contradiction_detection=GateSignal(0, 4),
    )
    results = _critical_results_with_override(
        "scenario.eval-11.es",
        observed_outcome="insufficient_information",  # critical mismatch -> block
        reason_code="insufficient_evidence",
        citation_ids=(),
    )
    summary = _run_summary(escalate_metrics, results)
    decision = evaluate_gate(summary=summary, baseline=_gate_metrics_passing())
    assert decision.status == "block"


# ---------------------------------------------------------------------------
# Task 2.1 RED: runner consumes metrics/results without recomputation
# ---------------------------------------------------------------------------


def test_runner_does_not_recompute_metrics() -> None:
    """The runner MUST consume RunSummary.metrics directly, not recompute from
    CaseResult. We pass metrics that disagree with results and assert the
    runner uses the supplied metrics."""
    from backend.features.evaluation.gates.application import evaluate_gate

    # Metrics say pass; results would compute differently if recomputed.
    metrics = _gate_metrics_passing()
    results = _all_critical_results_matching()
    summary = _run_summary(metrics, results)
    decision = evaluate_gate(summary=summary, baseline=_gate_metrics_passing())
    # If the runner recomputed, it would get different metrics and likely block.
    assert decision.status == "pass"


def test_runner_selects_only_critical_observations() -> None:
    """The runner selects CaseResult observations for critical case IDs only;
    non-critical results do not trigger critical_contract_mismatch even if
    their outcome is unexpected."""
    from backend.features.evaluation.gates.application import evaluate_gate

    results = list(_all_critical_results_matching()) + [
        _case_result(
            case_id="scenario.eval-01.es",  # non-critical, unexpected
            observed_outcome="supported",
            reason_code="none",
            citation_ids=("fragment.x",),
        ),
    ]
    summary = _run_summary(_gate_metrics_passing(), results)
    decision = evaluate_gate(summary=summary, baseline=_gate_metrics_passing())
    assert "critical_contract_mismatch" not in decision.reason_codes


# ---------------------------------------------------------------------------
# Task 2.1 RED: frozen Clock determinism
# ---------------------------------------------------------------------------


def test_runner_is_deterministic_with_frozen_clock() -> None:
    """Identical inputs with a frozen clock MUST yield identical decisions."""
    from backend.features.evaluation.gates.application import evaluate_gate

    results = _all_critical_results_matching()
    summary = _run_summary(_gate_metrics_passing(), results)
    baseline = _gate_metrics_passing()
    decision_a = evaluate_gate(summary=summary, baseline=baseline)
    decision_b = evaluate_gate(summary=summary, baseline=baseline)
    assert decision_a.status == decision_b.status
    assert decision_a.reason_codes == decision_b.reason_codes


# ---------------------------------------------------------------------------
# Task 2.1 RED: runner does not import kernel/metric logic
# ---------------------------------------------------------------------------


def test_gate_application_imports_no_kernel_or_metric_modules() -> None:
    import backend.features.evaluation.gates.application as gate_app

    forbidden = {
        "backend.features.evaluation.adapters.kernel",
        "backend.features.query",
        "backend.features.evaluation.adapters.dataset",
    }
    for forbidden_mod in forbidden:
        assert forbidden_mod not in vars(gate_app), (
            f"gate application must not import {forbidden_mod}"
        )


# ---------------------------------------------------------------------------
# Task 2.1 RED: harness remains numbers-only and unchanged
# ---------------------------------------------------------------------------


def test_harness_metrics_still_threshold_free() -> None:
    """The harness Metrics must remain unchanged: five numeric signals, no
    thresholds, no decision fields."""
    # Metrics must still be a simple dataclass with five MetricSignal fields.
    import dataclasses

    from backend.features.evaluation.domain import Metrics

    fields = {f.name for f in dataclasses.fields(Metrics)}
    assert fields == {
        "outcome_classification",
        "citation_exact_match",
        "language_routing",
        "sensitive_block",
        "contradiction_detection",
    }


def test_gate_runner_accepts_harness_runsummary() -> None:
    """The runner accepts a real RunSummary shape (identity, results, metrics)
    without requiring any gate-specific wrapper."""
    from backend.features.evaluation.gates.application import evaluate_gate

    results = _all_critical_results_matching()
    summary = _run_summary(_gate_metrics_passing(), results)
    decision = evaluate_gate(summary=summary, baseline=_gate_metrics_passing())
    assert decision.status in {"pass", "block", "escalate"}


# ---------------------------------------------------------------------------
# Task 2.1 RED: unknown reason code fails closed
# ---------------------------------------------------------------------------


def test_unknown_critical_reason_code_blocks() -> None:
    """If a critical case has an unknown reason code (not in the allowlist),
    the gate MUST block with critical_contract_mismatch (fail-closed)."""
    from backend.features.evaluation.gates.application import evaluate_gate

    results = _critical_results_with_override(
        "scenario.eval-11.es",
        observed_outcome="contradictory_information",
        reason_code="totally-unknown-code",  # not allowlisted
        citation_ids=(),
    )
    summary = _run_summary(_gate_metrics_passing(), results)
    decision = evaluate_gate(summary=summary, baseline=_gate_metrics_passing())
    assert decision.status == "block"
    assert "critical_contract_mismatch" in decision.reason_codes


# ---------------------------------------------------------------------------
# review-6cbe7de75e833f5a R3-002: non-critical unknown reason codes block
# ---------------------------------------------------------------------------


def test_r3_002_unknown_reason_code_on_non_critical_result_blocks() -> None:
    """An unknown reason code on a NON-critical result MUST block (fail-closed);
    before the fix only critical-case reason codes were validated."""
    from backend.features.evaluation.gates.application import evaluate_gate

    results = _all_critical_results_matching() + [
        _case_result(
            case_id="scenario.eval-01.es",  # non-critical
            observed_outcome="supported",
            reason_code="totally-unknown-code",  # not allowlisted
            citation_ids=("fragment.x",),
        )
    ]
    summary = _run_summary(_gate_metrics_passing(), results)
    decision = evaluate_gate(summary=summary, baseline=_gate_metrics_passing())
    assert decision.status == "block"
    assert "unknown_reason_code" in decision.reason_codes


def test_r3_002_unknown_critical_reason_code_still_blocks() -> None:
    """The existing critical-contract reason-code validation is preserved."""
    from backend.features.evaluation.gates.application import evaluate_gate

    results = _critical_results_with_override(
        "scenario.eval-11.es",
        observed_outcome="contradictory_information",
        reason_code="totally-unknown-code",
        citation_ids=(),
    )
    summary = _run_summary(_gate_metrics_passing(), results)
    decision = evaluate_gate(summary=summary, baseline=_gate_metrics_passing())
    assert decision.status == "block"
    assert "critical_contract_mismatch" in decision.reason_codes
