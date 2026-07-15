# OpsKnowledge Platform Architecture

This document is the authoritative architecture reference for the OpsKnowledge platform. It records the logical and physical structure, module ownership, data model, flows, port contracts, topology, Azure migration mapping, risks, and traceability. It elaborates — and must never contradict — `AGENTS.md` and `RAG_ROADMAP.md`.

**How to read this document:** start with [Architecture overview](#architecture-overview) for the shape and boundaries, then jump to the flow or section relevant to your change. Every architectural decision here is traceable to a roadmap invariant or an SDD decision (see [Traceability](#traceability)).

## Architecture overview

| Aspect | Decision | Source |
|--------|----------|--------|
| Shape | Feature-organized modular monolith with hexagonal boundaries | `AGENTS.md` durable baseline; design #3163 |
| Process | One process, one database (PostgreSQL) | `AGENTS.md` durable baseline |
| Repository | Monorepo: backend, web, tests, compose, docs | proposal #3161 |
| Corporate data source | Approved versioned entries (`runbooks`, `adrs`, `operational-policies`) | `RAG_ROADMAP.md` Phase 3; spec #3162 |
| Prototype corpus | Development-only manifest-controlled synthetic technical entries | spec #3162; `RAG_ROADMAP.md` product boundary |
| Prototype generation | Public OpenAI (Responses API, `text-embedding-3-small`) as accepted risk | spec #3162 (Public-OpenAI Free-Text Accepted-Risk Boundary) |
| Corporate generation | Azure OpenAI or another approved controlled provider | spec #3162; `RAG_ROADMAP.md` Phase 8 |
| Excluded | LangChain, LlamaIndex, streaming, visual interpretation, email/Notifier, unevidenced reranking, Redis, queues, Kubernetes, microservices | `AGENTS.md`; design #3163 |

### Logical architecture

```text
                            ┌─────────────────────────────────────────────┐
                            │                  Inbound adapters            │
                            │  FastAPI HTTP  ·  Admin CLI  ·  React SPA    │
                            └───────────────┬──────────────┬─────────────┘
                                            │              │
                            ┌───────────────▼──────────────▼─────────────┐
                            │              Application (use cases)         │
                            │  Query  ·  Indexing  ·  Session  ·  Governance │
                            │  Authorize ·  Screen ·  Clock ·  Persist      │
                            └───────────────┬──────────────┬─────────────┘
                                            │              │
                            ┌───────────────▼──────────────▼─────────────┐
                            │                  Domain                      │
                             │  Corpus ·  Entry ·  Fragment ·  Embedding     │
                             │  IndexVersion ·  Session ·  Question ·  Answer│
                             │  Citation ·  Outcome ·  Policy ·  Alert       │
                             └───────────────┬──────────────┬─────────────┘
                                             │              │
                             ┌───────────────▼──────────────▼─────────────┐
                             │               Outbound adapters              │
                             │  PostgreSQL/pgvector ·  OpenAI ·  Docling    │
                             │  Approved Source (corporate) ·  Entra (corp) │
                             └─────────────────────────────────────────────┘
```

Dependency direction is strictly inward: adapters depend on application and domain; application depends on domain; domain depends on nothing inward. Frameworks, providers, and infrastructure never appear inside `domain` or `application`.

### Physical architecture (prototype — target/planned)

**Status:** This is a TARGET/PLANNED architecture, not a deployed system. No runtime stack, FastAPI app, web client, database instance, or Docker Compose orchestration exists yet. The diagrams and component descriptions below define the intended topology for future bounded implementation changes, not a current capability (see `AGENTS.md` testing/CI/OpenAPI section; testing baseline #3111).

**Gate ordering (critical):** request → sensitive screen → per-request environment + demo-identity gate → provider egress. Sensitive screening and the demo gate run BEFORE persistence and BEFORE any provider call. PostgreSQL owns all durable state but is NOT an inline hop to OpenAI — it persists results after commit and serves retrieval, it never calls OpenAI and is never on the egress path.

```text
┌──────────────────────────────────────────────────────────────────┐
│ Developer workstation (development profile only)                │
│                                                                  │
│  ┌──────────┐   ┌──────────┐   ┌───────────────────────────────┐ │
│  │  React    │   │  FastAPI │   │  Admin CLI                      │ │
│  │  (Vite)   │──▶│  (uvicorn)│◀──│  (local ingestion)             │ │
│  └──────────┘   └─────┬────┘   └───────────────┬───────────────┘ │
│                       │                          │                 │
│                       ▼                          ▼                 │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ Sensitive screen (pre-filter, runs BEFORE persistence/egress)│ │
│  │ → blocks high-confidence sensitive payloads                  │ │
│  │ → rejected payloads do NOT persist; log event only           │ │
│  └──────────────────────────┬───────────────────────────────────┘ │
│                             ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ Per-request environment + demo-identity gate                 │ │
│  │ → checks environment + demo identity immediately before      │ │
│  │   EVERY public-OpenAI embeddings and generation call         │ │
│  │ → failed gate prevents the provider invocation               │ │
│  └──────────────────────────┬───────────────────────────────────┘ │
│                             ▼ (demo profile only)                  │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ Public OpenAI (demo only)                                     │ │
│  │ Responses API · text-embedding-3-small                        │ │
│  │ Egress deny-by-default; synthetic documents/fragments only    │ │
│  │ No content logging; demo-only identities                      │ │
│  └──────────────────────────┬───────────────────────────────────┘ │
│                             │ (after generation, one transaction)  │
│                             ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ PostgreSQL + pgvector (all durable state, single DB)          │ │
│  │ → persists question/outcome/answer/citations/session/analytical│ │
│  │ → serves retrieval from ACTIVE IndexVersion; never calls OpenAI│ │
│  │ → NOT an inline hop to the provider                           │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ── DEMO / CORPORATE BOUNDARY (visible) ──────────────────────   │
│  Corporate MVP: Azure OpenAI + validated OIDC + private endpoints │
│  → public OpenAI is NEVER used for corporate data or queries      │
└──────────────────────────────────────────────────────────────────┘
```

One process, one database, one developer identity. Docker Compose orchestrates the prototype locally. No Redis, no queues, no Kubernetes, no microservices. The sensitive screen and per-request demo gate run before persistence and before provider egress; PostgreSQL persists results after commit and serves retrieval — it is never on the OpenAI egress path. Corporate access crosses the demo/corporate boundary to Azure OpenAI with validated OIDC and private endpoints. The components above are PLANNED; none is deployed or running today.

## Backend demo environment and identity gate

The development-only synthetic corpus exception is enforced at the backend, not only by convention:

| Gate | Enforcement | Source |
|------|-------------|--------|
| Profile startup check | The `development` profile is the ONLY profile that may wire the local file adapter and synthetic corpus. Startup fails outside `development` if synthetic-corpus wiring is present. | `AGENTS.md` prototype/corporate boundaries; spec #3162 |
| CI denial | CI proves the denial: a non-`development` profile that attempts to wire synthetic corpus fails the build. No partial synthetic index may become active outside `development`. | `AGENTS.md`; spec #3162 |
| Corporate boundary | Corporate users, corporate data, and the corporate MVP free-text path MUST NOT use the public-OpenAI demo mode. Corporate MVP free text uses Azure OpenAI or another approved controlled provider. | `AGENTS.md` corporate boundary; `RAG_ROADMAP.md` Phase 8 |

The backend demo gate is distinct from the accepted public-OpenAI free-text demo risk (see [Accepted demo free-text risk](#accepted-demo-free-text-risk)). The gate controls which corpus may be wired; the accepted risk controls which provider may receive free-text questions. Do not merge them.

## Per-request environment and demo-identity gate ordering

The backend MUST evaluate the per-request environment check and demo-identity gate **immediately before every public-OpenAI embeddings and generation call**, not once per request. The canonical ordering is:

```text
request → authorize/policy → sensitive screen → (retrieval) →
per-request environment + demo-identity gate → provider egress (embeddings or generation) →
one PostgreSQL transaction (after commit) → JSON response
```

| Step | What it checks | Failure behavior |
|------|----------------|------------------|
| Sensitive screen | High-confidence sensitive patterns; runs before persistence and before provider egress | Rejected payload does NOT persist; only a safe blocking event is logged |
| Per-request environment + demo-identity gate | Environment is the demo/public-OpenAI profile AND identity is demo-only, evaluated immediately before each provider call | Failed gate prevents that specific OpenAI invocation; no embedding or generation is sent |
| Provider egress | Public OpenAI (demo) or Azure OpenAI (corporate) | Provider failure → `unavailable`, no answer, no fabrication |
| Persistence | ONE PostgreSQL transaction after generation, only after commit | Persistence failure → `unavailable`, no answer exposed |

PostgreSQL owns all durable state but is **never** an inline hop to OpenAI: it persists the committed result and serves retrieval; it does not sit on the egress path and does not call the provider. The gate is re-evaluated before each provider call because a single request may trigger both an embeddings call and a generation call, and an ingestion operation may trigger multiple embeddings calls.

## Monorepo tree

The tree below is the target layout. Runtime source, package manifests, and lockfiles are produced by bounded implementation changes, not by this planning change. This document defines ownership and boundaries, not file creation.

```text
RAG/
├── AGENTS.md                         # Normative contributor contract
├── RAG_ROADMAP.md                    # Product boundary, phases, safety invariants
├── governance/
│   └── direct-dependencies.yaml      # Dependency governance evidence
├── docs/
│   └── architecture/
│       └── platform-architecture.md  # This document
├── backend/                          # FastAPI/Python modular monolith (future)
│   ├── features/
│   │   ├── query/                     # domain · application · adapters
│   │   ├── indexing/                  # domain · application · adapters
│   │   ├── session/                   # domain · application · adapters
│   │   ├── governance/               # domain · application · adapters
│   │   └── corpus/                    # domain · application · adapters
│   └── shared/                        # cross-cutting ports, Clock, Authorize
├── web/                              # React/TypeScript/Vite SPA (future)
├── tests/                            # unit, architecture, integration, acceptance
└── compose/                          # Docker Compose orchestration (future)
```

## Module ownership

| Feature | Owns (domain) | Owns (application) | Inbound adapters | Outbound adapters |
|---------|---------------|--------------------|------------------|-------------------|
| `corpus` | Entry, Fragment, Embedding, Provenance, Revocation | Manifest validation, hash check, provenance assignment | Admin CLI (ingestion) | Docling parser, local file adapter (development-only) |
| `indexing` | IndexVersion, IndexRun, IndexOperation | Sync, build, publish, rollback, cleanup, revocation recheck | Admin CLI (sync/publish/rollback) | PostgreSQL/pgvector, Approved Source (corporate) |
| `query` | Question, Answer, Citation, Outcome, Result | Screen, authorize, retrieve, generate, persist | FastAPI HTTP (query endpoint) | OpenAI (prototype) / Azure OpenAI (corporate), pgvector retriever |
| `session` | Session, SessionActivity, SessionCount | Warning, extension, 20-question limit, inactivity expiry | FastAPI HTTP (session endpoints) | PostgreSQL |
| `governance` | Policy, PolicyAcceptance, Actor, Action, Resource, Alert | Authorize, sensitive screen, contradiction alert, audit | FastAPI HTTP (ops panel) | Entra (corporate), PostgreSQL |

PostgreSQL owns all durable state across every feature. No feature owns its own database.

## Conceptual data model

```text
┌──────────────┐  1   N ┌──────────────┐  1   N ┌──────────────────┐
│ Entry        │───────▶│ Fragment     │───────▶│ Embedding         │
│ id           │        │ id           │        │ id                │
│ collection   │        │ entry_id     │        │ fragment_id       │
│ (runbooks/   │        │ language     │        │ vector (pgvector) │
│  adrs/       │        │ section/page │        │ model             │
│  operational-│        │ text         │        └──────────────────┘
│  policies)   │        │ provenance   │
│ revision     │        │ ocr_mark     │
│ version      │        │ revocation   │
│ approval     │        └──────────────┘
│ file_name    │
│ source       │
│ (approved-   │
│  source/     │
│  synthetic)  │
│ classification│
└──────────────┘

┌──────────────┐  1   N ┌──────────────────┐  1   N ┌──────────────────┐
│ IndexVersion │───────▶│ IndexRun         │───────▶│ IndexOperation    │
│ id           │        │ id               │        │ id                │
│ state        │        │ version_id       │        │ run_id            │
│ (BUILDING/   │        │ started/finished │        │ type              │
│  ACTIVE/     │        │ outcome          │        │ idempotency_key   │
│  PREVIOUS)   │        └──────────────────┘        │ result            │
└──────────────┘                                      └──────────────────┘
unique(IndexVersion where state=ACTIVE)   max 1
unique(IndexVersion where state=PREVIOUS) max 1

┌──────────────┐  1   N ┌──────────────────┐  1   N ┌──────────────────┐
│ Session      │───────▶│ SessionActivity  │        │ Question          │
│ id           │        │ session_id       │        │ id                │
│ actor        │        │ type/count       │        │ session_id        │
│ started/last │        └──────────────────┘        │ text (retained)   │
│ expired      │                                     │ language          │
└──────────────┘                                     │ outcome           │
                                                     └────────┬─────────┘
                                                              │ 1
                                                              │
                                              ┌───────────────▼───────────────┐
                                              │ Answer · Citation · Analytical │
                                              │ answer · citations[] · retained │
                                              └───────────────────────────────┘

┌──────────────┐        ┌──────────────────┐        ┌──────────────────┐
│ Policy       │ 1   N  │ PolicyAcceptance │        │ Alert            │
│ version      │───────▶│ actor/version/ts │        │ id               │
│ active       │        └──────────────────┘        │ fragments/revisions │
└──────────────┘                                     │ state (open/     │
                                                     │  resolved/dismissed)│
                                                     │ panel-only       │
                                                     └──────────────────┘
```

Key invariants on this model:

- `Entry.collection` is one of `runbooks`, `adrs`, `operational-policies`. Each entry MUST carry a version, approval status, and synthetic classification when not corporate.
- `Entry.source` is `approved-source` (corporate) or `synthetic` (development-only). Synthetic entries never migrate into a corporate index.
- `Embedding.model` records which provider produced the vector; retrieval filters by language and provenance before ranking.
- `IndexVersion` enforces at most one `ACTIVE` and one `PREVIOUS` via partial unique constraints.
- `Question.text` is retained for 12 months, then stripped; the analytical record survives as non-reconstructable aggregate metrics.
- `Alert` is panel-only: contradiction alerts are visible and managed only in the operations panel, never delivered to readers and never sent by email/Notifier.

## Query flow

```text
HTTP request (free-text question)
    │
    ▼
authenticate (development identity / corporate OIDC)
    │
    ▼
authorize — deny-by-default, audited; runs before identified records or
    │           restricted operations are returned
    ▼
policy acceptance gate — block until current version accepted
    │
    ▼
sensitive screen — high-confidence patterns; rejected payloads do NOT persist;
    │                record only the blocking event
    ▼
language detection — filter retrieval to the query language
    │
    ▼
active index + revocation filter — retrieve from ACTIVE IndexVersion only;
    │                               remove revoked fragments before ranking
    ▼
retrieve (pgvector similarity + metadata filters)
    │
    ▼
outcome validation — supported / insufficient_information /
    │                  contradictory_information / out_of_scope
    ▼
per-request environment + demo-identity gate — evaluated immediately before
    │   EVERY public-OpenAI generation call; a failed gate prevents the
    │   invocation (environment is not demo-only or identity is not demo-only)
    ▼
generate (OpenAI Responses API, prototype; Azure OpenAI, corporate)
    │
    ▼
ONE PostgreSQL transaction persists:
    question · outcome · answer · citations · session activity/count · analytical record
    │
    ▼
JSON response (only after commit)
```

**Failure rules:**

- Persistence failure → API returns `unavailable`, exposes NO answer, nothing persists.
- Idempotency key replay → returns the prior committed result, no duplicate writes.
- Authorization denial → HTTP 403; persists nothing, is logged as an audited access-control event; creates NO resolved query outcome. Authorization runs before query resolution, so a denied request never enters the outcome taxonomy.
- Session expired → returns `session_expired`, no answer.
- **Provider failure/unavailable:** when the configured generation or embedding provider is unavailable (timeout, rate limit, or outage), the system abstains, returns `unavailable`, recommends a human expert, persists NO answer, and never fabricates evidence. Only idempotent operations have bounded retries; generation is NOT retried past a bounded timeout. A timeout is never replaced with an ungrounded answer.

**Six-state outcome taxonomy (canonical):** every resolved query SHALL classify into one of `supported`, `insufficient_information`, `contradictory_information`, `out_of_scope`, `unavailable`, `session_expired`. Provider failure and persistence failure SHALL resolve to `unavailable`. Session inactivity SHALL resolve to `session_expired`. No ad-hoc statuses.

## Ingestion and index flow

```text
Admin CLI command (sync / publish / rollback)
    │
    ▼
pg_try_advisory_xact_lock — acquired at OPERATION ENTRY, BEFORE any
    │                       scan, parse, embedding, build, publication,
    │                       or rollback work — for every sync, publish,
    │                       and rollback operation
    │
    ├─ not acquired → HTTP 409 index_operation_busy
    │                  (no hidden retries, immediate return)
    │
    └─ acquired → continue below
          │
          ▼
manifest validation — reject unlisted, hash-mismatched, non-synthetic,
    │                    or corporate-derived files
    ▼
parse (Docling) — structure-aware chunks; OCR marked with provenance + quality
    │
    ▼
synthetic fragments — assign `synthetic` provenance; development-only
    │
    ▼
provider guard — reject any corporate-classified document/fragment/identity
    │               before egress in the prototype
    ▼
per-request environment + demo-identity gate — evaluated immediately before
    │   EVERY public-OpenAI embeddings call; a failed gate prevents the
    │   invocation
    ▼
embeddings (Public OpenAI text-embedding-3-small, demo only)
    │
    ▼
revocation recheck → publish / rollback → commit → cleanup (post-commit, retryable)
```

**Lock scope:**

- `pg_try_advisory_xact_lock` is acquired at the START of every index operation (sync, publish, rollback), BEFORE any source scan, parsing, embedding, build, publication, or rollback work. The lock is acquired at operation entry only — there are no mid-operation lock upgrades or hidden retries.
- On contention, the operation immediately returns HTTP 409 `index_operation_busy`. There are no silent retries, no queuing, and no partial concurrency. The caller decides whether to retry.

**Invariants:**

- At most one `ACTIVE` and one `PREVIOUS` IndexVersion.
- Publication idempotency keys prevent duplicates; replay returns the prior committed result.
- Cleanup runs after commit and is retryable; abandoned builds recover without invalidating a committed active index.
- Revocation is rechecked during publish and rollback; removed documents are removed completely from retrieval.
- The local file adapter wires ONLY under the `development` profile; startup fails elsewhere and CI proves the denial.

## Session flow

```text
conversation start
    │
    ▼
Session created — active context kept only in the active session
    │
    ▼
each turn — re-evaluate evidence; history helps interpret but is never evidence
    │
    ▼
20-question limit → require new conversation (no sign-out)
    │
    ▼
five-minute warning before inactivity expiration
    │
    ▼
explicit extension (allowed) OR inactivity expiration
    │
    ▼
expiration → delete usable conversation context; preserve authorized analytical records
```

Temporal behavior is tested with a `Clock` protocol: `SystemClock` in production, `FrozenClock` in CI. Separate CI cases assert both visible outcome and persisted state for: five-minute warning, explicit extension, 20-question limit, inactivity expiration, 12-month retention cutoff, and idempotent retry/failure.

## Port contracts

These are the TARGET/planned stable abstractions that keep providers replaceable. No implementations exist yet — the protocols define the intended contracts for future bounded implementation changes. Implementations will belong to outbound adapters; domain and application will depend only on the protocols.

```python
class Clock(Protocol):
    def now(self) -> datetime: ...

class Authorize(Protocol):
    def check(self, actor: Actor, action: Action, resource: Resource) -> None: ...

class Retrieve(Protocol):
    def search(self, query: str, language: Language, index_version: IndexVersionId) -> list[Fragment]: ...

class Generate(Protocol):
    def answer(self, question: str, evidence: list[Fragment], language: Language) -> Answer: ...

class Embed(Protocol):
    def vectorize(self, text: str) -> Vector: ...

class ParsePdf(Protocol):
    def parse(self, path: Path, provenance: Provenance) -> list[Fragment]: ...

class Persist(Protocol):
    def commit_query(self, record: QueryRecord) -> None: ...
```

FastAPI exposes non-streaming JSON models for queries, sessions, retained history, index commands, alert state, and policy acceptance. HTTP-level rejection results include HTTP 403 (authorization denial, audited, no resolved query outcome) and HTTP 409 `index_operation_busy`. Resolved-query outcome results are exactly the six canonical states: `supported`, `insufficient_information`, `contradictory_information`, `out_of_scope`, `unavailable`, `session_expired`. Session-level results include `session_expired`. No seventh outcome exists; `denied` is an HTTP 403 access-control rejection, not a resolved-query outcome.

### Canonical OpenAPI artifact and client paths (future bootstrap)

The canonical OpenAPI artifact and TypeScript client paths are FUTURE — no runtime, FastAPI app, or web client exists yet. These paths are committed now so successor bootstrap changes have a fixed target; they are not a current capability.

| Property | Canonical path | Status |
|----------|----------------|--------|
| OpenAPI artifact | `apps/api/openapi/openapi.json` | Future — produced by FastAPI once the bootstrap exists |
| TypeScript client | `apps/web/src/api/generated.ts` | Future — generated from the OpenAPI artifact |
| Drift direction | FastAPI → `apps/api/openapi/openapi.json` → `apps/web/src/api/generated.ts` | Future — CI SHALL regenerate both and fail on uncommitted diffs once the bootstrap exists |
| Drift check | CI SHALL check for client drift once the bootstrap exists | Future bootstrap acceptance gate, not a current capability |

Drift direction is strictly one-way: FastAPI generates the OpenAPI artifact, the artifact generates the TypeScript client. The client is never hand-edited; edits flow back through FastAPI and the artifact. No current runtime claim is made — these are future bootstrap acceptance gates.

## Prototype topology (target/planned)

The table below describes the TARGET/planned prototype topology. No runtime stack currently exists — these are the intended components for future bounded implementation changes, not a deployed system.

| Component | Prototype (target/planned) |
|-----------|----------------------------|
| Runtime | FastAPI/uvicorn single process |
| Database | PostgreSQL + pgvector (single instance) |
| Generation | Public OpenAI Responses API + `text-embedding-3-small` |
| Corpus | Development-only manifest-controlled synthetic technical entries |
| Ingestion | Admin CLI invoking local file adapter (development-only) |
| Identity | Development-only identity |
| Logging | JSON logs, safe fields only |
| Orchestration | Docker Compose |
| Client | React/TypeScript/Vite SPA |
| Egress | Synthetic-only documents and fragments; high-confidence sensitive screen |

## Prototype → Azure mapping and TI gates (target/planned)

The mappings below describe the TARGET/planned migration from the (also not-yet-deployed) prototype topology to the corporate MVP. Neither side is currently deployed.

| Prototype | Corporate MVP | TI gate |
|-----------|---------------|---------|
| Compose / CLI / images | Container Apps / Jobs / ACR | Subscription, region, capacity |
| PostgreSQL + pgvector | Flexible Server + pgvector | pgvector availability, region, capacity |
| Public OpenAI + local synthetic corpus | Azure OpenAI + Approved Source via Graph | Azure OpenAI approval, Graph/Entra permissions |
| Development identity + JSON logs | Entra ID + OpenTelemetry + App Insights + Log Analytics | Tenant, group IDs, owners, membership rules |
| Compose environment | Managed Identity + Key Vault + Bicep | Private networking, budget, ownership |

**TI gates are blocking.** Concrete tenant, group, region, endpoint, and network values are TI-gated and SHALL NOT be invented. Corporate deployment is blocked until all TI gates are met. No corporate Azure integration is introduced before TI clearance.

## Risk register

| Risk | Likelihood | Impact | Mitigation | Source |
|------|-----------|--------|------------|--------|
| Baseline becomes implementation | Medium | Medium | Separate bounded implementation SDD changes | proposal #3161 |
| Provider/data boundary breach | Medium | High | Ports; synthetic/authorized demo data only; provider guard | proposal #3161; spec #3162 |
| Roadmap mismatch (alert delivery) | Medium | Medium | Panel-only alerts preserved; Notifier/email excluded | proposal #3161; `RAG_ROADMAP.md` Phase 4 |
| Free-text query mistaken for synthetic | Medium | High | Architecture SHALL NOT claim question text is provably synthetic | spec #3162 |
| Sensitive data leakage | Low | High | High-confidence screen; rejected payloads do not persist; log event only | spec #3162; `RAG_ROADMAP.md` Phase 8 |
| Partial index becomes active | Low | High | Partial unique constraints; lock contention returns 409 | spec #3162; design #3163 |
| Unrecorded direct dependency | Medium | Medium | CI reconciliation against manifests/lockfiles | spec #3162; `AGENTS.md` |
| TI-gated values invented | Low | High | TI gates block corporate deployment; no invented values | design #3163 |

## Accepted demo free-text risk

This is a SEPARATE concern from the development-only synthetic corpus exception. Do not merge them.

| Concern | Boundary | Data egress | Identity | Provider | Corporate use |
|---------|----------|-------------|----------|----------|---------------|
| Development-only synthetic corpus exception | `development` profile only; startup fails elsewhere; CI proves denial | Synthetic manifest documents and fragments only | Development-only | n/a | Never |
| Accepted public-OpenAI free-text demo risk | Prototype/demo environment only; UI shows explicit demo warnings and non-corporate demo policy | Synthetic-only documents and fragments; high-confidence sensitive screen before any embedding or generation; rejected payloads do not persist | Demo-only identities | Public OpenAI | Never; corporate MVP free text uses Azure OpenAI or another approved controlled provider |

**Critical distinction:** the architecture SHALL NOT claim that arbitrary user-entered question text is provably synthetic. The free-text path is an accepted demo risk, not a synthetic query. Document and chunk egress remains synthetic-only.

**Honest residual risk:** the public-OpenAI prototype accepts free-text questions from users. Arbitrary user-entered question text is NOT provably synthetic — a user MAY type sensitive or non-synthetic text that reaches the public provider. To bound (not eliminate) this risk:

- A high-confidence sensitive screen runs BEFORE any embedding or generation. It blocks high-confidence sensitive payloads; it does not promise perfect detection.
- Rejected payloads do NOT persist; only a safe blocking event is logged.
- The UI shows explicit demo warnings and a visible non-corporate demo policy on every screen.
- Identities and environment are demo-only.
- The accepted risk applies ONLY to the public-OpenAI demo profile. Corporate MVP free text MUST NOT use this path; it uses Azure OpenAI or another approved controlled provider.

This is an accepted demo risk, not a guarantee that no sensitive text can ever reach the public provider. The sensitive screen reduces likelihood; it does not provably eliminate leakage from free text.

## Excluded dependencies and surfaces

These are intentionally excluded and require a new SDD change before introduction:

- LangChain, LlamaIndex (framework-heavy orchestration)
- Streaming responses (non-streaming JSON only)
- Visual interpretation / image understanding as evidence
- Email / Notifier delivery (contradiction alerts are panel-only)
- Unevidenced reranking (MVP adds FTS + RRF; reranking only if evaluation proves value)
- Redis, queues, Kubernetes, microservices

No flow, adapter, or diagram in this document includes email or Notifier. Contradiction alerts are visible and managed only in the operations panel (see `RAG_ROADMAP.md` Phase 4 and `governance` module ownership above).

## Logical observability and latency budgets (future, Phase 9)

This section defines the LOGICAL observability surface. It is a future Phase 9 implementation requirement, NOT a current runtime claim. No metrics, traces, or alerting pipeline exists yet.

| Signal | Safe labels (allowed) | NEVER logged | Source |
|--------|-----------------------|--------------|--------|
| Query outcome | outcome, operation, provider class, language, version | content, question text, answer text, citations, tokens, secrets, payloads | design #3163; `AGENTS.md` safe observability |
| Provider health | timeout, rate-limit, outage (class only) | provider request/response bodies, keys | design #3163 |
| Index lock contention | operation, contention event, 409 count | corpus content, fragment text | `AGENTS.md` index concurrency |
| Job lifecycle | attempt, failure, recovery, operation | job payload content | design #3163; `AGENTS.md` retention job ownership |
| Latency | phase, p95, operation | content, token counts | design #3163 |

**Latency budgets (logical, to be implemented in Phase 9):**

- Client-send → UI immediate-feedback: measured from client send to visible processing indicator.
- Request-start → committed JSON response: measured from request start to the committed JSON response (after the one-transaction durability commit).
- Target: complete responses in under 10 seconds for at least 95% of normal queries (`RAG_ROADMAP.md` Phase 9).
- Target: visible processing feedback in under one second (`RAG_ROADMAP.md` Phase 9).

**Administrator alert routing (future):** administrator alert routing and release gates are future Phase 9 implementation requirements, not current runtime claims. No alert delivery mechanism exists in the prototype. Contradiction alerts are panel-only and are never sent by email/Notifier.

## Retention and cleanup job recovery

Retention and cleanup jobs are retryable, run after commit, and never block the query durability transaction. They share the `pg_try_advisory_xact_lock` discipline with index operations when they mutate shared state.

| Property | Rule | Source |
|----------|------|--------|
| Timing | Jobs run AFTER commit, never inside the query durability transaction. | `AGENTS.md` retention job ownership; design #3163 |
| Retry | Retries are idempotent and bounded; a retry produces the same result as the original. | design #3163 |
| Lock discipline | When a job mutates shared state, it acquires `pg_try_advisory_xact_lock` at operation entry, same as sync/publish/rollback. Contention returns 409; no hidden retries. | `AGENTS.md`; design #3163 |
| Abandoned build recovery | Abandoned builds recover WITHOUT invalidating a committed active index. Recovery re-establishes consistency from the last committed state. | `AGENTS.md` index cleanup; design #3163 |
| Auditability | Job attempts, failures, and recoveries are auditable and visible to administrators. | design #3163 |
| Active context | Inactivity expiration deletes usable conversation context while preserving authorized analytical records. | `AGENTS.md` sessions and retention |

The `RunRetention` protocol is the stable abstraction for retention batches:

```python
class RunRetention(Protocol):
    def run(self, now: datetime) -> JobResult: ...
```

An Admin CLI invokes retention batches in the prototype; an MVP scheduler invokes the same idempotent batches. `SystemClock`/`FrozenClock` preserve testability.

## Traceability

Spec #3162 rev8 defines exactly **7 requirements and 7 scenarios** for the platform-architecture contract. Spec #3227 defines **9 requirements and 9 scenarios** for the OpsKnowledge domain contract (`sdd/reposition-rag-as-portfolio-platform/spec`). The traceability table below maps all 7 legacy platform requirements plus all 9 OpsKnowledge requirements, preserving the legacy mappings where still relevant.

**Contract supersession:** the prior dental-domain SDD change `define-dental-guidance-domain-and-corpus` (Engram #3122, #3125, #3133, #3134) is superseded by `reposition-rag-as-portfolio-platform` (Engram #3226, #3227, #3228, #3229). Historical artifacts are retained as audit history and are never deleted. The immutable supersession index is `openspec/changes/reposition-rag-as-portfolio-platform/supersession-index.md`. Supersession relations are persisted via `engram_mem_compare` (sync IDs recorded in the index).

### Legacy platform-architecture traceability (spec #3162 rev8)

| # | Spec requirement (#3162 rev8, 7 requirements) | Design decision (#3163) | Roadmap invariant | This document |
|---|------------------------------------------------|------------------------|-------------------|---------------|
| 1 | Approved Versioned Collections and Isolated Development-Only Synthetic Exception | Canonical collections + development-only local entries | Product boundary; cross-phase invariant 1 | [Conceptual data model](#conceptual-data-model); [Ingestion and index flow](#ingestion-and-index-flow); [Accepted demo free-text risk](#accepted-demo-free-text-risk); [Backend demo environment and identity gate](#backend-demo-environment-and-identity-gate) |
| 2 | Public-OpenAI Free-Text Accepted-Risk Boundary | Prototype egress accepted risk; no synthetic claim; honest residual risk | Product boundary | [Accepted demo free-text risk](#accepted-demo-free-text-risk); [Query flow](#query-flow); [Physical architecture (prototype — target/planned)](#physical-architecture-prototype--targetplanned) |
| 3 | Index Lifecycle Locking, Idempotency, and Revocation | Index lifecycle lock/idempotency/cleanup; lock at operation entry | Cross-phase invariant 7 | [Ingestion and index flow](#ingestion-and-index-flow); [Conceptual data model](#conceptual-data-model); [Retention and cleanup job recovery](#retention-and-cleanup-job-recovery) |
| 4 | Query Durability and Provider Failure Behavior | Query durability one transaction | Cross-phase invariants 4, 8 | [Query flow](#query-flow); [Session flow](#session-flow); [Conceptual data model](#conceptual-data-model) |
| 5 | Identity, Authorization, Logging, and Azure Integration Contract | Corporate trust OIDC/Entra/Managed Identity | Phase 8 | [Port contracts](#port-contracts); [Prototype → Azure mapping](#prototype--azure-mapping-and-ti-gates-targetplanned) |
| 6 | Sessions, Retention, and Temporal Operation Contracts | Clock protocol; FrozenClock in CI; retention job recovery | Phase 6 data lifecycle | [Session flow](#session-flow); [Port contracts](#port-contracts); [Retention and cleanup job recovery](#retention-and-cleanup-job-recovery) |
| 7 | Architecture, Tooling, and Governance Contracts | Governance file as evidence, not allowlist; pending blocks production | `AGENTS.md` dependency governance | [Prototype topology](#prototype-topology-targetplanned); `governance/direct-dependencies.yaml` |
| — | (Roadmap-only, not a spec requirement) Panel-only contradiction alerts | Notifier/email excluded | Phase 4 source conflicts | [Module ownership](#module-ownership); [Excluded dependencies](#excluded-dependencies-and-surfaces) |

### OpsKnowledge domain-contract traceability (spec #3227, 9 requirements)

| # | Spec requirement (#3227) | Design decision (#3228) | Roadmap invariant | This document |
|---|--------------------------|------------------------|-------------------|---------------|
| OK1 | OpsKnowledge Identity | Terminology/boundary migration; titles use OpsKnowledge | Product boundary; `AGENTS.md` title | [Architecture overview](#architecture-overview); title |
| OK2 | Approved Versioned Collections | `runbooks`, `adrs`, `operational-policies`; version+approval+classification per entry | Product boundary; cross-phase invariant 1 | [Conceptual data model](#conceptual-data-model); [Ingestion and index flow](#ingestion-and-index-flow) |
| OK3 | Corpus Separation | Synthetic/corporate separation preserved; dev-only denial | `AGENTS.md` prototype/corporate boundaries; cross-phase invariant 1 | [Backend demo environment and identity gate](#backend-demo-environment-and-identity-gate); [Accepted demo free-text risk](#accepted-demo-free-text-risk) |
| OK4 | Bilingual Fragment Isolation | Fragment-level language tag; query-language filter before ranking | `AGENTS.md` safety; `RAG_ROADMAP.md` Phase 4; cross-phase invariant 2 | [Query flow](#query-flow); [Conceptual data model](#conceptual-data-model) |
| OK5 | Role Contract | Four roles: `reader`, `contributor`, `reviewer`, `admin`; deny-by-default | `AGENTS.md` authorization; `RAG_ROADMAP.md` Phases 0/8; cross-phase invariant 8 | [Module ownership](#module-ownership); [Port contracts](#port-contracts) |
| OK6 | Citation-Only Evidence and Escalation | Every claim cites current approved entry; `human expert` escalation | `AGENTS.md` safety; `RAG_ROADMAP.md` cross-phase invariants 3–5 | [Query flow](#query-flow); [Failure rules](#failure-rules) |
| OK7 | Six-State Outcome Taxonomy | Exactly six outcomes; provider/persistence failure → `unavailable`; session inactivity → `session_expired` | `AGENTS.md` provider/sessions; `RAG_ROADMAP.md` Phase 7 | [Query flow](#query-flow); [Failure rules](#failure-rules); [Port contracts](#port-contracts) |
| OK8 | Sensitive Screening | High-confidence screen before embedding/generation/storage; block event only logged | `AGENTS.md` security; `RAG_ROADMAP.md` Phase 8 | [Per-request gate ordering](#per-request-environment-and-demo-identity-gate-ordering); [Query flow](#query-flow) |
| OK9 | Dental-Contract Supersession | Historical artifacts retained, never deleted; linked from roadmap, architecture, AGENTS | `AGENTS.md` hierarchy; `RAG_ROADMAP.md` Phase 0 | [Traceability](#traceability); `AGENTS.md` Contract supersession; supersession-index.md |

**Audit note:** the legacy table maps the 7 platform-architecture requirements from spec #3162 rev8 (preserved for historical traceability). The OpsKnowledge table maps all 9 requirements from spec #3227. The roadmap-only row (panel-only contradiction alerts) is preserved for completeness.

## Checklist

Before an implementation change leaves planning:

- [ ] The change respects the modular-monolith shape and hexagonal boundaries.
- [ ] No excluded dependency is introduced.
- [ ] The synthetic exception and the free-text demo risk are kept as distinct concerns.
- [ ] No flow or adapter includes email/Notifier.
- [ ] Index lifecycle locking, idempotency, and one-transaction query durability are preserved.
- [ ] Authorization, sensitive screening, and safe-field logging are preserved.
- [ ] TI-gated values are not invented.
- [ ] Direct production dependencies are recorded in `governance/direct-dependencies.yaml`.
- [ ] Traceability rows exist for every spec requirement affected.

## Next step

When implementation is authorized, begin with bounded implementation SDD changes (e.g. test harness bootstrap, minimal grounded OpsKnowledge core), not with infrastructure or UI. Each change must establish the test harness first, then re-evaluate Strict TDD per `AGENTS.md` and testing baseline #3111.