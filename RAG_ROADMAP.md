# OpsKnowledge Roadmap

This document is the shared development route for OpsKnowledge: a bilingual technical knowledge platform over approved, versioned runbooks, ADRs, and operational policies. It records the current product decisions and assigns each capability to the future SDD phase where it belongs.

No SDD change is active. The test-harness bootstrap is complete; each future candidate change below must run through its own SDD lifecycle and remain independently reviewable and reversible.

## Product boundary

- OpsKnowledge answers process and operational questions for backend and AI engineering reviewers using approved, versioned technical collections.
- Approved versioned collections (`runbooks`, `adrs`, `operational-policies`) are the only approved knowledge sources for the corporate product. A development-only prototype may use versioned, manifest-controlled synthetic technical entries that are visibly labeled non-corporate, cannot migrate into corporate indexes, and are rejected outside the development environment.
- OpsKnowledge explains what the approved entries state. It does not create clinical recommendations or analyze patient cases.
- Every technical claim must be supported by a verifiable citation from a current approved entry.
- Questions outside the approved entries, unsupported questions, and direct source contradictions must end in abstention and recommend a human expert.
- The MVP is a standalone web application. Teams and external tool integrations are deferred.
- The initial rollout is limited to the main site and a five-user pilot.

## Guiding principles

- Safety and traceability take priority over answer coverage.
- Treat entry revisions, language, citations, abstention, authorization, and observability as product capabilities.
- Never mix Spanish and English corpora in one retrieval operation.
- Never treat conversation history, the glossary, historical support answers, or model knowledge as answer evidence.
- Measure retrieval and answer quality before optimizing components.
- Keep providers replaceable and SDD changes small, testable, and reversible.
- Publish document indexes atomically and retain a known-good rollback boundary.

## Delivery map

```text
0. Product baseline and evaluation assets
                 ↓
0. Test-harness bootstrap
                 ↓
Pre-Phase 1 CI hardening
                 ↓
1. Minimal grounded OpsKnowledge core
                 ↓
2. Reproducible safety and quality evaluation
                 ↓
3. Approved-source ingestion and index lifecycle
                 ↓
4. Bilingual retrieval and source-conflict handling
                 ↓
5. Grounded conversational generation
                 ↓
6. Application services and data lifecycle
                 ↓
7. Reader and operations web experience
                 ↓
8. Corporate identity, privacy, and security
                 ↓
9. Operations, analytics, and controlled pilot
                 ↓
10. Scale-out and later integrations
```

| Milestone | Phases | Outcome |
|---|---:|---|
| Validated foundations | 0–2 | A measurable OpsKnowledge core with explicit safety gates |
| Document-aware core | 3–5 | Current approved entries produce fully grounded answers or safe abstentions |
| Pilot-ready product | 6–9 | A secure web product ready for the one-week controlled pilot |
| Wider production adoption | 10 | Capacity, additional sites, integrations, and formal production targets |

## Phase 0 — Product baseline and evaluation assets

**Phase status:** [ ] Completed

**Objective:** Convert the agreed product boundary into a reproducible, controlled bilingual evaluation foundation without requiring unavailable corporate material.

**Scope:**

- Record the actors: readers, contributors, reviewers, and administrators. Operational responsibilities (synchronization, rollback, global pause, contradiction management) are assigned to the `admin` role.
- Establish one manifest-controlled, versioned, approved, language-tagged, visibly non-corporate, development-only synthetic sample spanning `runbooks`, `adrs`, and `operational-policies`.
- Build representative answerable, ambiguous, contradictory, out-of-scope, and unanswerable cases with Spanish/English parity.
- Keep approved entries as the only answer evidence: every technical claim requires a citation from a current approved entry, and unsupported, out-of-scope, or contradictory cases abstain and recommend a human expert.
- Keep Spanish and English retrieval isolated before evidence reaches the model.
- Preserve the development-only synthetic-corpus exception: synthetic entries cannot migrate into a corporate index, and corporate data is never implied or substituted.
- Treat historical corporate metrics, historical Q&A/support reports, and corporate glossaries as optional future controlled evaluation references only. They are neither current prerequisites nor answer evidence, automatic ground truth, or replacements for approved entries.

**Pending input:** One governed synthetic bilingual sample: manifest-controlled, versioned, approved, language-tagged, visibly non-corporate, and development-only across `runbooks`, `adrs`, and `operational-policies`. This is the sole current prerequisite; no corporate material is required or fabricated.

