# AGENTS.md — OpsKnowledge Contributor Contract

This file is the normative contract for every human or AI contributor working in the OpsKnowledge repository. It states what MUST NOT change without a new SDD change, what MUST hold in every commit, and where the authoritative details live. It links out instead of duplicating the roadmap and architecture docs.

## Instruction hierarchy

When sources conflict, the higher source wins:

1. **Rules** in this `AGENTS.md` (normative invariants).
2. **`RAG_ROADMAP.md`** (product boundary, phase ordering, cross-phase safety invariants).
3. **`docs/architecture/platform-architecture.md`** (logical/physical architecture, flows, mappings, traceability).
4. **SDD spec and design artifacts** in Engram (per-change requirements and decisions).

Lower sources may elaborate but never contradict higher sources. Any conflict is a defect: open an SDD change to reconcile.

## Durable architecture baseline

- **Shape:** feature-organized modular monolith with hexagonal boundaries. Each feature exposes `domain`, `application`, inbound adapters, and outbound adapters. Frameworks, providers, and infrastructure stay outside `domain` and `application`.
- **One process, one database:** PostgreSQL owns all durable state. No microservices, queues, Redis, or Kubernetes in the prototype.
- **Monorepo:** backend, web, tests, compose, and docs share one repository. Runtime source, package manifests, and lockfiles belong to bounded implementation changes, not to this baseline change.
- **Excluded dependencies:** LangChain, LlamaIndex, streaming, visual interpretation, email/Notifier, and unevidenced reranking. Do not introduce them.

Changing the shape, splitting the monolith, or adding an excluded dependency requires a new SDD change.

## Safety, evidence, and escalation invariants

These are non-negotiable and inherited from `RAG_ROADMAP.md` cross-phase safety invariants:

- Safety and traceability outrank answer coverage.
- Every technical claim requires a valid citation from a current approved entry.
- Unsupported, out-of-scope, and contradictory cases abstain and recommend a human expert.
- Retrieval is filtered to the query language before evidence reaches the model.
- Conversation history, glossary entries, support history, and model knowledge are never answer evidence.
- Images are not interpreted; only extracted OCR text may be considered, with explicit provenance and quality controls.
- Patient-specific analysis is out of scope.
- No partial index may become active.
- **Provider failure:** when the configured generation or embedding provider is unavailable (timeout, rate limit, or outage), the system abstains, returns `unavailable`, recommends a human expert, persists no answer, and never fabricates evidence. Only idempotent operations have bounded retries; generation is not retried past a bounded timeout.

## Prototype vs corporate boundaries

Two distinct boundaries MUST stay separate:

1. **Development-only synthetic corpus exception.** A development profile MAY ingest manifest-controlled PDFs listed as `{path, sha256, classification=synthetic}`. They are visibly non-corporate, cannot be wired outside the `development` profile, and never migrate into a corporate index. Startup fails outside `development`; CI proves the denial.
2. **Accepted public-OpenAI free-text demo risk.** The public-OpenAI prototype MAY accept free-text questions, using ONLY synthetic manifest documents and fragments. The architecture SHALL NOT claim that arbitrary user-entered question text is provably synthetic. A high-confidence sensitive screen runs before any embedding or generation; rejected payloads do not persist. The UI shows explicit demo warnings and a visible non-corporate demo policy. Identities and environment are demo-only.

These are two separate concerns. Do not merge them, do not generalize the synthetic-corpus exception into the accepted-risk mode, and do not describe the free-text path as "synthetic queries."

**Corporate boundary:** corporate users, corporate data, and the corporate MVP free-text path MUST NOT use the public-OpenAI demo mode. Corporate MVP free text uses Azure OpenAI or another approved controlled provider. Document and chunk egress is always synthetic-only in the prototype and corporate-controlled in the MVP.

## Security, authorization, data, and logging

- **Identity:** development uses a development-only identity. Corporate MVP validates OIDC tokens by signature, issuer, audience, and a single allowed tenant. A versioned Entra-group-to-internal-role mapping drives authorization. Service calls use Managed Identity; egress is deny-by-default with private endpoints.
- **Authorization:** protected use cases are deny-by-default and audited. Authorization runs before identified records or restricted operations are returned.
- **Sensitive data:** a high-confidence sensitive screen blocks matching payloads before model processing or storage. Record only the blocking event, never the sensitive text.
- **Logging:** JSON logs only. Log safe fields (timestamps, actor roles, action types, outcomes, durations). NEVER log content, question text, answer text, citations, tokens, secrets, credentials, or provider payloads.
- **TI gates:** concrete tenant, group, region, endpoint, and network values are TI-gated. Do not invent them. Corporate deployment is blocked until TI gates are met.

## Index concurrency, revocation, and atomic persistence

- **Lock contention:** sync, publication, and rollback run inside `pg_try_advisory_xact_lock`. Contention immediately returns HTTP 409 `index_operation_busy` with no hidden retries.
- **Idempotency:** publication idempotency keys prevent duplicates; replay returns the prior committed result.
- **Schema invariant:** at most one `ACTIVE` and one `PREVIOUS` IndexVersion.
- **Cleanup:** runs after commit, is retryable, and abandoned builds recover without invalidating a committed active index.
- **Revocation:** removed documents are removed completely from retrieval. Revocation is rechecked during publish and rollback.
- **Query durability:** after authorization, screening, and generation, ONE PostgreSQL transaction persists question, outcome, answer, citations, session activity/count, and the analytical record. The API responds only after commit. Persistence failure returns `unavailable` and exposes no answer.

