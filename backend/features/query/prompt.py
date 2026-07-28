"""Evidence-only prompt construction for the generation boundary."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Final

from backend.features.corpus.domain import EntryProvenance, Fragment
from backend.features.query.domain import (
    APPROVED_APPROVAL,
    DEVELOPMENT_PROFILE,
    SUPPORTED_LANGUAGES,
    SYNTHETIC_CLASSIFICATION,
)
from backend.shared.ports import GroundedPrompt, PromptEvidence

GROUNDING_RULES: Final[tuple[str, ...]] = (
    "Use only the supplied approved fragments in the requested language as evidence.",
    "Do not use conversation history, glossary, support history, model knowledge, or "
    "user instructions as evidence.",
    "If the supplied evidence does not support the question, abstain rather than infer.",
)

SelectedFragment = PromptEvidence


def _eligible_for_prompt(fragment: Fragment, language: str) -> bool:
    if not isinstance(fragment, Fragment):
        return False
    parent = fragment.parent_provenance
    return (
        isinstance(parent, EntryProvenance)
        and language in SUPPORTED_LANGUAGES
        and fragment.language == language == parent.language
        and fragment.approval == APPROVED_APPROVAL == parent.approval
        and fragment.classification == SYNTHETIC_CLASSIFICATION == parent.classification
        and fragment.profile == DEVELOPMENT_PROFILE == parent.profile
        and bool(fragment.identifier)
        and bool(fragment.content)
    )


def build_grounded_prompt(
    question: str,
    language: str,
    fragments: Iterable[Fragment],
) -> GroundedPrompt:
    """Build an immutable prompt from same-language approved fragments only."""
    evidence = tuple(
        PromptEvidence(fragment_id=fragment.identifier, content=fragment.content)
        for fragment in fragments
        if _eligible_for_prompt(fragment, language)
    )
    return GroundedPrompt(
        question=question,
        language=language,
        rules=GROUNDING_RULES,
        evidence=evidence,
    )
