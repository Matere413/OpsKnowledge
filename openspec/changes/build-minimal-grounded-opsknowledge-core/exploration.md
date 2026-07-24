# Exploration: build-minimal-grounded-opsknowledge-core

## Current State

Phase 0 and the two pre-Phase 1 CI hardening changes are merged on `master` at `36843ce3`. The repository currently contains:

- A working test harness (`Makefile`, `pyproject.toml`, frozen `uv.lock`, `uv` 0.11.29 version gate, focused-test scanner, dependency-boundary scanner, vulnerability audit, license inventory).
- A complete bilingual synthetic evaluation dataset (5 entries, 8 fragments, 32 paired scenarios across `runbooks`, `adrs`, `operational-policies`) at `evaluation-dataset/`, validated by `scripts/ci/validate_evaluation_dataset.py` and wired into `make ci`.
- An authoritative OpsKnowledge domain contract at `openspec/specs/opsknowledge-domain-contract/spec.md` (9 requirements, 9 scenarios) covering citation-only evidence, language-isolated retrieval, the six-state outcome taxonomy, sensitive screening, the role contract, and corpus separation.
- Approved architectural dependencies in `governance/direct-dependencies.yaml` (`openai`, `fastapi`, `sqlalchemy`, `psycopg`, `alembic`, `pgvector`, `docling`) plus one pending entry (`azure-identity`).
- No application runtime source. There is no `backend/`, no `web/`, no `compose/`, no FastAPI app, no React app, no database driver wiring. The `pyproject.toml` declares empty `dependencies = []`.

The Phase 1 roadmap objective is to build the smallest understandable pipeline that answers only from supplied textual evidence: `approved entry text → structure-aware chunks → embeddings → simple similarity search → evidence-constrained prompt → answer or abstention with citations`. Out of scope: approved-source synchronization, persistent vector storage, web UI, authentication, analytics, conversation history, reranking, and framework-heavy orchestration.

## Affected Areas

- `backend/` (does not exist yet) — new feature-organized modular monolith source tree.
  - `backend/features/query/` — domain (`Question`, `Answer`, `Citation`, `Outcome`), application (`answer_question` use case), inbound adapter (CLI or in-process call), outbound adapters (`Embed`, `Generate`, `Retrieve`).
  - `backend/features/corpus/` — domain (`Entry`, `Fragment`, `Embedding`), application (`load_synthetic_corpus`), outbound adapter (synthetic manifest file reader; later Phase 3 swaps for the approved-source adapter).
  - `backend/shared/` — port contracts (`Embed`, `Generate`, `Retrieve`), `Clock` protocol, safe logging helpers.
- `pyproject.toml` — adds direct production dependencies (most likely `openai` only, possibly nothing if a stdlib-only embedding fallback is chosen) and a `backend` package source layout.
- `governance/direct-dependencies.yaml` — every new direct production dependency needs an entry; `openai` is already approved for the prototype path.
- `uv.lock` — refresh if `pyproject.toml` production dependencies change.
- `tests/` — new unit and integration tests for the chunker, in-memory index, prompt builder, six-state outcome classification, abstention paths, and sensitive screening.
- `Makefile` — likely no changes; `make ci` is already the canonical gate.
- `openspec/specs/opsknowledge-core/` — new canonical spec, populated only after archive.
- `RAG_ROADMAP.md` — Phase 1 checkbox flipped to `[x]` Completed only after archive.
- `docs/architecture/platform-architecture.md` — update the `Backend demo environment and identity gate` and `Physical architecture` sections to reference the now-deployed (no longer "target/planned") components.

## Approaches

### 1. Backend skeleton + in-memory synthetic-only pipeline (recommended)

Establish `backend/` with hexagonal features (`corpus`, `query`, `shared`), wire port protocols `Embed`, `Generate`, `Retrieve`, implement an in-memory `Retrieve` over the synthetic manifest fragments, call the `openai` client (`text-embedding-3-small` + `gpt-4o-mini` Responses API) behind the protocols, and expose the answer path through a Python entry point (CLI or `python -m`) — no HTTP, no database, no auth. Consume the existing evaluation dataset to prove the six outcomes and language isolation.

