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
