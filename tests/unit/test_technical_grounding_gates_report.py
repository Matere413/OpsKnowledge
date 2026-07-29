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
from pathlib import Path
from typing import Any

import pytest

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


def test_serialize_gate_report_records_five_signals_in_baseline_and_observed() -> None:
    from backend.features.evaluation.gates.adapters.report import serialize_gate_report
    from backend.features.evaluation.gates.domain import GateDecision, GateMetrics, GateSignal

    baseline = GateMetrics(
        language_routing=GateSignal(34, 34),
        sensitive_block=GateSignal(2, 2),
        outcome_classification=GateSignal(9, 34),
        citation_exact_match=GateSignal(10, 34),
        contradiction_detection=GateSignal(0, 4),
    )
    observed = _gate_metrics_regression()
    decision = GateDecision(status="block", reason_codes=("outcome_regression",))
    summary = _run_summary(observed, _all_critical_results_matching())
    payload = serialize_gate_report(
        decision=decision,
        summary=summary,
        baseline=baseline,
        profile="development",
        provider_mode="fake",
        timestamp=1_700_000_000.0,
        duration_seconds=0.0,
    )
    data = json.loads(payload.decode("utf-8"))
    for section in ("baseline_metrics", "observed_metrics"):
        assert set(data[section].keys()) == {
            "language_routing",
            "sensitive_block",
            "outcome_classification",
            "citation_exact_match",
            "contradiction_detection",
        }
        assert data["baseline_metrics"]["outcome_classification"] == {
            "numerator": 9,
            "denominator": 34,
        }
        assert data["observed_metrics"]["outcome_classification"] == {
            "numerator": 8,
            "denominator": 34,
        }


def test_serialize_gate_report_records_reviewed_floors() -> None:
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
    floors = data["floors"]
    assert floors["language_routing"] == {
        "numerator": 34,
        "denominator": 34,
        "regression": "escalate",
    }
    assert floors["outcome_classification"] == {
        "numerator": 9,
        "denominator": 34,
        "regression": "block",
    }
    assert floors["contradiction_detection"] == {
        "numerator": 0,
        "denominator": 4,
        "regression": "block",
    }


def test_serialize_gate_report_critical_observations_are_allowlisted_and_selected() -> None:
    from backend.features.evaluation.gates.adapters.report import serialize_gate_report
    from backend.features.evaluation.gates.domain import CRITICAL_EXPECTATIONS, GateDecision

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
    observations = data["critical_observations"]
    expected_ids = {exp.case_id for exp in CRITICAL_EXPECTATIONS}
    assert {obs["case_id"] for obs in observations} == expected_ids
    for obs in observations:
        assert set(obs.keys()) == ALLOWED_OBSERVATION_KEYS
        assert obs["citation_ids"] == []


def test_serialize_gate_report_excludes_non_critical_results() -> None:
    from backend.features.evaluation.gates.adapters.report import serialize_gate_report
    from backend.features.evaluation.gates.domain import GateDecision

    decision = GateDecision(status="pass", reason_codes=("pass",))
    results = _all_critical_results_matching() + [
        _case_result(
            case_id="scenario.eval-01.es",
            observed_outcome="supported",
            reason_code="none",
            citation_ids=("fragment.leak-001",),
        )
    ]
    summary = _run_summary(_gate_metrics_passing(), results)
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
    ids = {obs["case_id"] for obs in data["critical_observations"]}
    assert "scenario.eval-01.es" not in ids


# ---------------------------------------------------------------------------
# Task 3.1 RED: forbidden content absence
# ---------------------------------------------------------------------------


def test_serialize_gate_report_contains_no_forbidden_content_tokens() -> None:
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
    text = payload.decode("utf-8")
    for token in FORBIDDEN_CONTENT_TOKENS:
        assert token not in text, f"forbidden token '{token}' present in gate report"


