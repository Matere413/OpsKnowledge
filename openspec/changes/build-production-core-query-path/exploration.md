## Exploration: build-production-core-query-path

### Current State

The repository is a clean `master` checkout at `e5e6577`, with PR #28 / merge `12ba6926` immediately preceding the roadmap reframe. The production runtime does not exist yet. The current implementation is a bounded corpus foundation only:

- `backend/features/corpus/` loads an immutable, manifest-controlled, approved synthetic corpus and fails closed unless the active profile is `development`.
- `backend/features/query/` contains only package markers; there is no query domain, application service, retrieval implementation, prompt builder, provider adapter, outcome classifier, or CLI.
- `backend/shared/ports.py` defines `Retrieve`, `Generate`, safe JSON logging, the six outcome values, and a safe response that deliberately omits answer text. These are contracts, not implementations. There is no embedding port.
- `Corpus` exposes fragments but discards the loaded `Entry` mapping. Fragments therefore do not currently carry explicit parent revision, logical-entry, collection, section, or page metadata needed for robust contradiction grouping and future rendered citations.
- The evaluation dataset is static input only: five synthetic entries, eight fragments, and 32 scenario records. Scenarios contain expected outcomes and evidence identifiers, but no literal query text or generated answers; runtime tests must use independent deterministic question fixtures.
- The test harness is operational (`pytest`, Ruff, Pyright, frozen `uv`, focused-test and dependency-boundary guards, and `make ci`). The existing corpus/core suite passes: 44 focused smoke and corpus tests passed.
- The active `build-minimal-grounded-opsknowledge-core` artifacts describe the superseded prototype-oriented plan. They remain historical, must not be rewritten by this exploration, and credit only the corpus/ports slice as delivered. The archived roadmap-reframe lineage explicitly leaves retrieval, prompt, provider, outcome, and CLI work pending.

The governing roadmap and architecture require language filtering before evidence reaches a model, citation-only grounding, deterministic abstention, safe provider failure, no persistence in this slice, and preservation of the separate development synthetic boundary. Phase 2 evaluation remains incomplete, and Phase 8 identity, privacy, controlled-provider, and TI gates remain co-prerequisites for corporate processing.

### Affected Areas

- `backend/features/query/` — add the first query domain/application kernel: deterministic language routing, retrieval, evidence-constrained prompt construction, outcome rules, citation validation, and provider-failure mapping.
- `backend/features/corpus/{domain.py,application.py}` — likely provide an explicit parent-entry/provenance view or query-owned projection; contradiction detection and future citations cannot safely infer revisions by parsing identifiers alone.
- `backend/shared/ports.py` — clarify the existing `Retrieve`/`Generate` contracts and typed failure semantics without adding persistence or provider-specific imports.
- `tests/unit/` — add deterministic safety tests for same-language retrieval, sensitive-screen ordering, prompt evidence boundaries, contradictions, abstention, citation allow-lists, and fake-provider failures.
- `tests/architecture/` — affected only by a later CLI slice; subprocess and one-JSON-response coverage should not be bundled into the first kernel unless the review forecast remains below budget.
- `backend/features/query/cli.py`, `pyproject.toml`, `uv.lock`, `governance/direct-dependencies.yaml` — follow-up CLI/provider surfaces. The first kernel should not require a live provider or a new production dependency.
- `evaluation-dataset/` and `scripts/ci/validate_evaluation_dataset.py` — consumed as development-only synthetic fixtures; no dataset validator/runtime-evaluator merger is justified here.
- `RAG_ROADMAP.md` and archived SDD artifacts — reference-only during exploration. Phase completion and roadmap checkboxes remain governed by verification plus archive, not by this implementation planning step.

### Approaches

1. **Bundle retrieval, prompt, provider, outcomes, and CLI in one change** — implement the entire pending list against the synthetic fixture and expose it through a safe JSON command.
   - Pros: one visible end-to-end path; fewer interim interfaces.
   - Cons: combines query policy, inbound adapter, subprocess contract, dependency wiring, and provider-boundary decisions; likely exceeds the 400 authored-line review budget; encourages wiring public OpenAI before corporate Phase 8/TI gates; produces a large rollback boundary.
   - Effort: High

