# Apply Progress: OpsKnowledge Quality Evaluation Harness

Change: `add-opsknowledge-quality-evaluation-harness`
Project: `opsknowledge`
Mode: Standard (Strict TDD `false` per `openspec/config.yaml` and `sdd/opsknowledge/testing-capabilities`)
Delivery strategy: `auto-chain` (resolved by user after ask-on-risk)
Chain strategy: `stacked-to-main`
Work unit: `unit-3-safe-reports-opt-in-wiring` (Unit 3 of 3 — final implementation slice)
Attempt ordinal: 5 (Unit 1 = ordinal 1; Unit 2 = ordinal 3; Unit 3 = ordinal 5 per native runtime objective)
Native generation 5 / ordinal 5 active at revision `sha256:b8daee14ea1511d7f38c67682d929419ba7e586a39953c11c9e56c4bb1f94f7e`.

## Completed Tasks

### Unit 1 (merged as PR #33 / commit 97cb0ee)
- [x] 1.1 RED: fail-closed validation and mapping contract tests
- [x] 1.2 GREEN: evaluation package foundations, immutable domain/ports/mapping, dataset adapter with validator-before-load behavior and 32 reviewed ES/EN rows
- [x] 1.3 RED: exact base/injected case population inputs, base-byte preservation, deterministic identity/order/bytes, and no wall-clock read contracts
- [x] 1.4 GREEN: Clock protocol plus SystemClock/FrozenClock and stable deterministic input/identity support

### Unit 2 (merged as PR #35 / merge commit 714eddf)
- [x] 2.1 RED: language isolation, mapping-as-input-only, typed ES/EN provider-timeout -> unavailable, no fabricated evidence/external calls, five numeric threshold-free formulas
- [x] 2.2 GREEN: application.py and adapters/kernel.py; development resolve_query, LexicalRetriever/FakeProvider, 34 cases, language recorded without content
- [x] 2.3 GREEN: domain.py denominators (outcome/citation /34, language/retrieval, sensitive/sensitive, contradiction/contradictory)

### Unit 3 (this slice)
- [x] 3.1 RED: canary tests for allowlisted deterministic JSON summary, JSONL scenario rows, concise human output, forbidden-content absence, incomplete-promotion rejection, and atomic current/previous retention
- [x] 3.2 RED: architecture tests for safe fixed command/path behavior, nonzero failure with no promotion, no new dependencies/external surfaces, opt-in target, and unchanged make ci membership/order
- [x] 3.3 GREEN: report adapter, CLI, opt-in make eval-quality, and exactly one reviewed safe baseline under evaluation-runs/current/; previous/ created only on replacement

## Files Changed

### Unit 1 (historical -- merged in PR #33)
| File | Action | What Was Done |
|------|--------|---------------|
| `backend/features/evaluation/{__init__,domain,ports,mapping}.py` | Created | Contracts, immutable domain, ports, 32 reviewed ES/EN mapping rows. |
| `backend/features/evaluation/adapters/{__init__,dataset,clock}.py` | Created | Dataset gate (validate before load), SystemClock/FrozenClock. |
| `tests/unit/test_quality_evaluation_harness.py` | Created | 15 Unit 1 contracts. |

### Unit 2 (historical -- merged in PR #35 / merge commit 714eddf)
| File | Action | What Was Done |
|------|--------|---------------|
| `backend/features/evaluation/domain.py` | Modified | Added `case_type` to CaseRecord; added MetricSignal, Metrics, compute_metrics with five threshold-free formulas and explicit denominators. |
| `backend/features/evaluation/application.py` | Created | assemble_cases (32 base + 2 injected = 34), run_evaluation, RunSummary, manifest digest, mapping validation before assembly. |
| `backend/features/evaluation/adapters/kernel.py` | Created | KernelAdapter wrapping unchanged resolve_query/LexicalRetriever/FakeProvider; typed ProviderFailure("provider-timeout") for injected pair; records safe fields + language only. |
| `tests/unit/test_quality_evaluation_harness.py` | Modified | Added 6 Unit 2 tests. |
| `openspec/changes/.../tasks.md` | Modified | Marked tasks 2.1-2.3 `[x]`. |