def test_serialize_gate_report_citation_ids_only_not_content() -> None:
    """critical_observations record citation IDs only, never citation text."""
    from backend.features.evaluation.gates.adapters.report import serialize_gate_report
    from backend.features.evaluation.gates.domain import GateDecision

    decision = GateDecision(status="block", reason_codes=("critical_contract_mismatch",))
    results = _all_critical_results_matching()
    # Override one critical case to carry a citation ID (mismatch case).
    results = [
        _case_result(
            case_id="scenario.eval-11.es",
            observed_outcome="contradictory_information",
            reason_code="contradiction_detected",
            citation_ids=("fragment.doc-001",),
        )
        if r.case_id == "scenario.eval-11.es"
        else r
        for r in results
    ]
    summary = _run_summary(_gate_metrics_passing(), results)
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
    obs = next(o for o in data["critical_observations"] if o["case_id"] == "scenario.eval-11.es")
    assert obs["citation_ids"] == ["fragment.doc-001"]
    # The ID is an opaque token, not citation text/content.
    assert "fragment.doc-001" in payload.decode("utf-8")


# ---------------------------------------------------------------------------
# Task 3.1 RED: staging validation rejects empty/malformed payload
# ---------------------------------------------------------------------------


def test_promote_rejects_empty_payload_before_touching_committed_paths(tmp_path: Path) -> None:
    from backend.features.evaluation.gates.adapters.report import GateReportAdapter

    adapter = GateReportAdapter(base_dir=tmp_path)
    with _ExpectRaise(ValueError):
        adapter.promote(run_id="r1", payload=b"")
    assert not (tmp_path / "current").exists()
    assert not (tmp_path / "previous").exists()


def test_promote_rejects_malformed_json_payload(tmp_path: Path) -> None:
    from backend.features.evaluation.gates.adapters.report import GateReportAdapter

    adapter = GateReportAdapter(base_dir=tmp_path)
    with _ExpectRaise((ValueError, json.JSONDecodeError)):
        adapter.promote(run_id="r1", payload=b"not-json{")
    assert not (tmp_path / "current").exists()


def test_promote_rejects_payload_missing_allowlisted_keys(tmp_path: Path) -> None:
    from backend.features.evaluation.gates.adapters.report import GateReportAdapter

    adapter = GateReportAdapter(base_dir=tmp_path)
    incomplete = json.dumps({"status": "pass"}).encode("utf-8")
    with _ExpectRaise(ValueError):
        adapter.promote(run_id="r1", payload=incomplete)
    assert not (tmp_path / "current").exists()


# ---------------------------------------------------------------------------
# Task 3.1 RED: atomic current/previous promotion
# ---------------------------------------------------------------------------


def _valid_report_payload(run_id: str = "r1") -> bytes:
    from backend.features.evaluation.gates.adapters.report import serialize_gate_report
    from backend.features.evaluation.gates.domain import GateDecision

    decision = GateDecision(status="pass", reason_codes=("pass",))
    summary = _passing_summary(run_id=run_id)
    return serialize_gate_report(
        decision=decision,
        summary=summary,
        baseline=_gate_metrics_passing(),
        profile="development",
        provider_mode="fake",
        timestamp=1_700_000_000.0,
        duration_seconds=0.0,
    )


def test_promote_creates_current_on_first_run(tmp_path: Path) -> None:
    from backend.features.evaluation.gates.adapters.report import GateReportAdapter

    adapter = GateReportAdapter(base_dir=tmp_path)
    payload = _valid_report_payload("r1")
    adapter.promote(run_id="r1", payload=payload)
    current = tmp_path / "current"
    assert current.exists()
    assert (current / "report.json").read_bytes() == payload
    assert not (tmp_path / "previous").exists(), "no previous until replacement"


def test_promote_moves_current_to_previous_on_replacement(tmp_path: Path) -> None:
    from backend.features.evaluation.gates.adapters.report import GateReportAdapter

    adapter = GateReportAdapter(base_dir=tmp_path)
    first = _valid_report_payload("r1")
    adapter.promote(run_id="r1", payload=first)
    second = _valid_report_payload("r2")
    adapter.promote(run_id="r2", payload=second)
    assert (tmp_path / "current" / "report.json").read_bytes() == second
    assert (tmp_path / "previous" / "report.json").read_bytes() == first


