"""Provider-independent query value types and safety constants."""

from __future__ import annotations

from typing import Final, Literal

from backend.features.corpus.domain import ALLOWED_LANGUAGES

SUPPORTED_LANGUAGES: Final[frozenset[str]] = ALLOWED_LANGUAGES
DEVELOPMENT_PROFILE: Final[str] = "development"
APPROVED_APPROVAL: Final[str] = "approved"
SYNTHETIC_CLASSIFICATION: Final[str] = "synthetic"

type QueryLanguage = Literal["en", "es"]
