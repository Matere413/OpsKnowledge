"""Corpus application layer: loading policy and the loaded corpus surface.

The application layer orchestrates the manifest adapter (an outbound port) and
enforces the development-only synthetic boundary as pure domain rules. It
exposes no retrieval interface by design: retrieval is a query-feature concern
(Work Unit 2). The loaded :class:`Corpus` is an immutable snapshot of approved,
synthetic, development-only fragments ordered by stable identifier.

Fail-closed errors are raised as :class:`CorpusLoadError` carrying a safe
``reason_code`` (a stable identifier, never free text and never content). The
application layer never logs content; it only raises safe reason codes so the
inbound adapter (CLI, later slice) can emit safe JSON diagnostics.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from backend.features.corpus.domain import (
    ALLOWED_COLLECTIONS,
    ALLOWED_LANGUAGES,
    ALLOWED_OCR_QUALITY,
    ALLOWED_PROVENANCE,
    Entry,
    Fragment,
)

DEVELOPMENT_PROFILE: Final[str] = "development"
SYNTHETIC_CLASSIFICATION: Final[str] = "synthetic"
APPROVED_APPROVAL: Final[str] = "approved"


class CorpusLoadError(Exception):
    """Fail-closed corpus loading error.

    Carries a safe, stable ``reason_code`` (never content, never free text)
    so callers can emit safe JSON diagnostics without leaking payload text.
    The string representation deliberately omits content: it surfaces only the
    reason code and the affected artifact path/identifier.
    """

    __slots__ = ("reason_code", "artifact_ref")

    def __init__(self, reason_code: str, artifact_ref: str = "") -> None:
        self.reason_code = reason_code
        self.artifact_ref = artifact_ref
        super().__init__(f"{reason_code}: {artifact_ref}" if artifact_ref else reason_code)


@dataclass(frozen=True, slots=True)
class Corpus:
    """Immutable loaded corpus snapshot.

    Exposes only the approved, synthetic, development-only fragments ordered
    by stable ascending identifier. No retrieval, search, or query method is
    exposed: those belong to the query feature.
    """

    fragments: tuple[Fragment, ...]

    @property
    def fragment_ids(self) -> tuple[str, ...]:
        """Return the stable ascending fragment identifiers."""
        return tuple(fragment.identifier for fragment in self.fragments)


def assert_profile_allowed(profile: str) -> None:
    """Fail closed when the active profile is not ``development``.

    This is the startup boundary: a non-development profile must never reach
    retrieval or generation. The check is independent of manifest contents so
    a misconfigured runtime fails closed even before reading the manifest.
    """
    if profile != DEVELOPMENT_PROFILE:
        raise CorpusLoadError("profile-not-development", artifact_ref=profile)


def validate_entry_payload(payload: dict, artifact_ref: str) -> Entry:
    """Validate a single entry payload against the development/synthetic boundary.

    Returns an immutable :class:`Entry` on success. Raises
    :class:`CorpusLoadError` with a safe reason code on any violation. Content
    is never included in the error.
    """
    identifier = _require_str(payload, "id", artifact_ref, "entry-missing-field")
    logical_entry_id = _require_str(
        payload, "logical_entry_id", artifact_ref, "entry-missing-field"
    )
    revision = _require_str(payload, "revision", artifact_ref, "entry-missing-field")
    collection = _require_str(payload, "collection", artifact_ref, "entry-missing-field")
    language = _require_str(payload, "language", artifact_ref, "entry-missing-field")
    approval = _require_str(payload, "approval", artifact_ref, "entry-missing-field")
    classification = _require_str(payload, "classification", artifact_ref, "entry-missing-field")
    profile = _require_str(payload, "profile", artifact_ref, "entry-missing-field")
    content = _require_str(payload, "content", artifact_ref, "entry-missing-field")
    content_sha256 = _require_str(payload, "content_sha256", artifact_ref, "entry-missing-field")

    if profile != DEVELOPMENT_PROFILE:
        raise CorpusLoadError("entry-profile-not-development", artifact_ref)
    if classification != SYNTHETIC_CLASSIFICATION:
        raise CorpusLoadError("entry-classification-not-synthetic", artifact_ref)
    if approval != APPROVED_APPROVAL:
        raise CorpusLoadError("entry-approval-not-approved", artifact_ref)
    if language not in ALLOWED_LANGUAGES:
        raise CorpusLoadError("entry-language-unsupported", artifact_ref)
    if collection not in ALLOWED_COLLECTIONS:
        raise CorpusLoadError("entry-collection-unsupported", artifact_ref)

    actual_hash = _sha256_content(content)
    if content_sha256 != actual_hash:
        raise CorpusLoadError("entry-content-hash-mismatch", artifact_ref)

    return Entry(
        identifier=identifier,
        logical_entry_id=logical_entry_id,
        revision=revision,
        collection=collection,
        language=language,
        approval=approval,
        classification=classification,
        profile=profile,
        content=content,
        content_sha256=content_sha256,
    )


def validate_fragment_payload(
    payload: dict,
    artifact_ref: str,
    entries_by_id: dict[str, Entry],
) -> Fragment:
    """Validate a single fragment payload against the boundary and its parent.

    Returns an immutable :class:`Fragment` on success. Raises
    :class:`CorpusLoadError` with a safe reason code on any violation. Content
    is never included in the error.
    """
    identifier = _require_str(payload, "id", artifact_ref, "fragment-missing-field")
    entry_id = _require_str(payload, "entry_id", artifact_ref, "fragment-missing-field")
    language = _require_str(payload, "language", artifact_ref, "fragment-missing-field")
    provenance = _require_str(payload, "provenance", artifact_ref, "fragment-missing-field")
    approval = _require_str(payload, "approval", artifact_ref, "fragment-missing-field")
    classification = _require_str(payload, "classification", artifact_ref, "fragment-missing-field")
    profile = _require_str(payload, "profile", artifact_ref, "fragment-missing-field")
    content = _require_str(payload, "content", artifact_ref, "fragment-missing-field")
    content_sha256 = _require_str(payload, "content_sha256", artifact_ref, "fragment-missing-field")
    source_reference = payload.get("source_reference", "")
    quality = payload.get("quality", "")
    if not isinstance(source_reference, str):
        source_reference = ""
    if not isinstance(quality, str):
        quality = ""
    fictitious_raw = payload.get("fictitious")
    fictitious = fictitious_raw is True

    if profile != DEVELOPMENT_PROFILE:
        raise CorpusLoadError("fragment-profile-not-development", artifact_ref)
    if classification != SYNTHETIC_CLASSIFICATION:
        raise CorpusLoadError("fragment-classification-not-synthetic", artifact_ref)
    if approval != APPROVED_APPROVAL:
        raise CorpusLoadError("fragment-approval-not-approved", artifact_ref)
    if language not in ALLOWED_LANGUAGES:
        raise CorpusLoadError("fragment-language-unsupported", artifact_ref)
    if provenance not in ALLOWED_PROVENANCE:
        raise CorpusLoadError("fragment-provenance-unsupported", artifact_ref)

    # OCR provenance requires a non-empty source_reference and a quality value.
    if provenance == "ocr":
        if not source_reference:
            raise CorpusLoadError("fragment-ocr-source-missing", artifact_ref)
        if quality not in ALLOWED_OCR_QUALITY:
            raise CorpusLoadError("fragment-ocr-quality-unsupported", artifact_ref)
    else:
        # Non-OCR fragments must not carry OCR metadata.
        if source_reference:
            raise CorpusLoadError("fragment-source-not-ocr", artifact_ref)
        if quality:
            raise CorpusLoadError("fragment-quality-not-ocr", artifact_ref)

    actual_hash = _sha256_content(content)
    if content_sha256 != actual_hash:
        raise CorpusLoadError("fragment-content-hash-mismatch", artifact_ref)

    # Parent resolution and language match.
    parent = entries_by_id.get(entry_id)
    if parent is None:
        raise CorpusLoadError("fragment-parent-missing", artifact_ref)
    if parent.language != language:
        raise CorpusLoadError("fragment-language-mismatch", artifact_ref)

    return Fragment(
        identifier=identifier,
        entry_id=entry_id,
        language=language,
        provenance=provenance,
        approval=approval,
        classification=classification,
        profile=profile,
        content=content,
        content_sha256=content_sha256,
        source_reference=source_reference,
        quality=quality,
        fictitious=fictitious,
    )


def _require_str(payload: dict, key: str, artifact_ref: str, reason: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise CorpusLoadError(reason, artifact_ref)
    return value


def _sha256_content(content: str) -> str:
    import hashlib

    return hashlib.sha256(content.encode("utf-8")).hexdigest()
