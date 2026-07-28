"""Evaluation outbound ports.

Unit 1 owns the Clock protocol and adapters; the case-executor, validator, and
report-store protocols are declared here so the domain stays framework-free and
are wired by later chained units.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Clock(Protocol):
    """Deterministic time port.

    The harness derives run identity from ``now()`` and durations from
    ``elapsed_since_start()``. Frozen runs MUST NOT read the wall clock:
    ``FrozenClock`` returns the injected timestamp and a fixed duration.
    """

    def now(self) -> float: ...
    def elapsed_since_start(self) -> float: ...


@runtime_checkable
class DatasetValidator(Protocol):
    """Validate the manifest-controlled dataset before execution."""

    def validate(self, root: Path) -> list[Any]: ...


@runtime_checkable
class CaseExecutor(Protocol):
    """Resolve a single case through the in-process kernel (Unit 2)."""

    def execute(self, case: Any) -> Any: ...


@runtime_checkable
class ReportStore(Protocol):
    """Persist reviewed safe baselines under ``evaluation-runs/`` (Unit 3)."""

    def promote(self, run_id: str, payload: bytes) -> None: ...
