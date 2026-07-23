# Proposal: Build OpsKnowledge Evaluation Dataset

## Intent

Establish the missing Phase 0 foundation: a reviewed, reproducible bilingual synthetic corpus and scenario dataset that later changes can consume without fabricating corporate evidence or authoritative answers.

## Scope

### In Scope
- Static, manifest-controlled synthetic entries across `runbooks`, `adrs`, and `operational-policies`, with stable IDs, language/revision metadata, approval, classification, hashes, and fragment provenance.
- A 32-scenario catalog (16 semantically paired Spanish/English cases): 16 answerable/grounded and 16 abstention/safety cases. It covers ambiguous/incomplete, contradiction, out-of-scope, unanswerable, prompt-override, OCR-uncertainty, and sensitive synthetic identifiers deterministically.
- Dependency-free structural validation that fails closed on malformed or non-synthetic data, invalid references/provenance, duplicate IDs, mixed-language evidence, parity failure, or balance deviation.

### Out of Scope
- Runtime evaluation, retrieval or model/provider calls, database seeding, corporate ingestion, profile wiring, metrics, reports, baselines, or Phase 2 release thresholds.
- Literal generated reference answers. The dataset defines outcome, evidence/claim expectations, abstention reason, and reviewer notes only.

## Capabilities

### New Capabilities
- `evaluation-dataset`: Governed bilingual synthetic corpus, scenarios, and structural validation for later evaluation work.

### Modified Capabilities
- None.

## Approach

Use reviewed versioned static fixtures plus a manifest and deterministic validator; add no production dependencies. Assumptions: 32 scenarios is the initial reviewable slice; parity means equivalent intent, outcome, safety classification, and evidence shape in each language. Contradictions use paired approved synthetic revisions; OCR cases use provenance-marked extracted text only; sensitive cases contain obviously fictitious identifiers.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `evaluation-dataset/` | New | Manifest, synthetic entries/fragments, scenario catalog |
| `tests/` | Modified | Dependency-free structural-validator coverage |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Synthetic text becomes accidental answer authority | Med | Store claims/evidence expectations, not gold answers |
| Nominal bilingual parity | Med | Validate paired semantic fields and require review |
| Safety cases imply image/corporate evidence | Low | OCR text only with provenance; visibly synthetic classification |

## Rollback Plan

Revert the self-contained dataset, validator, and related tests. No runtime state, provider calls, database records, or corporate data are introduced.

## Dependencies

- Existing Phase 0 domain contract, test harness, and reviewer approval of synthetic content.
- No external services or new production dependencies.

## Success Criteria

- [ ] All three approved collection types have approved, hashed, language-tagged synthetic entries with traceable fragments.
- [ ] Exactly 32 scenarios preserve Spanish/English parity and a 50/50 grounded versus abstention/safety balance.
- [ ] Structural validation deterministically fails closed for every documented integrity and isolation violation.
- [ ] No artifact performs retrieval, generation, persistence, corporate ingestion, or Phase 2 measurement.
