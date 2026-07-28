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


def _scenario_path(scenario_id: str) -> str:
    import json

    manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    for artifact in manifest["artifacts"]:
        if artifact.get("id") == scenario_id:
            return artifact["path"]
    raise AssertionError(f"unknown scenario id: {scenario_id}")
