# Exploration: Reposition RAG as a Portfolio Platform

## Revision History

| Date (UTC) | Revision | Reason |
|---|---|---|
| 2026-07-14 | 1 | Initial exploration. Drift detected: artifact inherited a 400-line review budget from prior SDD context. Corrected to use the active session preflight value `review_budget_lines: 800`; re-assessed the 800–1,200-line forecast against that budget; updated the workload forecast, risk register, "Ready for Proposal" steps, and skill resolution accordingly. Substantive product recommendation (Approach A: compliance-aware / audit-sensitive document QA) and all other evidence preserved. |

## Purpose

Evaluate options for repositioning the RAG repository from its current identity as an **enterprise dental-aligner design guidance product** toward a **broad, demonstrable engineering portfolio platform**, while:

Evaluate options for repositioning the RAG repository from its current identity as an **enterprise dental-aligner design guidance product** toward a **broad, demonstrable engineering portfolio platform**, while:

- preserving the safety, evidence, persistence, and governance contracts that are the project's strongest engineering signal
- avoiding a vague "general-purpose RAG" that would lose the niche credibility and the demonstrable domain rigor
- maximizing the surface area of demonstrable engineering craft (architecture, observability, testing, security, data modeling, migrations) for hiring reviewers
- producing a bounded, reviewable change proposal that does not erase the existing archived contracts without authorization

This exploration is read-only. No project files outside the OpenSpec change folder and the Engram observation are created. The user-level product narrative and concrete product-domain choice are deferred to a follow-up bounded proposal.

---

## Current State

### What the repository actually is today

