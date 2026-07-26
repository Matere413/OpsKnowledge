# Phase 1 Lineage Closure — Reframed, Not Complete

## Outcome

Phase 1 (`Minimal grounded OpsKnowledge core`) is **absorbed into the future production-core path; it is not complete.** This note closes the prior SDD lineage with bounded evidence. It does not mark Phase 1 complete, delete the prior change, or claim any runtime capability beyond the delivered corpus slice.

## Authoritative evidence

| Field | Value |
|---|---|
| Pull request | PR #28 — `feat(core): add fail-closed corpus boundary` |
| Merge commit | `12ba692673c49bd59523c7ed818a6f3d3e131ed4` |
| Merged at | 2026-07-24T02:38:27Z |
| Branch | `Matere413/feat/minimal-grounded-core-pr1` |
| Prior SDD change | `openspec/changes/build-minimal-grounded-opsknowledge-core/` (active; not re-archived) |
| Receipt / history | Read-only; never rewritten or deleted |

## Delivered scope (only this is credited)

PR #28 / `12ba6926` delivered a bounded, fail-closed, development-only corpus slice and the shared hexagonal port contracts — nothing more:

- **Fail-closed synthetic corpus boundary:** `backend/features/corpus/domain.py`, `backend/features/corpus/application.py`, `backend/features/corpus/adapters/manifest_loader.py`. The loader fails closed outside the `development` profile and rejects non-`synthetic`/unapproved entries.
- **Shared hexagonal ports (defined, not implemented):** `backend/shared/ports.py` — protocols for retrieval, generation, and safe JSON logging. These are contracts only; no adapter implementation ships in this slice.
- **Corpus domain/application/loader tests:** `tests/unit/test_opsknowledge_core.py`.
- **SDD artifacts for the prior change:** `openspec/changes/build-minimal-grounded-opsknowledge-core/{exploration, proposal, design, tasks, specs/opsknowledge-core/spec}.md`.

No retrieval, prompt, provider, outcome, CLI, dependency wiring, or persistence behavior was delivered by PR #28.

## Pending production-core work (NOT delivered)

The following remain pending future production-core work. No runtime capability is inferred from the merge:

1. **Retrieval** — language-filtered, deterministic evidence selection (`backend/features/query/{domain,application}`).
2. **Prompt** — evidence-constrained prompt construction.
3. **Provider** — replaceable generation provider and deterministic fake adapter; timeout/rate-limit/outage → `unavailable`, no fabrication (`backend/features/query/adapters/openai_provider.py`).
4. **Outcome** — six-state deterministic rules, citation validation, abstention with human-expert escalation.
5. **CLI** — single safe JSON response, no persistence (`backend/features/query/cli.py`), plus `pyproject.toml`/`uv.lock` dependency wiring.

These map to the unchecked tasks (Phase 2: 2.1–2.4; Phase 3: 3.1–3.4) in `openspec/changes/build-minimal-grounded-opsknowledge-core/tasks.md`.

## Preservation guarantees

- PR #28, its merge receipt, and prior SDD artifacts are **unchanged**. This change never rewrites, re-archives, or deletes them.
- No `openspec/changes/archive/` entry for `build-minimal-grounded-opsknowledge-core` is modified.
- Phase 2 evaluation assets and the cross-phase safety invariants in `RAG_ROADMAP.md` and `AGENTS.md` are retained verbatim.
- The development-only synthetic corpus exception and the accepted public-OpenAI free-text demo risk remain two separate validation-only concerns; neither authorizes corporate processing.
- Corporate data processing remains blocked until identity, authorization, privacy/sensitive screening, controlled provider, and TI gates are all documented as passed (Phase 8 is a co-prerequisite of Phases 3–5).

## Rollback

Revert only this closure note and the roadmap/architecture wording edits introduced by `reframe-roadmap-for-direct-corporate-product`. Never alter PR #28, merge `12ba6926`, its receipt/history, or prior SDD artifacts.