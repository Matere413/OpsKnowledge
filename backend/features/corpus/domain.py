"""Corpus domain model.

Immutable, provider-independent value objects describing the manifest-controlled
synthetic knowledge boundary. Domain objects carry no I/O, no framework, and no
retrieval semantics: retrieval belongs to the query feature (Work Unit 2).

The :class:`Fragment` value object is the only corpus surface the application
layer exposes. It is frozen so callers cannot mutate loaded evidence in place.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

# Controlled vocabularies mirror the CI dataset validator
# (``scripts/ci/validate_evaluation_dataset.py``) so the runtime loader and the
# repository guard enforce the same boundary. Any change here requires a new
# SDD change.
ALLOWED_LANGUAGES: Final[frozenset[str]] = frozenset({"es", "en"})
ALLOWED_COLLECTIONS: Final[frozenset[str]] = frozenset({"runbooks", "adrs", "operational-policies"})
ALLOWED_PROVENANCE: Final[frozenset[str]] = frozenset({"original", "ocr"})
ALLOWED_APPROVALS: Final[frozenset[str]] = frozenset({"approved"})
ALLOWED_CLASSIFICATIONS: Final[frozenset[str]] = frozenset({"synthetic"})
ALLOWED_PROFILES: Final[frozenset[str]] = frozenset({"development"})
ALLOWED_OCR_QUALITY: Final[frozenset[str]] = frozenset({"low", "medium", "high"})


@dataclass(frozen=True, slots=True)
class Fragment:
    """Immutable fragment of an approved, synthetic, development-only entry.

    A fragment is the unit of evidence the query feature may cite. It carries
    provenance and language so retrieval can filter by language and the
    application layer can prove every citation points at approved, synthetic,
    development-only, language-matched content.

    Attributes mirror the evaluation-dataset fragment payload fields. The
    ``content`` attribute is reachable by the application layer for prompt
    construction but MUST NEVER appear in logs or CLI output (safe-field
    contract). ``fictitious`` marks a fragment that carries obviously
    non-corporate sensitive identifiers.
    """

    identifier: str
    entry_id: str
    language: str
    provenance: str
    approval: str
    classification: str
    profile: str
    content: str
    content_sha256: str
    source_reference: str
    quality: str
    fictitious: bool

    @property
    def is_ocr(self) -> bool:
        """Return True when this fragment was extracted via OCR provenance."""
        return self.provenance == "ocr"


@dataclass(frozen=True, slots=True)
class Entry:
    """Immutable parent entry a fragment references.

    Entries carry the logical grouping, revision, collection, and language a
    fragment inherits. The loader validates that every fragment's parent entry
    exists, is approved, synthetic, development-only, and language-matched.
    """

    identifier: str
    logical_entry_id: str
    revision: str
    collection: str
    language: str
    approval: str
    classification: str
    profile: str
    content: str
    content_sha256: str
