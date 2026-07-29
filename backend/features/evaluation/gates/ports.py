"""Technical grounding safety gate outbound ports.

Gate-specific protocols so the domain and application stay framework-free and
are wired by adapters in later slices. Distinct from the harness ports in
``backend/features/evaluation/ports.py``: the gate owns its own report store
and critical-observation selector contracts.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from backend.features.evaluation.gates.domain import GateDecision, GateMetrics


@runtime_checkable
class GateReportStore(Protocol):
    """Publish allowlisted gate evidence atomically (later slice)."""

    def promote(self, run_id: str, payload: bytes) -> None: ...


@runtime_checkable
class CriticalObservationSelector(Protocol):
    """Select CaseResult observations for critical contract evaluation.

    The runner consumes harness ``CaseResult`` values through this port; it does
    NOT reproduce kernel or metric logic.
    """

    def select(self, case_id: str) -> Any: ...


@runtime_checkable
class GateClock(Protocol):
    """Deterministic time port for the gate (frozen in CI)."""

    def now(self) -> float: ...

    def elapsed_since_start(self) -> float: ...


# Re-export decision/metrics so callers import ports from one place.
_ = (GateDecision, GateMetrics)
