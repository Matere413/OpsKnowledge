# Proposal: Reframe Roadmap for Direct Corporate Product

## Intent

Retire the prototype-first roadmap narrative without implying that the planned runtime exists. Absorb Phase 1 into the production-core path, preserve PR #28 and merge commit `12ba6926` as immutable historical evidence, retain Phase 2 evaluation, and require corporate identity, authorization, privacy screening, controlled provider, and TI gates before corporate data processing.

## Scope

### In Scope
- Update `RAG_ROADMAP.md` with an absorbed Phase 1 status and an exact PR #28 delivery receipt: fail-closed synthetic corpus boundary, shared hexagonal ports, and corpus domain/application/loader only.
- Rehome unimplemented retrieval, prompt, provider, outcome, and CLI work under future production-core scope; state explicitly that it is not complete.
- Move Phase 8 corporate gates to a co-prerequisite position with Phases 3–5, preserve Phase 2 and all safety invariants, and keep the synthetic fixture separate from public-OpenAI demo risk.
- Make only the minimum architecture wording updates needed for hierarchy coherence; close/document the prior Phase 1 SDD lineage with bounded evidence while preserving its active/archived artifacts and Engram lineage.

### Out of Scope
- No runtime implementation, source code, manifests, lockfiles, tests, corporate data, provider integration, or TI values.
- No rewrite, deletion, or re-archive of PR #28, its receipt/history, or unrelated archived SDD artifacts.
- No Phase 0 input rewrite owned by `audit-opsknowledge-phase-0-inputs`; overlap is resolved by one owning change, not duplicated edits.

## Capabilities

### New Capabilities
None — documentation and SDD-governance reconciliation only.

### Modified Capabilities
None — no requirement-level behavior changes. `opsknowledge-domain-contract` and `evaluation-dataset` remain unchanged; only roadmap/lineage wording is clarified.

## Approach

Use the roadmap as the authoritative change surface, cite the merged commit and bounded inventory, and preserve the previous SDD as auditable history. Add a clearly named future production-core work area for incomplete items. Reconcile architecture labels with a production-targeted, still-planned corporate path while retaining the explicit no-runtime caveat and separate demo-risk table. Coordinate the Phase 0 overlap before apply.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `RAG_ROADMAP.md` | Modified | Product boundary, Phase 1/2/8 ordering, receipt, next step. |
| `docs/architecture/platform-architecture.md` | Modified | Minimal planned-topology and Azure-mapping wording. |
| Prior Phase 1 SDD/Engram lineage | Closure note | Bounded PR #28 evidence; incomplete work remains pending. |
| `audit-opsknowledge-phase-0-inputs` | Referenced | Existing owner for Phase 0 input wording. |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Readers infer retrieval/provider/CLI are delivered | Med | Enumerate PR #28 contents and pending work explicitly. |
| Boundary or lineage is lost | Low | Preserve both safety distinctions, commit hash, and historical artifacts. |
| Overlap creates conflicting roadmap edits | Med | Assign Phase 0 wording to the audit change and reconcile before apply. |

## Rollback Plan

Revert only this change’s roadmap, architecture, and closure-note edits; restore the prior roadmap pointers and pending work labels. Never rewrite PR #28 or modify archived evidence.

## Dependencies

- Maintainer resolution of the Phase 0 ownership overlap.
- Existing PR #28 merge receipt and prior SDD artifacts.

## Success Criteria

- [ ] The 48-line product-documentation implementation edit (across `RAG_ROADMAP.md` and `docs/architecture/platform-architecture.md`) stays below the 400-line review budget. The full native frozen transaction snapshot is 463 changed lines, including 415 added lines across the six SDD planning/lineage artifacts in this change folder; the maintainer approved a `size:exception` so the frozen transaction remains one documentation delivery and is NOT split or re-scoped. No runtime, manifest, lockfile, or test file is touched.
- [ ] PR #28/`12ba6926` remains discoverable, with only its delivered corpus/ports slice credited; retrieval/provider/CLI remain visibly pending.
- [ ] Phase 2, early corporate gates, TI blocking, and the two separate synthetic/demo boundaries are explicit and consistent with `AGENTS.md`.
