# Tasks: Audit OpsKnowledge Phase 0 Inputs

## Review Workload Forecast

| Field | Value |
|---|---|
| Estimated changed lines | 55–90 authored roadmap lines; SDD planning/lifecycle artifacts excluded |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single bounded documentation work unit |
| Delivery strategy | ask-always |
| Chain strategy | pending (not selected) |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|---|---|---|---|---|---|
| 1 | Reconcile Phase 0 and Phase 4 wording and verify the roadmap-only diff | PR 1 | `uv run --frozen pytest` (focused documentation/architecture tests, then `make ci`) | N/A: documentation-only; no runtime boundary | Revert only changed Phase 0/Phase 4 text in `RAG_ROADMAP.md`; retain SDD audit artifacts |

## Phase 1: Roadmap Reconciliation

- [x] 1.1 Edit only `RAG_ROADMAP.md`: make the governed synthetic bilingual sample the sole current Phase 0 prerequisite, spanning `runbooks`, `adrs`, and `operational-policies` with manifest, version, approval, language, non-corporate, and development-only controls.
- [x] 1.2 Reconcile Phase 0 scope, outputs, and completion language: require Spanish/English parity and a 50% answerable/grounded plus 50% abstention/safety slice; classify historical metrics, Q&A/support reports, and glossaries as optional future evaluation references, never evidence or blockers.
- [x] 1.3 Remove `add-approved-domain-terminology-map` from Phase 0; retain `build-opsknowledge-evaluation-dataset` as the next product change and place `add-approved-terminology-query-expansion` only in Phase 4 as query-understanding-only, never evidence.
- [x] 1.4 Preserve citation-only current-approved-entry evidence, abstention/human-expert escalation, language-isolated retrieval, and synthetic-versus-corporate/demo boundaries; do not edit `AGENTS.md`, architecture, runtime, data, or `openspec/config.yaml` (its Engram project mismatch is a separate follow-up).

## Phase 2: Traceability and Verification

- [x] 2.1 Inspect the focused diff and record acceptance evidence for every specification scenario: immediate prerequisite, balanced bilingual slice, unavailable corporate inputs, historical references, candidate sequencing, and documentation-only scope.
- [x] 2.2 Confirm the diff allowlist contains authored roadmap changes only; update apply-progress evidence without counting planning artifacts as product scope or authored roadmap lines.
- [x] 2.3 Run the canonical `make ci` gate and record its exact result in the SDD verification output.

## Subsequent Lifecycle Handoffs (Not Apply Tasks)

After apply, hand off the completed roadmap diff, focused acceptance evidence, rollback boundary, and `make ci` result to the independent `sdd-verify` phase. Archive only after verification passes; `sdd-archive` owns archive reports and milestone-completion evidence. These later phases are prerequisites for completion, not implementation tasks in this artifact.