### Unit 3 (this slice)
| File | Action | What Was Done |
|------|--------|---------------|
| `backend/features/evaluation/adapters/report.py` | Created | Safe serialization (JSON summary, JSONL records, human output) with allowlisted fields only; atomic ReportAdapter with current/previous retention and incomplete-promotion rejection. |
| `backend/features/evaluation/cli.py` | Created | Opt-in CLI entry point using FrozenClock; resolves dataset root, runs evaluation, promotes baseline atomically. |
| `Makefile` | Modified | Added opt-in `eval-quality` target (not in `ci`); uses `$(UV_RUN) run --frozen python -m backend.features.evaluation.cli evaluation-dataset`. |
| `tests/unit/test_quality_evaluation_harness.py` | Modified | Added 5 canary tests: allowlisted JSON summary, 34-row JSONL, concise human output, incomplete-promotion rejection, atomic retention. |
| `tests/architecture/test_quality_evaluation_harness.py` | Created | 14 architecture contracts: eval-quality target exists/opt-in, fixed UV_RUN argv, validated dataset root, no forbidden imports (10 modules parametrized), unchanged ci membership/order. |
| `evaluation-runs/current/summary.json` | Created | One reviewed safe baseline (deterministic JSON summary). |
| `evaluation-runs/current/records.jsonl` | Created | One reviewed safe baseline (34 JSONL scenario rows). |
| `evaluation-runs/current/report.txt` | Created | One reviewed safe baseline (concise human output). |
| `openspec/changes/.../tasks.md` | Modified | Marked tasks 3.1-3.3 `[x]`. |

## Work Unit Evidence

| Evidence | Value |
|---|---|
| Focused test command and exact result | `uv run --frozen pytest tests/unit/test_quality_evaluation_harness.py -k "json_summary or jsonl_records or human_output or incomplete_promotion or atomic_retention"` -> 5 passed, 21 deselected, exit 0 |
| Architecture test command and exact result | `uv run --frozen pytest tests/architecture/test_quality_evaluation_harness.py` -> 14 passed, exit 0 |
| Full harness test command and exact result | `uv run --frozen pytest tests/unit/test_quality_evaluation_harness.py tests/architecture/test_quality_evaluation_harness.py` -> 40 passed, exit 0 |
| No regressions | `uv run --frozen pytest tests/` -> 357 passed, exit 0 |
| Quality gates (Unit 3 scope) | `ruff check` All checks passed; `ruff format --check` 48 files already formatted; `pyright` 0 errors, 0 warnings; `check_focused_tests.py` clean |
| Runtime harness command/scenario and exact result | `make eval-quality` -> exit 0; output shows run_id `25b742...`, total_cases 34, five metrics (9/34, 10/34, 34/34, 2/2, 0/4); `evaluation-runs/current/` has summary.json + records.jsonl (34 rows) + report.txt; no `previous/` directory (created only on replacement) |
| Rollback boundary | Remove `backend/features/evaluation/adapters/report.py`, `backend/features/evaluation/cli.py`, `tests/architecture/test_quality_evaluation_harness.py`, revert the 5 canary tests from `test_quality_evaluation_harness.py`, revert the `eval-quality` target in `Makefile`, remove `evaluation-runs/`, and revert the three task checkboxes. Units 1/2 (domain, ports, mapping, dataset, clock, application, kernel), dependencies, `make ci`, and runtime state are untouched. |

## RED/GREEN Discipline (Standard mode, behavior-first)

- 3.1 RED: 5 canary tests written first; confirmed failing with `ModuleNotFoundError: No module named 'backend.features.evaluation.adapters.report'` (all 5 failed on import).
- 3.2 RED: 3 architecture tests written first; confirmed failing with `AssertionError: Makefile target 'eval-quality' not found` (3 target-dependent tests failed; 11 invariant tests passed correctly).
- 3.3 GREEN: report adapter, CLI, and Makefile target implemented; all 5 canary tests + 14 architecture tests pass; runtime harness produces deterministic safe output.

