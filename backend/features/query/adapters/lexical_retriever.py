"""Deterministic lexical retrieval over an immutable corpus snapshot."""

from __future__ import annotations

import re
from dataclasses import dataclass

from backend.features.corpus.application import Corpus
from backend.features.corpus.domain import (
    ALLOWED_COLLECTIONS,
    ALLOWED_OCR_QUALITY,
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

_TOKEN_PATTERN = re.compile(r"[^\W_]+", re.UNICODE)


def normalize_tokens(value: str) -> frozenset[str]:
    if not isinstance(value, str):
        return frozenset()
    return frozenset(_TOKEN_PATTERN.findall(value.casefold()))


def _eligible(fragment: Fragment, language: str, profile: str) -> bool:
    parent = getattr(fragment, "parent_provenance", None)
    return (
        isinstance(fragment, Fragment)
        and isinstance(parent, EntryProvenance)
        and language in SUPPORTED_LANGUAGES
        and profile == DEVELOPMENT_PROFILE
        and all((fragment.identifier, fragment.content, parent.logical_entry_id, parent.revision))
        and (fragment.language, parent.language) == (language, language)
        and isinstance(fragment.fictitious, bool)
        and (fragment.approval, parent.approval) == (APPROVED_APPROVAL, APPROVED_APPROVAL)
        and (fragment.classification, parent.classification)
        == (SYNTHETIC_CLASSIFICATION, SYNTHETIC_CLASSIFICATION)
        and (fragment.profile, parent.profile) == (profile, profile)
        and parent.collection in ALLOWED_COLLECTIONS
        and fragment.provenance in ALLOWED_PROVENANCE
        and isinstance(fragment.source_reference, str)
        and isinstance(fragment.quality, str)
        and (
            (
                fragment.provenance == "ocr"
                and bool(fragment.source_reference)
                and fragment.quality in ALLOWED_OCR_QUALITY
            )
            or (not fragment.source_reference and not fragment.quality)
        )
    )


@dataclass(frozen=True, slots=True)
class LexicalRetriever:
    corpus: Corpus

    def retrieve(
        self, question: str, language: str, profile: str = DEVELOPMENT_PROFILE
    ) -> tuple[Fragment, ...]:
        query_tokens = normalize_tokens(question)
        if not query_tokens:
            return ()

        ranked: list[tuple[int, str, Fragment]] = []
        for fragment in self.corpus.fragments:
            if not _eligible(fragment, language, profile):
                continue
            score = len(query_tokens & normalize_tokens(fragment.content))
            if score:
                ranked.append((-score, fragment.identifier, fragment))
        ranked.sort(key=lambda item: (item[0], item[1]))
        return tuple(fragment for _, _, fragment in ranked)