2. **Build a deterministic query kernel first, then add CLI and controlled provider as separate slices** — implement retrieval, evidence-constrained prompting, deterministic outcomes/citation validation, sensitive screening, and a deterministic fake provider in-process; add the safe CLI as a thin inbound adapter afterward; defer any live OpenAI/Azure adapter to a separately gated change.
   - Pros: smallest independently reversible safety unit; tests the core invariants without network or new dependencies; keeps domain/application provider-independent; makes the 400-line forecast visible before deciding on chained PRs; preserves Phase 2 and Phase 8 gates.
   - Cons: the first change has no user-facing command; parent-entry metadata and provider error semantics must be settled before implementation; end-to-end CLI proof arrives in the next slice.
   - Effort: Medium

3. **Complete Phase 2 evaluation before implementing the query kernel** — build the measurement harness and baseline first, then use it to drive retrieval and grounding implementation.
   - Pros: stronger quality gates before runtime behavior; directly follows the roadmap’s safety emphasis.
   - Cons: does not deliver the pending production-core contract; the static dataset currently lacks query text and cannot evaluate a runtime path by itself; delays the foundational interfaces needed by the evaluator.
   - Effort: High

### Recommendation

Use Approach 2. The named change should enter proposal with the narrow scope of a **deterministic grounded query kernel**:

1. Reuse the existing fail-closed development corpus loader and expose enough immutable parent metadata to group revisions and validate provenance without heuristic identifier parsing.
2. Add deterministic `es`/`en` language routing and retrieval that filters language, approval, classification, and profile before ranking; use a stdlib lexical score with stable tie-breaking, not embeddings or an external vector service.
3. Build prompts whose evidence section contains only the selected, same-language fragments and an explicit no-general-knowledge/no-unsupported-claim policy.
4. Apply deterministic pre-provider rules for sensitive input, empty/incomplete evidence, contradiction, and out-of-scope cases. Validate generated citation identifiers against the retrieved, approved, same-language set; invalid citations fail closed rather than being repaired or fabricated.
5. Keep `Generate` replaceable and implement only a deterministic fake/test adapter in this slice. Timeout, rate-limit, outage, and non-success behavior must map to `unavailable`, recommend a human expert, make no additional attempt, and expose no answer.
6. Keep the response/persistence boundary in-process and side-effect free. The kernel may retain an internal generated answer solely for citation validation; it must not log or persist question, answer, citation content, tokens, secrets, or provider payloads.

The proposal should explicitly exclude the live OpenAI/Azure adapter, embeddings, PostgreSQL/pgvector, HTTP, sessions, authentication, persistence, web UI, and Phase 2 metrics. A second bounded change should add `backend/features/query/cli.py` and subprocess tests for one safe JSON object, startup/profile denial, and content-free stderr. A later provider change may add a controlled corporate adapter only after the Phase 8/TI gate is documented; the existing `openai` governance entry is approved for the historical prototype risk, not a license to process corporate data.

The orchestrator should not convert these logical slices into chained PRs without the configured ask-before-splitting decision. The kernel plus its tests is likely near or above the 400-line budget; bundling the CLI or a provider dependency makes the risk high. Proposal and task planning should forecast authored lines separately for the kernel, CLI, and controlled-provider slices.

### Risks

- The current `Corpus` surface loses parent entry metadata, so contradiction detection and future citation rendering can become unsafe if the implementation derives revisions from identifier strings.
- The existing `Generate` protocol does not define a typed provider failure contract or prompt payload boundary; the proposal must define those before coding.
- The lower-authority active core spec omits answer text from CLI output and introduces an explicit session-expiry flag. Those prototype decisions must be consciously retained or superseded; `session_expired` belongs to the later session feature and must not be fabricated by the kernel.
- The approved public-OpenAI dependency is prototype-only and high risk. Adding a live provider now would blur the accepted demo risk with the corporate path and violate the Phase 8/TI sequencing.
- The static evaluation dataset has no query strings or gold answers, so passing unit tests will prove contract behavior, not retrieval quality. Phase 2 evaluation remains a release prerequisite.
- Sensitive screening must occur before retrieval/provider processing for any path that could later add egress; rejected content must never reach logs or persistence.
- Combining the kernel, CLI, tests, lockfile, and provider adapter is likely to exceed the 400-line review budget and weaken rollback clarity.

### Ready for Proposal

Yes. The repository evidence is sufficient for a proposal, provided the orchestrator confirms that the first proposal owns the deterministic query kernel only, keeps the CLI as a follow-up slice, and treats live provider integration as separately gated work. No code or existing artifact should be modified during exploration.
