"""Clock adapters for the evaluation harness.

``SystemClock`` reads the real clock for production-style runs. ``FrozenClock``
returns an injected timestamp and fixed duration so repeated runs are
byte-identical without any wall-clock read. Both satisfy the Clock protocol.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from backend.features.evaluation.ports import Clock


@dataclass(frozen=True, slots=True)
class SystemClock(Clock):
    """Real wall-clock adapter (used only outside frozen runs)."""

    _start: float = 0.0

    def __post_init__(self) -> None:
        if not self._start:
            object.__setattr__(self, "_start", time.monotonic())

    def now(self) -> float:
        return time.time()

    def elapsed_since_start(self) -> float:
        return time.monotonic() - self._start


@dataclass(frozen=True, slots=True)
class FrozenClock(Clock):
    """Deterministic, wall-clock-free clock.

    Returns the injected timestamp and duration on every call so run identity
    and serialized output are byte-stable. ``duration_seconds`` is injected
    and monotonic: it never reads ``time.monotonic`` so two frozen runs cannot drift.
    """

    timestamp: float
    duration_seconds: float

    def now(self) -> float:
        return self.timestamp

    def elapsed_since_start(self) -> float:
        return self.duration_seconds
