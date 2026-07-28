"""Kernel adapter: execute cases through the unchanged development boundary.

Wraps the existing ``resolve_query`` / ``LexicalRetriever`` / ``FakeProvider``
boundary without modifying it. Records only safe fields (ids, enums, reason
codes, citation ids) and the routed language; never records question, answer,
citation content, or provider payloads. The injected failure pair uses a
``FakeProvider`` that raises typed ``ProviderFailure("provider-timeout")`` so
the kernel records ``unavailable`` with no fabricated evidence or external calls.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from backend.features.corpus.application import Corpus
from backend.features.evaluation.domain import CaseRecord, CaseResult
from backend.features.query.adapters.fake_provider import FakeProvider
from backend.features.query.adapters.lexical_retriever import LexicalRetriever
from backend.features.query.application import resolve_query
from backend.shared.ports import ProviderFailure

_TIMEOUT_REASON: Final[str] = "provider-timeout"


@dataclass(frozen=True, slots=True)
class KernelAdapter:
    """Execute a CaseRecord through the development kernel boundary."""

    corpus: Corpus

    def execute(self, case: CaseRecord) -> CaseResult:
        retriever = LexicalRetriever(self.corpus)
        response = resolve_query(
            case.question,
            retriever,
            _provider_for(case),
            profile="development",
            language=case.language,
            safety_classification=case.safety_classification,
        )
        return CaseResult(
            case_id=case.scenario_id,
            language=case.language,
            observed_outcome=response.outcome,
            reason_code=response.reason_code,
            citation_ids=response.citations,
            citations_match=_citations_match(response.citations, case.expected_evidence_ids),
        )


def _provider_for(case: CaseRecord) -> FakeProvider:
    """Injected failure cases get a typed ``provider-timeout``; others get the
    default deterministic fake provider. No external provider is constructed."""
    if case.scenario_id.startswith("injected-provider-failure-"):
        return FakeProvider(failure=ProviderFailure(_TIMEOUT_REASON))
    return FakeProvider()


def _citations_match(observed: tuple[str, ...], expected: tuple[str, ...]) -> bool:
    """Exact citation-set match: same ids, same order-independent set."""
    return set(observed) == set(expected) and len(observed) == len(expected)