- A **roadmap-and-contracts-only** workspace. No runtime, no test harness, no manifests, no lockfiles, no Git repo. `AGENTS.md` and `RAG_ROADMAP.md` are the authoritative normative documents; `docs/architecture/platform-architecture.md` is the architectural reference; `architecture/direct-dependencies.yaml` is dependency-governance evidence.
- The product boundary (`RAG_ROADMAP.md` §Product boundary) commits to a **dental-aligner design process guidance** assistant for a corporate client. The narrative is enterprise clinical/operations software, not a public product.
- Phase 0 documentation is **complete** (Engram observations #3110–#3194, #3125 dental spec, #3162 platform spec, #3163 design, #3161 proposal, #3134/#3194 tasks, #3110 init, #3137 archive-report). Two archived SDD changes:
  - `define-dental-guidance-domain-and-corpus` — locks the canonical domain boundary, six-role actor model, Spanish/English corpus, evidence rules, response taxonomy, governance placeholders.
  - `define-rag-platform-architecture` — locks the feature-organized modular monolith with hexagonal boundaries, prototype stack (FastAPI/React/Vite, PostgreSQL/pgvector, SQLAlchemy 2, Alembic, Psycopg 3, Docling, public OpenAI), Azure migration mapping with TI gates, data ownership/lifecycle, atomic index versioning, query durability in one transaction, accepted public-OpenAI free-text demo risk, and dependency governance.
- All eleven future-roadmap features (Phases 1–10) are described as **candidate SDD changes**; none has begun implementation.
- The project's strongest portfolio signals today are **architectural, not visual**: a hexagonal modular monolith, a single durable DB, a documented contract for the corporate/demo separation, an index-lifecycle locking story, atomic query persistence, OIDC/Entra mapping, and a documentation/architecture governance file.
- The "narrative" of the project is currently **enterprise SaaS for a regulated niche** (clinical dental, SharePoint ingestion, 5-technician pilot, 12-month retention, panel-only contradiction alerts). That narrative is the **wrong** portfolio narrative for a candidate seeking broad engineering signal: a hiring reviewer for general backend/AI engineering may not recognize clinical-domain rigor; a hiring reviewer for healthcare AI may not be evaluating this candidate at all.

### What the user now wants

The user has asked to reposition the project. Their stated goal: **portfolio / demonstrating broad engineering ability**. This is a *purpose* change, not a *feature* change. It implies three concrete decisions that this exploration must answer:

1. **What is the new product narrative?** (domain, persona, scope)
2. **What stays, what becomes configurable example, and what requires new SDD?**
3. **How do we maximize the visible engineering surface without scope creep?**

### What the AGENTS.md invariant hierarchy says

`AGENTS.md` is the highest-source contributor contract. It states:

- Instruction hierarchy: AGENTS.md > RAG_ROADMAP.md > platform-architecture.md > SDD artifacts.
- "Durable architecture baseline" — feature-organized modular monolith, one process, one database, monorepo, excluded dependencies (LangChain, LlamaIndex, streaming, visual interpretation, email/Notifier, unevidenced reranking, Redis, queues, Kubernetes, microservices).
- Cross-phase safety invariants are listed in `RAG_ROADMAP.md` §Cross-phase safety invariants. Many are domain-agnostic (evidence, citations, abstention, language isolation, partial-index prohibition, index-lifecycle lock/idempotency, one-transaction query durability, OIDC contract, safe-field logging). Several are dental-specific (SharePoint as sole source, Consultation App recommendation, OCR-without-visual-interpretation, patient-specific analysis out of scope, no partial synthetic migration into corporate).
- The instruction hierarchy requires **any conflict between sources to be resolved by opening a new SDD change**. Repositioning will produce at least one such conflict (SharePoint-only corpus, six dental roles, Consultation App abstraction); each must be reconciled with a bounded change, not silently edited.

### What the existing SDD artifacts allow without new work

- The platform architecture is already **stack-independent** in its data-model, flow, and port-contract layers. The "dental" parts of the contracts are concentrated in three places:
  - The dental domain spec (Engram #3125) — six roles, SharePoint eligibility, Spanish/English only, Consultation App recommendation.
  - The platform-architecture document (sections on "Dental Design Guidance RAG Roadmap" and the SharePoint→Azure mapping) — corporate-data-source labelling.
  - The roadmap's Phase 8 Entra mapping — six dental roles.
- The **port contracts** (`Clock`, `Authorize`, `Retrieve`, `Generate`, `Embed`, `ParsePdf`, `Persist`, `RunRetention`) are deliberately abstract. They are already domain-agnostic.
- The **safety engineering** is also largely domain-agnostic: high-confidence sensitive screen, per-request environment + demo-identity gate, atomic one-transaction query persistence, `pg_try_advisory_xact_lock` for index operations, partial unique constraints on `IndexVersion`, idempotency keys, panel-only alerts, retention-job recovery, JSON safe-field logging.
- The **dental-specific** parts that need re-decision are: domain, actors, language pair, corporate data source, Consultation App abstraction, "no patient data" warning, OCR-derivation provenance, and SharePoint ingestion. All of these can be **re-parameterized** without re-architecting the platform.

### Key tension: the user wants both "broad" and "niche"

Hiring reviewers reward two different portfolio shapes:

- **Breadth of engineering surface**: a system that visibly demonstrates backend, frontend, data, infra, security, testing, observability, and architecture decisions across realistic boundaries. The current roadmap already covers most of these.
- **Niche depth**: a system that visibly demonstrates rigor in a specific real-world constraint (clinical, regulated, high-stakes, or otherwise demanding). The current roadmap's clinical/SharePoint/Entra story provides that — but only for healthcare-AI reviewers.

The user wants the broader signal. The exploration must not abandon rigor, but it should **swap the niche from "healthcare/clinical" to something that signals the same engineering craft to a broader reviewer audience without becoming a generic chatbot demo**.

---

## Affected Areas

These are the locations the repositioning will touch conceptually, with **the rule of what each change does** (the bounded proposal that follows this exploration is the one that decides whether to update them now or later).

| File / artifact | Current role | Repositioning impact |
|---|---|---|
| `RAG_ROADMAP.md` | Authoritative product-boundary and phase plan. Names the product "Dental Design Guidance RAG Roadmap". | Title, product-boundary prose, and phase-context prose are dental-specific. Phase structure, safety invariants, and architecture direction are largely domain-agnostic. **Update later** under a bounded change; do not edit in this exploration. |
| `AGENTS.md` | Normative contributor contract. Refers to dental domain only by indirect cross-reference (it never asserts a domain). | **Stays intact** for safety, architecture, dependency governance, and durable baseline rules. The AGENTS.md durable baseline is already domain-agnostic. No dental-specific content to remove. |
| `docs/architecture/platform-architecture.md` | Authoritative architecture reference. Multiple sections label the product "dental-guidance RAG". | **Update later** under a bounded change: rename product labels and reframe the corporate-Azure mapping section. The diagrams, data model, flows, and port contracts stay. |
| `architecture/direct-dependencies.yaml` | Dependency governance evidence. Lists seven approved + one pending + excluded entries. | **Stays intact**; the dependency set (FastAPI, SQLAlchemy, Alembic, psycopg, pgvector, docling, openai; excluded LangChain/LlamaIndex/Redis/Kubernetes) is domain-agnostic. |
| Engram #3125 (dental spec) | Six-requirement, fifteen-scenario domain spec. | **Replace or supersede** under a bounded change if the user picks a non-dental domain. The 6 response states and citation/evidence rules are domain-agnostic and should be preserved as the new domain spec's evidence/response backbone. |
| Engram #3161/#3162/#3163 (platform proposal/spec/design) | Domain-agnostic platform contracts. | **Stays intact**. Confirm there is no hard-wired dental reference in #3162 (there is: a "dental-guidance" string in the header, and the SharePoint/Entra/Consultation App specifics in the cross-phase invariants). Update those later. |
| Engram #3114 (dental exploration), #3122/#3133/#3134/#3135/#3136/#3137 (dental proposal, design, tasks, apply, verify, archive) | Dental-domain lifecycle artifacts. | **Archive or supersede** under a bounded change. The archive is an audit trail and must not be deleted. A successor change can declare a new domain and supersede the dental domain. |
| `openspec/changes/` (filesystem, hybrid mode) | Does not exist yet (Engram-only project). | The current project uses Engram-only artifacts; the hybrid mode means the proposal/spec/design/tasks/verify files for this change will live **both in Engram and in `openspec/changes/reposition-rag-as-portfolio-platform/`**. |
| `openspec/specs/` | Empty. | A new domain spec will be added here under a bounded change. |
| `openspec/config.yaml` | Missing. | The repositioning change does not require creating it; that is the sdd-init concern. A future bootstrap change (test harness, Phase 0) may need it. |
| Future candidate SDD changes listed in Phase 1–10 of the roadmap | 44 candidate changes, almost all dental-specific (SharePoint ingestion, Consultation App integration, etc.). | **Re-frame as portfolio examples** in a later bounded change, not in this exploration. |

### Excluded Dependencies and Other Hard "Do Not Touch" Surfaces

- `architecture/direct-dependencies.yaml` `excluded:` list — preserved.
- One-process, one-database invariant — preserved.
- Modular-monolith shape, hexagonal boundaries — preserved.
- Index-lifecycle `pg_try_advisory_xact_lock` discipline — preserved.
- One-transaction query durability — preserved.
- JSON safe-field logging policy — preserved.
- Sensitive-data pre-screen, per-request environment + demo-identity gate — preserved.

These are the most valuable engineering signals in the project; they survive any repositioning.

---

## Approaches

This section compares three positioning strategies. The recommendation is at the end of the section.

### Approach A — "Generic Compliance-Aware Document QA" (RECOMMENDED)

**Narrative**: a corporate document question-answering platform that combines **grounded answer generation with safety/evidence rigor for any regulated or audit-sensitive content**. The product helps analysts answer questions from a controlled, versioned, authoritative document library; every claim is cited; the system abstains rather than hallucinates; the index lifecycle is auditable; sensitive queries are pre-screened.

**Why this works for portfolio breadth**: it carries the same engineering surface as the dental narrative (modular monolith, hexagonal, atomic index, language-isolated retrieval, abstention taxonomy, sensitive screen, audit logging) but the domain is **any** approved, versioned document library: financial compliance, internal HR policy, engineering runbooks, regulatory guidance, customer-support knowledge, code-style guides, etc. The hiring reviewer recognizes the **problem class** (regulated document QA) without needing to be in healthcare AI.

**Why this preserves rigor**: the safety invariants (every claim cited, no general-knowledge fill, abstention taxonomy, language isolation, sensitive screen, atomic persistence) are exactly the engineering signals reviewers reward. They are not dental-specific.

**Domain placeholder**: a synthetic "internal compliance library" or "internal engineering runbook library" — both domain-agnostic and easy to demonstrate publicly without leaking any real corporate content.

**Trade-off vs. current narrative**: the clinical/stakeholder/SharePoint/Entra/Consultation App specifics are dropped or replaced with a generic "approved document library" + "internal identity" + "managed helpdesk/ticketing" abstraction. The roadmap's Phase 8 Entra mapping becomes "any OIDC provider", and the roadmap's SharePoint ingestion becomes "any S3/Azure-Blob/SharePoint-style document source" — the protocol is already there in `ParsePdf` and the `corpus` feature module.

| Pros | Cons |
|---|---|
| Maximum breadth of engineering signal: backend, data, retrieval, security, observability, testing, governance, architecture — all visible. | The clinical lean goes away; reviewers evaluating healthcare-AI fit will not see that signal. (Mitigation: a one-line "this was originally a clinical deployment" note in the README is enough.) |
| Reuses the full roadmap: hexagonal modular monolith, atomic index, language isolation, safe-field logging, OIDC mapping, advisory abstention, per-request gate, sensitive screen, retention with redaction. | Requires the most careful re-naming (RAG_ROADMAP.md, AGENTS.md cross-refs, platform-architecture.md, the dental spec, all 44 candidate SDD changes). |
| Domain-agnostic by construction, so the future roadmap is smaller and the demo corpus is small. | Must avoid drifting into "general-purpose RAG" — the niche must remain a specific document class with the same safety posture. |
| Easy to demo publicly: synthetic "Compliance Guide 1.0" PDF is innocuous and clearly labeled. | The five-technician pilot framing from Phase 9 is dropped; a different "evaluation harness" framing is needed (e.g., internal alpha + public demo). |

**Effort**: Medium. Most contract-level work is already done; renaming and re-scoping is bounded.

**What stays / becomes configurable / requires new SDD**: see the next section.

### Approach B — "Internal Engineering Knowledge Platform"

**Narrative**: a corporate assistant that helps engineers, SREs, and ops teams query an internal runbook / postmortem / architecture-decision-record (ADR) library with strict citation, version awareness, and abstention when the runbook is silent.

**Why this works for portfolio**: the reviewer pool for backend / platform / SRE / DevEx engineering is the largest single reviewer pool the candidate might face. The narrative aligns the project with their daily work.

**Trade-off**: the engineering surface is real, but the safety/audit story is narrower (no clinical data, no patient data, no language isolation needed). This shrinks the visible safety engineering surface.

**Effort**: Medium. The hexagonal modular monolith, atomic index, and abstention taxonomy all transfer cleanly. Language isolation becomes optional.

| Pros | Cons |
|---|---|
| Largest reviewer pool overlap. | Smaller safety/audit surface (less OIDC, no sensitive-data screen, no language isolation, no contradiction alerts). |
| Runbook/ADR libraries are public-friendly; demo is small and obviously synthetic. | Less "wow" factor for healthcare/regulated-industry reviewers. |
| Easy to map to the existing features: `corpus` becomes "ADR library", `governance` becomes "team identity", `indexing` becomes "versioned ADR publishing". | Loses the "patient-specific analysis is out of scope" clarity that makes the dental story compelling. |

### Approach C — "Generic Chatbot over Documents" (REJECTED)

**Narrative**: a multi-tenant RAG-as-a-service over arbitrary user-uploaded documents.

**Why this is rejected**: this is exactly the "vague/general-purpose RAG" the user said to avoid. The engineering signal collapses (no real safety/audit story, no real domain rigor, no real corpus governance). It looks like every other tutorial-grade RAG demo and earns zero portfolio differentiation.

| Pros | Cons |
|---|---|
| Trivially demoable. | No portfolio differentiation. |
| | Directly violates the user's instruction to avoid a vague general-purpose RAG. |
| | Drops the safety/evidence engineering that is the project's strongest signal. |

### Approach D — "Healthcare AI Specialist" (REJECTED for this user)

**Narrative**: keep the current dental/clinical narrative exactly as it is; market the project to healthcare-AI reviewers specifically.

**Why this is rejected**: the user explicitly stated the goal is to serve as a portfolio for **broad** engineering ability, not to specialize in healthcare AI. A healthcare-only repositioning would narrow the audience.

| Pros | Cons |
|---|---|
| Preserves the existing roadmap verbatim. | Narrows the reviewer pool to healthcare-AI only, the opposite of the user's stated goal. |
| Existing artifacts are reused. | Does not address the user's intent. |

---

## Recommendation

**Recommend Approach A: a "compliance-aware / audit-sensitive document QA" platform** with the following concrete product narrative to be locked by a follow-up bounded proposal:

> **A grounded, citation-backed question-answering platform over an approved, versioned document library, designed for organizations that need every claim to be traceable, every abstention to be safe, and every index to be auditable. The system supports regulated document classes (compliance, internal policy, engineering runbooks, customer-support knowledge) and refuses to answer when the evidence cannot support the claim.**

The follow-up bounded proposal will then need to ask the user to confirm a few decisions, listed in the "Open Decisions for the Follow-up Proposal" section below.

### Why Approach A wins on the three criteria the user gave

- **Avoids vague/general-purpose RAG**: keeps a specific, recognizable problem class (regulated document QA) and the same evidence/abstention/audit story.
- **Preserves valuable safety/evidence engineering**: the four most impressive pieces of engineering in the project (atomic query persistence, index-lifecycle lock + idempotency, sensitive screen + per-request demo gate, safe-field logging) are already domain-agnostic and stay untouched.
- **Maximizes demonstrable skills for hiring reviewers**: the engineering surface area is at least as broad as the current roadmap (hexagonal modular monolith, single durable DB, OIDC/Entra or any OIDC, OTel-shaped observability, index lifecycle, language-isolated retrieval if multilingual, abstention taxonomy, sensitive screen, retention with redaction) but the niche is recognizable to the broadest reviewer pool.

### What the follow-up proposal will change vs. preserve

This is the classification the user is asking for. The "stay / configurable / new SDD" split assumes Approach A is the target and is the basis for the follow-up proposal.

**Stays intact (no change required):**

- `AGENTS.md` durable architecture baseline, durable contributor rules, safety invariants, security rules, retention rules, logging rules, dependency governance, testing/CI/OpenAPI "future" rules. None of these are domain-specific.
- The platform-architecture document's **diagrams, data model, flows, port contracts, prototype → Azure mapping, retention-job recovery, observability shape**. These are domain-agnostic.
- `architecture/direct-dependencies.yaml` (FastAPI, SQLAlchemy, Alembic, psycopg, pgvector, docling, openai; excluded LangChain/LlamaIndex/Redis/Kubernetes/streaming/visual-interpretation/email/Notifier/unevidenced-reranking).
- The 6-state response taxonomy (`supported`, `insufficient_information`, `contradictory_information`, `out_of_scope`, `unavailable`, `session_expired`).
- The evidence contract: only current approved corpus, every claim cited, conversation history / glossary / model knowledge never evidence, language-isolated retrieval if multilingual, OCR-without-visual-interpretation.
- The index-lifecycle story: `pg_try_advisory_xact_lock` at operation entry, partial unique constraints, idempotency keys, post-commit cleanup, recovery without invalidating committed active index.
- The one-transaction query durability rule.
- The per-request environment + demo-identity gate ordering.
- The high-confidence sensitive screen (still relevant for any document class that may contain PII, customer data, internal secrets).
- The JSON safe-field logging policy.

**Becomes configurable example (small text/label changes, no contract change):**

- The product name and tagline: from "Dental-Aligner Design Guidance RAG" to "Compliance-Aware Document QA Platform" (or whatever the user picks). One file rename in each header.
- The "in-domain" / "out-of-scope" examples in the dental spec become **examples** of a generic evidence-boundary contract. The contract itself stays; only the example text changes.
- The actor role list (technicians, support, clinical team, supervisors, industrial engineering, administrators) becomes a **configurable example** of a six-role split. The platform supports any role list; the demo shows a sample.
- The language-pair list (Spanish, English) becomes a **configurable example** of a language-isolation contract. The platform supports any pair or single language; the demo shows Spanish/English.
- The "Consultation App" abstraction becomes a **configurable example** of a "human-helpdesk / escalation" abstraction. The contract is "for abstentions, recommend the configured escalation path"; the example name is configurable.
- The "approved SharePoint guide" becomes a **configurable example** of an "approved document source". The contract is "documents from the configured authoritative source, with filename / metadata rules declared in the corpus inventory"; the example source is configurable.
- The "no patient data" warning becomes a **configurable example** of a "no sensitive data" warning; the contract is "warn users not to enter sensitive data; sensitive payloads do not persist".
- Phase 9's "five-technician pilot" becomes a **configurable example** of a controlled-pilot methodology. The contract is "a controlled evaluation harness runs before broader release"; the example size is configurable.

**Requires a new bounded SDD change (the follow-up to this exploration):**

- **Domain definition spec**: replace or supersede the dental domain spec (Engram #3125) with a domain-agnostic "evidence-boundary + escalation + actor + language" spec. The new spec should preserve all evidence/citation/response/operational-state rules from the dental spec and the platform spec, and replace the dental-specific terms with generic terms.
- **Roadmap rename + product-boundary update**: a bounded `reposition-rag-as-portfolio-platform` change (this one) that updates `RAG_ROADMAP.md` (title, product-boundary prose, candidate-SDD-changes section), the platform-architecture document (header references to "dental"), and the AGENTS.md "Where to look" references if they exist. Must respect the instruction hierarchy in AGENTS.md (this change is below AGENTS.md and may not contradict it).
- **Roadmap-rename of all 44 candidate SDD changes**: each candidate SDD change in Phases 1–10 currently has a dental-specific name (e.g., `integrate-sharepoint-guide-source`, `add-entra-single-sign-on`, `add-clinical-grounding-safety-gates`, `add-language-isolated-hybrid-retrieval`). The bounded proposal should declare the **renaming policy** (preserve the contract, swap the example label) and apply it to the 44 candidate changes in the same change or a follow-up.
- **Demo corpus contract**: declare the demo corpus under the new narrative. The current "manifest-controlled synthetic PDFs labeled non-corporate" rule is preserved; the new demo corpus is a synthetic "Compliance Guide 1.0" / "Internal Runbook v2" set, still synthetic and visibly non-corporate, still rejected outside the `development` profile.
- **Identity abstraction**: the Phase 8 Entra mapping for dental roles becomes "any OIDC provider with a configurable role mapping". The corporate OIDC contract (signature, issuer, audience, single tenant) stays.
- **Sensitive-data abstraction**: the dental "no patient data" warning becomes a generic "no sensitive data" warning. The high-confidence screen stays.
- **Escalation abstraction**: the dental "Consultation App" recommendation becomes a configurable escalation channel. The contract "every abstention recommends the configured escalation" stays.

The bounded proposal can either roll all of these into one change or split them into chained PRs. Under the active `review_budget_lines: 800`, the central forecast (1,000 lines) exceeds 800 and the upper bound (1,200) exceeds by a wider margin, so the budget risk is **Medium** and chained PRs are **recommended** under the `ask-always` delivery strategy (not automatically mandatory — the user must confirm). The follow-up proposal must forecast the actual line count in the tasks phase and present a chained-PR plan the user can accept, reject, or modify.

### What the follow-up proposal does NOT do

- Does not implement the platform. No runtime, no test harness, no manifests, no lockfiles. The "no runtime stack" baseline stays.
- Does not change the excluded-dependencies list.
- Does not change the cross-phase safety invariants.
- Does not introduce streaming, LangChain, LlamaIndex, Redis, Kubernetes, microservices, email/Notifier, visual interpretation, or unevidenced reranking.
- Does not delete any archived SDD artifact. Archives are an audit trail.
- Does not introduce TI-gated values. The Azure migration section is reframed to "any OIDC provider + any managed AI service" with the same TI-gate discipline.
- Does not weaken the per-request environment + demo-identity gate. The accepted public-OpenAI free-text demo risk stays as the prototype boundary.
- Does not change the 12-month retention semantics or the safety-screen ordering.
- Does not change the modular-monolith shape or the hexagonal boundary rules.
- Does not change `architecture/direct-dependencies.yaml` (the dependency set is already domain-agnostic).

---

## Open Decisions for the Follow-up Proposal

The follow-up bounded proposal must confirm these with the user before it is written. They are not invented by this exploration.

1. **Product narrative confirmation** — confirm Approach A is the target, or pick Approach B. (Approach C and D are rejected; this exploration does not anticipate the user picking them.)
2. **Tagline / product name** — short, public-friendly name for the platform (e.g., "Compliance-Aware Document QA Platform", "Audit-Sensitive Document Assistant", "Grounded Document Q&A for Regulated Teams"). The exploration does not pick a name; the user does.
3. **Demo corpus** — a tiny, public-friendly synthetic document set (e.g., one English "Compliance Guide 1.0" + one Spanish "Guía de Cumplimiento 1.0" PDF, plus a third "Engineering Runbook 2.0" if the user wants a multi-corpus example). Manifest-controlled, labeled non-corporate, never migrates to corporate. The user picks the corpus example.
4. **Escalation target label** — replaces "Consultation App". A neutral term such as "human helpdesk" or "internal support channel". The user picks the term.
5. **Actor role example** — replaces the six dental roles. A neutral six-role example (e.g., "analyst, peer-reviewer, manager, content-owner, ops, admin"). The user picks the example.
6. **Language pair example** — keeps Spanish/English (good for portfolio breadth and a strong second-language signal) or simplifies to a single language for the demo. The user picks.
7. **Repository name** — the project directory is `RAG`; the user may or may not want to rename it. The exploration does not pick; the user decides.
8. **Roadmap-renaming strategy** — single bounded change that re-renames all 44 candidate SDD changes, or a follow-up change that does it incrementally. The exploration recommends chained PRs (a 4-slice plan) because the rename is text-only but the central forecast (1,000 lines) exceeds the active 800-line budget. The proposal must forecast the actual line count; the user may accept the chained plan, request a different split, or authorize a single oversized change.

---

## Review Workload Forecast

| Field | Value |
|---|---|
| Change name | `reposition-rag-as-portfolio-platform` |
| This exploration artifact | Engram topic `sdd/reposition-rag-as-portfolio-platform/explore` (English) + `openspec/changes/reposition-rag-as-portfolio-platform/exploration.md` (English) |
| Active review budget | **`review_budget_lines: 800`** (selected at session preflight) |
| Delivery strategy | `ask-always` (selected at session preflight) |
| Estimated changed lines in follow-up proposal | 800–1,200 (header renames across 3 markdown files + spec supersession + roadmap candidate-rename sweep). Central case ≈ 1,000. |
| 800-line budget risk (follow-up change) | **Medium** — lower bound (800) lands at the budget; central case (1,000) exceeds by ~25%; upper bound (1,200) exceeds by ~50%. The change does NOT strictly require splitting under the budget rule alone. |
| Chained PRs recommended | **Recommended under `ask-always`** — not strictly mandatory by the 800-line rule (the lower bound fits), but recommended because: (a) the central forecast exceeds the budget, (b) `ask-always` requires the user to be asked before oversized work, and (c) text-only renames are clean to slice. The user may accept the plan, request a different split, or authorize a single change. |
| Proposed chained-PR plan | 4 slices, each ≤ 800 lines: (1) product narrative + roadmap header rename, (2) dental domain spec supersession with new domain spec, (3) platform-architecture document and AGENTS.md "Where to look" cross-refs, (4) Phase 1–10 candidate-SDD-change rename sweep. |
| Per-slice budget target | ≤ 800 (the active review budget), not 400 |

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Repositioning is read as a retreat from a real product | Medium | Medium | The repositioning preserves all safety/evidence engineering; the README and proposal explicitly state the engineering signals are the portfolio's primary asset. |
| Cross-source conflicts between AGENTS.md, RAG_ROADMAP.md, and platform-architecture.md during the rename | High | Medium | The instruction hierarchy requires a bounded SDD change for any conflict; the follow-up proposal will declare each cross-source update explicitly. |
| The new narrative is too generic and looks like every other RAG | Medium | High | The recommendation is a **narrow** "regulated document QA" niche, not "RAG over anything". The abstention/evidence/audit story is the niche. |
| The active 800-line review budget is exceeded by the rename sweep (central forecast ~1,000) | Medium | Medium | Chained PRs are recommended in the forecast under the `ask-always` strategy. The proposal phase must produce a line-count forecast and a chained-PR plan, and present it to the user for an explicit decision (accept, modify, or reject in favor of a single oversized change). |
| The dental domain spec is silently dropped, losing valuable evidence engineering | Medium | High | The follow-up proposal must explicitly supersede (not delete) the dental spec, preserve the 6-state response taxonomy and the evidence/citation rules verbatim, and migrate them into the new domain spec. |
| Demo corpus accidentally leaks | Low | High | The existing "development-only synthetic PDFs, labeled non-corporate, startup fails outside development, CI proves denial" rule stays. The follow-up proposal must declare the demo corpus under the same rule. |
| Identity / Entra contract becomes vendor-locked again under "any OIDC" | Low | Medium | The OIDC contract (signature, issuer, audience, single tenant) stays. Phase 8 Entra is reframed as one example; any approved OIDC is allowed; the corporate boundary rule stays. |
| Per-request demo gate is dropped because the new narrative does not need it | Low | High | The gate stays. The accepted public-OpenAI free-text demo risk applies to any development-only OpenAI demo, not only to clinical data. |
| The user wanted a different narrative (not Approach A or B) | Medium | Medium | The exploration presents the four approaches and rejects C/D with explicit reasons; the user can pick B or supply a fifth. |

---

## Ready for Proposal

**Yes, with explicit preconditions.** The bounded proposal that follows this exploration should:

1. **Ask the user to pick a product narrative** (Approach A or Approach B; C and D are rejected by this exploration with reasons).
2. **Ask the user to confirm the eight open decisions** (tagline, demo corpus, escalation label, actor example, language pair example, repository name, roadmap-rename strategy, etc.).
3. **Forecast the 800-line review budget** and propose a chained-PR plan (4 slices, each ≤ 800 lines, or whatever the user prefers). Under `ask-always`, present the forecast and the chained plan to the user and ask them to accept, modify, or reject in favor of a single change.
4. **Preserve all safety/evidence/audit/architecture invariants** without modification.
5. **Reference and supersede** (not delete) the dental domain spec #3125, the dental exploration #3114, and the dental proposal/design/tasks/apply/verify/archive-report artifacts. Archives are an audit trail and must remain.
6. **Declare the demo corpus under the same "development-only synthetic manifest" rule** as the current project.
7. **Reframe the Phase 8 OIDC mapping** as one example of a generic OIDC contract, preserving the signature/issuer/audience/single-tenant rules.
8. **Reframe the Phase 4 SharePoint ingestion** as one example of a generic "approved document source" ingestion, preserving the filename/metadata contract shape.

**Implications for later phases**:

- All 44 candidate SDD changes in Phases 1–10 will need label-level renaming. The follow-up proposal must either do this in the same change (chained PRs) or declare a follow-up change that does it.
- The first implementation change (`build-minimal-grounded-dental-rag` in Phase 1) must be renamed in step with this repositioning. The proposal must declare a renamed candidate name (e.g., `build-minimal-grounded-rag-core` or `build-grounded-citation-rag-mvp`).
- The Phase 2 evaluation cases need a renamed demo dataset. The current `build-consultation-evaluation-dataset` candidate must be reframed as a generic safety/quality evaluation dataset under the new narrative.
- The Phase 3 SharePoint ingestion must be reframed as a generic "approved document source" ingestion. The contract shape stays.
- The Phase 8 Entra mapping stays as a **single example** under the new narrative; the contract allows any approved OIDC.

**Do not start the proposal until the user confirms Approach A vs. B and answers the eight open decisions.** This is a change that crosses the project boundary and must not invent defaults.

---

## Cross-References

- Project context: Engram #3110 (SDD project init).
- Prior decisions: #3114, #3121, #3122, #3125, #3133, #3134, #3135, #3136, #3137 (dental domain and corpus lifecycle).
- Prior decisions: #3161, #3162, #3163, #3194 (platform architecture lifecycle).
- Roadmap: `RAG_ROADMAP.md` (534 lines, full file read; Phases 0–10 + cross-phase invariants + delivery map).
- Architecture: `docs/architecture/platform-architecture.md` (556 lines, full file read).
- Contributor contract: `AGENTS.md` (110 lines, full file read; durable baseline + invariants).
- Dependency governance: `architecture/direct-dependencies.yaml` (258 lines, full file read; 7 approved + 1 pending + 6 excluded).
- Skill resolution: `sdd-explore` (read), `_shared/sdd-phase-common.md` (read), `_shared/openspec-convention.md` (read), `cognitive-doc-design` (read).

## Skill Resolution

- `sdd-explore` — read; used as the contract for the explore phase and the persistence rules.
- `_shared/sdd-phase-common.md` — read; used for retrieval and persistence rules.
- `_shared/openspec-convention.md` — read; used to determine the file path and write rules.
- `cognitive-doc-design` — read; applied for the artifact's progressive disclosure (purpose → current state → affected areas → approaches → recommendation → risks → readiness).
- All other skills are out of scope for this exploration.
