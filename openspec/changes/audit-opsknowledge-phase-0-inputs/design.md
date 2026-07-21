# Design: Audit OpsKnowledge Phase 0 Inputs

## Technical Approach

Perform one documentation-only reconciliation in `RAG_ROADMAP.md`. Revise Phase 0 as a reproducible bilingual evaluation-foundation plan and align Phase 4 terminology ownership; do not alter the domain contract, architecture, `AGENTS.md`, data, or runtime. This implements all requirements in `phase-0-roadmap-reconciliation`.

## Architecture Decisions

| Decision | Alternatives considered | Rationale |
|---|---|---|
| Edit the roadmap only | Amend governing contracts or create dataset artifacts | The delta spec permits roadmap wording only; higher-order invariants already define the boundary. |
| Make one governed synthetic sample immediate | Keep corporate inputs as Phase 0 blockers | Enables an actionable development-only foundation without fabricating corporate material. |
| Keep terminology expansion in Phase 4 only | Retain a Phase 0 terminology-map candidate | Query expansion is a retrieval concern and glossary content is never evidence. |

## Data Flow

```text
Current domain contract / safety invariants
                 |
                 v
Phase 0 wording ──> bilingual evaluation foundation ──> dataset change
                 |
                 +──> Phase 4 query-understanding-only terminology expansion
```

## File Changes

| File | Action | Description |
|---|---|---|
| `RAG_ROADMAP.md` | Modify | Reconcile only Phase 0 and Phase 4 roadmap wording. |
| `openspec/changes/audit-opsknowledge-phase-0-inputs/design.md` | Create | This implementation design. |

## Interfaces / Contracts

No runtime interfaces, APIs, data structures, or migrations are introduced. The wording strategy is:

| Target section | Planned wording outcome |
|---|---|
| Phase 0 Objective and Scope | State a controlled evaluation foundation and one immediate sample: manifest-controlled, versioned, approved, language-tagged, visibly non-corporate, development-only synthetic `runbooks`, `adrs`, and `operational-policies`. |
| Phase 0 Pending inputs | Make that sample the sole current prerequisite. Describe corporate metrics, Q&A/support reports, and glossaries as optional future controlled references; they are neither blockers nor answer evidence. |
| Phase 0 Expected outputs | State the first bilingual slice is 50% answerable/grounded and 50% abstention/safety, with Spanish/English parity. Preserve explicit evaluation-only status for historical references. |
| Phase 0 Candidate changes and completion/next-step text | Remove `add-approved-domain-terminology-map`; retain `build-opsknowledge-evaluation-dataset` as the next product change after the reconciled foundation. Permit normal SDD planning, verification, and archive artifacts. |
| Phase 4 Bilingual retrieval and candidate list | Retain `add-approved-terminology-query-expansion` only here; state approved terminology supports query understanding/expansion only, never answer evidence. |

Invariant preservation: retain citation-only current-approved-entry evidence, abstention and human-expert escalation, language-isolated retrieval, and the synthetic development-only/corporate separation verbatim in meaning. Do not claim corporate references are synthetic, approved evidence, or automatic ground truth.

## Testing Strategy

| Layer | What to Test | Approach |
|---|---|---|
| Documentation review | All target sections and exclusions | Inspect the focused diff against this wording table and the domain contract. |
| Requirement traceability | Each requirement and scenario | Use the matrix below; reject missing or contradictory wording. |
| Repository gate | Documentation change safety | Run `make ci` as the canonical required gate. |

| Requirement / scenario | Design evidence |
|---|---|
| Current input / immediate prerequisite | Phase 0 Objective, Scope, Pending inputs |
| Dataset balance / bilingual slice | Phase 0 Expected outputs |
| Controlled references / unavailable inputs / not evidence | Phase 0 Pending inputs and Expected outputs |
| Phase 4 placement / sequencing | Phase 0 candidates and next step; Phase 4 retrieval and candidates |
| Documentation-only scope | File-change allowlist and focused diff; SDD artifacts allowed |

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file classification, or process-integration boundary.

## Migration / Rollout

No migration required. Apply as one reviewable roadmap-only diff. Roll back by reverting only the changed Phase 0/Phase 4 roadmap text in a follow-up SDD change; retain OpenSpec and Engram audit artifacts. The `openspec/config.yaml` Engram-project mismatch is a separate follow-up and is not changed here.

## Open Questions

None.
