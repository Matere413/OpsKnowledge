"""Contract and identity tests for the approved source inventory.

Work Unit 1 (PR 1) proves the provider-neutral contracts:

* Immutable metadata-only output (Spec R1 / Scenario: Metadata-only result).
* Independent Spanish/English identities without cross-language revision
  comparison (Spec R3 / Scenario: Bilingual revisions remain distinct).
* Denial before port invocation (Spec R8 / Scenario: Corporate access is denied).

Adapter, fixture, scanner behavior, and architecture tests belong to later
work units and are intentionally not covered here.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, is_dataclass
from typing import Any, cast, get_type_hints

import pytest

from backend.features.indexing.application import (
    CORPORATE_SOURCE,
    DEVELOPMENT_PROFILE,
    InventoryApprovedSources,
)
from backend.features.indexing.domain import (
    ALLOWED_LANGUAGES,
    Collection,
    CompleteSnapshot,
    Diagnostic,
    EntryId,
    Language,
    RejectedSnapshot,
    Revision,
    SourceArtifact,
    SourceIdentity,
)
from backend.features.indexing.ports import ApprovedSourceRepository


class _RecordingRepository:
    """Fake repository recording whether it was invoked (no adapter behavior)."""

    def __init__(self, result: object) -> None:
        self._result = result
        self.invoked = False

    def inventory(self) -> object:
        self.invoked = True
        return self._result


def _identity(entry: str, language: str, revision: str) -> SourceIdentity:
    return SourceIdentity(
        collection=Collection(value="runbooks"),
        entry=EntryId(value=entry),
        language=Language(value=language),
        revision=Revision(value=revision),
    )


def _artifact(entry: str, language: str, revision: str) -> SourceArtifact:
    from backend.features.indexing.domain import (
        Approval,
        Classification,
        RepositoryRelativePath,
        Sha256,
    )

    suffix = "ESP" if language == "es" else "EN"
    return SourceArtifact(
        path=RepositoryRelativePath(value=f"runbooks/runbook-1_{suffix}_REV_{revision}.pdf"),
        identity=_identity(entry, language, revision),
        approval=Approval(value="approved"),
        classification=Classification(value="synthetic"),
        sha256=Sha256(value="0" * 64),
    )


# R1 / Scenario: Metadata-only result — immutable, metadata-only value objects.

_DOMAIN_VALUE_TYPES = [
    "RepositoryRelativePath",
    "Collection",
    "EntryId",
    "Language",
    "Revision",
    "Approval",
    "Classification",
    "Sha256",
    "SourceIdentity",
    "SourceArtifact",
    "CompleteSnapshot",
    "RejectedSnapshot",
    "Diagnostic",
]


@pytest.mark.parametrize("type_name", _DOMAIN_VALUE_TYPES)
def test_domain_value_objects_are_frozen_slot_dataclasses(type_name: str) -> None:
    """Every domain value object is a frozen, slot-based dataclass (R1)."""
    import backend.features.indexing.domain as domain

    cls: Any = getattr(domain, type_name)
    # Read __slots__ while cls is Any; is_dataclass() narrows away from Any.
    slots: tuple[str, ...] = cls.__slots__
    assert is_dataclass(cls), f"{type_name} is not a dataclass"
    assert slots, f"{type_name} is not slot-based"
    ctor: Any = cls
    instance = ctor(**{s: _value_for_slot(s) for s in slots})
    try:
        setattr(instance, slots[0], _value_for_slot(slots[0]))
    except FrozenInstanceError:
        pass
    else:
        raise AssertionError(f"{type_name} is not frozen")


def _value_for_slot(slot: str) -> object:
    import backend.features.indexing.domain as domain

    simple = {"value": "x", "code": "unsafe-path", "reference": "r/x"}
    if slot in simple:
        return simple[slot]
    return {
        "artifacts": (),
        "diagnostics": (),
        "identity": _identity("e", "es", "1"),
        "path": domain.RepositoryRelativePath(value="r/x"),
        "approval": domain.Approval(value="approved"),
        "classification": domain.Classification(value="synthetic"),
        "sha256": domain.Sha256(value="0" * 64),
        "collection": domain.Collection(value="runbooks"),
        "entry": domain.EntryId(value="e"),
        "language": domain.Language(value="es"),
        "revision": domain.Revision(value="1"),
    }[slot]


def test_source_artifact_exposes_only_metadata_fields() -> None:
    """SourceArtifact carries metadata only — no content, bytes, or absolute path."""
    hints = get_type_hints(type(_artifact("runbook-1", "es", "2")))
    assert set(hints) == {"path", "identity", "approval", "classification", "sha256"}
    forbidden = {"content", "bytes", "text", "absolute_path", "secret", "token", "payload"}
    assert not (forbidden & set(hints))


def test_rejected_snapshot_exposes_only_safe_diagnostics() -> None:
    """RejectedSnapshot carries only safe Diagnostic tuples (R1, R6)."""
    diag = Diagnostic(code="unsafe-path", reference="runbooks/evil.pdf")
    rejected = RejectedSnapshot(diagnostics=(diag,))
    assert set(get_type_hints(type(rejected))) == {"diagnostics"}
    assert set(get_type_hints(type(diag))) == {"code", "reference"}
    assert rejected.diagnostics == (diag,)


def test_complete_snapshot_empty_is_valid() -> None:
    """A completed zero-artifact scan yields a valid empty immutable snapshot."""
    snapshot = CompleteSnapshot(artifacts=())
    assert set(get_type_hints(type(snapshot))) == {"artifacts"}
    assert snapshot.artifacts == ()


# R3 / Scenario: Bilingual revisions remain distinct — independent identities.


def test_spanish_and_english_revisions_are_distinct_identities() -> None:
    """``runbook-1_ESP_REV_2`` and ``runbook-1_EN_REV_7`` are distinct identities.

    Identity includes language, so the two revisions are independent and are
    never compared across languages (Spec R3 / Scenario: Bilingual revisions
    remain distinct).
    """
    spanish = _identity("runbook-1", "es", "2")
    english = _identity("runbook-1", "en", "7")
    assert spanish != english
    assert hash(spanish) != hash(english)


def test_same_entry_same_language_same_revision_are_equal() -> None:
    """Two artifacts with identical identity components are the same identity."""
    a = _identity("runbook-1", "es", "2")
    b = _identity("runbook-1", "es", "2")
    assert a == b
    assert hash(a) == hash(b)


def test_same_revision_token_es_vs_en_remain_distinct() -> None:
    """Even with the same revision token, ES and EN identities are distinct.

    Guards against any cross-language revision comparison: revision ``2`` in
    Spanish and revision ``2`` in English are different identities.
    """
    assert _identity("runbook-1", "es", "2") != _identity("runbook-1", "en", "2")


def test_distinct_revisions_within_same_language_are_distinct() -> None:
    """Within one language, different revisions are distinct identities."""
    assert _identity("runbook-1", "es", "2") != _identity("runbook-1", "es", "7")


def test_complete_snapshot_can_hold_both_bilingual_artifacts() -> None:
    """A complete snapshot can carry both ES and EN artifacts independently."""
    snapshot = CompleteSnapshot(
        artifacts=(_artifact("runbook-1", "es", "2"), _artifact("runbook-1", "en", "7"))
    )
    identities = [a.identity for a in snapshot.artifacts]
    assert len(identities) == 2
    assert len(set(identities)) == 2


# R8 / Scenario: Corporate access is denied — denial before port invocation.


def _use_case(repo: object, profile: str, source_mode: str) -> InventoryApprovedSources:
    return InventoryApprovedSources(
        repository=cast(ApprovedSourceRepository, repo),
        profile=profile,
        source_mode=source_mode,
    )


def test_non_development_profile_denies_before_port_invocation() -> None:
    """A non-development profile is rejected without invoking the repository."""
    repo = _RecordingRepository(CompleteSnapshot(artifacts=()))
    result = _use_case(repo, "production", "local").inventory()
    assert isinstance(result, RejectedSnapshot)
    assert repo.invoked is False
    assert result.diagnostics[0].code == "profile-not-development"


def test_corporate_source_mode_denies_before_port_invocation() -> None:
    """Corporate source mode is rejected without invoking the repository."""
    repo = _RecordingRepository(CompleteSnapshot(artifacts=()))
    result = _use_case(repo, DEVELOPMENT_PROFILE, CORPORATE_SOURCE).inventory()
    assert isinstance(result, RejectedSnapshot)
    assert repo.invoked is False
    assert result.diagnostics[0].code == "corporate-source-denied"


def test_development_local_profile_invokes_the_port() -> None:
    """A permitted development/local request reaches the port and returns its result."""
    canned = CompleteSnapshot(artifacts=(_artifact("runbook-1", "es", "2"),))
    repo = _RecordingRepository(canned)
    result = _use_case(repo, DEVELOPMENT_PROFILE, "local").inventory()
    assert repo.invoked is True
    assert result is canned


def test_profile_denial_takes_precedence_over_corporate_mode() -> None:
    """Profile denial fires first; corporate mode is not reached (fail-closed)."""
    repo = _RecordingRepository(CompleteSnapshot(artifacts=()))
    result = _use_case(repo, "production", CORPORATE_SOURCE).inventory()
    assert isinstance(result, RejectedSnapshot)
    assert repo.invoked is False
    assert result.diagnostics[0].code == "profile-not-development"


def test_approved_source_repository_is_a_runtime_checkable_protocol() -> None:
    """The repository port is a runtime-checkable, provider-neutral Protocol."""
    assert hasattr(ApprovedSourceRepository, "_is_protocol")
    assert isinstance(
        _RecordingRepository(CompleteSnapshot(artifacts=())), ApprovedSourceRepository
    )


def test_allowed_languages_are_exactly_es_and_en() -> None:
    """The controlled language vocabulary is exactly Spanish and English."""
    assert frozenset({"es", "en"}) == ALLOWED_LANGUAGES
