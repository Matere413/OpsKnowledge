"""Indexing domain model.

Immutable, provider-neutral value objects for one complete current snapshot of
approved source metadata. No I/O, no framework, no provider dependency, and no
interpreted content. Validation of manifest authority, filename grammar, and
hash agreement belongs to the outbound adapter, not the domain. Following the
corpus feature convention, the domain layer performs no runtime validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

# Controlled vocabularies mirror the corpus domain and the CI dataset validator
# so the inventory and evaluation boundaries enforce the same safety surface.
ALLOWED_LANGUAGES: Final[frozenset[str]] = frozenset({"es", "en"})
ALLOWED_COLLECTIONS: Final[frozenset[str]] = frozenset({"runbooks", "adrs", "operational-policies"})
ALLOWED_APPROVALS: Final[frozenset[str]] = frozenset({"approved"})
ALLOWED_CLASSIFICATIONS: Final[frozenset[str]] = frozenset({"synthetic"})
ALLOWED_PROFILES: Final[frozenset[str]] = frozenset({"development"})
LANGUAGE_ES: Final[str] = "es"
LANGUAGE_EN: Final[str] = "en"


@dataclass(frozen=True, slots=True)
class RepositoryRelativePath:
    """Immutable normalized repository-relative path to a source artifact."""

    value: str


@dataclass(frozen=True, slots=True)
class Collection:
    """Immutable controlled-vocabulary collection name."""

    value: str


@dataclass(frozen=True, slots=True)
class EntryId:
    """Immutable entry identifier parsed from the filename grammar."""

    value: str


@dataclass(frozen=True, slots=True)
class Language:
    """Immutable controlled-vocabulary language tag (``es`` or ``en``)."""

    value: str


@dataclass(frozen=True, slots=True)
class Revision:
    """Immutable revision token parsed from the filename grammar."""

    value: str


@dataclass(frozen=True, slots=True)
class Approval:
    """Immutable approval state from the authoritative manifest."""

    value: str


@dataclass(frozen=True, slots=True)
class Classification:
    """Immutable classification from the authoritative manifest."""

    value: str


@dataclass(frozen=True, slots=True)
class Sha256:
    """Immutable lowercase 64-hex content hash from the authoritative manifest."""

    value: str


@dataclass(frozen=True, slots=True)
class SourceIdentity:
    """Immutable identity of one approved source artifact.

    Identity is ``(collection, entry, language, revision)``. Spanish and English
    revisions of the same entry are distinct identities; revisions are never
    compared across languages.
    """

    collection: Collection
    entry: EntryId
    language: Language
    revision: Revision


@dataclass(frozen=True, slots=True)
class SourceArtifact:
    """Immutable metadata for one approved source artifact.

    Exposes only metadata: path, identity, approval, classification, and hash.
    No interpreted content, bytes, absolute path, secret, credential, or provider
    payload is reachable from this type.
    """

    path: RepositoryRelativePath
    identity: SourceIdentity
    approval: Approval
    classification: Classification
    sha256: Sha256


@dataclass(frozen=True, slots=True)
class CompleteSnapshot:
    """Immutable complete current inventory snapshot.

    An empty tuple is valid only after exact manifest coverage finishes without
    omission. The tuple is stably ordered by ascending repository-relative path.
    """

    artifacts: tuple[SourceArtifact, ...]


@dataclass(frozen=True, slots=True)
class RejectedSnapshot:
    """Immutable whole-snapshot rejection with safe diagnostics only."""

    diagnostics: tuple[Diagnostic, ...]


@dataclass(frozen=True, slots=True)
class Diagnostic:
    """Safe, stable diagnostic for a rejected snapshot.

    Exposes only a stable ``code`` and a repository-relative ``reference``. It
    MUST NOT carry absolute paths, bytes, document text, secrets, credentials, or
    provider/OS error text. Diagnostics are sorted by reference then code.
    """

    code: str
    reference: str


# Closed diagnostic taxonomy for the inventory boundary.
DIAGNOSTIC_CODES: Final[frozenset[str]] = frozenset(
    {
        "profile-not-development",
        "corporate-source-denied",
        "unsafe-path",
        "unsafe-link",
        "manifest-invalid",
        "filename-invalid",
        "identity-duplicate",
        "coverage-missing",
        "coverage-unlisted",
        "source-unreadable",
        "source-non-regular",
        "hash-mismatch",
        "scan-incomplete",
    }
)


__all__ = [
    "ALLOWED_APPROVALS",
    "ALLOWED_CLASSIFICATIONS",
    "ALLOWED_COLLECTIONS",
    "ALLOWED_LANGUAGES",
    "ALLOWED_PROFILES",
    "Approval",
    "Classification",
    "Collection",
    "CompleteSnapshot",
    "DIAGNOSTIC_CODES",
    "Diagnostic",
    "EntryId",
    "LANGUAGE_EN",
    "LANGUAGE_ES",
    "Language",
    "RejectedSnapshot",
    "RepositoryRelativePath",
    "Revision",
    "Sha256",
    "SourceArtifact",
    "SourceIdentity",
]