**Expected outputs:** an approved bilingual evaluation-dataset foundation and explicit dataset-governance rules. The first slice targets 50% answerable/grounded cases and 50% abstention/safety cases with Spanish/English parity. Historical corporate metrics, Q&A/support reports, and glossaries may later support controlled evaluation or impact measurement, but never answer evidence or automatic ground truth.

**Canonical contract source:** `define-dental-guidance-domain-and-corpus` (superseded by `reposition-rag-as-portfolio-platform`) is the historical source of canonical domain, corpus, actor, language, evidence, outcome, and placeholder contracts consumed by Phases 1, 2, 4–9. The OpsKnowledge domain contract (Engram: proposal #3226, spec #3227, design #3228, tasks #3229) supersedes it. Historical artifacts (#3122, #3125, #3133, #3134) are retained as audit history and are never deleted. See `openspec/changes/reposition-rag-as-portfolio-platform/supersession-index.md`.

**Candidate SDD changes:**

- [x] `define-dental-guidance-domain-and-corpus` (superseded by `reposition-rag-as-portfolio-platform`)
- [x] `define-rag-platform-architecture`
- [x] `bootstrap-opsknowledge-test-harness`
- [ ] `build-opsknowledge-evaluation-dataset`

**Completion notes:**

- `define-dental-guidance-domain-and-corpus` — complete and superseded by `reposition-rag-as-portfolio-platform`. Historical SDD artifacts: Engram `sdd/define-dental-guidance-domain-and-corpus/{proposal (#3122), spec (#3125), design (#3133), tasks (#3134)}`. OpsKnowledge replacement artifacts: Engram `sdd/reposition-rag-as-portfolio-platform/{proposal (#3226), spec (#3227), design (#3228), tasks (#3229)}`.
- `define-rag-platform-architecture` — complete (documentation only; no runtime, manifests, or lockfiles). Establishes the shared technology and architecture baseline: feature-organized modular monolith with hexagonal boundaries, prototype stack (FastAPI/React/Vite, PostgreSQL/pgvector, SQLAlchemy 2/Alembic/Psycopg 3, Docling, public OpenAI), Azure migration mapping with TI gates, data ownership/lifecycle, index lifecycle concurrency/revocation, atomic query persistence, accepted public-OpenAI free-text demo risk, and dependency governance. Artifacts: `AGENTS.md` (normative contributor contract), `governance/direct-dependencies.yaml` (governance evidence template), `docs/architecture/platform-architecture.md` (detailed architecture reference). SDD artifacts: Engram `sdd/define-rag-platform-architecture/{proposal (#3161), spec (#3162), design (#3163), tasks (#3194)}`. Implementation changes must establish the test harness first, then re-evaluate Strict TDD (testing baseline #3111).
- `bootstrap-opsknowledge-test-harness` — complete. The bootstrap chain merged to `master` at `425f7ec`; its canonical local and GitHub Actions gate passed with 111 tests.
- The Phase 0 foundation is complete when the governed synthetic bilingual sample and its 50/50 evaluation slice are established under these controls. The next product change is `build-opsknowledge-evaluation-dataset`; optional historical references do not block it.

## Pre-Phase 1 — CI hardening

**Objective:** Close the remaining CI-platform gaps after the test-harness bootstrap and before product implementation begins.

**Ordering:** Both changes follow the completed Phase 0/test-harness boundary and precede `build-minimal-grounded-opsknowledge-core`. The scanner hardening is required before the next implementation PR. The Actions pin refresh is independently reviewable and reversible, so it remains a separate change. Neither change is Phase 9 product observability work.

**Candidate SDD changes:**

- [x] `harden-focused-test-scanner-import-aliases`
- [x] `refresh-github-actions-node-runtime-pins`

**Completion notes:**

- `harden-focused-test-scanner-import-aliases` — complete. Archived hybrid SDD change at `openspec/changes/archive/2026-07-19-harden-focused-test-scanner-import-aliases/`; implementation and CI delivery merged through PR #11.
- `refresh-github-actions-node-runtime-pins` — complete. Archived hybrid SDD change at `openspec/changes/archive/2026-07-21-refresh-github-actions-node-runtime-pins/`; canonical `test-harness` spec synchronized and post-archive verification reran successfully (`uv run --frozen pytest tests/architecture/test_github_actions_workflow.py -v`, `make ci`).

## Phase 1 — Minimal grounded OpsKnowledge core

**Phase status:** [ ] Completed

**Objective:** Implement the smallest understandable pipeline that answers only from supplied textual evidence.

```text
Approved entry text (runbook / ADR / policy)
    ↓
Structure-aware chunks
    ↓
Embeddings
    ↓
Simple similarity search
    ↓
Evidence-constrained prompt
    ↓
Answer or abstention with citations
```

**Components:** document reader, chunker, embedding provider, in-memory index, retriever, prompt builder, replaceable LLM provider, answer model, citation model, and abstention result.

**Rules established for this phase:**

- The model may not use general knowledge to fill gaps.
- A response cannot contain an unsupported technical assertion.
- If any assertion is unsupported, the generated answer is blocked as a whole.
- Images are not interpreted and are not shown as evidence.
- Provider interfaces must remain replaceable because the final AI platform is not yet approved.

**Deliberately out of scope:** approved-source synchronization, persistent vector storage, web UI, authentication, analytics, conversation history, reranking, and framework-heavy orchestration.

**Candidate SDD change:**

- [ ] `build-minimal-grounded-opsknowledge-core`

## Phase 2 — Reproducible safety and quality evaluation

**Phase status:** [ ] Completed

**Objective:** Establish measurable gates before adding production document and application complexity.

**Metrics:**

- Retrieval Recall@K.
- Answer correctness.
- Faithfulness and claim-to-citation support.
- Citation document, revision, section, page, and fragment validity.
- Correct abstention rate.
- Contradiction detection rate.
- Language-routing accuracy.
- Unsupported-claim escape rate.
- Query latency and cost per query.

**Mandatory safety cases:**

- No evidence exists.
- Evidence is related but incomplete.
- Two approved entries directly contradict each other.
- The query is outside the approved entries.
- The query attempts to override assistant rules.
- OCR contains uncertain numbers, symbols, units, or table structure.
- The question contains a possible sensitive identifier.

**Acceptance direction:** no unsupported technical claim may pass the evaluation gate. Related but insufficient evidence may show up to three cited fragments, followed by an explicit negative answer and human-expert escalation.

**Expected outputs:** repeatable evaluation command, machine-readable report, reviewed test set, baseline results, and release-blocking safety thresholds.

**Candidate SDD changes:**

- [ ] `add-opsknowledge-quality-evaluation-harness`
- [ ] `add-technical-grounding-safety-gates`
- [ ] `add-language-and-abstention-evaluation`

## Phase 3 — Approved-source ingestion and index lifecycle

**Phase status:** [ ] Completed

**Objective:** Reliably transform the approved entry library into a versioned, traceable, and reversible index.

**Source and identity contract:**

- The approved entry repository is the source of truth.
- File names follow `<entry-id>_ESP_REV_<revision>.pdf` or `<entry-id>_EN_REV_<revision>.pdf` (or the equivalent for the approved corporate source).
- The entry identifier is identical across languages.
- Spanish and English revisions are independent and must never be compared as equivalent revision numbers.
- Presence in the approved repository determines current availability; removed documents must be removed completely from retrieval.

**Extraction:**

- Extract selectable text, headings, sections, pages, footnotes, and textual tables.
- Preserve table headers, rows, columns, units, and surrounding context.
- Permit automatic OCR for text and tables embedded in images.
- Do not perform visual interpretation or expose images in answers.
- Mark OCR-derived content and preserve its page-level origin.
- Apply automatic OCR quality checks and exclude uncertain fragments rather than silently trusting them.

**Synchronization and publication:**

- Run scheduled synchronization during the weekend so Monday starts with current content.
- Allow an administrator to start a manual synchronization.
- Detect additions, modifications, replacements, and deletions.
- Reject or flag files that violate the naming contract.
- Prevent concurrent synchronization runs.
- Build and validate a new index while the previous index remains active.
- Publish a valid index automatically and atomically.
- On failure, retain the previous active index and notify the administrator.
- Keep only the active index and the immediately previous index.
- Permit an audited administrative rollback to the previous index.

**Candidate SDD changes:**

- [ ] `integrate-approved-source-repository`
- [ ] `add-versioned-pdf-and-ocr-ingestion`
- [ ] `add-atomic-index-publication`
- [ ] `add-index-rollback`

## Phase 4 — Bilingual retrieval and source-conflict handling

**Phase status:** [ ] Completed

**Objective:** Select the correct evidence without crossing language or document-governance boundaries.

**Bilingual retrieval:**

- Detect whether the question is Spanish or English.
- Apply language as a mandatory pre-retrieval filter.
- Search only the matching corpus and answer in the question language.
- Never fall back silently to the other language.
- Ask for clarification when the language is mixed or ambiguous.
- Use approved terminology only for query understanding and expansion, never as answer evidence.

**Retrieval capabilities:** persistent vector storage, lexical search, hybrid retrieval, metadata filters, relevance thresholds, reranking, result diversification, and document/revision filters.

**Source conflicts:**

- Multiple complementary approved entries may support one answer.
- On direct contradiction, do not select a winner or synthesize a conclusion.
- Show both contradictory fragments with entry name, revision, section, and page.
- Recommend a human expert.
- Create a deduplicated contradiction alert for the administrator, visible and managed only in the operations panel.
- Allow the administrator to mark an alert open, resolved, or dismissed; a note is optional.
- Suppress a dismissed alert for the same fragments and revisions.
- Invalidate suppression when either source content or revision changes.
- Dismissing an administrative alert does not change the reader-facing abstention.

Every retrieval change must be compared against the Phase 2 baseline.

**Candidate SDD changes:**

- [ ] `add-language-isolated-hybrid-retrieval`
- [ ] `add-approved-terminology-query-expansion`
- [ ] `add-source-contradiction-detection`
- [ ] `add-contradiction-alert-workflow`

## Phase 5 — Grounded conversational generation

**Phase status:** [ ] Completed

**Objective:** Produce concise, actionable, conversational answers whose claims are individually traceable to current evidence.

**Answer contract:**

- Lead with the direct answer or numbered process steps.
- Show one of: `supported`, `insufficient_information`, `contradictory_information`, `out_of_scope`, `unavailable`, or `session_expired`. No ad-hoc statuses.
- Attach citations to the claims they support rather than providing an undifferentiated source list.
- Each citation shows entry name, language, revision, section, page, exact fragment, and source link.
- Mark citations derived from OCR and advise verification in the original document.
- Do not expose numeric confidence scores.
- Do not show or interpret source images.
- For insufficient evidence, show at most three related fragments, avoid a partial conclusion, and finish by recommending a human expert.
- For out-of-scope questions, do not attempt a general-knowledge answer.
- Mention the human expert only; do not open, prefill, or claim to submit an escalation.

**Conversation behavior:**

- Support follow-up questions within a conversation.
- Re-evaluate evidence on every turn; conversation history helps interpret the query but is never evidence.
- Limit one conversation to 20 user questions, then require a new conversation without requiring sign-out.
- Keep conversation context only in the active session.
- Do not preserve a reader-visible conversation history across sessions.

**Candidate SDD changes:**

- [ ] `add-fully-grounded-answer-generation`
- [ ] `add-verifiable-inline-citations`
- [ ] `add-safe-insufficient-evidence-responses`
- [ ] `add-bounded-conversational-followups`

## Phase 6 — Application services and data lifecycle

**Phase status:** [ ] Completed

**Objective:** Expose stable application boundaries and store only the data required by the approved product policies.

**Service boundaries:**

- Query and conversational-session service.
- Citation and evidence service.
- Feedback service.
- Synchronization and index-lifecycle service.
- Contradiction-alert service.
- Technical-review service.
- Analytics service.
- Policy-version and acceptance service.
- Audit service.

**Data lifecycle:**

- Store question text, answer, sources, revisions, feedback, and corporate identity for 12 months.
- After 12 months, remove query content and user association; retain only non-reconstructable aggregate metrics.
- Retain administrative audit records for 12 months.
- Apply automated, auditable expiration and aggregation.
- Keep active conversation context for 30 minutes of inactivity.
- Warn five minutes before expiration and allow explicit extension.
- Delete usable conversation context on expiration while preserving authorized analytical records.
- Do not provide data exports in the MVP.

**Architecture direction:** keep domain behavior independent from LLM vendors, embedding providers, PDF parsers, vector stores, email providers, and hosting platforms.

**Candidate SDD changes:**

- [ ] `expose-opsknowledge-application-services`
- [ ] `add-query-feedback-and-review-data-model`
- [ ] `add-twelve-month-data-retention`
- [ ] `add-versioned-policy-acceptance`

## Phase 7 — Reader and operations web experience

**Phase status:** [ ] Completed

**Objective:** Deliver a standalone, accessible desktop web application for readers and authorized operational roles.

**Client baseline:**

- Desktop-first on corporate Windows workstations.
- Support current corporate Microsoft Edge and Google Chrome versions.
- Spanish interface for the MVP.
- Spanish and English questions and generated answers remain supported.
- Meet WCAG 2.2 AA as the baseline, without requiring formal certification for the MVP.

**Reader experience:**

- Text-only questions; no attachments, images, or audio.
- Conversation view with concise answers and inline citations.
- Evidence panel with entry metadata, fragments, OCR indicator, and source links.
- Clear `supported`, `insufficient_information`, `contradictory_information`, `out_of_scope`, `unavailable`, and `session_expired` states.
- Useful / not useful feedback on every answer, with an optional comment.
- A not-useful rating recommends a human expert but does not claim automatic escalation.
- Permanent reminder not to enter sensitive data.

**Operations panel:**

- Search and filter queries by date, user, language, feedback, review classification, entry, and response outcome.
- Permit authorized roles to view full query text and reader identity during the retention period.
- Provide review classifications: correct, incorrect, incomplete, or should have abstained.
- Do not require review correction text or reviewer comments in the MVP.
- Provide synchronization status, history, rejected files, active revisions, manual synchronization, rollback, and contradiction management.
- Permit only administrators to pause and resume the assistant globally.
- Do not expose policy-acceptance reports or export query data in the MVP.

**Candidate SDD changes:**

- [ ] `add-reader-grounded-chat-ui`
- [ ] `add-citation-and-evidence-panel`
- [ ] `add-answer-feedback-ui`
- [ ] `add-operations-and-review-dashboard`
- [ ] `add-administrative-index-controls`

## Phase 8 — Corporate identity, privacy, and security

**Phase status:** [ ] Completed

**Objective:** Restrict the system and its data to approved corporate identities and controlled infrastructure.

**Identity and authorization:**

- Use Microsoft Entra ID single sign-on.
- Restrict access to the corporate tenant.
- Map permissions from corporate groups for readers, contributors, reviewers, and administrators. Operational responsibilities (synchronization, rollback, global pause, contradiction management) are assigned to the `admin` role.
- All four roles with analytical access may view full query text and reader identity.
- Only administrators may manage synchronization, rollback, global pause, and contradiction state.
- Audit access to identified query history and administrative actions.

**Policy and sensitive-data controls:**

- Require acceptance on first use and whenever the policy version changes.
- Block querying until the current version is accepted.
- Store user, policy version, and acceptance timestamp internally without adding an administrative acceptance report.
- Warn users not to enter sensitive information.
- Detect only high-confidence obvious patterns such as known identifiers, email addresses, or telephone numbers.
- Block a high-confidence sensitive query before model processing or storage.
- Record only the blocking event, not the sensitive text.
- Do not promise perfect name or sensitive-data detection.

**AI and infrastructure boundary:**

- Questions, guide fragments, embeddings, and outputs must remain in a corporate-controlled environment.
- Azure OpenAI is the preferred provisional managed option for the MVP.
- Final selection depends on TI confirmation of subscription, authorization, region, budget, private networking, and compliance.
- Use managed identities, encryption, private networking, and secretless service-to-service access where the approved platform supports them.
- Keep provider abstractions so an approved alternative or self-hosted model can replace Azure OpenAI.
- User queries and documents cannot override the system policy.
- Do not create a special administrator alert category for prompt-rule-evasion attempts in the MVP.

**Pending TI inputs:**

- Azure subscription and Azure OpenAI approval.
- Allowed processing region and data policies.
- Network and private-endpoint requirements.
- Budget and operational ownership.
- Entra group identifiers, owners, and membership rules.

**Candidate SDD changes:**

- [ ] `add-entra-single-sign-on`
- [ ] `add-entra-group-authorization`
- [ ] `add-versioned-policy-access-gate`
- [ ] `add-sensitive-query-preprocessing`
- [ ] `deploy-controlled-ai-provider-integration`
- [ ] `add-security-and-access-auditing`

## Phase 9 — Operations, analytics, and controlled pilot

**Phase status:** [ ] Completed

**Objective:** Operate OpsKnowledge safely, understand its behavior, and validate the pilot before broader adoption.

**Observability:**

- Monitor application health, Entra authentication, approved-source access, synchronization, index status, retrieval, model provider, database, latency, and failures.
- Show a safe unavailable state and recommend a human expert during outages.
- Send application and synchronization failure notifications to the administrator.
- Do not define a formal availability percentage for the MVP.
- Target visible processing feedback in under one second.
- Target complete responses in under 10 seconds for at least 95% of normal queries.
- Never replace a timeout with an ungrounded answer.

**Analytics:**

- Measure query volume, language, topics, supported answers, abstentions, contradictions, human-expert recommendations, latency, entries used, and useful / not useful feedback.
- Store analytics with corporate identity for the approved 12-month period.
- Allow authorized roles to inspect all retained questions for a specific reader.
- Do not permit Excel or CSV export in the MVP.

**Pilot:**

- Main site only; other sites are deferred.
- Main operating window: Monday–Friday, 06:00–15:00, with possible overtime until 18:00.
- Five users with varied experience and, where possible, both query languages.
- One-week initial validation, not an ROI or support-reduction study.
- Reviewer examines 100% of pilot answers daily.
- Review results are data only and do not create automatic alerts.
- Incorrect answers are evaluated during daily review; the administrator decides and performs any global pause manually.
- Phase 1 success focuses on critical safety, citation correctness, abstention behavior, usability, and absence of blocking defects.
- A wider impact-measurement phase will be defined after the pilot and after the historical support baseline is available.

**Candidate SDD changes:**

- [ ] `add-opsknowledge-health-and-latency-monitoring`
- [ ] `add-query-quality-analytics`
- [ ] `add-administrator-operational-alerts`
- [ ] `run-five-user-safety-pilot`

## Phase 10 — Scale-out and later integrations

**Phase status:** [ ] Completed

**Objective:** Expand only after the pilot establishes safe and useful behavior.

**Deferred decisions and capabilities:**

- Define the second pilot or wider rollout using Phase 9 evidence.
- Obtain total users, active users, shift distribution, peak concurrency, and queries per user before final capacity sizing.
- Expand beyond the main site.
- Define a formal availability SLO and support model.
- Add horizontal scaling, queues, batch ingestion, retries, circuit breakers, caches, provider fallback, and cost controls as measured load requires.
- Consider an English interface.
- Consider Teams integration.
- Consider integration with approved operations tools.
- Consider human-expert deep links or prefilled escalation only after the standalone flow is validated.
- Consider controlled exports only with explicit authorization and audit requirements.
- Revisit visual interpretation only through a separately reviewed safety change; it is not part of the current roadmap baseline.

**Candidate SDD changes:**

- [ ] `define-wider-rollout-and-capacity-plan`
- [ ] `add-production-resilience-and-scaling`
- [ ] `add-additional-site-support`
- [ ] `add-teams-escalation-entrypoint`
- [ ] `integrate-approved-operations-tool`
- [ ] `integrate-human-expert-escalation`

## Cross-phase safety invariants

These constraints apply to every future SDD change and cannot be postponed to a later hardening phase:

1. Only current approved entries can support a corporate-product answer. A development-only prototype may use manifest-controlled synthetic evidence under the isolated exception defined in the product boundary; that evidence can never enter a corporate index.
2. Retrieval must be filtered to the query language before evidence reaches the model.
3. Conversation history, glossary entries, support history, and model knowledge are never answer evidence.
4. Every technical claim requires a valid citation.
5. Unsupported, out-of-scope, and contradictory cases abstain and recommend a human expert.
6. Patient-specific analysis is outside scope.
7. No partial index may become active.
8. Authorization occurs before identified records or restricted operations are returned.
9. Images are not interpreted; only extracted OCR text may be considered, with explicit provenance and quality controls.
10. Significant safety behavior changes require evaluation against the Phase 2 baseline before release.

## SDD workflow for each future change

Each candidate change follows the complete lifecycle only when the team explicitly starts SDD:

```text
Exploration
    ↓
Proposal
    ↓
Specification + Design
    ↓
Tasks
    ↓
Implementation
    ↓
Verification
    ↓
Archive
```

Do not create one change named `build-complete-rag-platform`. Prefer bounded changes with explicit acceptance criteria, measurable results, independent rollback boundaries, and a clear owning phase.

## Next step

Phase 0 documentation baseline and the test-harness bootstrap are complete (see Phase 0 completion notes). Before Phase 1 implementation, complete `harden-focused-test-scanner-import-aliases`; `refresh-github-actions-node-runtime-pins` also belongs in this pre-Phase-1 CI-hardening boundary and remains independent for review and rollback. Obtain the pending Phase 0 and Phase 8 inputs before beginning product implementation. Architecture baseline and contributor contract: `AGENTS.md` and `docs/architecture/platform-architecture.md`. CI contributor rules: `docs/contributing/ci.md`. Dependency governance evidence: `governance/direct-dependencies.yaml`.
