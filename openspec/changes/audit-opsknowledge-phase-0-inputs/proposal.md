# Proposal: Audit OpsKnowledge Phase 0 Inputs

## Intent

Reconcile Phase 0 with the OpsKnowledge repositioning so unavailable corporate material does not block the synthetic, development-only evaluation foundation or weaken evidence rules.

## Scope

### In Scope
- Update `RAG_ROADMAP.md` Phase 0 objective, scope, pending inputs, expected outputs, candidate list, and next-step language.
- Require a synthetic, manifest-controlled, versioned, approved, language-tagged, visibly non-corporate, development-only sample across `runbooks`, `adrs`, and `operational-policies`.
- Define the initial bilingual dataset slice as 50% answerable/grounded and 50% abstention/safety cases; require Spanish/English parity.
- Reclassify historical support metrics, Q&A reports, and glossaries as optional future controlled references, never answer evidence.
- Remove the Phase 0 terminology-map candidate and retain its query-understanding-only placement as `add-approved-terminology-query-expansion` in Phase 4.

### Out of Scope
- Creating the evaluation dataset or starting `build-opsknowledge-evaluation-dataset`.
- Corporate-data intake, runtime changes, or changes to safety, evidence, language-isolation, or demo/corporate invariants.
- Specs, design, tasks, or roadmap implementation in this change.

## Capabilities

### New Capabilities
None — this is a roadmap reconciliation only.

### Modified Capabilities
None — no existing product requirement changes.

## Approach

Make a bounded documentation-only reconciliation using the current domain contract: retain the synthetic sample as the sole immediate input; make unavailable corporate inputs explicitly optional/later; align Phase 0 outputs and next step with a reproducible bilingual evaluation foundation. Preserve the terminology map for Phase 4 retrieval, where it remains non-evidence.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `RAG_ROADMAP.md` | Modified | Reconcile Phase 0 and Phase 4 candidate placement. |
| `AGENTS.md` | Referenced | Governing invariants; no planned edit. |
| `openspec/specs/opsknowledge-domain-contract/spec.md` | Referenced | Governing collection, evidence, and language rules. |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Corporate inputs are treated as required or answer evidence | Med | State they are optional/later controlled references only. |
| Synthetic sample crosses the corporate boundary | Low | Preserve classification, manifest, approval, and development-only requirements. |
| Engram project mismatch in `openspec/config.yaml` | Med | Track separately; do not change unless it blocks persistence. |

## Rollback Plan

Revert only the roadmap reconciliation in a follow-up SDD change, restoring prior wording while retaining archived proposal evidence. Do not introduce corporate data or alter runtime behavior.

## Dependencies

- Approved synthetic sample governance under the existing demo contract.
- Maintainer review of the reconciled roadmap wording.

## Success Criteria

- [ ] Phase 0 names the synthetic bilingual sample as its current required input and the 50/50 dataset distribution.
- [ ] Phase 0 no longer blocks on corporate metrics, Q&A reports, or glossaries; Phase 4 owns terminology query expansion.
- [ ] All existing evidence, abstention, language-isolation, and demo/corporate boundaries remain explicit and unchanged.
