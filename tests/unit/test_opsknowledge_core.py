"""OpsKnowledge core unit tests.

Covers the corpus boundary (Work Unit 1 / PR 1):

- Profile denial outside ``development``.
- Non-synthetic / unapproved manifest records fail closed.
- Invalid parents (fragment -> entry) fail closed.
- Mixed languages (fragment language != parent entry language) fail closed.
- Unlisted paths (payload file absent from manifest) fail closed.
- Safe fail-closed diagnostics: only safe reason codes are surfaced, no
  fragment content reaches the caller, and retrieval is never exposed.

The query, provider, and CLI behaviors are intentionally NOT exercised here;
they arrive in later slices (Work Units 2 and 3).
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

from backend.features.corpus.adapters.manifest_loader import (
    CorpusLoadError,
    load_corpus,
)
from backend.features.corpus.domain import Fragment
from backend.shared.ports import (
    OUTCOMES,
    SAFE_LOG_FIELDS,
    SafeResponse,
    emit_safe_log,
    is_safe_log_event,
)

# ---------------------------------------------------------------------------
# Manifest / payload builders for self-contained temporary corpora.
# ---------------------------------------------------------------------------
# Each builder writes canonical JSON (sorted keys, single trailing LF) so the
# loader's hash and shape checks mirror the real evaluation-dataset contract.
# Content hashes are recomputed from the written content; tests never hardcode
# hashes so mutating a payload automatically keeps hashes consistent.


def _canonical_write(path: Path, payload: object) -> None:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    path.write_text(encoded + "\n", encoding="utf-8")


def _content_sha256(content: str) -> str:
    import hashlib

    return hashlib.sha256(content.encode("utf-8")).hexdigest()


_ExcType = type[BaseException] | tuple[type[BaseException], ...]


def _expect_raises(exc_type: _ExcType, callable_: Callable[[], object], /) -> BaseException:
    """Assert ``callable_`` raises ``exc_type`` and return the caught instance.

    The focused-test policy forbids ``pytest.raises``; this helper uses a plain
    try/except so the test file stays policy-clean while still asserting the
    exception type and giving callers access to the caught instance.

    Callers that need typed access to attributes cast via ``assert isinstance``.
    """
    try:
        callable_()
    except exc_type as caught:  # type: ignore[misc]
        return caught
    raise AssertionError(f"expected {exc_type} was not raised")


def _expect_corpus_error(callable_: Callable[[], object], /) -> CorpusLoadError:
    """Assert ``callable_`` raises ``CorpusLoadError`` and return it typed."""
    caught = _expect_raises(CorpusLoadError, callable_)
    assert isinstance(caught, CorpusLoadError)
    return caught


def _artifact(
    path: str, kind: str, identifier: str, sha256: str, revision: str | None = None
) -> dict:
    entry: dict = {"id": identifier, "kind": kind, "path": path, "sha256": sha256}
    if revision is not None:
        entry["revision"] = revision
    return entry


def _manifest_sha256(payload: dict) -> str:
    """Stable manifest hash mirroring the CI validator self-reference rule.

    The manifest is self-referential: its own sha256 changes its canonical
    bytes. The stable hash is computed over canonical bytes with the manifest
    artifact entry's sha256 set to the empty string.
    """
    import copy
    import hashlib

    shadow = copy.deepcopy(payload)
    for artifact in shadow.get("artifacts", []):
        if isinstance(artifact, dict) and artifact.get("kind") == "manifest":
            artifact["sha256"] = ""
            break
    encoded = json.dumps(shadow, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256((encoded + "\n").encode("utf-8")).hexdigest()


def _write_entry(
    root: Path,
    rel: str,
    *,
    identifier: str,
    logical_entry_id: str,
    revision: str,
    collection: str,
    language: str,
    approval: str = "approved",
    classification: str = "synthetic",
    profile: str = "development",
    content: str = "synthetic entry content for example.test.",
) -> str:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "id": identifier,
        "logical_entry_id": logical_entry_id,
        "revision": revision,
        "collection": collection,
        "language": language,
        "approval": approval,
        "classification": classification,
        "profile": profile,
        "content": content,
        "content_sha256": _content_sha256(content),
    }
    _canonical_write(path, payload)
    return _content_sha256_of_file(path)


def _content_sha256_of_file(path: Path) -> str:
    import hashlib

    raw = path.read_bytes()
    # canonical bytes = sorted-key JSON + trailing LF (what the loader checks)
    payload = json.loads(raw.decode("utf-8"))
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256((encoded + "\n").encode("utf-8")).hexdigest()


def _write_fragment(
    root: Path,
    rel: str,
    *,
    identifier: str,
    entry_id: str,
    language: str,
    provenance: str = "original",
    approval: str = "approved",
    classification: str = "synthetic",
    profile: str = "development",
    content: str = "synthetic fragment content for example.test.",
    source_reference: str = "",
    quality: str = "",
    fictitious: bool | None = None,
) -> str:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict = {
        "id": identifier,
        "entry_id": entry_id,
        "language": language,
        "provenance": provenance,
        "source_reference": source_reference,
        "quality": quality,
        "approval": approval,
        "classification": classification,
        "profile": profile,
        "content": content,
        "content_sha256": _content_sha256(content),
    }
    if fictitious is not None:
        payload["fictitious"] = fictitious
    _canonical_write(path, payload)
    return _content_sha256_of_file(path)


def _build_manifest(
    root: Path,
    *,
    profile: str = "development",
    approval: str = "approved",
    classification: str = "synthetic",
    artifacts: list[dict],
) -> Path:
    manifest_path = root / "manifest.json"
    payload = {
        "schema_version": "1",
        "dataset_id": "opsknowledge-evaluation-dataset",
        "profile": profile,
        "approval": approval,
        "classification": classification,
        "artifacts": artifacts,
    }
    manifest_sha = _manifest_sha256(payload)
    # Replace the manifest self-entry sha256 with the stable hash.
    for artifact in artifacts:
        if artifact.get("kind") == "manifest":
            artifact["sha256"] = manifest_sha
            break
    payload["artifacts"] = artifacts
    # Recompute because we may have changed a sha256 field above.
    final_sha = _manifest_sha256(payload)
    for artifact in artifacts:
        if artifact.get("kind") == "manifest":
            artifact["sha256"] = final_sha
            break
    _canonical_write(manifest_path, payload)
    return manifest_path


def _valid_corpus(root: Path) -> Path:
    """Build a minimal valid development/synthetic/approved corpus under root."""
    entry_sha = _write_entry(
        root,
        "entries/runbook-001.rev.1.json",
        identifier="entry.runbook-001.rev.1",
        logical_entry_id="runbook-001",
        revision="1",
        collection="runbooks",
        language="es",
    )
    frag_sha = _write_fragment(
        root,
        "fragments/runbook-001.rev.1.es.original.json",
        identifier="fragment.runbook-001.rev.1.es.original",
        entry_id="entry.runbook-001.rev.1",
        language="es",
    )
    artifacts = [
        _artifact("manifest.json", "manifest", "manifest", "placeholder"),
        _artifact(
            "entries/runbook-001.rev.1.json",
            "entry",
            "entry.runbook-001.rev.1",
            entry_sha,
            revision="1",
        ),
        _artifact(
            "fragments/runbook-001.rev.1.es.original.json",
            "fragment",
            "fragment.runbook-001.rev.1.es.original",
            frag_sha,
        ),
    ]
    return _build_manifest(root, artifacts=artifacts)


# ---------------------------------------------------------------------------
# Happy path: development corpus loads immutable fragments.
# ---------------------------------------------------------------------------


def test_load_corpus_returns_immutable_fragments(tmp_path: Path) -> None:
    manifest = _valid_corpus(tmp_path)
    corpus = load_corpus(manifest, profile="development")

    fragments = corpus.fragments
    assert len(fragments) == 1
    fragment = fragments[0]
    assert isinstance(fragment, Fragment)
    assert fragment.identifier == "fragment.runbook-001.rev.1.es.original"
    assert fragment.entry_id == "entry.runbook-001.rev.1"
    assert fragment.language == "es"
    assert fragment.provenance == "original"
    assert fragment.approval == "approved"
    assert fragment.classification == "synthetic"
    assert fragment.profile == "development"
    # Content is available to the application layer but never on safe logs.
    assert fragment.content == "synthetic fragment content for example.test."

    # Immutability: mutating the returned tuple or a fragment must not be possible.
    _expect_raises(
        (AttributeError, TypeError),
        lambda: setattr(fragment, "content", "tampered"),
    )


def test_load_corpus_deterministic_order(tmp_path: Path) -> None:
    # Add a second entry+fragment to confirm stable identifier ordering.
    e1_sha = _write_entry(
        tmp_path,
        "entries/zzz.rev.1.json",
        identifier="entry.zzz.rev.1",
        logical_entry_id="zzz",
        revision="1",
        collection="adrs",
        language="en",
    )
    e2_sha = _write_entry(
        tmp_path,
        "entries/aaa.rev.1.json",
        identifier="entry.aaa.rev.1",
        logical_entry_id="aaa",
        revision="1",
        collection="adrs",
        language="en",
    )
    f1_sha = _write_fragment(
        tmp_path,
        "fragments/zzz.rev.1.en.original.json",
        identifier="fragment.zzz.rev.1.en.original",
        entry_id="entry.zzz.rev.1",
        language="en",
    )
    f2_sha = _write_fragment(
        tmp_path,
        "fragments/aaa.rev.1.en.original.json",
        identifier="fragment.aaa.rev.1.en.original",
        entry_id="entry.aaa.rev.1",
        language="en",
    )
    artifacts = [
        _artifact("manifest.json", "manifest", "manifest", "placeholder"),
        _artifact("entries/zzz.rev.1.json", "entry", "entry.zzz.rev.1", e1_sha, revision="1"),
        _artifact("entries/aaa.rev.1.json", "entry", "entry.aaa.rev.1", e2_sha, revision="1"),
        _artifact(
            "fragments/zzz.rev.1.en.original.json",
            "fragment",
            "fragment.zzz.rev.1.en.original",
            f1_sha,
        ),
        _artifact(
            "fragments/aaa.rev.1.en.original.json",
            "fragment",
            "fragment.aaa.rev.1.en.original",
            f2_sha,
        ),
    ]
    manifest = _build_manifest(tmp_path, artifacts=artifacts)

    corpus_a = load_corpus(manifest, profile="development")
    corpus_b = load_corpus(manifest, profile="development")
    ids_a = [f.identifier for f in corpus_a.fragments]
    ids_b = [f.identifier for f in corpus_b.fragments]
    assert ids_a == ids_b
    # Stable ascending identifier ordering (deterministic retrieval precondition).
    assert ids_a == sorted(ids_a)


# ---------------------------------------------------------------------------
# Profile boundary: non-development profile fails closed at startup.
# ---------------------------------------------------------------------------


def test_load_corpus_rejects_non_development_profile(tmp_path: Path) -> None:
    manifest = _valid_corpus(tmp_path)
    exc = _expect_corpus_error(lambda: load_corpus(manifest, profile="production"))
    reason = exc.reason_code
    assert reason == "profile-not-development"
    # Safe diagnostic: no fragment content surfaces in the error.
    assert "synthetic fragment content" not in str(exc)


def test_load_corpus_rejects_manifest_declaring_non_development_profile(tmp_path: Path) -> None:
    # Manifest itself declares a non-development profile: fail closed.
    entry_sha = _write_entry(
        tmp_path,
        "entries/runbook-001.rev.1.json",
        identifier="entry.runbook-001.rev.1",
        logical_entry_id="runbook-001",
        revision="1",
        collection="runbooks",
        language="es",
        profile="production",
    )
    frag_sha = _write_fragment(
        tmp_path,
        "fragments/runbook-001.rev.1.es.original.json",
        identifier="fragment.runbook-001.rev.1.es.original",
        entry_id="entry.runbook-001.rev.1",
        language="es",
        profile="production",
    )
    artifacts = [
        _artifact("manifest.json", "manifest", "manifest", "placeholder"),
        _artifact(
            "entries/runbook-001.rev.1.json",
            "entry",
            "entry.runbook-001.rev.1",
            entry_sha,
            revision="1",
        ),
        _artifact(
            "fragments/runbook-001.rev.1.es.original.json",
            "fragment",
            "fragment.runbook-001.rev.1.es.original",
            frag_sha,
        ),
    ]
    manifest = _build_manifest(tmp_path, profile="production", artifacts=artifacts)
    exc = _expect_corpus_error(lambda: load_corpus(manifest, profile="development"))
    assert exc.reason_code == "manifest-profile-not-development"


# ---------------------------------------------------------------------------
# Non-synthetic / unapproved records fail closed.
# ---------------------------------------------------------------------------


def test_load_corpus_rejects_non_synthetic_entry(tmp_path: Path) -> None:
    entry_sha = _write_entry(
        tmp_path,
        "entries/runbook-001.rev.1.json",
        identifier="entry.runbook-001.rev.1",
        logical_entry_id="runbook-001",
        revision="1",
        collection="runbooks",
        language="es",
        classification="corporate",
    )
    frag_sha = _write_fragment(
        tmp_path,
        "fragments/runbook-001.rev.1.es.original.json",
        identifier="fragment.runbook-001.rev.1.es.original",
        entry_id="entry.runbook-001.rev.1",
        language="es",
    )
    artifacts = [
        _artifact("manifest.json", "manifest", "manifest", "placeholder"),
        _artifact(
            "entries/runbook-001.rev.1.json",
            "entry",
            "entry.runbook-001.rev.1",
            entry_sha,
            revision="1",
        ),
        _artifact(
            "fragments/runbook-001.rev.1.es.original.json",
            "fragment",
            "fragment.runbook-001.rev.1.es.original",
            frag_sha,
        ),
    ]
    manifest = _build_manifest(tmp_path, classification="synthetic", artifacts=artifacts)
    exc = _expect_corpus_error(lambda: load_corpus(manifest, profile="development"))
    assert exc.reason_code == "entry-classification-not-synthetic"


def test_load_corpus_rejects_unapproved_entry(tmp_path: Path) -> None:
    entry_sha = _write_entry(
        tmp_path,
        "entries/runbook-001.rev.1.json",
        identifier="entry.runbook-001.rev.1",
        logical_entry_id="runbook-001",
        revision="1",
        collection="runbooks",
        language="es",
        approval="pending",
    )
    frag_sha = _write_fragment(
        tmp_path,
        "fragments/runbook-001.rev.1.es.original.json",
        identifier="fragment.runbook-001.rev.1.es.original",
        entry_id="entry.runbook-001.rev.1",
        language="es",
    )
    artifacts = [
        _artifact("manifest.json", "manifest", "manifest", "placeholder"),
        _artifact(
            "entries/runbook-001.rev.1.json",
            "entry",
            "entry.runbook-001.rev.1",
            entry_sha,
            revision="1",
        ),
        _artifact(
            "fragments/runbook-001.rev.1.es.original.json",
            "fragment",
            "fragment.runbook-001.rev.1.es.original",
            frag_sha,
        ),
    ]
    manifest = _build_manifest(tmp_path, artifacts=artifacts)
    exc = _expect_corpus_error(lambda: load_corpus(manifest, profile="development"))
    assert exc.reason_code == "entry-approval-not-approved"


def test_load_corpus_rejects_non_synthetic_fragment(tmp_path: Path) -> None:
    entry_sha = _write_entry(
        tmp_path,
        "entries/runbook-001.rev.1.json",
        identifier="entry.runbook-001.rev.1",
        logical_entry_id="runbook-001",
        revision="1",
        collection="runbooks",
        language="es",
    )
    frag_sha = _write_fragment(
        tmp_path,
        "fragments/runbook-001.rev.1.es.original.json",
        identifier="fragment.runbook-001.rev.1.es.original",
        entry_id="entry.runbook-001.rev.1",
        language="es",
        classification="corporate",
    )
    artifacts = [
        _artifact("manifest.json", "manifest", "manifest", "placeholder"),
        _artifact(
            "entries/runbook-001.rev.1.json",
            "entry",
            "entry.runbook-001.rev.1",
            entry_sha,
            revision="1",
        ),
        _artifact(
            "fragments/runbook-001.rev.1.es.original.json",
            "fragment",
            "fragment.runbook-001.rev.1.es.original",
            frag_sha,
        ),
    ]
    manifest = _build_manifest(tmp_path, artifacts=artifacts)
    exc = _expect_corpus_error(lambda: load_corpus(manifest, profile="development"))
    assert exc.reason_code == "fragment-classification-not-synthetic"


def test_load_corpus_rejects_unapproved_fragment(tmp_path: Path) -> None:
    entry_sha = _write_entry(
        tmp_path,
        "entries/runbook-001.rev.1.json",
        identifier="entry.runbook-001.rev.1",
        logical_entry_id="runbook-001",
        revision="1",
        collection="runbooks",
        language="es",
    )
    frag_sha = _write_fragment(
        tmp_path,
        "fragments/runbook-001.rev.1.es.original.json",
        identifier="fragment.runbook-001.rev.1.es.original",
        entry_id="entry.runbook-001.rev.1",
        language="es",
        approval="pending",
    )
    artifacts = [
        _artifact("manifest.json", "manifest", "manifest", "placeholder"),
        _artifact(
            "entries/runbook-001.rev.1.json",
            "entry",
            "entry.runbook-001.rev.1",
            entry_sha,
            revision="1",
        ),
        _artifact(
            "fragments/runbook-001.rev.1.es.original.json",
            "fragment",
            "fragment.runbook-001.rev.1.es.original",
            frag_sha,
        ),
    ]
    manifest = _build_manifest(tmp_path, artifacts=artifacts)
    exc = _expect_corpus_error(lambda: load_corpus(manifest, profile="development"))
    assert exc.reason_code == "fragment-approval-not-approved"


# ---------------------------------------------------------------------------
# Invalid parents: fragment references a missing/unapproved entry.
# ---------------------------------------------------------------------------


def test_load_corpus_rejects_fragment_with_missing_parent(tmp_path: Path) -> None:
    # Fragment exists and is listed, but its entry_id points to no loaded entry.
    frag_sha = _write_fragment(
        tmp_path,
        "fragments/orphan.rev.1.es.original.json",
        identifier="fragment.orphan.rev.1.es.original",
        entry_id="entry.does-not-exist.rev.1",
        language="es",
    )
    artifacts = [
        _artifact("manifest.json", "manifest", "manifest", "placeholder"),
        _artifact(
            "fragments/orphan.rev.1.es.original.json",
            "fragment",
            "fragment.orphan.rev.1.es.original",
            frag_sha,
        ),
    ]
    manifest = _build_manifest(tmp_path, artifacts=artifacts)
    exc = _expect_corpus_error(lambda: load_corpus(manifest, profile="development"))
    assert exc.reason_code == "fragment-parent-missing"


def test_load_corpus_rejects_fragment_whose_parent_is_not_listed(tmp_path: Path) -> None:
    # Entry file exists on disk but is NOT listed in the manifest; the fragment
    # references it. The entry never loads, so the parent is missing.
    _write_entry(
        tmp_path,
        "entries/unlisted.rev.1.json",
        identifier="entry.unlisted.rev.1",
        logical_entry_id="unlisted",
        revision="1",
        collection="runbooks",
        language="es",
    )
    frag_sha = _write_fragment(
        tmp_path,
        "fragments/unlisted.rev.1.es.original.json",
        identifier="fragment.unlisted.rev.1.es.original",
        entry_id="entry.unlisted.rev.1",
        language="es",
    )
    artifacts = [
        _artifact("manifest.json", "manifest", "manifest", "placeholder"),
        _artifact(
            "fragments/unlisted.rev.1.es.original.json",
            "fragment",
            "fragment.unlisted.rev.1.es.original",
            frag_sha,
        ),
    ]
    manifest = _build_manifest(tmp_path, artifacts=artifacts)
    exc = _expect_corpus_error(lambda: load_corpus(manifest, profile="development"))
    assert exc.reason_code == "fragment-parent-missing"


# ---------------------------------------------------------------------------
# Mixed languages: fragment language must match parent entry language.
# ---------------------------------------------------------------------------


def test_load_corpus_rejects_fragment_language_mismatch_with_parent(tmp_path: Path) -> None:
    entry_sha = _write_entry(
        tmp_path,
        "entries/runbook-001.rev.1.json",
        identifier="entry.runbook-001.rev.1",
        logical_entry_id="runbook-001",
        revision="1",
        collection="runbooks",
        language="es",
    )
    frag_sha = _write_fragment(
        tmp_path,
        "fragments/runbook-001.rev.1.en.original.json",
        identifier="fragment.runbook-001.rev.1.en.original",
        entry_id="entry.runbook-001.rev.1",
        language="en",  # mismatches the es parent
    )
    artifacts = [
        _artifact("manifest.json", "manifest", "manifest", "placeholder"),
        _artifact(
            "entries/runbook-001.rev.1.json",
            "entry",
            "entry.runbook-001.rev.1",
            entry_sha,
            revision="1",
        ),
        _artifact(
            "fragments/runbook-001.rev.1.en.original.json",
            "fragment",
            "fragment.runbook-001.rev.1.en.original",
            frag_sha,
        ),
    ]
    manifest = _build_manifest(tmp_path, artifacts=artifacts)
    exc = _expect_corpus_error(lambda: load_corpus(manifest, profile="development"))
    assert exc.reason_code == "fragment-language-mismatch"


# ---------------------------------------------------------------------------
# Unlisted paths: a payload file present on disk but absent from the manifest.
# ---------------------------------------------------------------------------


def test_load_corpus_rejects_unlisted_payload_file(tmp_path: Path) -> None:
    # Valid manifest + valid listed corpus, plus an extra unlisted entry file.
    manifest = _valid_corpus(tmp_path)
    _write_entry(
        tmp_path,
        "entries/extra.rev.1.json",
        identifier="entry.extra.rev.1",
        logical_entry_id="extra",
        revision="1",
        collection="runbooks",
        language="es",
    )
    exc = _expect_corpus_error(lambda: load_corpus(manifest, profile="development"))
    assert exc.reason_code == "payload-not-in-manifest"


def test_load_corpus_rejects_unlisted_fragment_file(tmp_path: Path) -> None:
    manifest = _valid_corpus(tmp_path)
    _write_fragment(
        tmp_path,
        "fragments/extra.rev.1.es.original.json",
        identifier="fragment.extra.rev.1.es.original",
        entry_id="entry.runbook-001.rev.1",
        language="es",
    )
    exc = _expect_corpus_error(lambda: load_corpus(manifest, profile="development"))
    assert exc.reason_code == "payload-not-in-manifest"


# ---------------------------------------------------------------------------
# Safe fail-closed diagnostics: no content leakage, no retrieval exposure.
# ---------------------------------------------------------------------------


def test_corpus_load_error_never_leaks_content(tmp_path: Path) -> None:
    # Craft a non-synthetic entry whose content is a recognizable canary.
    canary = "CANARY-SECRET-FRAGMENT-CONTENT-XYZ"
    entry_sha = _write_entry(
        tmp_path,
        "entries/runbook-001.rev.1.json",
        identifier="entry.runbook-001.rev.1",
        logical_entry_id="runbook-001",
        revision="1",
        collection="runbooks",
        language="es",
        classification="corporate",
        content=canary,
    )
    frag_sha = _write_fragment(
        tmp_path,
        "fragments/runbook-001.rev.1.es.original.json",
        identifier="fragment.runbook-001.rev.1.es.original",
        entry_id="entry.runbook-001.rev.1",
        language="es",
        content=canary,
    )
    artifacts = [
        _artifact("manifest.json", "manifest", "manifest", "placeholder"),
        _artifact(
            "entries/runbook-001.rev.1.json",
            "entry",
            "entry.runbook-001.rev.1",
            entry_sha,
            revision="1",
        ),
        _artifact(
            "fragments/runbook-001.rev.1.es.original.json",
            "fragment",
            "fragment.runbook-001.rev.1.es.original",
            frag_sha,
        ),
    ]
    manifest = _build_manifest(tmp_path, artifacts=artifacts)
    exc = _expect_corpus_error(lambda: load_corpus(manifest, profile="development"))
    message = str(exc)
    assert "CANARY-SECRET-FRAGMENT-CONTENT-XYZ" not in message
    # Reason code is a safe, stable identifier — not free text.
    assert exc.reason_code == "entry-classification-not-synthetic"


def test_corpus_exposes_no_retrieval_interface(tmp_path: Path) -> None:
    # The loaded corpus must not expose any retrieval/search method: retrieval
    # belongs to the query feature (Work Unit 2), not the corpus boundary.
    manifest = _valid_corpus(tmp_path)
    corpus = load_corpus(manifest, profile="development")
    assert not hasattr(corpus, "retrieve")
    assert not hasattr(corpus, "search")
    assert not hasattr(corpus, "query")
    # Fragments are the only surface; content is reachable by the application
    # layer but the corpus offers no retrieval semantics.
    assert hasattr(corpus, "fragments")


# ---------------------------------------------------------------------------
# Hash integrity: a tampered file fails closed even when fields look valid.
# ---------------------------------------------------------------------------


def test_load_corpus_rejects_tampered_entry_hash(tmp_path: Path) -> None:
    _write_entry(
        tmp_path,
        "entries/runbook-001.rev.1.json",
        identifier="entry.runbook-001.rev.1",
        logical_entry_id="runbook-001",
        revision="1",
        collection="runbooks",
        language="es",
    )
    frag_sha = _write_fragment(
        tmp_path,
        "fragments/runbook-001.rev.1.es.original.json",
        identifier="fragment.runbook-001.rev.1.es.original",
        entry_id="entry.runbook-001.rev.1",
        language="es",
    )
    # Tamper the manifest's declared entry sha256 so it no longer matches the file.
    artifacts = [
        _artifact("manifest.json", "manifest", "manifest", "placeholder"),
        _artifact(
            "entries/runbook-001.rev.1.json",
            "entry",
            "entry.runbook-001.rev.1",
            "0" * 64,  # wrong hash
            revision="1",
        ),
        _artifact(
            "fragments/runbook-001.rev.1.es.original.json",
            "fragment",
            "fragment.runbook-001.rev.1.es.original",
            frag_sha,
        ),
    ]
    manifest = _build_manifest(tmp_path, artifacts=artifacts)
    exc = _expect_corpus_error(lambda: load_corpus(manifest, profile="development"))
    assert exc.reason_code == "entry-hash-mismatch"


def test_load_corpus_rejects_tampered_fragment_hash(tmp_path: Path) -> None:
    entry_sha = _write_entry(
        tmp_path,
        "entries/runbook-001.rev.1.json",
        identifier="entry.runbook-001.rev.1",
        logical_entry_id="runbook-001",
        revision="1",
        collection="runbooks",
        language="es",
    )
    _write_fragment(
        tmp_path,
        "fragments/runbook-001.rev.1.es.original.json",
        identifier="fragment.runbook-001.rev.1.es.original",
        entry_id="entry.runbook-001.rev.1",
        language="es",
    )
    artifacts = [
        _artifact("manifest.json", "manifest", "manifest", "placeholder"),
        _artifact(
            "entries/runbook-001.rev.1.json",
            "entry",
            "entry.runbook-001.rev.1",
            entry_sha,
            revision="1",
        ),
        _artifact(
            "fragments/runbook-001.rev.1.es.original.json",
            "fragment",
            "fragment.runbook-001.rev.1.es.original",
            "0" * 64,  # wrong hash
        ),
    ]
    manifest = _build_manifest(tmp_path, artifacts=artifacts)
    exc = _expect_corpus_error(lambda: load_corpus(manifest, profile="development"))
    assert exc.reason_code == "fragment-hash-mismatch"


# ---------------------------------------------------------------------------
# OCR provenance validation: OCR fragments require source_reference + quality.
# ---------------------------------------------------------------------------


def test_load_corpus_accepts_ocr_fragment_with_source_and_quality(tmp_path: Path) -> None:
    entry_sha = _write_entry(
        tmp_path,
        "entries/runbook-001.rev.1.json",
        identifier="entry.runbook-001.rev.1",
        logical_entry_id="runbook-001",
        revision="1",
        collection="runbooks",
        language="es",
    )
    frag_sha = _write_fragment(
        tmp_path,
        "fragments/runbook-001.rev.1.es.ocr.json",
        identifier="fragment.runbook-001.rev.1.es.ocr",
        entry_id="entry.runbook-001.rev.1",
        language="es",
        provenance="ocr",
        source_reference="synthetic-ocr/runbook-001-page-3.txt",
        quality="low",
    )
    artifacts = [
        _artifact("manifest.json", "manifest", "manifest", "placeholder"),
        _artifact(
            "entries/runbook-001.rev.1.json",
            "entry",
            "entry.runbook-001.rev.1",
            entry_sha,
            revision="1",
        ),
        _artifact(
            "fragments/runbook-001.rev.1.es.ocr.json",
            "fragment",
            "fragment.runbook-001.rev.1.es.ocr",
            frag_sha,
        ),
    ]
    manifest = _build_manifest(tmp_path, artifacts=artifacts)
    corpus = load_corpus(manifest, profile="development")
    frag = corpus.fragments[0]
    assert frag.provenance == "ocr"
    assert frag.source_reference == "synthetic-ocr/runbook-001-page-3.txt"
    assert frag.quality == "low"


def test_load_corpus_rejects_ocr_fragment_without_source_reference(tmp_path: Path) -> None:
    entry_sha = _write_entry(
        tmp_path,
        "entries/runbook-001.rev.1.json",
        identifier="entry.runbook-001.rev.1",
        logical_entry_id="runbook-001",
        revision="1",
        collection="runbooks",
        language="es",
    )
    frag_sha = _write_fragment(
        tmp_path,
        "fragments/runbook-001.rev.1.es.ocr.json",
        identifier="fragment.runbook-001.rev.1.es.ocr",
        entry_id="entry.runbook-001.rev.1",
        language="es",
        provenance="ocr",
        source_reference="",  # missing
        quality="low",
    )
    artifacts = [
        _artifact("manifest.json", "manifest", "manifest", "placeholder"),
        _artifact(
            "entries/runbook-001.rev.1.json",
            "entry",
            "entry.runbook-001.rev.1",
            entry_sha,
            revision="1",
        ),
        _artifact(
            "fragments/runbook-001.rev.1.es.ocr.json",
            "fragment",
            "fragment.runbook-001.rev.1.es.ocr",
            frag_sha,
        ),
    ]
    manifest = _build_manifest(tmp_path, artifacts=artifacts)
    exc = _expect_corpus_error(lambda: load_corpus(manifest, profile="development"))
    assert exc.reason_code == "fragment-ocr-source-missing"


def test_load_corpus_rejects_non_ocr_fragment_with_source_reference(tmp_path: Path) -> None:
    entry_sha = _write_entry(
        tmp_path,
        "entries/runbook-001.rev.1.json",
        identifier="entry.runbook-001.rev.1",
        logical_entry_id="runbook-001",
        revision="1",
        collection="runbooks",
        language="es",
    )
    frag_sha = _write_fragment(
        tmp_path,
        "fragments/runbook-001.rev.1.es.original.json",
        identifier="fragment.runbook-001.rev.1.es.original",
        entry_id="entry.runbook-001.rev.1",
        language="es",
        provenance="original",
        source_reference="should-not-be-set",  # invalid for non-OCR
        quality="",
    )
    artifacts = [
        _artifact("manifest.json", "manifest", "manifest", "placeholder"),
        _artifact(
            "entries/runbook-001.rev.1.json",
            "entry",
            "entry.runbook-001.rev.1",
            entry_sha,
            revision="1",
        ),
        _artifact(
            "fragments/runbook-001.rev.1.es.original.json",
            "fragment",
            "fragment.runbook-001.rev.1.es.original",
            frag_sha,
        ),
    ]
    manifest = _build_manifest(tmp_path, artifacts=artifacts)
    exc = _expect_corpus_error(lambda: load_corpus(manifest, profile="development"))
    assert exc.reason_code == "fragment-source-not-ocr"


# ---------------------------------------------------------------------------
# Controlled vocabulary: unsupported language/collection/provenance fail closed.
# ---------------------------------------------------------------------------


def test_load_corpus_rejects_unsupported_entry_language(tmp_path: Path) -> None:
    entry_sha = _write_entry(
        tmp_path,
        "entries/runbook-001.rev.1.json",
        identifier="entry.runbook-001.rev.1",
        logical_entry_id="runbook-001",
        revision="1",
        collection="runbooks",
        language="fr",  # unsupported
    )
    frag_sha = _write_fragment(
        tmp_path,
        "fragments/runbook-001.rev.1.fr.original.json",
        identifier="fragment.runbook-001.rev.1.fr.original",
        entry_id="entry.runbook-001.rev.1",
        language="fr",
    )
    artifacts = [
        _artifact("manifest.json", "manifest", "manifest", "placeholder"),
        _artifact(
            "entries/runbook-001.rev.1.json",
            "entry",
            "entry.runbook-001.rev.1",
            entry_sha,
            revision="1",
        ),
        _artifact(
            "fragments/runbook-001.rev.1.fr.original.json",
            "fragment",
            "fragment.runbook-001.rev.1.fr.original",
            frag_sha,
        ),
    ]
    manifest = _build_manifest(tmp_path, artifacts=artifacts)
    exc = _expect_corpus_error(lambda: load_corpus(manifest, profile="development"))
    assert exc.reason_code == "entry-language-unsupported"


def test_load_corpus_rejects_unsupported_collection(tmp_path: Path) -> None:
    entry_sha = _write_entry(
        tmp_path,
        "entries/runbook-001.rev.1.json",
        identifier="entry.runbook-001.rev.1",
        logical_entry_id="runbook-001",
        revision="1",
        collection="recipes",  # unsupported
        language="es",
    )
    frag_sha = _write_fragment(
        tmp_path,
        "fragments/runbook-001.rev.1.es.original.json",
        identifier="fragment.runbook-001.rev.1.es.original",
        entry_id="entry.runbook-001.rev.1",
        language="es",
    )
    artifacts = [
        _artifact("manifest.json", "manifest", "manifest", "placeholder"),
        _artifact(
            "entries/runbook-001.rev.1.json",
            "entry",
            "entry.runbook-001.rev.1",
            entry_sha,
            revision="1",
        ),
        _artifact(
            "fragments/runbook-001.rev.1.es.original.json",
            "fragment",
            "fragment.runbook-001.rev.1.es.original",
            frag_sha,
        ),
    ]
    manifest = _build_manifest(tmp_path, artifacts=artifacts)
    exc = _expect_corpus_error(lambda: load_corpus(manifest, profile="development"))
    assert exc.reason_code == "entry-collection-unsupported"


def test_load_corpus_rejects_unsupported_provenance(tmp_path: Path) -> None:
    entry_sha = _write_entry(
        tmp_path,
        "entries/runbook-001.rev.1.json",
        identifier="entry.runbook-001.rev.1",
        logical_entry_id="runbook-001",
        revision="1",
        collection="runbooks",
        language="es",
    )
    frag_sha = _write_fragment(
        tmp_path,
        "fragments/runbook-001.rev.1.es.original.json",
        identifier="fragment.runbook-001.rev.1.es.original",
        entry_id="entry.runbook-001.rev.1",
        language="es",
        provenance="translated",  # unsupported
    )
    artifacts = [
        _artifact("manifest.json", "manifest", "manifest", "placeholder"),
        _artifact(
            "entries/runbook-001.rev.1.json",
            "entry",
            "entry.runbook-001.rev.1",
            entry_sha,
            revision="1",
        ),
        _artifact(
            "fragments/runbook-001.rev.1.es.original.json",
            "fragment",
            "fragment.runbook-001.rev.1.es.original",
            frag_sha,
        ),
    ]
    manifest = _build_manifest(tmp_path, artifacts=artifacts)
    exc = _expect_corpus_error(lambda: load_corpus(manifest, profile="development"))
    assert exc.reason_code == "fragment-provenance-unsupported"


# ---------------------------------------------------------------------------
# Path safety: escaping/symlinked/absolute artifact paths fail closed.
# ---------------------------------------------------------------------------


def test_load_corpus_rejects_absolute_artifact_path(tmp_path: Path) -> None:
    entry_sha = _write_entry(
        tmp_path,
        "entries/runbook-001.rev.1.json",
        identifier="entry.runbook-001.rev.1",
        logical_entry_id="runbook-001",
        revision="1",
        collection="runbooks",
        language="es",
    )
    artifacts = [
        _artifact("manifest.json", "manifest", "manifest", "placeholder"),
        {
            "id": "entry.runbook-001.rev.1",
            "kind": "entry",
            "path": str(tmp_path / "entries/runbook-001.rev.1.json"),  # absolute
            "sha256": entry_sha,
            "revision": "1",
        },
    ]
    manifest = _build_manifest(tmp_path, artifacts=artifacts)
    exc = _expect_corpus_error(lambda: load_corpus(manifest, profile="development"))
    assert exc.reason_code == "manifest-artifact-absolute-path"


def test_load_corpus_rejects_out_of_root_artifact_path(tmp_path: Path) -> None:
    entry_sha = _write_entry(
        tmp_path,
        "entries/runbook-001.rev.1.json",
        identifier="entry.runbook-001.rev.1",
        logical_entry_id="runbook-001",
        revision="1",
        collection="runbooks",
        language="es",
    )
    artifacts = [
        _artifact("manifest.json", "manifest", "manifest", "placeholder"),
        _artifact(
            "../entries/runbook-001.rev.1.json",  # escapes root
            "entry",
            "entry.runbook-001.rev.1",
            entry_sha,
            revision="1",
        ),
    ]
    manifest = _build_manifest(tmp_path, artifacts=artifacts)
    exc = _expect_corpus_error(lambda: load_corpus(manifest, profile="development"))
    assert exc.reason_code == "manifest-artifact-out-of-root"


def test_load_corpus_rejects_dangling_artifact_reference(tmp_path: Path) -> None:
    artifacts = [
        _artifact("manifest.json", "manifest", "manifest", "placeholder"),
        _artifact(
            "entries/missing.rev.1.json",
            "entry",
            "entry.missing.rev.1",
            "0" * 64,
            revision="1",
        ),
    ]
    manifest = _build_manifest(tmp_path, artifacts=artifacts)
    exc = _expect_corpus_error(lambda: load_corpus(manifest, profile="development"))
    assert exc.reason_code == "manifest-dangling-reference"


# ---------------------------------------------------------------------------
# Manifest ID consistency: manifest artifact id must match payload id.
# ---------------------------------------------------------------------------


def test_load_corpus_rejects_manifest_entry_id_mismatch(tmp_path: Path) -> None:
    entry_sha = _write_entry(
        tmp_path,
        "entries/runbook-001.rev.1.json",
        identifier="entry.runbook-001.rev.1",
        logical_entry_id="runbook-001",
        revision="1",
        collection="runbooks",
        language="es",
    )
    frag_sha = _write_fragment(
        tmp_path,
        "fragments/runbook-001.rev.1.es.original.json",
        identifier="fragment.runbook-001.rev.1.es.original",
        entry_id="entry.runbook-001.rev.1",
        language="es",
    )
    artifacts = [
        _artifact("manifest.json", "manifest", "manifest", "placeholder"),
        _artifact(
            "entries/runbook-001.rev.1.json",
            "entry",
            "entry.WRONG-id.rev.1",  # mismatched id
            entry_sha,
            revision="1",
        ),
        _artifact(
            "fragments/runbook-001.rev.1.es.original.json",
            "fragment",
            "fragment.runbook-001.rev.1.es.original",
            frag_sha,
        ),
    ]
    manifest = _build_manifest(tmp_path, artifacts=artifacts)
    exc = _expect_corpus_error(lambda: load_corpus(manifest, profile="development"))
    assert exc.reason_code == "entry-id-mismatch"


# ===========================================================================
# Shared ports (task 1.3): retrieval, generation, safe JSON logging.
# ===========================================================================


def test_safe_log_fields_closed_set_excludes_content() -> None:
    # The closed set MUST NOT include any content-bearing field.
    forbidden = {
        "question",
        "answer",
        "citations",
        "citation_text",
        "content",
        "tokens",
        "secret",
        "api_key",
        "provider_payload",
        "model_output",
        "prompt",
    }
    assert forbidden.isdisjoint(SAFE_LOG_FIELDS)
    # Safe fields are exactly the operational, content-free set.
    assert (
        frozenset(
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
        == SAFE_LOG_FIELDS
    )


def test_emit_safe_log_writes_json_line_with_only_safe_fields() -> None:
    import io
    import json as _json

    stream = io.StringIO()
    event = {
        "timestamp": "2026-07-23T00:00:00Z",
        "profile": "development",
        "outcome": "supported",
        "reason_code": "none",
        "duration_ms": 12,
        "attempt_count": 1,
        "language": "es",
        "operation": "query",
        "provider_class": "fake",
        "version": "0.0.0",
    }
    emit_safe_log(event, stream=stream)
    captured = stream.getvalue()
    parsed = _json.loads(captured)
    assert parsed == event
    assert captured.endswith("\n")


def test_emit_safe_log_rejects_content_field() -> None:
    # A content-bearing field must be rejected so it can never be logged.
    exc = _expect_raises(ValueError, lambda: emit_safe_log({"question": "leak"}))
    assert "question" in str(exc)


def test_emit_safe_log_rejects_answer_and_citation_text() -> None:
    _expect_raises(ValueError, lambda: emit_safe_log({"answer": "leak"}))
    _expect_raises(ValueError, lambda: emit_safe_log({"citation_text": "leak"}))
    _expect_raises(ValueError, lambda: emit_safe_log({"tokens": 123}))


def test_is_safe_log_event_accepts_safe_subset() -> None:
    assert is_safe_log_event({"outcome": "unavailable", "profile": "development"})
    assert is_safe_log_event({})  # empty is safe


def test_is_safe_log_event_rejects_unsafe_key() -> None:
    assert not is_safe_log_event({"question": "leak"})
    assert not is_safe_log_event({"outcome": "supported", "content": "leak"})


def test_outcomes_taxonomy_is_six_states() -> None:
    assert (
        frozenset(
            {
                "supported",
                "insufficient_information",
                "contradictory_information",
                "out_of_scope",
                "unavailable",
                "session_expired",
            }
        )
        == OUTCOMES
    )


def test_safe_response_omits_answer_text() -> None:
    response = SafeResponse(
        outcome="supported",
        citations=("fragment.runbook-001.rev.1.es.original",),
        escalation="none",
        profile="development",
        reason_code="none",
    )
    # SafeResponse carries no answer/question/content field by construction.
    assert not hasattr(response, "answer")
    assert not hasattr(response, "question")
    assert not hasattr(response, "content")
    assert response.citations == ("fragment.runbook-001.rev.1.es.original",)


def test_shared_ports_expose_no_persistence_interface() -> None:
    # The shared ports module MUST NOT expose any persistence interface.
    import backend.shared.ports as ports

    forbidden = {"persist", "save", "store", "write_record", "repository", "session_store"}
    exposed = {name for name in dir(ports) if not name.startswith("_")}
    assert forbidden.isdisjoint(exposed)


def test_retrieve_and_generate_are_runtime_checkable_protocols() -> None:
    from backend.shared.ports import Generate, Retrieve

    # Protocol objects are runtime_checkable: isinstance works on duck-typed
    # implementations without requiring inheritance.
    class _FakeRetrieve:
        def retrieve(self, question: str, language: str, profile: str) -> tuple:
            return ()

    class _FakeGenerate:
        def generate(self, question: str, evidence: tuple, language: str):
            from backend.shared.ports import GeneratedAnswer

            return GeneratedAnswer(internal_text="", citation_ids=())

    assert isinstance(_FakeRetrieve(), Retrieve)
    assert isinstance(_FakeGenerate(), Generate)


def test_safe_logger_protocol_is_runtime_checkable() -> None:
    from backend.shared.ports import SafeLogger

    class _StderrLogger:
        def log(self, event: dict) -> None:
            emit_safe_log(event)

    assert isinstance(_StderrLogger(), SafeLogger)
