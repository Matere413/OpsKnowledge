"""Indexing outbound ports.

Provider-neutral repository port implemented by outbound adapters. The port
returns a complete current snapshot or a whole-snapshot rejection; it never
returns a partial subset. Implementations MUST NOT depend on a provider and
MUST run only in the development profile against a manifest-controlled
synthetic fixture.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from backend.features.indexing.domain import (
    CompleteSnapshot,
    RejectedSnapshot,
)

# Union alias keeps the port signature readable and stable.
type InventoryResult = CompleteSnapshot | RejectedSnapshot


@runtime_checkable
class ApprovedSourceRepository(Protocol):
    """Outbound repository port for a complete approved source snapshot.

    Implementations return exactly one of:

    * :class:`CompleteSnapshot` — a complete, validated, stably ordered current
      inventory. An empty tuple is valid only after exact manifest coverage
      finishes without omission.
    * :class:`RejectedSnapshot` — a whole-snapshot rejection carrying only safe
      diagnostics. No partial valid subset is ever returned.

    The port is provider-neutral: a local development adapter and a future
    corporate adapter (after Phase 8 and TI gates) implement the same contract.
    The application layer invokes this port only after the profile and corporate
    gates have passed, so an implementation is never reached for a denied
    request.
    """

    def inventory(self) -> InventoryResult:
        """Return a complete current snapshot or a whole-snapshot rejection."""
        ...


__all__ = [
    "ApprovedSourceRepository",
    "InventoryResult",
]
