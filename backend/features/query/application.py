"""Safe, provider-independent resolution for the grounded query kernel."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final

from backend.features.corpus.domain import (
    ALLOWED_COLLECTIONS,
    ALLOWED_PROVENANCE,
    EntryProvenance,
    Fragment,
)
from backend.features.query.domain import (
    APPROVED_APPROVAL,
    DEVELOPMENT_PROFILE,
    SUPPORTED_LANGUAGES,
    SYNTHETIC_CLASSIFICATION,
)
from backend.features.query.prompt import build_grounded_prompt
from backend.shared.ports import (
    Generate,
    GeneratedAnswer,
    ProviderFailure,
    Retrieve,
    SafeResponse,
)

_HUMAN_EXPERT: Final[str] = "human expert"
_ENGLISH_HINTS: Final[frozenset[str]] = frozenset(
    {"do", "for", "how", "is", "service", "the", "what"}
)
_SPANISH_HINTS: Final[frozenset[str]] = frozenset(
    {"cómo", "como", "de", "el", "es", "la", "para", "qué", "que", "servicio"}
)
_SENSITIVE_PATTERNS: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r"\bexample\.test\b", re.IGNORECASE),
    re.compile(r"\btest-[a-z0-9-]{2,}\b", re.IGNORECASE),
    re.compile(r"\binvalid(?:-[a-z0-9-]+)?\b", re.IGNORECASE),
    re.compile(r"\b[A-Z]{2,}-\d{4,}\b"),
    re.compile(r"\b(?:[a-z0-9-]+\.)+(?:internal|local|corp|intranet|private)\b", re.IGNORECASE),
)
_OVERRIDE_MARKERS: Final[tuple[str, ...]] = (
    "ignore previous",
    "ignore the grounding",
    "disregard",
    "without citations",
    "model knowledge",
    "system prompt",
)
_OUT_OF_SCOPE_MARKERS: Final[tuple[str, ...]] = (
    "out of scope",
    "weather",
    "medical",
    "patient",
    "screenshot",
    "image",
)


def _response(
    outcome: str,
    profile: str,
    reason_code: str,
    *,
    escalation: str = _HUMAN_EXPERT,
    citations: tuple[str, ...] = (),
    routed_language: str | None = None,
) -> SafeResponse:
    return SafeResponse(
        outcome,
        citations,
        escalation,
        profile,
        reason_code,
        routed_language,
    )


def _screen(
    question: str,
    safety_classification: str | None,
) -> tuple[str, str] | None:
    text = question.casefold()
    if safety_classification == "sensitive" or any(
        pattern.search(question) is not None for pattern in _SENSITIVE_PATTERNS
    ):
        return "unavailable", "sensitive_blocked"
    if safety_classification == "override" or any(marker in text for marker in _OVERRIDE_MARKERS):
        return "out_of_scope", "prompt_override_blocked"
    if safety_classification not in (None, "safe"):
        return "out_of_scope", "out_of_scope"
    if any(marker in text for marker in _OUT_OF_SCOPE_MARKERS):
        return "out_of_scope", "out_of_scope"
    return None


def _route_language(question: str, requested: str | None) -> str | None:
    if requested is not None:
        return requested if requested in SUPPORTED_LANGUAGES else None
    tokens = set(re.findall(r"[^\W_]+", question.casefold(), re.UNICODE))
    english = len(tokens & _ENGLISH_HINTS)
    spanish = len(tokens & _SPANISH_HINTS)
    if english == spanish or max(english, spanish) == 0:
        return None
    return "en" if english > spanish else "es"


def _eligible_fragment(fragment: object, language: str, profile: str) -> bool:
    if not isinstance(fragment, Fragment):
        return False
    parent = fragment.parent_provenance
    return (
        isinstance(parent, EntryProvenance)
        and bool(fragment.identifier)
        and bool(fragment.content)
        and fragment.language == language == parent.language
        and fragment.approval == APPROVED_APPROVAL == parent.approval
        and fragment.classification == SYNTHETIC_CLASSIFICATION == parent.classification
        and fragment.profile == profile == parent.profile
        and parent.collection in ALLOWED_COLLECTIONS
        and fragment.provenance in ALLOWED_PROVENANCE
    )


def _has_contradictory_revisions(fragments: tuple[Fragment, ...]) -> bool:
    revisions: dict[str, set[str]] = {}
    for fragment in fragments:
        revisions.setdefault(fragment.parent_provenance.logical_entry_id, set()).add(
            fragment.parent_provenance.revision
        )
    return any(len(values) > 1 for values in revisions.values())


def _valid_citations(answer: GeneratedAnswer, fragments: tuple[Fragment, ...]) -> tuple[str, ...]:
    if not isinstance(answer, GeneratedAnswer):
        return ()
    citation_ids = answer.citation_ids
    if (
        not isinstance(citation_ids, tuple)
        or not citation_ids
        or any(not isinstance(identifier, str) or not identifier for identifier in citation_ids)
    ):
        return ()
    allowed = {fragment.identifier for fragment in fragments}
    return citation_ids if set(citation_ids).issubset(allowed) else ()


def _observed_language(fragments: tuple[Fragment, ...]) -> str | None:
    languages = {fragment.language for fragment in fragments}
    if len(languages) != 1:
        return None
    return next(iter(languages))


def _provider_failure_response(
    profile: str,
    failure: BaseException,
    *,
    routed_language: str | None,
) -> SafeResponse:
    if isinstance(failure, ProviderFailure):
        reason_code = failure.reason_code or "provider_failure"
    else:
        reason_code = "provider-error"
    return _response(
        "unavailable",
        profile,
        reason_code,
        routed_language=routed_language,
    )


@dataclass(frozen=True, slots=True)
class QueryApplication:
    retriever: Retrieve
    generator: Generate
    profile: str = DEVELOPMENT_PROFILE

    def resolve(
        self,
        question: str,
        language: str | None = None,
        safety_classification: str | None = None,
    ) -> SafeResponse:
        if self.profile != DEVELOPMENT_PROFILE:
            return _response("unavailable", self.profile, "profile_not_development")
        screened = _screen(question, safety_classification)
        if screened is not None:
            outcome, reason_code = screened
            return _response(outcome, self.profile, reason_code)

        routed_language = _route_language(question, language)
        if routed_language is None:
            return _response("out_of_scope", self.profile, "language_ambiguous")

        try:
            retrieved = self.retriever.retrieve(question, routed_language, self.profile)
        except Exception:
            return _response("unavailable", self.profile, "retrieval_failure")
        fragments = tuple(
            fragment
            for fragment in retrieved
            if _eligible_fragment(fragment, routed_language, self.profile)
        )
        if not fragments:
            return _response("insufficient_information", self.profile, "insufficient_evidence")
        observed_language = _observed_language(fragments)
        if _has_contradictory_revisions(fragments):
            return _response(
                "contradictory_information",
                self.profile,
                "contradiction_detected",
                routed_language=observed_language,
            )

        prompt = build_grounded_prompt(question, routed_language, fragments)
        try:
            answer = self.generator.generate(prompt)
        except Exception as failure:
            return _provider_failure_response(
                self.profile,
                failure,
                routed_language=observed_language,
            )
        citations = _valid_citations(answer, fragments)
        if not citations:
            return _response(
                "unavailable",
                self.profile,
                "invalid_citations",
                routed_language=observed_language,
            )
        return _response(
            "supported",
            self.profile,
            "none",
            escalation="none",
            citations=citations,
            routed_language=observed_language,
        )


def resolve_query(
    question: str,
    retriever: Retrieve,
    generator: Generate,
    *,
    profile: str = DEVELOPMENT_PROFILE,
    language: str | None = None,
    safety_classification: str | None = None,
) -> SafeResponse:
    return QueryApplication(retriever, generator, profile).resolve(
        question, language, safety_classification
    )
