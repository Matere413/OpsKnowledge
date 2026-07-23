# Exploration: Build OpsKnowledge Evaluation Dataset

The recommended scope is a bounded Phase 0 dataset artifact: create a governed, reproducible bilingual synthetic evaluation corpus and reviewed scenario set, without implementing the runtime evaluator, retrieval pipeline, model calls, corporate ingestion, or production analytics.

## Current State

`RAG_ROADMAP.md` identifies this as the next Phase 0 change. The current prerequisite is one manifest-controlled, versioned, approved, language-tagged, visibly non-corporate, development-only synthetic sample across `runbooks`, `adrs`, and `operational-policies`. The first slice must be 50% answerable/grounded and 50% abstention/safety, with Spanish/English parity.

The repository currently contains only the Python 3.12 test harness and architecture-contract tests; no application runtime, corpus manifest, evaluation dataset, evaluator command, or database exists. The architecture defines future `corpus`, `query`, and `indexing` ownership, but explicitly says runtime source and manifests are produced by bounded implementation changes. The dataset therefore needs to be a standalone, deterministic input artifact that later Phase 1/2 changes can consume.

The dataset is not answer evidence by itself unless its synthetic entries are explicitly represented as the development-only approved corpus. Historical corporate metrics, support Q&A, and glossaries are optional controlled references only: they are not prerequisites, ground truth, or answer evidence.

## Affected Areas

- `RAG_ROADMAP.md` — defines the Phase 0 scope, 50/50 target, safety cases, and next-change boundary; no roadmap edit is required by this exploration.
- `AGENTS.md` — requires synthetic corpus isolation, citation-only claims, language isolation, abstention, safe logging, and no corporate-boundary leakage.
- `docs/architecture/platform-architecture.md` — defines synthetic entry metadata, provenance, fragment shape, future module ownership, and the planned demo/profile gates.
- `openspec/config.yaml` — requires hybrid persistence, RFC 2119/Given-When-Then downstream specs, frozen pytest verification, and bounded reversible changes.
- `tests/` and `pyproject.toml` — provide the current dependency-free runtime/test baseline; adding dataset tooling or production dependencies would be a separate decision and must be governed.
- `openspec/changes/build-opsknowledge-evaluation-dataset/exploration.md` — this phase artifact only; no proposal, spec, design, or tasks are created.

## Intended Scope

The future proposal should define:

1. A small manifest-controlled bilingual synthetic collection covering all three approved collection types, with stable IDs, independent language/revision metadata, classification, approval state, and content hashes.
2. A deterministic scenario catalog with explicit case type, language, query, expected outcome, expected evidence/claims, abstention reason where applicable, and traceable source fragments.
3. Spanish/English parity for answerable, ambiguous/incomplete, contradictory, out-of-scope, unanswerable, prompt-override, OCR-uncertainty, and sensitive-identifier cases where the language is meaningful.
4. Validation rules that fail closed on missing provenance, invalid source references, mixed-language evidence, duplicate IDs, non-synthetic classification, malformed manifest entries, and deviation from the 50/50 target.
5. A clear boundary between dataset validation and the later Phase 2 evaluation harness, metrics, baseline report, and release-blocking thresholds.

## Unresolved Product Questions

- What exact dataset format and directory are preferred: JSON/YAML files, Python fixtures, or a manifest plus separate entry/scenario documents?
- What initial scenario count constitutes a useful but reviewable slice, and how should rounding work for the 50/50 distribution?
- Which synthetic operational topics and terminology should be represented, and who is the reviewer/owner for approval?
- How should direct contradiction be encoded: two entries with conflicting revisions, two distinct entries, or both?
- Which OCR uncertainty and sensitive-identifier patterns can be safely synthetic without implying real corporate data?
- Should expected answers be literal reference answers, claim sets, outcome labels, or only evidence/abstention expectations? Claim sets are safer and more reusable than model-generated gold answers.
- Is a dataset-only validator acceptable in this change, or must the change include a repeatable command and machine-readable validation report? The latter begins to overlap Phase 2 and should remain limited to structural dataset validation.

## Approaches

1. **Static reviewed fixtures** — Store synthetic entries and scenarios as versioned repository files with a manifest and a small structural validator.
   - Pros: deterministic, auditable, easy to review and consume without runtime infrastructure; keeps provider and framework dependencies out.
   - Cons: requires disciplined schema evolution and review; limited ergonomic authoring support.
   - Effort: Medium

2. **Generated dataset from scenario templates** — Define compact templates and generate bilingual entries/scenarios during validation or preparation.
   - Pros: improves parity and reduces repetitive authoring; can enforce balanced case counts.
   - Cons: generated text can obscure provenance, introduce nondeterminism, or look like fabricated ground truth; adds tooling and review complexity.
   - Effort: Medium/High

3. **Database-backed seed dataset** — Seed the future PostgreSQL corpus/index model and evaluate through the planned application boundary.
   - Pros: resembles the target architecture.
   - Cons: runtime and database do not exist; couples Phase 0 to Phase 1/3 implementation, violates bounded sequencing, and risks synthetic data escaping its development boundary.
   - Effort: High; not recommended

## Recommendation

Use static reviewed fixtures with a manifest, stable provenance, explicit expected outcomes/claim support, and a dependency-free structural validator. Keep expected answers out of scope unless needed as non-authoritative reviewer notes; the canonical expected data should be outcome, evidence references, abstention reason, language, and safety classification. Treat any command as a dataset-validation command only, not the Phase 2 evaluator. Make all files visibly synthetic and enforce that the dataset cannot be wired outside the development profile in the later runtime change.

This approach best satisfies the roadmap’s only current prerequisite while preserving the prototype/corporate boundary, citation-only evidence, language isolation, and the later Phase 2 responsibility for retrieval/answer metrics and release thresholds.

## Risks

- A dataset that contains answer text rather than claim/evidence expectations may become accidental ground truth or mask unsupported claims.
- Synthetic cases may be too simple to expose retrieval, contradiction, OCR, language-routing, and abstention failures.
- “Parity” can be nominal if Spanish and English cases are translated but not semantically equivalent; parity needs an explicit review rule.
- Contradictory or OCR cases may accidentally imply that images are answer evidence; only extracted OCR text with provenance may be represented.
- Introducing YAML/JSON tooling or runtime dependencies can expand the change beyond the current empty production dependency baseline.
- A future runtime may accidentally consume synthetic fixtures as corporate data; profile, classification, and CI denial requirements must remain explicit.

## Ready for Proposal

Yes, with the product questions above resolved or explicitly bounded in the proposal. The next phase should create the proposal only; it should not implement the Phase 2 evaluation harness, retrieval metrics, model evaluation, corporate data intake, or application runtime.
