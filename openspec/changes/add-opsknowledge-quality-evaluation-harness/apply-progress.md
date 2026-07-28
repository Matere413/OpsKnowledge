# Apply Progress: OpsKnowledge Quality Evaluation Harness

Change: `add-opsknowledge-quality-evaluation-harness`
Project: `opsknowledge`
Mode: Standard (Strict TDD `false` per `openspec/config.yaml` and `sdd/opsknowledge/testing-capabilities`)
Delivery strategy: `auto-chain` (resolved by user after ask-on-risk)
Chain strategy: `stacked-to-main`
Work unit: `unit-2-kernel-runner-metrics` (Unit 2 of 3)
Attempt ordinal: 3 (Unit 1 = ordinal 1; Unit 2 = ordinal 3 per native runtime objective)

## Completed Tasks

### Unit 1 (merged as PR #33 / commit 97cb0ee)
- [x] 1.1 RED: fail-closed validation and mapping contract tests
- [x] 1.2 GREEN: evaluation package foundations, immutable domain/ports/mapping, dataset adapter with validator-before-load behavior and 32 reviewed ES/EN rows
- [x] 1.3 RED: exact base/injected case population inputs, base-byte preservation, deterministic identity/order/bytes, and no wall-clock read contracts
- [x] 1.4 GREEN: Clock protocol plus SystemClock/FrozenClock and stable deterministic input/identity support

### Unit 2 (this slice)
- [x] 2.1 RED: language isolation, mapping-as-input-only, typed ES/EN provider-timeout → unavailable, no fabricated evidence/external calls, five numeric threshold-free formulas
- [x] 2.2 GREEN: application.py and adapters/kernel.py; development resolve_query, LexicalRetriever/FakeProvider, 34 cases, language recorded without content
- [x] 2.3 GREEN: domain.py denominators (outcome/citation /34, language/retrieval, sensitive/sensitive, contradiction/contradictory)

## Files Changed

### Unit 1 (historical — merged in PR #33)
| File | Action | What Was Done |
|------|--------|---------------|
| `backend/features/evaluation/{__init__,domain,ports,mapping}.py` | Created | Contracts, immutable domain, ports, 32 reviewed ES/EN mapping rows. |
| `backend/features/evaluation/adapters/{__init__,dataset,clock}.py` | Created | Dataset gate (validate before load), SystemClock/FrozenClock. |
| `tests/unit/test_quality_evaluation_harness.py` | Created | 15 Unit 1 contracts. |

### Unit 2 (this slice)
| File | Action | What Was Done |
|------|--------|---------------|
| `backend/features/evaluation/domain.py` | Modified | Added `case_type` to CaseRecord; added MetricSignal, Metrics, compute_metrics with five threshold-free formulas and explicit denominators (outcome/citation /34, language /retrieval, sensitive /sensitive, contradiction /contradictory). |
| `backend/features/evaluation/application.py` | Created | assemble_cases (32 base + 2 injected = 34), run_evaluation, RunSummary, manifest digest, mapping validation before assembly. |
| `backend/features/evaluation/adapters/kernel.py` | Created | KernelAdapter wrapping unchanged resolve_query/LexicalRetriever/FakeProvider; typed ProviderFailure("provider-timeout") for injected pair; records safe fields + language only. |
| `tests/unit/test_quality_evaluation_harness.py` | Modified | Added 6 Unit 2 tests: language isolation (2 params), mapping-as-input-only, injected provider failure (2 params), five numeric metrics. |
| `openspec/changes/.../tasks.md` | Modified | Marked tasks 2.1-2.3 `[x]`. |

## Work Unit Evidence

