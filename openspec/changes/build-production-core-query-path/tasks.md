# Tasks: Deterministic Grounded Query Kernel

## Review Workload Forecast

| Field | Value |
|---|---|
| Estimated changed lines | 520–680 authored implementation and test lines |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 → PR 2 → PR 3 |
| Delivery strategy | ask-on-risk |
| Chain strategy | stacked-to-main |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|---|---|---|---|---|---|
| 1 | Immutable provenance and provider value contracts | PR 1 | `uv run --frozen pytest tests/unit/test_opsknowledge_core.py tests/unit/test_grounded_query_kernel.py -q` | N/A: no inbound runtime exists | Revert corpus domain/application, shared ports, and contract tests |
| 2 | Deterministic lexical retrieval and evidence-only prompts | PR 2 | `uv run --frozen pytest tests/unit/test_grounded_query_kernel.py -q` | N/A: in-process adapters only; no HTTP/CLI/live provider | Revert query domain, prompt, lexical adapter, and their tests |
| 3 | Safe resolution, fake provider, and quality gate | PR 3 | `uv run --frozen pytest tests/unit/test_grounded_query_kernel.py -q` | N/A: provider is deterministic fake; no external side effects | Revert query application/fake adapter, tests, and Pyright config |

## Phase 1: Contracts and Provenance

- [x] 1.1 RED: Extend `tests/unit/test_opsknowledge_core.py` for immutable parent provenance, explicit metadata copying, parent-language validation, and no identifier-based revision inference.
- [x] 1.2 Add frozen `EntryProvenance` to `backend/features/corpus/domain.py`; populate and fail closed in `backend/features/corpus/application.py`.
- [x] 1.3 RED: Add `tests/unit/test_grounded_query_kernel.py` contract checks for immutable prompt evidence, typed provider failures, and content-free `SafeResponse`.
- [x] 1.4 Add `GroundedPrompt`/`PromptEvidence` and `ProviderFailure` to `backend/shared/ports.py`; preserve the six-state taxonomy and content-free response surface.

## Phase 2: Retrieval and Prompt Boundary

- [x] 2.1 RED: Test `en`/`es` isolation, exclusion of unsafe/ambiguous/corporate/wrong-language metadata, lexical ranking, and fragment-ID tie stability.
- [x] 2.2 Create `backend/features/query/domain.py` and `backend/features/query/adapters/lexical_retriever.py` with pre-ranking filters and deterministic stdlib token scoring.
- [x] 2.3 RED: Test `backend/features/query/prompt.py` excludes history, glossary, support history, model knowledge, and user instructions from evidence.
- [x] 2.4 Create `backend/features/query/prompt.py` with immutable selected-fragment records containing only query, rules, and same-language evidence.

## Phase 3: Resolution and Provider Safety

- [x] 3.1 RED: Test sensitive pre-screening (`unavailable` + `sensitive_blocked` detail, no calls), insufficient, contradictory revisions, out-of-scope/override, human escalation, and no `session_expired`.
- [x] 3.2 Create `backend/features/query/application.py` to screen, route, retrieve, abstain conservatively, invoke `Generate`, and return `SafeResponse`.
- [x] 3.3 RED: Test valid/invalid/missing citation allow-lists, fake reproducibility, timeout/rate-limit/outage failures, no fabricated evidence, and no content logging/persistence.
- [x] 3.4 Create `backend/features/query/adapters/fake_provider.py` with deterministic responses and typed failure mapping; validate citations in the application.

## Phase 4: Verification

- [x] 4.1 Update `pyproject.toml` Pyright coverage for `backend` and `tests` without dependency or lockfile changes.
- [x] 4.2 Run focused tests, `uv run --frozen ruff check .`, `uv run --frozen pyright`, and `make ci`; confirm no CLI, HTTP/UI, sessions, auth, persistence, embeddings, live providers, metrics, or new dependencies.
