# Design: Reframe Roadmap for Direct Corporate Product

## Technical Approach

Treat this as documentation and lineage reconciliation, not Phase 1 completion. Keep the numeric Phase 1 history and its artifacts, label the delivered corpus slice as absorbed into the future production-core path, and explicitly rehome retrieval, prompt, provider, outcome, and CLI work as pending. The roadmap remains the change surface; architecture receives only wording needed to agree with `AGENTS.md`. Phase 2 evaluation and every cross-phase safety invariant remain unchanged. Phase 8 is represented as a co-prerequisite with Phases 3–5, so no corporate data processing is allowed before identity, authorization, privacy/sensitive-screen, controlled-provider, and TI gates pass.

## Architecture Decisions

| Decision | Choice | Alternatives considered | Rationale |
|---|---|---|---|
| Roadmap ownership | Edit Phase 1/2/8 sequencing and future-core wording in `RAG_ROADMAP.md`; leave Phase 0 wording to `audit-opsknowledge-phase-0-inputs`. | Duplicate or rewrite Phase 0 text. | Prevents competing ownership and preserves the completed Phase 0 reconciliation. |
| Phase 1 closure | Add a bounded lineage-closure note stating `reframed—not complete`; cite PR #28, merge `12ba6926`, receipt lineage, and the exact delivered corpus/ports inventory. | Mark all Phase 1 tasks complete, delete the active folder, or rewrite its spec. | Preserves auditable history while making the incomplete scope unambiguous. |
| Corporate boundary | Show `Phase 8 gates ∥ Phases 3–5 → corporate processing`; retain the development synthetic fixture and public-OpenAI demo-risk boundary as separate validation-only concerns. | Treat the demo as a corporate stepping stone or defer gates until pilot. | Matches the normative contract and blocks accidental corporate egress. |

## Data Flow

```text
Phase 0 owner (audit change) ──read-only baseline──┐
PR #28 + immutable receipt ──> lineage closure ────┼─> direct corporate roadmap
Phase 1 remainder ───────────> future production core┘
Phase 8 identity/privacy/provider/TI gates ──parallel prerequisite──> Phases 3–5 corporate path
```

The closure note records only the fail-closed synthetic corpus boundary, shared hexagonal ports, and corpus domain/application/loader delivered by PR #28. Retrieval, prompt, provider, outcome, and CLI work remain future work; no runtime capability is inferred from the merge.

## Sequencing and Ownership

1. Before apply, verify that the Phase 0/Phase 4 wording owned by `audit-opsknowledge-phase-0-inputs` is the accepted baseline. If its status is not settled, stop; do not edit those sections here.
2. Update the roadmap’s product boundary, delivery map, retained Phase 1 history/status, Phase 2 pointer, Phase 8 co-prerequisite statement, and next step.
3. Make the minimum architecture edits: identify the direct corporate target as planned, keep the development topology/demo-risk table, and state that corporate processing is blocked until all gates pass.
4. Create the closure note and perform a focused cross-document diff/lineage review.

## File Changes

| File | Action | Description |
|---|---|---|
| `RAG_ROADMAP.md` | Modify | Reframe ordering and status without renumbering; preserve Phase 2, safety invariants, Phase 0 ownership, and explicit future work. |
| `docs/architecture/platform-architecture.md` | Modify | Reconcile planned direct-corporate wording, gate ordering, and prototype-to-corporate mapping; preserve no-runtime and separate demo boundaries. |
| `openspec/changes/reframe-roadmap-for-direct-corporate-product/phase-1-lineage-closure.md` | Create | Auditable bounded closure record with PR/receipt evidence and pending-work inventory. |
| `AGENTS.md` | Verify only | Normative source; no edit unless review proves a contradiction. |
| `openspec/changes/audit-opsknowledge-phase-0-inputs/**` and `.git/gentle-ai/review-transactions/.../review-receipt.json` | Read only | Ownership and immutable evidence; never rewrite or delete. |

## Interfaces / Contracts

No runtime interfaces, APIs, schemas, or data migrations are introduced. The documentation contract is:

```text
corporate_processing_allowed = identity && authorization && privacy_screen
                               && controlled_provider && TI_gates
```

The development synthetic corpus and accepted public-OpenAI free-text risk remain distinct and never authorize corporate processing.

## Testing Strategy

| Layer | What to test | Approach |
|---|---|---|
| Documentation | Allowlist, wording coherence, preserved Phase 2/invariants, and no false completion. | Focused diff review, `git diff --check`, and `make ci`. |
| Lineage | PR #28 scope, merge hash, receipt lineage, and pending Phase 1 inventory remain discoverable. | Compare closure note with Git/GitHub evidence and unchanged prior artifacts. |
| Runtime | N/A — no runtime files or behavior change. | No runtime threat or behavior tests are manufactured. |

## Threat Matrix

N/A — this change adds no routing, shell, subprocess, VCS/PR automation, executable-file classification, or process-integration boundary. PR #28 and its receipt are read-only historical evidence.

## Migration / Rollout

No migration required. Apply as one documentation-only delivery. The 48-line product-documentation implementation edit (across `RAG_ROADMAP.md` and `docs/architecture/platform-architecture.md`) stays below the 400-line review budget; the full native frozen transaction snapshot is 463 changed lines, including 415 added lines across the six SDD planning/lineage artifacts in this change folder, and the maintainer approved a `size:exception` so the frozen transaction is kept as one documentation delivery rather than split or re-scoped. Roll back by reverting only this change’s roadmap, architecture, and closure-note edits; never alter PR #28, merge `12ba6926`, receipt/history, prior SDD artifacts, or Engram lineage.

## Open Questions

None. Phase 0 ownership is an apply gate, not an unresolved design decision.
