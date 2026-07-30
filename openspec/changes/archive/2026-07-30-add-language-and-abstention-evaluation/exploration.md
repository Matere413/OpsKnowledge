# Exploration: add-language-and-abstention-evaluation

## Current State

The first genuinely pending roadmap item after the archived `add-technical-grounding-safety-gates` work is the Phase 2 candidate `add-language-and-abstention-evaluation` (`RAG_ROADMAP.md`, lines 201–205). The roadmap checkbox for the archived safety-gates change is stale (`[ ]`), but the archive exists at `openspec/changes/archive/2026-07-29-add-technical-grounding-safety-gates/`, its completion evidence is recorded, and its artifacts explicitly place expanded language and abstention evaluation in the next change.

The current Phase 2 substrate is a deterministic, development-only evaluation harness:

- `backend/features/evaluation/application.py` validates the synthetic dataset, assembles 32 mapped scenarios plus two injected provider-failure cases, runs the existing kernel, and returns safe results.
- `backend/features/evaluation/domain.py` computes only five threshold-free signals: outcome classification, exact citation-set match, language routing, sensitive blocking, and contradiction detection.
- `evaluation-runs/current/summary.json` records the current baseline: outcome `9/34`, citation exact match `10/34`, language routing `34/34`, sensitive block `2/2`, and contradiction detection `0/4`.
- The archived safety gate consumes those five signals and critical case outputs without adding metrics or cases. `make eval-quality-gate` is opt-in and remains outside `make ci` and `ci-pr2a`.
- The static dataset provides 32 bilingual scenarios (16 `es`, 16 `en`, 16 semantic pairs, 16 supported and 16 abstention/safety cases), expected outcomes, evidence IDs, claim expectations, and abstention reasons. It deliberately contains no question text or gold answers; the harness-owned mapping supplies deterministic input questions.

The Phase 2 roadmap still calls for correct abstention, unsupported-claim escape, language-routing accuracy, citation validity, contradiction detection, and other quality signals. The current implementation does not expose a distinct correct-abstention signal or unsupported-claim escape signal. There is also a metric-contract ambiguity: the `language_routing` documentation describes retrieval-eligible cases, while the current computation uses all result records as its denominator (`len(results)`, currently 34).

## Affected Areas

- `RAG_ROADMAP.md` — authoritative sequence and Phase 2 metric/acceptance contract; exploration must not edit its stale checkbox.
- `backend/features/evaluation/application.py` — existing 34-case execution and reviewed question mapping are the likely measurement input boundary.
- `backend/features/evaluation/domain.py` — current five-signal model and denominator semantics need an explicit extension or a separate measurement model.
- `backend/features/evaluation/adapters/` — dataset validation, kernel execution, and safe report boundaries must remain intact; the dataset remains development-only and manifest-controlled.
- `backend/features/evaluation/gates/` and `openspec/specs/technical-grounding-safety-gates.spec.md` — adjacent release-gate ownership; new measurements must not silently become new floors or alter the existing gate contract.
- `evaluation-runs/` — any new baseline must remain safe, deterministic, reviewable, and distinct from release thresholds.
- `tests/unit/` and `tests/architecture/` — metric semantics, bilingual parity, abstention/reason-code coverage, safe output, determinism, and opt-in/CI boundaries require focused proof.
- `openspec/specs/evaluation-dataset/spec.md` — authoritative prohibition on runtime wiring, Phase 2 metrics inside the dataset capability, and literal gold answers.
- `openspec/changes/archive/2026-07-29-add-opsknowledge-quality-evaluation-harness/` — completed harness contract and explicit deferral of language-routing and abstention-accuracy expansion.

## Approaches

1. **Extend the existing harness measurement surface** — preserve the 34-case execution and add reviewed language/abstention measurements and safe report fields around the existing `RunSummary`.
   - Pros: reuses deterministic execution, mappings, `Clock`, dataset validation, and safe serialization; keeps one Phase 2 run and one baseline lineage.
   - Cons: risks expanding the numbers-only harness beyond its archived contract; denominator changes could invalidate the existing baseline; may require a new contract/version rather than a silent extension.
   - Effort: Medium.