## Runtime Attempt Evidence

- Command: `make eval-quality`
- Exit code: 0
- run_id: `25b742108455f8dc4d377495359c3f9a942a0836254a08b393a2768579fc0de3`
- total_cases: 34
- Five numeric metrics: outcome_classification 9/34, citation_exact_match 10/34, language_routing 34/34, sensitive_block 2/2, contradiction_detection 0/4
- Deterministic: stable run_id across repeated frozen runs
- Safe output: no question/answer/citation/claim/payload content in summary.json, records.jsonl, or report.txt
- No thresholds or runtime state
- Baseline structure: `evaluation-runs/current/` only (no `previous/` on first run)
- RDD: disabled/unmanaged per upstream issue #1892

## Deviations from Design

None -- implementation matches design.md. The allowlisted JSON/JSONL/human
serialization, atomic baseline retention with current/previous promotion,
incomplete-promotion rejection, opt-in Makefile target outside ci, and
unchanged ci membership/order are all per the design's Architecture Decisions,
Data Flow, Interfaces/Contracts, and Testing Strategy sections.

## Issues Found

- **CLI path resolution**: `cli.py` is at `backend/features/evaluation/cli.py`,
  so `Path(__file__).resolve().parents[3]` resolves to the project root (not
  `parents[4]`). Fixed during implementation; no design deviation.
- **Line budget**: pure authored code/test lines = 395 (8 Makefile + 108 test
  additions + 105 report.py + 47 cli.py + 126 architecture test), within the
  400-line budget. Baseline files (summary.json + records.jsonl + report.txt)
  are generated goldens excluded from the authored count.

## Independent Verification

- [x] 4.1 Run focused unit/architecture tests; record evidence for all eight authoritative scenarios; add no integration/E2E layer.
- [x] 4.2 Run `make eval-quality`; verify 34 records, five numeric metrics, deterministic safe output, bounded baselines, no thresholds/state.
- [x] 4.3 Run unchanged `make ci`; verify membership/order and do not initiate RDD review or enablement.

### Verification Evidence

- Independent standard verification passed: 8/8 requirements and 8/8 scenarios compliant.
- Focused tests passed: Unit 1 = 6, Unit 2 = 3, Unit 3 = 5, architecture = 14; full `tests/` = 357 passed.
- `make eval-quality` ran exactly once with exit 0, produced 34 unique safe records and five numeric metrics, and reproduced the deterministic current baseline.
- Retention was proven by observing byte-identical current/previous baselines; only validation-created `evaluation-runs/previous/` was removed afterward, leaving the intended first-baseline current shape.
- `make ci` ran exactly once with exit 0; all 11 canonical stages passed and its pytest stage collected 357 tests. `eval-quality` remains opt-in and outside `ci`.
- No dependency, lockfile, governance, dataset, kernel-boundary, or CI membership/order drift was found. Development-only profile and typed provider-failure semantics were confirmed.
- RDD remains disabled/unmanaged under upstream issue #1892; no review or 4R approval was initiated.
- Runtime finish inputs: generation 7, ordinal 7, launch revision `sha256:b7a36ead3c8f80643cbffb0f15d7045e7da21b2a8349cee3de887f0f375a4364`, max changed lines 400.

## Workload / PR Boundary

- Mode: chained PR slice (stacked-to-main) -- final implementation slice
- Current work unit: unit-3-safe-reports-opt-in-wiring
- Boundary: starts from merged Unit 2 (PR #35 / merge commit 714eddf); ends with the report adapter, CLI, opt-in `make eval-quality`, one reviewed safe baseline, architecture tests, and all Unit 3 tests passing. No verification/archive tasks, no commit/push/PR/review, no full `make ci` run.
- Estimated review budget impact: ~395 authored changed lines for this slice (within 400).

## Status

13/13 tasks complete (Units 1-3 plus independent verification tasks 4.1-4.3). Ready for archive only after normal downstream orchestration.
