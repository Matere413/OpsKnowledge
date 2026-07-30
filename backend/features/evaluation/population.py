"""Reviewed, immutable population contract for language/abstention scoring."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Final

from backend.features.evaluation.domain import INJECTED_FAILURE_CASE_IDS

HUMAN_EXPERT: Final[str] = "human expert"
POPULATION_VERSION: Final[str] = "language-abstention-v1"
REPLACED_POPULATION_VERSION: Final[str] = "quality-evaluation-harness-v1"


class PopulationValidationError(ValueError):
    """Fail-closed population error containing only a safe reason code."""


@dataclass(frozen=True, slots=True)
class PopulationCase:
    case_id: str
    language: str
    expected_outcome: str
    expected_reason_code: str
    expected_escalation: str
    language_eligible: bool
    abstention_eligible: bool
    escape_required: bool
    provider_failure: bool = False


@dataclass(frozen=True, slots=True)
class PopulationDefinition:
    version: str
    cases: tuple[PopulationCase, ...]
    digest: str

    def validate(self, case_ids: tuple[str, ...] | None = None) -> None:
        if self.digest != _digest(self.version, self.cases):
            raise PopulationValidationError("population-digest-mismatch")
        expected = tuple(case.case_id for case in self.cases)
        actual = expected if case_ids is None else case_ids
        if len(expected) != 34 or len(actual) != len(set(actual)):
            raise PopulationValidationError("population-duplicate-or-count")
        if set(actual) != set(expected):
            raise PopulationValidationError("population-id-mismatch")
        counts = (
            sum(case.language_eligible for case in self.cases),
            sum(case.abstention_eligible for case in self.cases),
            sum(case.escape_required for case in self.cases),
        )
        if counts != (30, 18, 18) or any(count == 0 for count in counts):
            raise PopulationValidationError("population-denominator-invalid")


_SPECS: Final[tuple[tuple[str, str], ...]] = (
    (("supported", "none"),) * 8
    + (("insufficient_information", "insufficient_evidence"),) * 2
    + (("contradictory_information", "contradiction_detected"),) * 2
    + (
        ("out_of_scope", "out_of_scope"),
        ("unavailable", "provider-timeout"),
        ("out_of_scope", "prompt_override_blocked"),
        ("unavailable", "sensitive_blocked"),
    )
)


def _base_case(language: str, number: int, outcome: str, reason: str) -> PopulationCase:
    abstention = outcome != "supported"
    return PopulationCase(
        f"scenario.eval-{number:02d}.{language}",
        language,
        outcome,
        reason,
        HUMAN_EXPERT if abstention else "none",
        number != 16,
        abstention,
        abstention,
    )  # noqa: E501


def _base_cases() -> tuple[PopulationCase, ...]:
    return tuple(
        _base_case(language, number, outcome, reason)
        for language in ("es", "en")
        for number, (outcome, reason) in enumerate(_SPECS, 1)
    )  # noqa: E501


IN_MEMORY_TIMEOUT_CASES: Final[tuple[PopulationCase, ...]] = tuple(
    PopulationCase(
        case_id, language, "unavailable", "provider-timeout", HUMAN_EXPERT, False, True, True, True
    )  # noqa: E501
    for case_id, language in zip(INJECTED_FAILURE_CASE_IDS, ("es", "en"), strict=True)
)


def _digest(version: str, cases: tuple[PopulationCase, ...]) -> str:
    material = json.dumps(
        {"version": version, "cases": [asdict(c) for c in cases]},
        sort_keys=True,
        separators=(",", ":"),
    )  # noqa: E501
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


_CASES: Final[tuple[PopulationCase, ...]] = tuple(
    sorted(_base_cases() + IN_MEMORY_TIMEOUT_CASES, key=lambda c: c.case_id)
)  # noqa: E501
CURRENT_POPULATION: Final[PopulationDefinition] = PopulationDefinition(
    POPULATION_VERSION, _CASES, _digest(POPULATION_VERSION, _CASES)
)  # noqa: E501
CURRENT_POPULATION.validate()
POPULATION_DIGEST: Final[str] = CURRENT_POPULATION.digest
POPULATION: Final[PopulationDefinition] = CURRENT_POPULATION
