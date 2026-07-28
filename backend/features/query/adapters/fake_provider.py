"""Deterministic, in-memory generation adapter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from backend.shared.ports import GeneratedAnswer, GroundedPrompt, ProviderFailure

_FAILURE_ALIASES: Final[dict[str, str]] = {
    "timeout": "provider-timeout",
    "rate-limit": "provider-rate-limit",
    "rate_limit": "provider-rate-limit",
    "outage": "provider-outage",
}


def _typed_failure(failure: str | ProviderFailure | BaseException) -> ProviderFailure:
    if isinstance(failure, ProviderFailure):
        return failure
    if isinstance(failure, TimeoutError):
        return ProviderFailure("provider-timeout")
    if isinstance(failure, ConnectionError):
        return ProviderFailure("provider-outage")
    if isinstance(failure, BaseException):
        return ProviderFailure("provider-error")
    return ProviderFailure(_FAILURE_ALIASES.get(failure.casefold(), failure))


@dataclass(frozen=True, slots=True)
class FakeProvider:
    response: GeneratedAnswer | None = None
    failure: str | ProviderFailure | BaseException | None = None

    def generate(self, prompt: GroundedPrompt) -> GeneratedAnswer:
        if self.failure is not None:
            raise _typed_failure(self.failure)
        if self.response is not None:
            return self.response
        return GeneratedAnswer(
            internal_text="Deterministic fake grounded answer.",
            citation_ids=tuple(evidence.fragment_id for evidence in prompt.evidence),
        )