2. **Add a separate language-and-abstention evaluator over the existing harness output** — leave the five-signal harness and technical gate unchanged, and own the additional measurements in a new bounded capability.
   - Pros: preserves the archived ownership boundary; separates measurement from thresholds; allows explicit metric denominators and new evidence without rewriting the existing baseline.
   - Cons: creates a second evaluation/report surface; requires careful correlation with the 34-case run and a clear relationship to the existing opt-in gate.
   - Effort: Medium.

3. **Broaden Phase 2 into a full quality evaluator** — add new question/case coverage and attempt the remaining roadmap metrics such as retrieval recall, answer correctness, OCR quality, latency, and cost in one change.
   - Pros: gives a more complete Phase 2 picture.
   - Cons: exceeds the bounded next-step intent; the dataset has no authoritative question or answer text, and live providers, embeddings, persistence, corporate data, and new dependencies are outside the current boundary.
   - Effort: High.

## Recommendation

Use `add-language-and-abstention-evaluation` as the next bounded Phase 2 change. Enter proposal with an explicit measurement contract for language routing and abstention behavior, preferably as a separate capability or an explicitly versioned extension that leaves the archived five-signal harness and technical-grounding thresholds understandable. Reuse the existing development-only 34-case execution and reviewed mapping unless proposal decisions demonstrate that additional reviewed cases are necessary. Keep all outputs content-free, deterministic, opt-in, and independent of live providers, embeddings, persistence, HTTP, UI, corporate data, and threshold tightening.

The proposal must resolve whether this change measures only language-routing accuracy and correct abstention, or also owns unsupported-claim escape, OCR uncertainty, citation validity, latency/cost, or retrieval recall. It must define denominators and case populations before implementation, especially for screened cases, provider-failure cases, mixed/ambiguous language, and the current language-metric denominator mismatch.

### Recommended proposal questions

- Which exact Phase 2 metrics belong to this change, and which remain separate future changes?
- Should the evaluator reuse the existing 34 cases and mapping, add reviewed in-memory cases, or modify the static dataset? How will it avoid question text becoming authoritative ground truth?
- What precisely counts as correct language routing and correct abstention: outcome only, reason code, citation emptiness, human-expert recommendation, or a compound contract?
- Should the existing `technical-grounding-safety-gates` consume the new measurements, or should its five-signal threshold contract remain unchanged until a later reviewed change?
- Should the new report be a sibling baseline under `evaluation-runs/`, and must it remain opt-in rather than entering `make ci`?
- Given the current `9/34` outcome and `0/4` contradiction baseline, is this change measurement-only, or is any kernel correction explicitly allowed? A measurement change must not imply that observed failures are fixed.
- Does the expected work exceed the 400-line review budget, requiring an ask before chained delivery is planned?

## Risks

- **Metric ambiguity:** “language and abstention” is not a complete contract; silently including all remaining Phase 2 metrics would create an oversized, poorly reversible change.
- **Baseline incompatibility:** changing the existing denominator or case population can make the archived five-signal baseline incomparable without a versioned migration.
- **Hidden ground truth:** the dataset intentionally has no queries or answers. New mapping/case fixtures must remain reviewed inputs and must not become answer authority.
- **Runtime failure mistaken for evaluation completion:** current outcome and contradiction results are low (`9/34` and `0/4`); measuring them will expose gaps but does not implement their fixes.
- **Gate ownership drift:** adding thresholds or changing `make ci` membership would cross the archived safety-gate boundary and require separate explicit scope.
- **Boundary leakage:** live providers, embeddings, PostgreSQL, corporate material, HTTP/UI, or excluded dependencies would violate the current Phase 2 and prototype/corporate constraints.
- **Review load:** new metric contracts, safe reports, fixtures, and architecture tests may exceed the 400-line budget and should be forecast before apply.

## Ready for Proposal

Conditional yes. The repository has enough evidence to open a proposal for `add-language-and-abstention-evaluation`, and no existing active or archived change already covers that exact roadmap item. The archived quality harness and safety-gates changes provide adjacent substrate and explicit deferral, while the open `build-production-core-query-path` and `build-minimal-grounded-opsknowledge-core` artifacts are historical implementation lineage and do not own Phase 2 evaluation. The proposal should first settle the metric list, case/mapping policy, denominator semantics, gate/CI ownership, and review-budget forecast.
