"""OpsKnowledge quality evaluation harness feature.

Dependency-free, development-only Phase 2 harness for the in-process grounded
query kernel. This unit owns the contracts, the reviewed ES/EN question
mapping, the dataset gate (validate before load), and the deterministic Clock.
The runner, metrics, reports, and CLI belong to later chained units and are
intentionally absent from this slice.
"""

from __future__ import annotations
