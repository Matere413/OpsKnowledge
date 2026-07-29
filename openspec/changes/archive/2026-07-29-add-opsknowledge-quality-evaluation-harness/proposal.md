# Proposal: Add OpsKnowledge Quality Evaluation Harness

## Intent

Create the first reproducible Phase 2 baseline for the grounded-query kernel. A harness-owned question mapping exercises the 32 scenarios without adding question fields or answer ground truth.

## Scope

### In Scope
- Add dependency-free `backend/features/evaluation/` execution with a reviewed ES/EN mapping and injected deterministic `Clock`.
- Run the unchanged 32 scenarios plus a labeled harness-injected provider-failure pair (ES/EN).
- Report outcome, citation-set, language-routing, sensitive-block, and contradiction-detection metrics in machine-readable and human-readable output under sibling `evaluation-runs/`; commit one reviewed baseline and retain only current and previous baselines.
- Add focused tests and opt-in `make eval-quality`.

### Out of Scope
- Dataset changes/question fields or a delta against unarchived `grounded-query-kernel`.
- Live providers, embeddings, persistence, HTTP, auth, UI, corporate data, excluded dependencies, thresholds, or `make ci` wiring.

## Capabilities

### New Capabilities
- `quality-evaluation-harness`: Deterministic in-process execution and baseline reporting for the reviewed synthetic scenario catalog.

### Modified Capabilities
- None.

## Approach

Validate first and fail closed. Load the development corpus, resolve mapped questions through `LexicalRetriever` and the fake-provider boundary, then compare safe outcomes, reason codes, citation sets, and language. Add typed provider-failure coverage without dataset edits. Reports exclude question, answer, citation content, claim text, and provider payloads. Numbers only; `add-technical-grounding-safety-gates` owns thresholds.

## Proposal question round

Approved decisions resolve Q1–Q5: mapping, five metrics, ES/EN failure pair, bounded `evaluation-runs/` evidence, and one-cycle opt-in execution.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/features/evaluation/` | New | Runner, mapping, reports, CLI, clock. |
| `tests/unit/`, `tests/architecture/` | New | Determinism, safety, report, Makefile tests. |
| `Makefile` | Modified | Add `eval-quality`; leave `ci` unchanged. |
| `evaluation-runs/` | New | Reviewed baseline evidence. |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Mapping becomes hidden ground truth | Med | Review it outside scenario records. |
| Reports leak protected content | High | Allowlist fields and test outputs. |
| Work exceeds 400 lines | Med | Forecast units; apply ask-on-risk. |
| Baseline becomes a release gate | Med | Emit numbers only; defer thresholds. |

## Rollback Plan

Remove the feature, tests, Makefile target, and committed run. Dataset, kernel, dependencies, and `make ci` remain unchanged; no runtime state requires recovery.

## Dependencies

- Existing dataset, validator, corpus loader, kernel, fake provider, stdlib, and locked environment. RDD remains disabled under issue #1892.

## Success Criteria

- [ ] `make eval-quality` deterministically reports 32 base plus two provider-failure cases.
- [ ] One reviewed baseline is committed under `evaluation-runs/` with five metrics and no thresholds.
- [ ] Tests prove fail-closed validation, safe output, language isolation, provider failure, and unchanged `ci` wiring.
