# Proposal: Reposition RAG as OpsKnowledge

## Intent

Reposition the repository as **OpsKnowledge**: a bilingual technical knowledge platform over approved, versioned runbooks, ADRs, and operational policies. It gives backend and AI engineering reviewers a rigorous portfolio narrative—not generic document chat—while retaining evidence-first safety and operational guarantees.

## Scope

### In Scope
- Rename product, roadmap, architecture, contributor-facing references, and relevant Phase 0–10 candidate-change labels to OpsKnowledge terminology.
- Define the OpsKnowledge domain contract: synthetic, visibly non-corporate policy/runbook collections; English/Spanish isolation; `reader`, `contributor`, `reviewer`, and `admin`; and `human expert` escalation.
- Supersede dental-domain contracts explicitly while preserving their audit trail and the durable platform contracts.

### Out of Scope
- Runtime, manifests, lockfiles, corpus files, migrations, or implementation.
- Changing architecture shape, dependencies, corporate TI gates, or safety/persistence/index-lifecycle guarantees.

## Capabilities

### New Capabilities
- `opsknowledge-domain-contract`: product boundary, collection governance, roles, bilingual evidence rules, outcome escalation, and dental-contract supersession.

### Modified Capabilities
None — `openspec/specs/` has no existing capability specs. Repository planning documents are updated by this change; the new contract defines their replacement behavior.

## Approach

Apply a terminology and boundary migration, not an architectural rewrite. Preserve citation-only answers, six outcomes, sensitive screening, atomic query persistence, versioned advisory-locked indexes, safe JSON logs, demo/corporate separation, exclusions, and TI gates. Reframe approved sources as versioned technical collections and rename future candidates consistently. Historical SDD artifacts remain intact and are marked superseded where applicable.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `RAG_ROADMAP.md` | Modified | OpsKnowledge boundary, phases, and candidate labels |
| `AGENTS.md` | Modified | Domain examples and escalation label; retain invariants |
| `docs/architecture/platform-architecture.md` | Modified | Product/source terminology and mappings |
| `openspec/changes/.../specs/` | New | OpsKnowledge domain delta/full contract |
| Engram dental SDD artifacts | Superseded | Retained as audit history, never deleted |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Narrative becomes generic RAG | Med | Anchor all claims to governed, versioned technical collections |
| Source-contract drift | High | Reconcile `AGENTS.md` → roadmap → architecture in that order |
| Rename sweep exceeds 800 lines | Med | Tasks must forecast slices; `ask-always` applies |

## Rollback Plan

Revert the documentation and new contract together; historical dental artifacts remain available as the prior audit baseline. No runtime or data migration exists.

## Dependencies

- User-approved product decisions and exploration `sdd/reposition-rag-as-portfolio-platform/explore`.

## Success Criteria

- [ ] OpsKnowledge consistently describes the product and candidate roadmap changes.
- [ ] New contract preserves stated invariants and uses `human expert` escalation.
- [ ] Dental artifacts are explicitly superseded, not deleted.
