"""Shared hexagonal ports and safe logging protocol.

This module defines the outbound ports the query feature (Work Unit 2) and CLI
(Work Unit 3) will depend on. Work Unit 1 lands the protocols themselves so the
corpus boundary and later slices share one contract surface.

Design invariants:

- No persistence interface is exposed here. The Phase 1 slice persists nothing:
  no question, answer, citation, provider payload, or model output is written
  to disk, a database, or a log. A future session/retention feature will
  introduce its own port under a separately reviewed SDD change.
- Logs are JSON and carry only safe fields. Content (question, answer,
  citation text, tokens, secrets, provider payloads) is NEVER logged. The
  :class:`SafeLogger` protocol and :func:`emit_safe_log` enforce this by
  accepting only the closed set of safe fields.
- ``Retrieve`` and ``Generate`` are outbound ports: the domain/application
  layers depend on the protocol, and a concrete adapter (e.g. an OpenAI
  provider or a deterministic fake) is injected at the boundary.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Any, Final, Protocol, TextIO, runtime_checkable

# Closed set of safe log fields. Anything outside this set is rejected so a
# caller cannot accidentally log question text, answer text, citation content,
# tokens, secrets, or provider payloads.
SAFE_LOG_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "timestamp",
        "profile",
        "outcome",
        "reason_code",
        "duration_ms",
        "attempt_count",
        "language",
        "operation",
        "provider_class",
        "version",
    }
)

# Controlled outcome taxonomy (canonical per the OpsKnowledge domain contract).
OUTCOMES: Final[frozenset[str]] = frozenset(
    {
        "supported",
        "insufficient_information",
        "contradictory_information",
        "out_of_scope",
        "unavailable",
        "session_expired",
    }
)


@dataclass(frozen=True, slots=True)
class PromptEvidence:
    """Immutable provider-boundary evidence record.

    ``content`` is intentionally available only inside the in-memory prompt
    boundary. It must never be copied to :class:`SafeResponse` or a log.
    """

    fragment_id: str
    content: str


@dataclass(frozen=True, slots=True)
class GroundedPrompt:
    """Immutable prompt containing only a question, rules, and approved evidence."""

    question: str
    language: str
    evidence: tuple[PromptEvidence, ...]
    rules: tuple[str, ...] = ()


class ProviderFailure(Exception):
    """Typed, content-free failure raised by a generation provider."""

    __slots__ = ("reason_code",)

    reason_code: str

    def __init__(self, reason_code: str) -> None:
        self.reason_code = reason_code
        super().__init__(reason_code)


@dataclass(frozen=True, slots=True)
class GeneratedAnswer:
    """Provider-internal answer representation.

    Carries internal text the application layer uses for citation validation
    only. This text MUST NEVER reach CLI output or logs: the safe response
    surface omits answer text by design. ``citation_ids`` are fragment
    identifiers the model claims to cite.
    """

    internal_text: str
    citation_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SafeResponse:
    """Safe CLI response surface.

    Carries only the spec's safe fields: ``outcome``, fragment-ID citations,
    escalation guidance, profile, and reason code. No answer text, no question
    text, no citation content, no tokens.
    """

    outcome: str
    citations: tuple[str, ...]
    escalation: str
    profile: str
    reason_code: str


@runtime_checkable
class Retrieve(Protocol):
    """Outbound retrieval port.

    Implementations return only approved, language-matched fragments for the
    given query. Retrieval MUST be deterministic: same input, profile, and
    corpus revision produce the same evidence set. Implementations MUST filter
    by the query language before any evidence reaches the model.
    """

    def retrieve(
        self,
        question: str,
        language: str,
        profile: str,
    ) -> tuple[Any, ...]:
        """Return a tuple of approved, language-matched fragments.

        Args:
            question: The free-text question (never logged by implementations).
            language: The detected query language tag.
            profile: The active runtime profile.

        Returns:
            A tuple of fragments (the corpus feature's ``Fragment`` type) whose
            language matches ``language`` and whose approval/classification/
            profile satisfy the boundary.
        """
        ...


@runtime_checkable
class Generate(Protocol):
    """Outbound generation port.

    Implementations call a generation provider. Timeout, rate limit, outage, or
    any non-success response MUST resolve the query to ``unavailable`` with a
    human-expert recommendation, make no further provider call, and persist no
    answer. The capability SHALL NOT fabricate citations, fragments, or
    outcomes to recover from a failure. Only one bounded attempt is permitted.
    """

    def generate(self, prompt: GroundedPrompt) -> GeneratedAnswer:
        """Generate an internal answer with citation IDs.

        Args:
            prompt: Immutable question, language, and selected evidence.

        Returns:
            A :class:`GeneratedAnswer` carrying internal text and citation IDs.
        """
        ...


@runtime_checkable
class SafeLogger(Protocol):
    """Safe JSON logging protocol.

    Implementations emit one JSON object per event containing only safe fields.
    Content (question, answer, citation text, tokens, secrets, provider
    payloads) is NEVER logged. The :func:`emit_safe_log` helper enforces the
    closed safe-field set.
    """

    def log(self, event: dict[str, Any]) -> None:
        """Emit a safe JSON log event.

        Args:
            event: A dict whose keys MUST be a subset of :data:`SAFE_LOG_FIELDS`.

        Raises:
            ValueError: if any key is outside the safe-field set.
        """
        ...


def emit_safe_log(
    event: dict[str, Any],
    *,
    stream: TextIO | None = None,
) -> None:
    """Emit a single safe JSON log line to ``stream`` (defaults to stderr).

    Validates that every key is in :data:`SAFE_LOG_FIELDS` so content can never
    be logged through this helper. The payload is serialized as compact JSON
    with a trailing newline. Values are not introspected for content here; the
    closed key set is the safety boundary (callers only ever pass safe fields).
    """
    unsafe = set(event) - SAFE_LOG_FIELDS
    if unsafe:
        raise ValueError(f"unsafe log fields rejected: {sorted(unsafe)}")
    target = stream if stream is not None else sys.stderr
    encoded = json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    target.write(encoded + "\n")
    target.flush()


def is_safe_log_event(event: dict[str, Any]) -> bool:
    """Return True when every key in ``event`` is a safe log field."""
    return set(event).issubset(SAFE_LOG_FIELDS)
