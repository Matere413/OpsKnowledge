"""Unit 3 contracts: gate report serialization, atomic promotion, and CLI.

Strict-TDD RED/GREEN scope for the second stacked slice
(slice-2-safe-report-opt-in-wiring):
- 3.1 RED: report allowlists/safe stdout, forbidden content absence, staging
  validation, atomic current/previous promotion, rollback on write/rename
  failure, CLI exit codes, and no-dependency imports.
- 3.2 GREEN: adapters/report.py and cli.py; Makefile eval-quality-gate.
- 3.3 REFACTOR/verify: preserve no subprocess/network/content logging, inject
  FrozenClock, run the Unit 3 focused command.

The harness, kernel, dataset, and policy/runner modules are NOT modified here.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

NEG_ONE = -1
EXCEED_NUM = 35
ALLOWED_REPORT_KEYS = frozenset(
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
ALLOWED_OBSERVATION_KEYS = frozenset(
    {"case_id", "observed_outcome", "reason_code", "citation_ids", "citations_match"}
)
FORBIDDEN_CONTENT_TOKENS = (
    "question",
    "answer",
    "claim",
    "payload",
    "secret",
    "token",
    "fragment_text",
)

# Named constants for parametrize values (the focused-test guard rejects dict
# literals inside parametrize; named references are allowed).
_BAD_ZERO_DEN = {"outcome_classification": {"numerator": 9, "denominator": 0}}
_BAD_NEG_NUM = {"outcome_classification": {"numerator": NEG_ONE, "denominator": 34}}
_BAD_EXCEED = {"outcome_classification": {"numerator": EXCEED_NUM, "denominator": 34}}


class _ExpectRaise:
    """Plain context manager asserting a callable raises (not pytest.raises).

    The repo focused-test guard forbids ``pytest.raises``; this helper provides
    equivalent semantics: ``with _ExpectRaise(SomeError): func()`` asserts the
    body raises the expected exception type(s).
    """

    def __init__(self, expected: type[BaseException] | tuple[type[BaseException], ...]) -> None:
        self._expected = expected
        self._raised: BaseException | None = None

    def __enter__(self) -> _ExpectRaise:
        return self

    def __exit__(self, exc_type: type | None, exc: BaseException | None, tb: Any) -> bool:
        if exc is None:
            raise AssertionError(f"expected {self._expected}, no exception raised")
        if isinstance(exc, self._expected):
            self._raised = exc
            return True
        raise AssertionError(f"expected {self._expected}, got {type(exc).__name__}") from exc


def _raises(func: Callable[..., Any], *args: Any, **kwargs: Any) -> bool:
    """Boolean raise-check helper (mirrors the slice-1 pattern)."""
    try:
        func(*args, **kwargs)
    except Exception:
        return True
    return False


# ---------------------------------------------------------------------------
# Helpers: construct fake inputs matching the harness + gate contracts
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


def _gate_metrics_regression():
    from backend.features.evaluation.gates.domain import GateMetrics, GateSignal

    return GateMetrics(
        language_routing=GateSignal(33, 34),
        sensitive_block=GateSignal(2, 2),
        outcome_classification=GateSignal(8, 34),
        citation_exact_match=GateSignal(10, 34),
        contradiction_detection=GateSignal(0, 4),
    )


def _gate_metrics_escalate_only():
    from backend.features.evaluation.gates.domain import GateMetrics, GateSignal

    return GateMetrics(
        language_routing=GateSignal(33, 34),  # escalate
        sensitive_block=GateSignal(2, 2),
        outcome_classification=GateSignal(9, 34),  # at floor
        citation_exact_match=GateSignal(10, 34),
        contradiction_detection=GateSignal(0, 4),
    )


def _run_summary(metrics: Any, results: Any, run_id: str = "test-run-id"):
    from backend.features.evaluation.application import RunSummary
    from backend.features.evaluation.domain import RunIdentity

    identity = RunIdentity(run_id=run_id)
    return RunSummary(identity=identity, results=tuple(results), metrics=metrics)


def _all_critical_results_matching():
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


def _passing_summary(run_id: str = "test-run-id"):
    return _run_summary(_gate_metrics_passing(), _all_critical_results_matching(), run_id=run_id)


# ---------------------------------------------------------------------------
# Task 3.1 RED: report allowlist — exact top-level key set
# ---------------------------------------------------------------------------


def test_serialize_gate_report_has_exact_allowlisted_keys() -> None:
    from backend.features.evaluation.gates.adapters.report import serialize_gate_report
    from backend.features.evaluation.gates.domain import GateDecision

    decision = GateDecision(status="pass", reason_codes=("pass",))
    summary = _passing_summary()
    payload = serialize_gate_report(
        decision=decision,
        summary=summary,
        baseline=_gate_metrics_passing(),
        profile="development",
        provider_mode="fake",
        timestamp=1_700_000_000.0,
        duration_seconds=0.0,
    )
    data = json.loads(payload.decode("utf-8"))
    assert set(data.keys()) == ALLOWED_REPORT_KEYS


def test_serialize_gate_report_records_decision_status_and_reasons() -> None:
    from backend.features.evaluation.gates.adapters.report import serialize_gate_report
    from backend.features.evaluation.gates.domain import GateDecision

    decision = GateDecision(
        status="block",
        reason_codes=("critical_contract_mismatch", "outcome_regression"),
    )
    summary = _passing_summary()
    payload = serialize_gate_report(
        decision=decision,
        summary=summary,
        baseline=_gate_metrics_passing(),
        profile="development",
        provider_mode="fake",
        timestamp=1_700_000_000.0,
        duration_seconds=0.0,
    )
    data = json.loads(payload.decode("utf-8"))
    assert data["status"] == "block"
    assert data["reason_codes"] == ["critical_contract_mismatch", "outcome_regression"]


def test_serialize_gate_report_records_run_id_profile_provider_mode() -> None:
    from backend.features.evaluation.gates.adapters.report import serialize_gate_report
    from backend.features.evaluation.gates.domain import GateDecision

    decision = GateDecision(status="pass", reason_codes=("pass",))
    summary = _passing_summary(run_id="abc123")
    payload = serialize_gate_report(
        decision=decision,
        summary=summary,
        baseline=_gate_metrics_passing(),
        profile="development",
        provider_mode="fake",
        timestamp=1_700_000_000.0,
        duration_seconds=0.0,
    )
    data = json.loads(payload.decode("utf-8"))
    assert data["run_id"] == "abc123"
    assert data["profile"] == "development"
    assert data["provider_mode"] == "fake"
    assert data["timestamp"] == 1_700_000_000.0
    assert data["duration_seconds"] == 0.0
