# Tasks: Technical Grounding Safety Gates

## Review Workload Forecast

Former uncommitted slice 2 measures 1,535 authored lines: report adapter 280, CLI 85, tests 1,161, and Makefile +9; native runtime recorded 1,686. Generated `evaluation-runs/gate/current/report.json` (3,136 bytes) and OpenSpec are excluded.

### Suggested Work Units

| Slice | PR | Estimate | Dependency; current material | Focused test | Runtime; rollback |
|---|---|---:|---|---|---|
| 2A report core | 2A | 380–395 | Unit 1; `report.py:1-143`, report tests `:1-252` | `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q -k serialize_gate_report` | N/A pure serializer; remove those hunks |
| 2B safety proof | 2B | 180–190 | 2A; report tests `:253-440` (test-only) | `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q -k 'critical_observations or forbidden or citation_ids'` | N/A — pure safety proof; remove coverage hunk |
| 2C promotion | 2C | 235–245 | 2B; `report.py:146-207`, tests `:447-623` | `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q -k 'promote_'` | N/A — temp-path adapter; remove promotion hunk/tests |
| 2D baseline | 2D | 190–200 | 2C; `report.py:209-280`, tests `:626-751` | `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q -k bootstrap_baseline` | N/A — snapshot loader only; remove baseline hunk/tests/evidence |
| 2E CLI | 2E | 255–265 | 2D; `cli.py:1-85`, report tests `:753-930` | `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q -k 'run_gate_'` | `uv run --frozen python -m backend.features.evaluation.gates.cli evaluation-dataset` → safe block/1; remove CLI/tests |
| 2F wiring | 2F | 235–245 | 2E; Makefile +9, architecture test 231 lines | `uv run --frozen pytest tests/architecture/test_technical_grounding_gates.py -q` | `make eval-quality-gate` → expected block; revert Make/test |

Maximum coherent slice is ~395; no size exception or fragmentation beyond these boundaries is required. Tests remain with the behavior they prove; 2B is intentionally a focused safety-proof slice. Current native revision: `sha256:0140b0c961450fb5eb05690533d07a2bbcbff993aded4b4540fd667472bb5967`, `next_action: continue` (PR 2D applied; 2E next).

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

## Phase 1: Completed Unit 1 (merged `b6aa528`)
- [x] 1.1–1.3 Policy RED/GREEN/REFACTOR: immutable contracts, floors, malformed evidence, and fail-closed precedence.
- [x] 2.1–2.3 Runner RED/GREEN/REFACTOR: critical whole-answer contracts, frozen-clock determinism, and unchanged numbers-only harness.

## Phase 2: Re-divided former Slice 2 (Strict TDD; stack in order)
- [x] 3.1 (2A) RED core allowlist/status/metadata tests; GREEN `report.py:1-143`; REFACTOR canonical safe JSON.
- [x] 3.2 (2B) RED critical-observation/content-safety tests; GREEN verifies 2A’s serializer (no duplicated production hunk); REFACTOR coverage.
- [x] 3.3 (2C) RED staging/atomic/rollback tests; GREEN `report.py:146-207`; REFACTOR cleanup and prior-byte preservation.
- [x] 3.4 (2D) RED baseline-source/validation tests; GREEN `report.py:209-280`; REFACTOR immutable baseline handling.
- [ ] 3.5 (2E) RED exit/stdout/no-network tests; GREEN `cli.py`; REFACTOR frozen `Clock` wiring and safe errors.
- [ ] 3.6 (2F) RED Make/CI/boundary tests; GREEN Makefile target and evidence wiring; REFACTOR no `ci`/`ci-pr2a` drift.

## Phase 3: Integration Verification
- [ ] 4.1 Run all gate focused tests; preserve every specification scenario and all threat-matrix rows (all five design rows are N/A, so no threat RED tests).
- [ ] 4.2 Run `make eval-quality-gate`; verify repeatable allowlisted evidence and non-zero `block`/`escalate`.
- [ ] 4.3 Run `make ci-pr2a`, then `make ci`; do not alter roadmap, archive/RDD claims, harness, kernel, dataset, providers, or dependencies.
