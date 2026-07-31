"""Indexing application use case.

``InventoryApprovedSources`` is the application gate: it rejects non-development
profiles and any corporate source mode BEFORE invoking the outbound repository
port. On denial it returns a :class:`RejectedSnapshot` with a safe diagnostic
and never reaches the port, so no source artifact is scanned for a denied
request. On a permitted request it delegates to the port and returns its
complete snapshot or whole-snapshot rejection unchanged.

The use case is provider-neutral and framework-free: it depends only on the
domain result types and the repository port. It does not construct diagnostics
that carry content, absolute paths, bytes, secrets, credentials, or provider
payloads.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from backend.features.indexing.domain import Diagnostic, RejectedSnapshot
from backend.features.indexing.ports import ApprovedSourceRepository, InventoryResult

DEVELOPMENT_PROFILE: Final[str] = "development"
CORPORATE_SOURCE: Final[str] = "corporate"

_PROFILE_NOT_DEVELOPMENT: Final[Diagnostic] = Diagnostic(
    code="profile-not-development", reference=""
)
_CORPORATE_SOURCE_DENIED: Final[Diagnostic] = Diagnostic(
    code="corporate-source-denied", reference=""
)


@dataclass(frozen=True, slots=True)
class InventoryApprovedSources:
    """Application use case for a complete approved source inventory.

    Attributes:
        repository: Outbound port returning a complete snapshot or rejection.
        profile: Active runtime profile. Only ``development`` is permitted.
        source_mode: Source mode selector. ``corporate`` is denied before the
            port is invoked.

    The use case is frozen so its configuration cannot be mutated after
    construction. Denial diagnostics are constructed once and reused.
    """

    repository: ApprovedSourceRepository
    profile: str = DEVELOPMENT_PROFILE
    source_mode: str = "local"

    def inventory(self) -> InventoryResult:
        """Return a complete snapshot or a whole-snapshot rejection.

        Denial precedence (fail-closed, before any port invocation):

        1. ``profile != development`` -> ``profile-not-development``.
        2. ``source_mode == corporate`` -> ``corporate-source-denied``.

        Only after both gates pass is the repository port invoked. The port's
        result is returned unchanged so the application layer never fabricates
        a partial snapshot or masks a rejection as empty.
        """
        if self.profile != DEVELOPMENT_PROFILE:
            return RejectedSnapshot(diagnostics=(_PROFILE_NOT_DEVELOPMENT,))

        if self.source_mode == CORPORATE_SOURCE:
            return RejectedSnapshot(diagnostics=(_CORPORATE_SOURCE_DENIED,))

        return self.repository.inventory()


__all__ = [
    "CORPORATE_SOURCE",
    "DEVELOPMENT_PROFILE",
    "InventoryApprovedSources",
]