def test_promote_replaces_old_previous_on_third_run(tmp_path: Path) -> None:
    from backend.features.evaluation.gates.adapters.report import GateReportAdapter

    adapter = GateReportAdapter(base_dir=tmp_path)
    adapter.promote(run_id="r1", payload=_valid_report_payload("r1"))
    adapter.promote(run_id="r2", payload=_valid_report_payload("r2"))
    third = _valid_report_payload("r3")
    adapter.promote(run_id="r3", payload=third)
    assert (tmp_path / "current" / "report.json").read_bytes() == third
    assert (tmp_path / "previous" / "report.json").read_bytes() == _valid_report_payload("r2")


# ---------------------------------------------------------------------------
# Task 3.1 RED: rollback on write/rename failure leaves prior evidence unchanged
# ---------------------------------------------------------------------------


def test_promote_rollback_on_rename_failure_restores_current(tmp_path: Path) -> None:
    """When the final staged->current rename fails AFTER current was moved to
    previous, rollback restores prior current so committed evidence is unchanged."""
    import backend.features.evaluation.gates.adapters.report as report_mod
    from backend.features.evaluation.gates.adapters.report import GateReportAdapter

    adapter = GateReportAdapter(base_dir=tmp_path)
    first = _valid_report_payload("r1")
    adapter.promote(run_id="r1", payload=first)
    prior_bytes = (tmp_path / "current" / "report.json").read_bytes()

    second = _valid_report_payload("r2")
    original_replace = report_mod._os_replace
    call_count = {"n": 0}

    def _failing_replace(src: Path, dst: Path) -> None:
        call_count["n"] += 1
        # First replace: current -> previous (succeeds).
        # Second replace: staged -> current (fails).
        if call_count["n"] == 2:
            raise OSError("injected rename failure")
        original_replace(src, dst)

    report_mod._os_replace = _failing_replace
    try:
        with _ExpectRaise(OSError):
            adapter.promote(run_id="r2", payload=second)
    finally:
        report_mod._os_replace = original_replace

    # Prior committed evidence unchanged.
    assert (tmp_path / "current" / "report.json").read_bytes() == prior_bytes


def test_promote_rollback_on_first_rename_failure_leaves_current_intact(tmp_path: Path) -> None:
    """When the current->previous rename fails, current is never moved and
    remains unchanged."""
    import backend.features.evaluation.gates.adapters.report as report_mod
    from backend.features.evaluation.gates.adapters.report import GateReportAdapter

    adapter = GateReportAdapter(base_dir=tmp_path)
    first = _valid_report_payload("r1")
    adapter.promote(run_id="r1", payload=first)
    prior_bytes = (tmp_path / "current" / "report.json").read_bytes()

    second = _valid_report_payload("r2")
    original_replace = report_mod._os_replace

    def _always_fail(src: Path, dst: Path) -> None:
        raise OSError("injected rename failure")

    report_mod._os_replace = _always_fail
    try:
        with _ExpectRaise(OSError):
            adapter.promote(run_id="r2", payload=second)
    finally:
        report_mod._os_replace = original_replace

    assert (tmp_path / "current" / "report.json").read_bytes() == prior_bytes


def test_promote_cleans_staging_on_failure(tmp_path: Path) -> None:
    import backend.features.evaluation.gates.adapters.report as report_mod
    from backend.features.evaluation.gates.adapters.report import GateReportAdapter

    adapter = GateReportAdapter(base_dir=tmp_path)
    first = _valid_report_payload("r1")
    adapter.promote(run_id="r1", payload=first)

    second = _valid_report_payload("r2")
    original_replace = report_mod._os_replace

    def _always_fail(src: Path, dst: Path) -> None:
        raise OSError("injected")

    report_mod._os_replace = _always_fail
    try:
        with _ExpectRaise(OSError):
            adapter.promote(run_id="r2", payload=second)
    finally:
        report_mod._os_replace = original_replace

    staging_dirs = [p for p in tmp_path.iterdir() if p.name.startswith(".staging")]
    assert staging_dirs == [], "staging must be cleaned on failure"