| Evidence | Value |
|---|---|
| Focused test command and exact result | `uv run --frozen pytest tests/unit/test_quality_evaluation_harness.py -k "population or provider or metrics or language_isolation or mapping_question or injected_provider or five_metrics"` -> 6 passed, 15 deselected, exit 0 |
| Full harness test command and exact result | `uv run --frozen pytest tests/unit/test_quality_evaluation_harness.py` -> 21 passed (15 Unit 1 + 6 Unit 2), exit 0 |
| No regressions | `uv run --frozen pytest tests/unit/` -> 95 passed (89 existing + 6 new), exit 0 |
| Quality gates (Unit 2 scope) | `ruff check` All checks passed; `ruff format --check` 45 files already formatted; `pyright` 0 errors, 0 warnings; `check_focused_tests.py` clean |
| Runtime harness command/scenario and exact result | N/A — CLI not wired in Unit 2 (per design: report/CLI are Unit 3). No runtime boundary exists for this slice. |
| Rollback boundary | Remove `backend/features/evaluation/application.py`, `backend/features/evaluation/adapters/kernel.py`, revert `domain.py` metric additions and `CaseRecord.case_type`, remove the 6 Unit 2 tests from `test_quality_evaluation_harness.py`, and revert the three task checkboxes. Unit 1 contracts, dataset, kernel, dependencies, `make ci`, and runtime state are untouched. |

## RED/GREEN Discipline (Standard mode, behavior-first)

- 2.1 RED: 6 tests written first; confirmed failing with `ModuleNotFoundError: No module named 'backend.features.evaluation.application'` (all 6 failed on import).
- 2.2/2.3 GREEN: implementation added; all 6 tests pass, full suite 95 passed.

## Deviations from Design

None — implementation matches design.md. The 34-case assembly, development
resolve_query/LexicalRetriever/FakeProvider boundary, typed ProviderFailure
injection, content-free result recording, and five numeric threshold-free
metrics with explicit denominators are all per the design's Architecture
Decisions, Data Flow, and Interfaces/Contracts sections.

## Issues Found

- **EN injected failure question design**: the EN corpus has only one entry
  (`adr-002`) with two revisions (rev 1 + rev 2). Any EN question matching
  shared tokens retrieves both revisions → the kernel's contradiction check
  fires before the provider call, returning `contradictory_information` instead
  of the intended `unavailable`. Resolved WITHOUT deviating from the design:
  the EN OCR fragment exists only at rev 1 (no rev 2 OCR), so a question using
  OCR-unique tokens (`scanned document provenance quality`) retrieves only that
  single-revision fragment, bypassing the contradiction check and reaching the
  provider where the typed `provider-timeout` fires. This is a corpus-structure
  reality, not a design gap — the design's intent (typed unavailable via
  ProviderFailure) is preserved exactly.
- **Line budget**: pure implementation code is 196 lines (application.py 134 +
  kernel.py 62) plus 78 domain additions and 99 test additions = 373 authored
  changed lines, within the 400-line Unit 2 budget.

## Remaining Tasks (Unit 3 — not in this slice)

- [ ] 3.1 RED: allowlisted JSON/JSONL/human output, incomplete-promotion rejection, atomic current/previous retention
- [ ] 3.2 RED: architecture tests (fixed UV_RUN argv, validated paths, non-zero failure/no promotion, no new deps/providers/embeddings/persistence/HTTP/auth/UI/corporate/external services, unchanged ci, RDD disabled per #1892)
- [ ] 3.3 GREEN: adapters/report.py, cli.py, opt-in eval-quality, one reviewed baseline
- [ ] 4.1-4.3 verification evidence

## Workload / PR Boundary

- Mode: chained PR slice (stacked-to-main)
- Current work unit: unit-2-kernel-runner-metrics
- Boundary: starts from merged Unit 1 (PR #33 / commit 97cb0ee); ends with the 34-case runner, kernel adapter, and five metrics + Unit 2 tests passing. No report, CLI, Makefile target, baseline files, architecture tests, or retention logic.
- Estimated review budget impact: ~373 authored changed lines for this slice (within 400).

## Status

7/13 tasks complete (Unit 1 + Unit 2). Ready for the next chained slice (Unit 3).