## Sessions and retention

- Active conversation context is kept only in the active session. It is not reader-visible across sessions.
- Inactivity expiration deletes usable conversation context while preserving authorized analytical records.
- Retention stores question text, answer, sources, revisions, feedback, and corporate identity for 12 months, then removes query content and user association, keeping only non-reconstructable aggregate metrics.
- Administrative audit records are retained for 12 months.
- Temporal behavior (five-minute warning, explicit extension, 20-question limit, inactivity expiration, 12-month cutoff, idempotent retry/failure) is tested with a `Clock` protocol: `SystemClock` in production, `FrozenClock` in CI.
- **Retention job ownership and recovery:** retention and cleanup jobs are retryable, run after commit, and never block the query durability transaction. They share the `pg_try_advisory_xact_lock` discipline with index operations when they mutate shared state, and recover abandoned builds without invalidating a committed active index.
- **Safe observability (future):** safe logical metrics, traces, and latency budgets (query outcomes, provider timeout/rate-limit/outage, index-lock contention, job attempt/failure/recovery, p95 latency) use only safe labels (outcome, operation, provider class, language, version); they never log content, citations, tokens, secrets, or payloads. Administrator alert routing and release gates are future Phase 9 implementation requirements, not current runtime claims.

## Dependency governance

- Direct production dependencies are recorded in `governance/direct-dependencies.yaml` with `name`, `scope`, `purpose`, `owning feature`, `license`, `risk`, and `approval decision`.
- That file is review EVIDENCE, not an allowlist. CI reconciles it with `pyproject.toml`/`package.json` and `uv.lock`/`pnpm-lock.yaml` and rejects unrecorded direct production dependencies.
- Do not fabricate manifests, lockfiles, or approval metadata. Where no decision exists, the file records the schema and instructions only.

## Testing, CI, and OpenAPI

- **Bootstrap invariant (future):** when a runtime stack exists, `make ci` SHALL restore locks, reconcile dependency evidence, and run Ruff, Pyright, unit, architecture, integration, OpenAPI/client drift, focused-test prohibition, vulnerability, and license checks. No runtime stack, test runner, `Makefile`, or CI pipeline exists yet; this is a mandatory bootstrap gate for the first implementation change, not a current capability.
- No runtime stack or test runner exists yet. Implementation changes must establish the test harness first, then re-evaluate Strict TDD.
- **OpenAPI (future):** FastAPI SHALL generate the canonical OpenAPI artifact at `apps/api/openapi/openapi.json` and the TypeScript client at `apps/web/src/api/generated.ts`; CI SHALL check for client drift once the bootstrap exists. Drift direction is FastAPI → OpenAPI artifact (`apps/api/openapi/openapi.json`) → TypeScript client (`apps/web/src/api/generated.ts`). These are future bootstrap acceptance gates, not current capabilities.

## Changes requiring SDD

A new SDD change is REQUIRED before:

- Changing the modular-monolith shape or splitting the process.
- Adding an excluded dependency (LangChain, LlamaIndex, streaming, visual interpretation, email/Notifier, unevidenced reranking, Redis, queues, Kubernetes, microservices).
- Crossing the prototype/corporate boundary or changing the synthetic-corpus exception.
- Changing index lifecycle locking, idempotency, or the one-transaction query durability rule.
- Changing the authorization model, OIDC contract, or logging safe-field policy.
- Introducing corporate Azure integrations (SharePoint via Graph, Entra, Azure OpenAI) before TI gates are met.
- Any change to the cross-phase safety invariants in `RAG_ROADMAP.md`.

Do not create one change named `build-complete-rag-platform`. Prefer bounded, independently reversible changes with explicit acceptance criteria.

## Where to look

- Product boundary, phases, and cross-phase safety invariants: `RAG_ROADMAP.md`
- Architecture diagrams, module tree, data model, flows, Azure mapping, risk register, traceability: `docs/architecture/platform-architecture.md`
- Dependency governance template: `governance/direct-dependencies.yaml`
- SDD artifacts per change: Engram topics `sdd/<change-name>/{proposal, spec, design, tasks}`

## Contract supersession

The prior dental-domain SDD change `define-dental-guidance-domain-and-corpus` is superseded by `reposition-rag-as-portfolio-platform`. Historical artifacts (Engram #3122, #3125, #3133, #3134) are retained as audit history, are never deleted, and are linked from `RAG_ROADMAP.md` (Phase 0 completion notes) and `docs/architecture/platform-architecture.md` (Traceability). The successor artifacts are Engram #3226, #3227, #3228, #3229. The immutable supersession index is `openspec/changes/reposition-rag-as-portfolio-platform/supersession-index.md`.

## Secrets and transient content

This file MUST NOT contain secrets, credentials, tokens, tenant IDs, region names, endpoint URLs, or transient conversation. If a value is TI-gated, it lives in a secured config, never here.