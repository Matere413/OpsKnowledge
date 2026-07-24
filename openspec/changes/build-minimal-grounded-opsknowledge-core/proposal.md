# Proposal: Minimal Grounded OpsKnowledge Core

## Intent

Phase 1 needs proof that OpsKnowledge answers only from approved evidence. This CLI accepts demo free text over the development-only synthetic corpus without crossing the corporate boundary.

## Scope

### In Scope
- Add hexagonal `backend/` corpus/query/shared slice.
- Load the manifest-controlled development corpus; retrieve by language-filtered keyword overlap.
- Expose `python -m backend.features.query.cli "..."` with citations, six outcomes, and human-expert escalation.
- Screen high-confidence sensitive input before providers; add an OpenAI port adapter and deterministic fake. Rejected text is never persisted or logged.

### Out of Scope
- HTTP/FastAPI, OpenAPI, web UI, authentication, sessions, analytics, databases, and durable persistence.
- Embeddings/vector storage, source synchronization, OCR/image interpretation, reranking, and corporate/Azure integrations.

## Capabilities

### New Capabilities
- `opsknowledge-core`: Development-only CLI flow with synthetic loading, language-isolated retrieval, grounded generation, citations, abstention, screening, and provider-failure handling.

### Modified Capabilities
- None. `opsknowledge-domain-contract` requirements remain unchanged; this change implements them rather than altering their contract.

## Approach

Keep domain/application provider-independent and put OpenAI behind an outbound port. Reuse manifest provenance; arbitrary free text is not synthetic, and prompts contain only approved same-language fragments. Provider timeout, rate-limit, or outage returns `unavailable`, recommends a human expert, persists no answer, and never fabricates evidence. Defer embeddings; use approved `openai` only if required. Forecast tasks against 400 authored lines and ask before splitting PRs.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/features/{corpus,query}/`, `backend/shared/` | New | Query slice and adapters. |
| `tests/` | New | Safety and provider coverage. |
| `pyproject.toml`, `uv.lock`, governance | Conditional | Record/lock `openai` if required. |
| `RAG_ROADMAP.md` | Deferred | Mark Phase 1 only after archive. |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Sensitive free text reaches public OpenAI | Med | Screen before calls; state residual detection risk. |
| Unsupported or wrong-language evidence | Med | Deterministic retrieval, citation allow-list, fail-closed outcomes. |
| Review scope exceeds 400 lines | Med | Forecast tasks; ask before splitting and chain slices if needed. |

## Rollback Plan

Revert backend, tests, CLI, and conditional dependency changes. Preserve the evaluation dataset and domain contract; revert the roadmap checkbox only if archive updated it.

## Dependencies

- `evaluation-dataset/` and `opsknowledge-domain-contract`.
- Python 3.12 and frozen `uv`/`make ci`.
- Existing `openai` approval; no excluded or TI-gated dependency.

## Success Criteria

- [ ] Fake tests cover both languages, all six outcomes, sensitive blocking, provider failure, and citation/language isolation.
- [ ] Supported responses cite only approved same-language fragments; unsupported, out-of-scope, and contradictory cases abstain with human-expert guidance.
- [ ] Sensitive/provider-failure paths make no provider call and persist no answer; `make ci` passes.