- **Pros**: Honors every cross-phase safety invariant (citation-only evidence, language-isolated retrieval, abstention, sensitive screen, no general knowledge); uses already-approved `openai` governance entry; no new dependencies needed; testable offline; smallest diff that advances the roadmap; keeps the 400-line review budget honest; easily chained into a slice per component.
- **Cons**: Requires a non-trivial first PR that establishes the directory layout, port contracts, and the test harness patterns. Without an HTTP boundary, the slice is less obviously a "product."
- **Effort**: Medium

### 2. FastAPI HTTP shell + the same pipeline

Same as approach 1, but expose the answer path through a `POST /query` endpoint and a `GET /health` endpoint, plus a Dockerfile stub. The HTTP adapter is required by the eventual `expose-opsknowledge-application-services` Phase 6 work.

- **Pros**: Real interface; the first end-to-end "question → JSON answer" feels like a product; aligns with `apps/api/openapi/openapi.json` future path; the OpenAPI artifact can be generated and locked as part of this change.
- **Cons**: Adds FastAPI/Starlette/Uvicorn/httpx dev-extra surface that Phase 1 explicitly leaves out as framework-heavy orchestration. Risks the change growing past the 400-line budget. Forces OpenAPI generation and TypeScript-client drift decisions earlier than the roadmap plans.
- **Effort**: Medium-High

### 3. Library-first, defer the entry point

Ship only the domain, application, and outbound-adapter code (no HTTP, no CLI), and let the Phase 2 evaluation harness import the library to run the slice. The pipeline is exercised only through `pytest`.

- **Pros**: Smallest possible diff; maximally testable; 400-line budget very safe; perfectly reversible; pure library code with no external surface.
- **Cons**: No observable end-to-end runnable artifact; reviewers may not "see" the answer; integration confidence is lower; pushes the user-facing "it works" demonstration to Phase 2 or Phase 7.
- **Effort**: Low

## Recommendation

Approach 1, with one bounded additional work unit that produces a small CLI entry point (`python -m backend.features.query.cli "..."`) so reviewers can run an end-to-end smoke test locally. The slice should be:

1. **Phase 1.1 — Backend skeleton + port protocols** (smallest possible diff: `backend/` directory, `pyproject.toml` `packages` discovery, port `Protocol` types, `Clock` protocol, `tests/` skeleton).
2. **Phase 1.2 — Synthetic corpus loader** (loads `evaluation-dataset/manifest.json` and its fragments into in-memory domain objects; reuses the existing validator as a load-time gate).
3. **Phase 1.3 — In-memory similarity retrieval** (token-frequency or constant-vector similarity; language-isolated filter; deterministic for tests).
4. **Phase 1.4 — Evidence-constrained prompt builder** (composes a prompt that only includes the retrieved fragments; the prompt explicitly forbids using model knowledge for unfilled claims).
5. **Phase 1.5 — OpenAI client + outcome classifier** (calls `text-embedding-3-small` for embeddings and the Responses API for generation; classifies the response into one of the six outcomes using the protocol from the domain contract; sensitive screen runs before the embedding call; on provider failure the path resolves to `unavailable` and persists nothing).
6. **Phase 1.6 — CLI entry point + focused tests** (`python -m backend.features.query.cli "..."` for the smoke test; focused Pytest cases for each scenario class).
7. **Phase 1.7 — Roadmap checkbox, governance entries, `make ci` proof** (no new governance entries required if `openai` is the only direct production dep; update `RAG_ROADMAP.md` after archive).

The 400-line review budget is safe for this slice if the change excludes generated tests and OpenSpec artifacts. If the apply forecast approaches 400 lines, split it via the `chained-pr` strategy: PR 1 = skeleton + corpus loader, PR 2 = retrieval + prompt + provider, PR 3 = CLI + outcome classifier + roadmap + tests.

## Risks

