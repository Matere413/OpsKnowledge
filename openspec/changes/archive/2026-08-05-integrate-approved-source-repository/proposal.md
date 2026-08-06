# Proposal: Integrate Approved Source Repository

## Intent

Deliver an executable, development-only local filesystem inventory boundary for approved synthetic source artifacts. A controlled logical manifest will be authoritative for approval, classification, collection, and content hashes; filename grammar will provide entry identity, language, and revision, but filenames will never prove approval. The adapter will return only a complete deterministic current snapshot, including a valid empty snapshot after a successful zero-artifact scan. Invalid, unreadable, partial, or incomplete scans will reject the complete snapshot rather than appear empty.

## Scope

### In Scope
- Provider-neutral immutable source descriptor, outbound repository port, and inventory use case owned by `indexing`.
- Development-profile local adapter over a synthetic approved-source fixture kept separate from `evaluation-dataset/`.
- Deterministic ordering, independent Spanish/English revision identity, fail-closed validation, safe diagnostics, and focused tests.

### Out of Scope
- PDF/OCR extraction, embeddings, PostgreSQL/index persistence, publication, rollback, cleanup, scheduling, administration, diff/synchronization, or provider egress.
- SharePoint/Graph, Entra, corporate documents, managed identity, private endpoints, and any corporate adapter in this change.

## Capabilities

### New Capabilities
- `approved-source-inventory`: Provider-independent, development-only discovery of a complete validated source snapshot.

### Modified Capabilities
- None. Existing `evaluation-dataset` and OpsKnowledge domain requirements remain unchanged; the evaluation corpus is not the approved-source fixture.

## Approach

Add an `indexing` feature with domain/application contracts and an outbound adapter. The local adapter will enforce development-only wiring, safe repository-relative paths, the roadmap filename grammar, manifest authority, hash agreement, duplicate detection, and explicit scan completeness. Its result will contain metadata only; it will not interpret document content. A future corporate adapter must implement the same port in a separate approved change after Phase 8 identity, authorization, privacy/sensitive-screening, controlled-provider, and TI gates pass.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/features/indexing/` | New | Source descriptor, port, inventory application service, and local outbound adapter. |
| Development synthetic source fixture | New | Controlled manifest and artifacts, separate from `evaluation-dataset/`. |
| `tests/unit/`, `tests/architecture/` | New/Modified | Determinism, empty-success, validation, scan-failure, and profile-boundary proof. |
| `backend/features/corpus/`, `backend/features/evaluation/` | Protected | Preserve existing provenance and validate-before-load evaluation boundaries. |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| A failed scan is mistaken for an empty repository. | High | Require explicit complete-scan evidence; reject all incomplete snapshots. |
| Filename or language/revision identity is trusted as approval. | Med | Make the logical manifest authoritative and include language in identity keys. |
| Development fixtures cross the corporate boundary. | High | Development-only wiring, no provider egress, and explicit Phase 8/TI blockers. |

## Rollback Plan

Revert the indexing feature, local adapter, fixture, and tests as one bounded change. No database, index, corporate source, or persistent state is introduced, so rollback requires no data migration or publication recovery.

## Dependencies

- Existing dependency-free Python test harness; no new production dependency is expected.
- Future corporate integration remains blocked by Phase 8 and TI gates.

## Success Criteria

- [ ] A development scan returns a byte-stable, complete current inventory, including a valid zero-artifact snapshot.
- [ ] Manifest authority, filename identity, independent ES/EN revisions, safe paths, hashes, and deterministic diagnostics are tested.
- [ ] Any invalid, unreadable, partial, or incomplete scan returns no snapshot and never masquerades as empty.
- [ ] `evaluation-dataset/` remains separate and no excluded or corporate integration is introduced.
