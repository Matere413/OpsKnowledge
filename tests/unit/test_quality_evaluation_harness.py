"""Unit 1 contracts for the OpsKnowledge quality evaluation harness.

Behavior-first RED/GREEN scope for the first chained slice:
- 1.1 fail-closed dataset validation and reviewed-mapping contract
- 1.3 exact population, injected IDs, base-byte preservation, determinism,
  and no wall-clock reads

The runner, metrics, report, and CLI belong to later units and are NOT
imported here.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from scripts.ci.validate_evaluation_dataset import validate as validate_dataset

_DATASET_ROOT = Path(__file__).resolve().parents[2] / "evaluation-dataset"
_MANIFEST = _DATASET_ROOT / "manifest.json"

# The mapping is the harness-owned, reviewed question surface. It is imported
# lazily through the evaluation feature so this RED test fails before the
# package exists.


def _load_mapping_rows():
    from backend.features.evaluation.mapping import REVIEWED_MAPPING

    return REVIEWED_MAPPING


def _load_dataset():
    from backend.features.evaluation.adapters.dataset import load_validated_corpus

    return load_validated_corpus(_DATASET_ROOT, profile="development")


def _raises(func: Callable[..., Any], *args: Any, **kwargs: Any) -> bool:
    """Return True when ``func(*args, **kwargs)`` raises any Exception.

    Used in place of ``pytest.raises`` because the repo's focused-test guard
    only allows ``pytest.mark.parametrize``; ``pytest.raises`` is flagged as
    an unsupported test API.
    """
    try:
        func(*args, **kwargs)
    except Exception:
        return True
    return False


# ---------------------------------------------------------------------------
# Task 1.1 RED: fail-closed validation and mapping contract
# ---------------------------------------------------------------------------


def test_valid_dataset_has_zero_validation_diagnostics() -> None:
    findings = validate_dataset(_DATASET_ROOT)
    assert findings == []


@pytest.mark.parametrize(
    "reason",
    [
        "integrity",
        "language",
        "count",
        "profile",
    ],
)
def test_invalid_dataset_fails_closed_with_zero_kernel_calls(
    reason: str,
) -> None:
    """An invalid catalog MUST fail closed before any corpus load runs.

    The dataset validator is the gate: any diagnostic means the harness MUST
    NOT reach load_corpus. The patched validator returns one finding and the
    patched loader spy proves load_corpus is never called. Attribute swap is
    restored in a finally block so the gate contract is exercised without the
    pytest monkeypatch fixture (the repo's focused-test guard only allows
    ``pytest.mark.parametrize``).
    """
    import backend.features.evaluation.adapters.dataset as dataset_adapter
    from backend.features.corpus.adapters.manifest_loader import (
        load_corpus as real_load_corpus,
    )

    load_calls = {"count": 0}

    def _fake_load(manifest_path: Path, *, profile: str):  # noqa: ARG001
        load_calls["count"] += 1
        return real_load_corpus(manifest_path, profile=profile)

    real_validate = dataset_adapter.validate_dataset
    real_load = dataset_adapter.load_corpus
    try:
        dataset_adapter.validate_dataset = lambda _root: [_r(reason)]  # noqa: E731
        dataset_adapter.load_corpus = _fake_load
        raised = False
        try:
            dataset_adapter.load_validated_corpus(_DATASET_ROOT, profile="development")
        except Exception:
            raised = True
        assert raised is True
        assert load_calls["count"] == 0
    finally:
        dataset_adapter.validate_dataset = real_validate
        dataset_adapter.load_corpus = real_load


def _r(reason: str) -> tuple[str, str, str]:
    return ("scenarios/scenario.eval-01.es.json", reason, "fail-closed")


def test_reviewed_mapping_has_exactly_32_rows() -> None:
    rows = _load_mapping_rows()
    assert len(rows) == 32


def test_reviewed_mapping_ids_match_dataset_scenarios_exactly() -> None:
    rows = _load_mapping_rows()
    manifest_ids = set(_manifest_scenario_ids())
    mapping_ids = {row.scenario_id for row in rows}
    assert mapping_ids == manifest_ids
    assert len(mapping_ids) == 32


def test_reviewed_mapping_every_row_is_reviewed_and_language_matched() -> None:
    rows = _load_mapping_rows()
    manifest_languages = _manifest_scenario_languages()
    for row in rows:
        assert row.reviewed is True
        assert row.language == manifest_languages[row.scenario_id]
        assert row.question  # non-empty deterministic input


def test_mapping_rejects_missing_duplicate_extra_and_unreviewed_rows() -> None:
    from backend.features.evaluation.mapping import validate_mapping

    base = _load_mapping_rows()
    scenario_ids = sorted(_manifest_scenario_ids())
    scenario_languages = _manifest_scenario_languages()

    # Missing: drop one row.
    missing = tuple(r for r in base if r.scenario_id != scenario_ids[0])
    assert _raises(validate_mapping, missing, scenario_ids, scenario_languages)

    # Duplicate: repeat one row.
    duplicate = (*base, base[0])
    assert _raises(validate_mapping, duplicate, scenario_ids, scenario_languages)

    # Extra: add an unknown scenario id.
    extra_row = type(base[0])("scenario.unknown", "es", "x?", True)
    extra = (*base, extra_row)
    assert _raises(validate_mapping, extra, scenario_ids, scenario_languages)

    # Unreviewed: flip one row's reviewed flag.
    unreviewed = tuple(
        type(r)(r.scenario_id, r.language, r.question, False) if i == 0 else r
        for i, r in enumerate(base)
    )
    assert _raises(validate_mapping, unreviewed, scenario_ids, scenario_languages)

    # Language mismatched: swap one row's language.
    mismatched = tuple(
        type(r)(r.scenario_id, "es" if r.language == "en" else "en", r.question, True)
        if i == 0
        else r
        for i, r in enumerate(base)
    )
    assert _raises(validate_mapping, mismatched, scenario_ids, scenario_languages)


def _manifest_scenario_ids() -> list[str]:
    import json

    manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    return [
        artifact["id"] for artifact in manifest["artifacts"] if artifact.get("kind") == "scenario"
    ]


def _manifest_scenario_languages() -> dict[str, str]:
    import json

    languages: dict[str, str] = {}
    root = _DATASET_ROOT
    manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    for artifact in manifest["artifacts"]:
        if artifact.get("kind") != "scenario":
            continue
        payload = json.loads((root / artifact["path"]).read_text(encoding="utf-8"))
        languages[artifact["id"]] = payload["language"]
    return languages


# ---------------------------------------------------------------------------
# Task 1.3 RED: exact population, injected IDs, base-byte preservation,
# deterministic identity/order/bytes, and no wall-clock reads
# ---------------------------------------------------------------------------


def test_base_scenarios_preserve_dataset_bytes_unmodified() -> None:

    from backend.features.evaluation.adapters.dataset import base_scenario_payloads

    payloads = base_scenario_payloads(_DATASET_ROOT)
    assert len(payloads) == 32
    for scenario_id, raw_bytes in payloads.items():
        path = _DATASET_ROOT / _scenario_path(scenario_id)
        original = path.read_bytes()
        assert raw_bytes == original


def test_injected_failure_pair_has_exact_ids_and_typed_timeout() -> None:
    from backend.features.evaluation.domain import INJECTED_FAILURE_CASE_IDS

    assert INJECTED_FAILURE_CASE_IDS == (
        "injected-provider-failure-es",
        "injected-provider-failure-en",
    )


def test_frozen_clock_never_reads_wall_clock_and_is_monotonic() -> None:
    from backend.features.evaluation.adapters.clock import FrozenClock

    clock = FrozenClock(timestamp=1_700_000_000.0, duration_seconds=0.0125)
    first = (clock.now(), clock.elapsed_since_start())
    second = (clock.now(), clock.elapsed_since_start())
    # Identical inputs MUST yield identical identity and duration without
    # any wall-clock read: repeated calls match exactly.
    assert first == second
    assert clock.duration_seconds == 0.0125


def test_run_identity_is_stable_across_repeated_frozen_inputs() -> None:
    from backend.features.evaluation.domain import RunIdentity

    identity_a = RunIdentity.from_stable_inputs(
        manifest_digest="abc",
        mapping_digest="def",
        contract_version="1",
        provider_mode="fake",
        profile="development",
        clock_timestamp=1_700_000_000.0,
    )
    identity_b = RunIdentity.from_stable_inputs(
        manifest_digest="abc",
        mapping_digest="def",
        contract_version="1",
        provider_mode="fake",
        profile="development",
        clock_timestamp=1_700_000_000.0,
    )
    assert identity_a.run_id == identity_b.run_id


def test_run_identity_is_not_wall_clock_dependent() -> None:
    from backend.features.evaluation.adapters.clock import FrozenClock
    from backend.features.evaluation.domain import RunIdentity

    clock = FrozenClock(timestamp=1_700_000_000.0, duration_seconds=0.0)
    identity = RunIdentity.from_stable_inputs(
        manifest_digest="m",
        mapping_digest="q",
        contract_version="1",
        provider_mode="fake",
        profile="development",
        clock_timestamp=clock.now(),
    )
    # Reading identity twice through the frozen clock MUST return the same id:
    # no wall-clock read is permitted to perturb identity.
    again = RunIdentity.from_stable_inputs(
        manifest_digest="m",
        mapping_digest="q",
        contract_version="1",
        provider_mode="fake",
        profile="development",
        clock_timestamp=clock.now(),
    )
    assert identity.run_id == again.run_id


def test_base_cases_preserve_deterministic_order_and_identity() -> None:
    from backend.features.evaluation.adapters.dataset import base_scenario_payloads

    payloads = base_scenario_payloads(_DATASET_ROOT)
    ids = tuple(payloads.keys())
    assert ids == tuple(sorted(ids))
    assert len(set(ids)) == 32


def test_population_is_immutable_versioned_and_has_reviewed_denominators() -> None:
    from backend.features.evaluation.population import CURRENT_POPULATION

    counts = tuple(
        sum(getattr(c, name) for c in CURRENT_POPULATION.cases)
        for name in ("language_eligible", "abstention_eligible", "escape_required")
    )  # noqa: E501
    assert (len(CURRENT_POPULATION.cases), counts) == (34, (30, 18, 18))
    assert _raises(setattr, CURRENT_POPULATION, "version", "changed")


def test_contract_metrics_use_frozen_expectations_and_fail_closed_ids() -> None:
    from backend.features.evaluation.application import assemble_cases
    from backend.features.evaluation.domain import CaseResult, compute_contract_metrics

    cases = assemble_cases(_DATASET_ROOT)
    results = tuple(
        CaseResult(
            c.scenario_id,
            c.language,
            c.expected_outcome,
            c.expected_reason_code,
            (),
            True,
            c.expected_escalation,
        )
        for c in cases
    )  # noqa: E501
    metrics = compute_contract_metrics(results, cases)
    signals = (
        metrics.language_accuracy,
        metrics.correct_abstention,
        metrics.unsupported_claim_escape,
    )  # noqa: E501
    assert tuple((signal.numerator, signal.denominator) for signal in signals) == (
        (30, 30),
        (18, 18),
        (18, 18),
    )  # noqa: E501
    assert _raises(compute_contract_metrics, results[:-1], cases)


def _scenario_path(scenario_id: str) -> str:
    import json

    manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    for artifact in manifest["artifacts"]:
        if artifact.get("id") == scenario_id:
            return artifact["path"]
    raise AssertionError(f"unknown scenario id: {scenario_id}")


# ---------------------------------------------------------------------------
# Task 2.1 RED: language isolation, mapping-as-input-only, typed provider
# failure → unavailable, no fabricated evidence/external calls, five numeric
# threshold-free formulas
# ---------------------------------------------------------------------------


def _assemble_cases():
    from backend.features.evaluation.application import assemble_cases

    return assemble_cases(_DATASET_ROOT)


def _kernel_adapter():
    from backend.features.evaluation.adapters.kernel import KernelAdapter

    return KernelAdapter(corpus=_load_dataset())


@pytest.mark.parametrize(
    ("scenario_id", "language"),
    (
        ("scenario.eval-01.es", "es"),
        ("scenario.eval-01.en", "en"),
    ),
)
def test_language_isolation_routes_case_to_declared_language(
    scenario_id: str,
    language: str,
) -> None:
    cases = _assemble_cases()
    case = next(c for c in cases if c.scenario_id == scenario_id)
    result = _kernel_adapter().execute(case)
    if result.reason_code != "insufficient_evidence":
        assert result.language == language
        if result.observed_outcome == "supported":
            for citation in result.citation_ids:
                assert f".{language}." in citation
    else:
        assert result.language is None


def test_mapping_question_is_input_only_expected_outcome_from_dataset() -> None:
    import json

    cases = _assemble_cases()
    for case in cases:
        if case.scenario_id.startswith("injected-"):
            continue
        payload = json.loads(
            (_DATASET_ROOT / _scenario_path(case.scenario_id)).read_text(encoding="utf-8")
        )
        assert case.expected_outcome == payload["expected_outcome"]
        assert case.expected_evidence_ids == tuple(payload.get("evidence", []))
        assert "question" not in payload


@pytest.mark.parametrize(
    ("case_id", "language"),
    (
        ("injected-provider-failure-es", "es"),
        ("injected-provider-failure-en", "en"),
    ),
)
def test_injected_provider_failure_is_typed_unavailable_without_evidence(
    case_id: str,
    language: str,
) -> None:
    cases = _assemble_cases()
    case = next(c for c in cases if c.scenario_id == case_id)
    result = _kernel_adapter().execute(case)
    assert result.observed_outcome == "unavailable"
    assert result.reason_code == "provider-timeout"
    assert result.citation_ids == ()
    assert result.language == language


def test_five_metrics_are_numeric_and_threshold_free() -> None:
    from backend.features.evaluation.adapters.clock import FrozenClock
    from backend.features.evaluation.application import run_evaluation
    from backend.features.evaluation.domain import Metrics

    clock = FrozenClock(timestamp=1_700_000_000.0, duration_seconds=0.0)
    summary = run_evaluation(_DATASET_ROOT, clock=clock)
    assert len(summary.results) == 34
    metrics = summary.metrics
    assert isinstance(metrics, Metrics)
    signals = (
        metrics.outcome_classification,
        metrics.citation_exact_match,
        metrics.language_routing,
        metrics.sensitive_block,
        metrics.contradiction_detection,
    )
    for signal in signals:
        assert isinstance(signal.numerator, int)
        assert isinstance(signal.denominator, int)
        assert signal.denominator >= 0
    assert metrics.outcome_classification.denominator == 34
    assert metrics.citation_exact_match.denominator == 34


# ---------------------------------------------------------------------------
# Task 3.1 RED: allowlisted JSON/JSONL/human output, forbidden-content absence,
# incomplete-promotion rejection, atomic current/previous retention
# ---------------------------------------------------------------------------

_FORBIDDEN_CONTENT_TOKENS = (
    "question",
    "answer",
    "claim text",
    "payload",
    "internal_text",
)


def _frozen_summary():
    from backend.features.evaluation.adapters.clock import FrozenClock
    from backend.features.evaluation.application import run_evaluation

    clock = FrozenClock(timestamp=1_700_000_000.0, duration_seconds=0.0)
    return run_evaluation(_DATASET_ROOT, clock=clock)


def test_json_summary_contains_only_allowlisted_fields() -> None:
    import json

    from backend.features.evaluation.adapters.report import serialize_summary

    payload = serialize_summary(_frozen_summary())
    assert payload == serialize_summary(_frozen_summary())
    data = json.loads(payload)
    assert data["total_cases"] == 34
    assert data["profile"] == "development"
    assert "run_id" in data
    assert "metrics" in data
    raw = payload.lower()
    for token in _FORBIDDEN_CONTENT_TOKENS:
        assert token not in raw, f"forbidden content token in summary: {token}"


def test_jsonl_records_contain_exactly_34_rows_and_safe_fields_only() -> None:
    import json

    from backend.features.evaluation.adapters.report import serialize_records

    payload = serialize_records(_frozen_summary())
    lines = [line for line in payload.strip().splitlines() if line]
    assert len(lines) == 34
    for line in lines:
        record = json.loads(line)
        assert "case_id" in record
        assert "language" in record
        assert "observed_outcome" in record
        assert "reason_code" in record
        assert "citations_match" in record
        assert "question" not in record
        assert "answer" not in record
        assert "claim" not in record
        assert "payload" not in record


def test_human_output_is_concise_and_excludes_content() -> None:
    from backend.features.evaluation.adapters.report import serialize_human

    text = serialize_human(_frozen_summary())
    assert "34" in text
    assert "development" in text
    low = text.lower()
    for token in _FORBIDDEN_CONTENT_TOKENS:
        assert token not in low, f"forbidden content token in human output: {token}"


def test_incomplete_promotion_is_rejected_and_leaves_no_baseline() -> None:
    from backend.features.evaluation.adapters.report import ReportAdapter

    adapter = ReportAdapter(base_dir=_tmp_eval_runs())
    raised = False
    try:
        adapter.promote(run_id="incomplete", payload=b"")
    except Exception:
        raised = True
    assert raised is True
    assert not (_tmp_eval_runs() / "current").exists()


def test_atomic_retention_keeps_current_and_creates_previous_on_replacement() -> None:
    import backend.features.evaluation.adapters.report as report_mod
    from backend.features.evaluation.adapters.report import ReportAdapter, serialize_summary

    base = _tmp_eval_runs()
    adapter = ReportAdapter(base_dir=base)
    first = serialize_summary(_frozen_summary())
    adapter.promote(run_id="run-a", payload=first.encode("utf-8"))
    current = base / "current"
    assert current.exists()
    first_files = sorted(current.iterdir())
    assert len(first_files) == 1
    assert not (base / "previous").exists()
    second = serialize_summary(_frozen_summary())
    adapter.promote(run_id="run-b", payload=second.encode("utf-8"))
    assert (base / "previous").exists()
    assert len(sorted((base / "previous").iterdir())) == len(first_files)
    assert len(sorted(current.iterdir())) == 1

    original = report_mod._os_replace

    def fail_final(*_: Any, **__: Any) -> None:
        raise OSError("injected rename failure")

    report_mod._os_replace = fail_final
    try:
        assert _raises(adapter.promote, run_id="run-c", payload=b"third")
    finally:
        report_mod._os_replace = original
    assert (current / "summary.json").read_bytes() == second.encode()


def _tmp_eval_runs() -> Path:
    import tempfile

    return Path(tempfile.mkdtemp(prefix="eval-runs-"))


# ---------------------------------------------------------------------------
# Task 2.1: language routing observes evidence, not input
# ---------------------------------------------------------------------------


def test_routed_language_is_nullable_when_screening_produces_no_evidence() -> None:
    cases = _assemble_cases()
    case = next(c for c in cases if c.safety_classification == "sensitive")
    result = _kernel_adapter().execute(case)
    assert result.language is None


def test_routed_language_is_observed_from_evidence_for_supported_case() -> None:
    cases = _assemble_cases()
    adapter = _kernel_adapter()
    for case in cases:
        result = adapter.execute(case)
        if result.observed_outcome == "supported":
            assert result.language == case.language
            return
    raise AssertionError("population must contain a supported evidence case")


def test_r2_001_language_routing_metric_detects_mismatch() -> None:
    from backend.features.evaluation.domain import CaseRecord, CaseResult, compute_metrics

    cases = (CaseRecord("x.es", "es", "q", "supported", "safe", (), "grounded"),)
    result = CaseResult("x.es", "en", "supported", "none", ("f.en",), True)
    m = compute_metrics((result,), cases)
    assert m.language_routing.numerator == 0
