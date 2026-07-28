"""Evaluation application: assemble 34 cases, run the kernel, compute metrics.

Unit 2 application layer. Validates the dataset (Unit 1 gate), validates the
reviewed mapping, assembles 32 base + 2 injected provider-failure cases,
executes each through the unchanged development kernel, records only safe
fields, and computes the five numeric, threshold-free metrics. No report, CLI,
persistence, or baseline promotion: those are Unit 3.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from backend.features.evaluation.adapters.dataset import (
    base_scenario_payloads,
    load_validated_corpus,
)
from backend.features.evaluation.adapters.kernel import KernelAdapter
from backend.features.evaluation.domain import (
    CONTRACT_VERSION,
    INJECTED_FAILURE_CASE_IDS,
    TOTAL_CASE_COUNT,
    CaseRecord,
    CaseResult,
    Metrics,
    RunIdentity,
    compute_metrics,
)
from backend.features.evaluation.mapping import (
    REVIEWED_MAPPING,
    mapping_digest,
    validate_mapping,
)
from backend.features.evaluation.ports import Clock

_PROFILE: Final[str] = "development"
_PROVIDER_MODE: Final[str] = "fake"


@dataclass(frozen=True, slots=True)
class RunSummary:
    """Immutable summary of one evaluation run. Safe fields only."""

    identity: RunIdentity
    results: tuple[CaseResult, ...]
    metrics: Metrics


def assemble_cases(root: Path) -> tuple[CaseRecord, ...]:
    """Assemble exactly 34 cases: 32 base scenarios + 2 injected failures.

    Base cases use unchanged dataset bytes plus the reviewed mapping question
    (input only). Injected cases are in-memory only; never edit or persist.
    """
    payloads = base_scenario_payloads(root)
    mapping_by_id = {row.scenario_id: row for row in REVIEWED_MAPPING}
    scenario_languages = {
        sid: json.loads(payload.decode("utf-8"))["language"] for sid, payload in payloads.items()
    }
    validate_mapping(REVIEWED_MAPPING, sorted(payloads), scenario_languages)
    base_cases: list[CaseRecord] = []
    for scenario_id in sorted(payloads):
        payload = json.loads(payloads[scenario_id].decode("utf-8"))
        row = mapping_by_id[scenario_id]
        base_cases.append(
            CaseRecord(
                scenario_id=scenario_id,
                language=payload["language"],
                question=row.question,
                expected_outcome=payload["expected_outcome"],
                safety_classification=payload["safety_classification"],
                expected_evidence_ids=tuple(payload.get("evidence", [])),
                case_type=payload["case_type"],
            )
        )
    injected = tuple(_injected_failure_case(cid, lang) for cid, lang in _injected_pairs())
    cases = tuple(base_cases) + injected
    if len(cases) != TOTAL_CASE_COUNT:
        raise RuntimeError(f"expected {TOTAL_CASE_COUNT} cases, got {len(cases)}")
    return cases


def _injected_pairs() -> tuple[tuple[str, str], ...]:
    return (
        (INJECTED_FAILURE_CASE_IDS[0], "es"),
        (INJECTED_FAILURE_CASE_IDS[1], "en"),
    )


def _injected_failure_case(case_id: str, language: str) -> CaseRecord:
    """In-memory injected provider-failure case (never persisted).

    The question retrieves a single non-contradictory fragment so the kernel
    reaches the provider call where typed ``provider-timeout`` fires. ES uses
    ``policy-003`` (single revision). EN's only entry (``adr-002``) has two
    revisions, but the OCR fragment exists only at rev 1; OCR-unique tokens
    retrieve only that single-revision fragment, avoiding contradiction.
    """
    question = (
        "politica operacional entrada referenciada"
        if language == "es"
        else "scanned document provenance quality"
    )
    return CaseRecord(
        scenario_id=case_id,
        language=language,
        question=question,
        expected_outcome="unavailable",
        safety_classification="safe",
        expected_evidence_ids=(),
        case_type="unanswerable",
    )


def run_evaluation(root: Path, *, clock: Clock) -> RunSummary:
    """Run the full 34-case evaluation and return the safe summary."""
    corpus = load_validated_corpus(root, profile=_PROFILE)
    cases = assemble_cases(root)
    adapter = KernelAdapter(corpus=corpus)
    results = tuple(adapter.execute(case) for case in cases)
    metrics = compute_metrics(results, cases)
    identity = RunIdentity.from_stable_inputs(
        manifest_digest=hashlib.sha256((root / "manifest.json").read_bytes()).hexdigest(),
        mapping_digest=mapping_digest(REVIEWED_MAPPING),
        contract_version=CONTRACT_VERSION,
        provider_mode=_PROVIDER_MODE,
        profile=_PROFILE,
        clock_timestamp=clock.now(),
    )
    return RunSummary(identity=identity, results=results, metrics=metrics)
