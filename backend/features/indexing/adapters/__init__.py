"""Indexing outbound adapters.

The local development adapter scans a manifest-controlled synthetic source
fixture kept strictly separate from ``evaluation-dataset/``. It returns only
immutable metadata for one complete current snapshot; it never parses,
interprets, persists, publishes, or synchronizes content, and it never calls a
provider. A future corporate adapter (after Phase 8 and TI gates) must
implement the same port in a separately approved change.
"""

from backend.features.indexing.adapters.local_repository import LocalApprovedSourceRepository

__all__ = [
    "LocalApprovedSourceRepository",
]