- **Crossing the prototype/corporate boundary**: the development-only synthetic corpus exception must remain `development` profile only. Phase 1 must not wire the synthetic corpus under any other profile. The CI denial must remain intact.
- **Provider failure masquerading as a valid answer**: the pipeline must classify every response into one of the six outcomes, and provider failures must resolve to `unavailable` with no answer and no persistence. Without this, the safety invariant "the model may not use general knowledge to fill gaps" is violated.
- **Sensitive payload leakage**: free-text questions pass through the public OpenAI prototype; the high-confidence sensitive screen must run before the embedding call and block matched payloads without persisting the text. The architecture says this is an "accepted risk" not a guarantee — Phase 1 must surface the screen's behavior in the spec.
- **Citation drift**: every claim must trace to a fragment returned by retrieval. The prompt builder must place the fragment identifiers visibly in the prompt, and the post-generation step must verify the cited fragment identifiers were in the prompt (or re-classify as `insufficient_information`).
- **Bilingual evidence mixing**: language-isolated retrieval is a hard invariant. The in-memory index must filter on language before returning candidates; the prompt must never contain fragments in both languages for one query.
- **Outcome-taxonomy drift**: only `supported | insufficient_information | contradictory_information | out_of_scope | unavailable | session_expired` are allowed. The outcome classifier must reject any seventh value; `session_expired` is not reachable in Phase 1 because there is no session yet — but the type system must accept it so Phase 6 does not rewrite the protocol.
- **400-line review budget overrun**: if the change bundles HTTP, OpenAPI, dependency updates, docs, and a CLI, it will likely exceed 400 lines. Plan to chain PRs early; do not import excluded dependencies (LangChain, LlamaIndex, Redis, Kubernetes, streaming, visual interpretation, email/Notifier, unevidenced reranking) under any circumstance.
- **Dependency governance drift**: adding any new direct production dependency without a governance entry fails `make ci`. Reuse the already-approved `openai` entry; avoid `numpy`/`tiktoken`/`httpx`/etc. unless the change adds and approves the entries explicitly.
- **Strict TDD re-evaluation**: the test-harness spec says Strict TDD stays `false` until a runtime change re-evaluates it. Phase 1 is a runtime change. The proposal must include a re-evaluation decision (recommended: keep `false` for the slice; require RED-GREEN-REFACTOR only where a use case is non-trivial).

## Decisions Required Before Proposal

The orchestrator should request the following from the user before launching `sdd-propose`:

1. **HTTP boundary in this slice?** Yes (FastAPI `POST /query` + OpenAPI artifact) or No (CLI only)? Recommendation: No for the first slice, defer to Phase 6 to honor Phase 1's "framework-heavy orchestration out of scope."
2. **Embedding strategy**: real `openai.text-embedding-3-small` calls vs. deterministic constant/in-memory vectors in the test path vs. both (real provider behind a feature flag, deterministic fake in tests). Recommendation: both, with the fake for unit tests and the real provider behind a `OpenAIEmbed` adapter gated by `OPENAI_API_KEY` and a `--live-embed` flag.
3. **Generation provider**: real OpenAI Responses API vs. deterministic scripted adapter. Recommendation: real provider behind a feature flag, scripted adapter for unit tests.
4. **Token accounting**: `len(text)` (stdlib only) vs. `tiktoken` (new governance entry). Recommendation: `len(text)` for Phase 1; add `tiktoken` later if needed.
5. **In-memory index data structure**: pure-Python cosine similarity over dense vectors (requires either numpy or a hand-rolled dot product) vs. BM25-like lexical scoring (stdlib only) vs. exact keyword overlap (simplest). Recommendation: exact keyword overlap for Phase 1; revisit in Phase 4 when hybrid retrieval arrives. This keeps the diff stdlib-only and trivially testable.
6. **Sensitive screen**: implement the high-confidence regex heuristic in this change or defer to Phase 8? Recommendation: implement the basic high-confidence block in Phase 1 because the pipeline runs against public OpenAI, and the architecture document names the per-request gate as part of the Phase 1 contract. Phase 8 can extend it.
7. **Single PR vs. chained PRs**: confirm `ask-before-splitting` is still the right call after the proposal's `sdd-tasks` forecast.
8. **Strict TDD re-evaluation**: confirm `strict_tdd: false` is preserved for the slice, or upgrade selectively.

## Ready for Proposal

Yes, conditional on the user answering the eight decision questions above. The repository state, governance baseline, evaluation-dataset foundation, domain contract, and test-harness gate are all ready. The orchestrator can launch `sdd-propose` once the user answers the decisions; the proposal should lock the choices into a bounded change that re-evaluates Strict TDD, keeps the cross-phase safety invariants, uses the approved `openai` governance entry, and stays inside the 400-line review budget by chaining if the forecast crosses the threshold.
