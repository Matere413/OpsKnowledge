# Proposal: Deterministic Grounded Query Kernel

## Intent

Build the first production-core query slice for automated evaluation: deterministic retrieval over approved development evidence, evidence-only prompting, and grounded answers or safe abstentions. It is foundational behavior, not Phase 2 completion or a user-facing product.

## Scope

### In Scope
- Expose immutable parent-entry provenance while preserving the fail-closed development synthetic boundary.
- Add deterministic `es`/`en` routing and stdlib lexical retrieval with approval, classification, profile, and stable ties.
- Add evidence-only prompts, sensitive/insufficient/contradictory/out-of-scope rules, citation allow-list validation, and a deterministic fake provider; failures map to `unavailable` and generated text stays memory-only.
- Add focused unit tests for safety and provider contracts.

### Out of Scope
- CLI, HTTP/UI, authentication, sessions, persistence/PostgreSQL/pgvector, embeddings, and live OpenAI/Azure providers.
- Phase 2 metrics/baselines/thresholds, ingestion, visual interpretation, or corporate processing before Phase 8/TI gates.

## Capabilities

### New Capabilities
- `grounded-query-kernel`: Deterministic retrieval, evidence-constrained generation, outcome classification, citation validation, abstention, and provider-failure handling.

### Modified Capabilities
- `opsknowledge-domain-contract`: Clarify this kernel’s fail-closed insufficient/contradictory/provider behavior, no-answer/no-citation insufficient responses, and defer `session_expired` to the later session capability.

## Approach

Reuse `load_corpus` and preserve explicit entry metadata; never infer revisions from identifiers. Keep domain/application provider-independent; use stable lexical scoring and same-language evidence. Screen before retrieval/provider processing, always abstain on contradictions, validate citations against retrieved approved fragments, and log/persist no content. Historical `build-minimal-grounded-opsknowledge-core` remains untouched; conflicting CLI/session rules are not inherited.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/features/query/` | New | Kernel domain, application flow, prompt, and fake adapter. |
| `backend/features/corpus/{domain.py,application.py}` | Modified | Preserve parent-entry provenance in the query projection. |
| `backend/shared/ports.py` | Modified | Typed provider failure and prompt-boundary contracts. |
| `tests/unit/` | New | Deterministic safety and contract coverage. |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Unsafe provenance grouping | Med | Explicit parent metadata and fail-closed validation. |
| Kernel plus tests exceed 400 lines | Med | Forecast separately; ask before chained PR splitting. |
| Prototype/corporate boundary blur | Low | No live provider, persistence, or corporate path. |

## Rollback Plan

Revert query modules, tests, and minimal corpus/port projection changes. Keep the dataset, canonical specs, and historical artifacts unchanged.

## Dependencies

- Existing `evaluation-dataset/`, corpus loader, Python 3.12, and frozen harness; no new production dependency.

## Success Criteria

- [ ] Identical fixtures produce identical language-filtered evidence, outcome, and citations.
- [ ] Insufficient, contradictory, sensitive, and provider-failure cases expose no answer/citations and recommend a human expert where applicable.
- [ ] Pytest, Ruff, Pyright, and `make ci` pass; no content appears in logs or durable state.