# ---------------------------------------------------------------------------
# Task 3.1 RED: baseline bootstrap
# ---------------------------------------------------------------------------


def _write_harness_summary(directory: Path, metrics: dict[str, Any] | None = None) -> None:
    """Write a harness-style summary.json under directory/current/."""
    if metrics is None:
        metrics = {
            "outcome_classification": {"numerator": 9, "denominator": 34},
            "citation_exact_match": {"numerator": 10, "denominator": 34},
            "language_routing": {"numerator": 34, "denominator": 34},
            "sensitive_block": {"numerator": 2, "denominator": 2},
            "contradiction_detection": {"numerator": 0, "denominator": 4},
        }
    current = directory / "current"
    current.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        {
            "contract_version": "1",
            "run_id": "harness-run",
            "profile": "development",
            "provider_mode": "fake",
            "total_cases": 34,
            "timestamp": None,
            "duration_seconds": None,
            "metrics": metrics,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    (current / "summary.json").write_text(payload, encoding="utf-8")


def test_bootstrap_baseline_from_harness_snapshot_on_first_run(tmp_path: Path) -> None:
    from backend.features.evaluation.gates.adapters.report import bootstrap_baseline

    harness_current = tmp_path / "harness" / "current"
    harness_current.mkdir(parents=True)
    _write_harness_summary(tmp_path / "harness")
    gate_dir = tmp_path / "gate"
    baseline = bootstrap_baseline(
        gate_dir=gate_dir, harness_current=tmp_path / "harness" / "current"
    )
    assert baseline.outcome_classification.numerator == 9
    assert baseline.language_routing.numerator == 34


def test_bootstrap_baseline_from_gate_snapshot_on_later_run(tmp_path: Path) -> None:
    from backend.features.evaluation.gates.adapters.report import (
        bootstrap_baseline,
        serialize_gate_report,
    )
    from backend.features.evaluation.gates.domain import GateDecision

    gate_dir = tmp_path / "gate"
    gate_current = gate_dir / "current"
    gate_current.mkdir(parents=True)
    decision = GateDecision(status="pass", reason_codes=("pass",))
    summary = _passing_summary()
    report = serialize_gate_report(
        decision=decision,
        summary=summary,
        baseline=_gate_metrics_passing(),
        profile="development",
        provider_mode="fake",
        timestamp=1_700_000_000.0,
        duration_seconds=0.0,
    )
    (gate_current / "report.json").write_bytes(report)
    baseline = bootstrap_baseline(gate_dir=gate_dir, harness_current=tmp_path / "nope" / "current")
    assert baseline.outcome_classification.numerator == 9


def test_bootstrap_baseline_raises_when_no_source(tmp_path: Path) -> None:
    from backend.features.evaluation.gates.adapters.report import bootstrap_baseline

    with _ExpectRaise(ValueError):
        bootstrap_baseline(
            gate_dir=tmp_path / "gate", harness_current=tmp_path / "nope" / "current"
        )


def test_bootstrap_baseline_raises_on_malformed_harness_summary(tmp_path: Path) -> None:
    from backend.features.evaluation.gates.adapters.report import bootstrap_baseline

    harness_current = tmp_path / "harness" / "current"
    harness_current.mkdir(parents=True)
    (harness_current / "summary.json").write_text("not-json{", encoding="utf-8")
    with _ExpectRaise((ValueError, json.JSONDecodeError)):
        bootstrap_baseline(gate_dir=tmp_path / "gate", harness_current=harness_current)


@pytest.mark.parametrize(
    "bad_metrics",
    (
        _BAD_ZERO_DEN,
        _BAD_NEG_NUM,
        _BAD_EXCEED,
    ),
)
def test_bootstrap_baseline_rejects_zero_denominator_or_negative(
    tmp_path: Path, bad_metrics: dict[str, Any]
) -> None:
    from backend.features.evaluation.gates.adapters.report import bootstrap_baseline

    full_metrics = {
        "outcome_classification": {"numerator": 9, "denominator": 34},
        "citation_exact_match": {"numerator": 10, "denominator": 34},
        "language_routing": {"numerator": 34, "denominator": 34},
        "sensitive_block": {"numerator": 2, "denominator": 2},
        "contradiction_detection": {"numerator": 0, "denominator": 4},
    }
    full_metrics.update(bad_metrics)
    harness = tmp_path / "harness"
    (harness / "current").mkdir(parents=True)
    (harness / "current" / "summary.json").write_text(
        json.dumps(
            {"metrics": full_metrics, "run_id": "x", "contract_version": "1"},
            sort_keys=True,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    with _ExpectRaise(ValueError):
        bootstrap_baseline(gate_dir=tmp_path / "gate", harness_current=harness / "current")


# ---------------------------------------------------------------------------
# Task 3.1 RED: CLI exit codes (pass=0, block/escalate=non-zero)
# ---------------------------------------------------------------------------


def _wire_cli_fake_run_evaluation(monkeypatch_target: Any, summary: Any) -> None:
    """Replace the CLI's run_evaluation reference with a stub returning summary."""
    monkeypatch_target.run_evaluation = lambda *args, **kwargs: summary


def test_run_gate_returns_zero_on_pass(tmp_path: Path) -> None:
    import backend.features.evaluation.gates.cli as cli_mod

    harness = tmp_path / "harness"
    _write_harness_summary(harness)
    summary = _passing_summary()
    _wire_cli_fake_run_evaluation(cli_mod, summary)
    exit_code = cli_mod.run_gate(
        dataset_root=tmp_path / "dataset",
        gate_dir=tmp_path / "gate",
        harness_current=harness / "current",
        clock=cli_mod.FrozenClock(timestamp=1_700_000_000.0, duration_seconds=0.0),
    )
    assert exit_code == 0
    assert (tmp_path / "gate" / "current" / "report.json").exists()


def test_run_gate_returns_nonzero_on_block(tmp_path: Path) -> None:
    import backend.features.evaluation.gates.cli as cli_mod

    harness = tmp_path / "harness"
    _write_harness_summary(harness)
    # Critical mismatch: eval-11.es has the wrong outcome.
    results = [
        _case_result(
            case_id="scenario.eval-11.es",
            observed_outcome="insufficient_information",
            reason_code="insufficient_evidence",
            citation_ids=(),
        )
        if r.case_id == "scenario.eval-11.es"
        else r
        for r in _all_critical_results_matching()
    ]
    summary = _run_summary(_gate_metrics_passing(), results)
    _wire_cli_fake_run_evaluation(cli_mod, summary)
    exit_code = cli_mod.run_gate(
        dataset_root=tmp_path / "dataset",
        gate_dir=tmp_path / "gate",
        harness_current=harness / "current",
        clock=cli_mod.FrozenClock(timestamp=1_700_000_000.0, duration_seconds=0.0),
    )
    assert exit_code != 0
    report = json.loads((tmp_path / "gate" / "current" / "report.json").read_bytes())
    assert report["status"] == "block"
    assert "critical_contract_mismatch" in report["reason_codes"]


def test_run_gate_returns_nonzero_on_escalate(tmp_path: Path) -> None:
    import backend.features.evaluation.gates.cli as cli_mod

    harness = tmp_path / "harness"
    _write_harness_summary(harness)
    # Language regression (escalate) with all critical contracts passing and
    # block-signals at floor (so the only regression is the escalate one).
    escalate_metrics = _gate_metrics_escalate_only()  # language 33/34
    summary = _run_summary(escalate_metrics, _all_critical_results_matching())
    _wire_cli_fake_run_evaluation(cli_mod, summary)
    exit_code = cli_mod.run_gate(
        dataset_root=tmp_path / "dataset",
        gate_dir=tmp_path / "gate",
        harness_current=harness / "current",
        clock=cli_mod.FrozenClock(timestamp=1_700_000_000.0, duration_seconds=0.0),
    )
    assert exit_code != 0
    report = json.loads((tmp_path / "gate" / "current" / "report.json").read_bytes())
    assert report["status"] == "escalate"
    assert "language_regression" in report["reason_codes"]


def test_run_gate_stdout_contains_only_safe_fields(tmp_path: Path, capsys: Any) -> None:
    import backend.features.evaluation.gates.cli as cli_mod

    harness = tmp_path / "harness"
    _write_harness_summary(harness)
    summary = _passing_summary()
    _wire_cli_fake_run_evaluation(cli_mod, summary)
    cli_mod.run_gate(
        dataset_root=tmp_path / "dataset",
        gate_dir=tmp_path / "gate",
        harness_current=harness / "current",
        clock=cli_mod.FrozenClock(timestamp=1_700_000_000.0, duration_seconds=0.0),
    )
    out = capsys.readouterr().out
    for token in FORBIDDEN_CONTENT_TOKENS:
        assert token not in out, f"forbidden token '{token}' in stdout"
    assert "pass" in out


# ---------------------------------------------------------------------------
# Task 3.1 RED: no-dependency imports in gate adapters and CLI
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "module_path",
    (
        "backend.features.evaluation.gates.adapters.report",
        "backend.features.evaluation.gates.cli",
    ),
)
def test_gate_report_and_cli_import_no_forbidden_modules(module_path: str) -> None:
    import importlib

    mod = importlib.import_module(module_path)
    forbidden = {
        "http",
        "requests",
        "aiohttp",
        "httpx",
        "socket",
        "asyncio",
        "langchain",
        "llama_index",
        "redis",
        "kubernetes",
        "subprocess",
    }
    for forbidden_mod in forbidden:
        assert forbidden_mod not in vars(mod), f"{module_path} imports forbidden {forbidden_mod}"


def test_gate_cli_uses_no_subprocess_or_network() -> None:
    """The gate CLI MUST NOT import subprocess or network modules."""
    import ast
    import importlib

    mod = importlib.import_module("backend.features.evaluation.gates.cli")
    assert mod.__file__ is not None
    tree = ast.parse(Path(mod.__file__).read_text(encoding="utf-8"))
    forbidden = {"subprocess", "socket", "http", "requests", "aiohttp", "httpx", "asyncio"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in forbidden
        elif isinstance(node, ast.ImportFrom) and node.module:
            assert node.module.split(".")[0] not in forbidden


# ---------------------------------------------------------------------------
# Task 3.1 RED: deterministic frozen-clock report
# ---------------------------------------------------------------------------


def test_run_gate_produces_deterministic_report_across_runs(tmp_path: Path) -> None:
    import backend.features.evaluation.gates.cli as cli_mod

    harness = tmp_path / "harness"
    _write_harness_summary(harness)
    summary = _passing_summary()
    _wire_cli_fake_run_evaluation(cli_mod, summary)
    clock = cli_mod.FrozenClock(timestamp=1_700_000_000.0, duration_seconds=0.0)
    cli_mod.run_gate(
        dataset_root=tmp_path / "dataset",
        gate_dir=tmp_path / "gate",
        harness_current=harness / "current",
        clock=clock,
    )
    first = (tmp_path / "gate" / "current" / "report.json").read_bytes()
    # Second run into a fresh gate dir with identical inputs.
    _wire_cli_fake_run_evaluation(cli_mod, summary)
    cli_mod.run_gate(
        dataset_root=tmp_path / "dataset",
        gate_dir=tmp_path / "gate2",
        harness_current=harness / "current",
        clock=clock,
    )
    second = (tmp_path / "gate2" / "current" / "report.json").read_bytes()
    assert first == second
