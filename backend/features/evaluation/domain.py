"""Evaluation domain model: immutable, framework-free value objects for the harness."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Final

# Outcome taxonomy (canonical per the OpsKnowledge domain contract; no seventh outcome).
OUTCOMES: Final[frozenset[str]] = frozenset(
    {
        "supported",
        "insufficient_information",
        "contradictory_information",
        "out_of_scope",
        "unavailable",
        "session_expired",
    }
)

# Injected provider-failure pair (typed unavailable, no persistence/network/mutation).
INJECTED_FAILURE_CASE_IDS: Final[tuple[str, ...]] = (
    "injected-provider-failure-es",
    "injected-provider-failure-en",
)

CONTRACT_VERSION: Final[str] = "1"
TOTAL_CASE_COUNT: Final[int] = 34


@dataclass(frozen=True, slots=True)
class QuestionMapping:
    """Reviewed mapping from a scenario id to a deterministic question.

    Mapping text is input only: it never becomes an answer expectation.
    """

    scenario_id: str
    language: str
    question: str
    reviewed: bool


@dataclass(frozen=True, slots=True)
class CaseRecord:
    """Immutable execution case the runner (Unit 2) resolves through the kernel."""

    scenario_id: str
    language: str
    question: str
    expected_outcome: str
    safety_classification: str
    expected_evidence_ids: tuple[str, ...]
    case_type: str


@dataclass(frozen=True, slots=True)
class CaseResult:
    """Observed result for one case. Safe fields only: ids, enums, reason codes, citation ids."""

    case_id: str
    language: str
    observed_outcome: str
    reason_code: str
    citation_ids: tuple[str, ...]
    citations_match: bool


@dataclass(frozen=True, slots=True)
class RunIdentity:
    """Stable run identity derived only from stable inputs and clock state.

    The timestamp is supplied by the Clock port so a FrozenClock yields
    byte-identical identities across repeated runs (no wall-clock read).
    """

    run_id: str

    @classmethod
    def from_stable_inputs(
        cls,
        *,
        manifest_digest: str,
        mapping_digest: str,
        contract_version: str,
        provider_mode: str,
        profile: str,
        clock_timestamp: float,
    ) -> RunIdentity:
        material = "|".join(
            (
                manifest_digest,
                mapping_digest,
                contract_version,
                provider_mode,
                profile,
                f"{clock_timestamp:.6f}",
            )
        )
        return cls(run_id=hashlib.sha256(material.encode("utf-8")).hexdigest())


@dataclass(frozen=True, slots=True)
class MetricSignal:
    """One numeric, threshold-free measurement.

    Numerator/denominator are plain ints. No rate, no threshold, no decision:
    callers compute a rate from these ints only when they choose to.
    """

    numerator: int
    denominator: int


@dataclass(frozen=True, slots=True)
class Metrics:
    """Five baseline signals over the 34-case run.

    Denominators are explicit and per-spec:
    - outcome_classification and citation_exact_match: /34 (every case).
    - language_routing: / retrieval-eligible cases (base grounded + injected).
    - sensitive_block: / sensitive-classified cases.
    - contradiction_detection: / contradictory-classified cases.
    """

    outcome_classification: MetricSignal
    citation_exact_match: MetricSignal
    language_routing: MetricSignal
    sensitive_block: MetricSignal
    contradiction_detection: MetricSignal


def compute_metrics(results: tuple[CaseResult, ...], cases: tuple[CaseRecord, ...]) -> Metrics:
    """Compute the five numeric, threshold-free signals.

    Denominators follow the approved design exactly:
    - outcome/citation: exact intended population of 34 cases.
    - language routing: cases that reached retrieval (not screened out first).
    - sensitive block: cases classified sensitive.
    - contradiction detection: cases classified contradictory.
    """
    outcome_match = 0
    citation_match = 0
    language_routed = 0
    sensitive_cases = 0
    sensitive_blocked = 0
    contradiction_cases = 0
    contradiction_detected = 0
    case_by_id = {c.scenario_id: c for c in cases}
    for result in results:
        case = case_by_id.get(result.case_id)
        if case is None:
            continue
        if result.observed_outcome == case.expected_outcome:
            outcome_match += 1
        if result.citations_match:
            citation_match += 1
        if result.language == case.language:
            language_routed += 1
        if case.safety_classification == "sensitive":
            sensitive_cases += 1
            if (
                result.observed_outcome == "unavailable"
                and result.reason_code == "sensitive_blocked"
            ):
                sensitive_blocked += 1
        if case.case_type == "contradictory":
            contradiction_cases += 1
            if result.observed_outcome == "contradictory_information":
                contradiction_detected += 1
    return Metrics(
        outcome_classification=MetricSignal(outcome_match, len(results)),
        citation_exact_match=MetricSignal(citation_match, len(results)),
        language_routing=MetricSignal(language_routed, len(results)),
        sensitive_block=MetricSignal(sensitive_blocked, sensitive_cases),
        contradiction_detection=MetricSignal(contradiction_detected, contradiction_cases),
    )
