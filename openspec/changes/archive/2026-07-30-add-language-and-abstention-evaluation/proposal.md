# Proposal: Language and Abstention Evaluation

## Intent

Replace the active 34-case Phase 2 baseline with a reviewed contract for language-routing accuracy, full-contract correct abstention, and unsupported-claim escape. The current denominator includes cases that never reach routing. Correct failures evidenced by this contract without weakening safety or traceability.

## Scope

### In Scope
- Replace, rather than append to, the current baseline with a versioned case population.
- Measure language accuracy for routing cases; exclude sensitive blocks and provider failures.
- Count correct abstention only when outcome, reason code, empty citations, and human-expert recommendation all match; measure unsupported-claim escape.
- Correct kernel/evaluation failures demonstrated by this contract.
- Keep reports deterministic, content-free, synthetic-development-only, opt-in, and non-persistent.

### Out of Scope
- OCR quality, retrieval recall, latency/cost, new answer-quality metrics, or unrelated failures.
- Changes to technical-grounding thresholds, archived gate semantics, `make ci`/`ci-pr2a` membership, roadmap checkboxes, or safety boundaries.
- Live providers, embeddings, PostgreSQL, HTTP/UI, corporate data, or excluded dependencies.

## Capabilities

### New Capabilities
- `language-and-abstention-evaluation`: Deterministic, content-free measurement for the three approved contracts.

### Modified Capabilities
- `quality-evaluation-harness`: Replace the active 34-case baseline while preserving validation, non-authoritative mapping, safe serialization, and opt-in/non-gating behavior.

## Approach

Preserve the manifest-controlled dataset and development kernel boundaries. Define the contract first, retain prior evidence as audit history, and keep the technical-grounding gate’s five-signal thresholds unchanged. Correct only failures in approved replacement cases. Tasks must forecast the 400-line review risk; this proposal does not choose a chain strategy.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/features/evaluation/` | Modified/New | Cases, metrics, safe reports, and bounded corrections. |
| `evaluation-runs/` | Modified | Replacement current baseline; prior evidence retained. |
| `tests/unit/`, `tests/architecture/` | Modified | Contract, determinism, safety, and boundary proof. |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Replacement reduces comparability and couples measurement to fixes. | High | Version identity, historical evidence, and contract-limited corrections. |
| Shared changes could drift gate ownership. | Med | Leave thresholds, CI membership, and gate spec unchanged; verify compatibility. |
| Scope exceeds the 400-line review budget. | High | Require task-phase forecast and later review-budget slicing decision. |

## Rollback Plan

Revert the replacement evaluator, corrections, tests, and baseline promotion; restore the prior baseline without changing archived evidence or gate thresholds.

## Dependencies

- Existing synthetic dataset/mapping, deterministic fake-provider kernel, and opt-in command.

## Success Criteria

- [ ] Replacement baseline reports all three metrics with explicit denominators and safe fields.
- [ ] Contract failures are corrected and deterministic focused proof passes without changing CI membership or thresholds.
- [ ] Reports exclude question, answer, citation content, claims, and provider payloads.
