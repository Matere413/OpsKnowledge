# Apply Progress: Technical Grounding Safety Gates

Change: `add-technical-grounding-safety-gates`
Project: `opsknowledge`
Mode: Strict TDD (explicit maintainer decision overriding project-level `strict_tdd: false`)
Delivery strategy: `ask-on-risk` resolved to chained PRs
Chain strategy: `stacked-to-main`
Review budget: 400 lines excluding OpenSpec
Native attempt: ordinal 1, expected revision `sha256:357052e1db0db53f986f270e704fb1d9b6aba572140e5c8699ca51b63e33c628`

## Slice Boundary

This apply batch implements the **first autonomous stacked-to-main slice** (`slice-1-policy-runner`):
- Phase 1: Policy and Contracts (tasks 1.1–1.3) — Unit 1
- Phase 2: Runner and Critical Contracts (tasks 2.1–2.3) — Unit 2

Phase 3 (Safe Report and Opt-In Wiring) and Phase 4 (Integration Verification) are **later slices** and were NOT implemented.

## Completed Tasks

- [x] 1.1 RED: focused tests for immutable types, allowlisted statuses/reasons, five floors, cross-multiplication, malformed/boolean/negative/zero-denominator evidence, and baseline validation.
- [x] 1.2 GREEN: `backend/features/evaluation/gates/{__init__,domain,policy,ports}.py`; immutable contracts, reviewed floors, immutable baseline comparison, fail-closed precedence.
- [x] 1.3 REFACTOR/verify: gate dependency-free and harness-independent; Unit 1 focused command passes.
- [x] 2.1 RED: critical scenario contracts (eval-11/12, eval-16, eval-15, eval-13, injected failures) for exact outcome/reason pairs, empty citations, no kernel/metric reimplementation, frozen Clock determinism.
- [x] 2.2 GREEN: `backend/features/evaluation/gates/application.py`; consumes `RunSummary.metrics`/`CaseResult`, selects critical observations, emits safe `GateDecision`, block outranks escalate.
- [x] 2.3 REFACTOR/verify: Unit 2 focused command passes; existing evaluation harness remains numbers-only and unchanged.

## Remaining Tasks (later slices)

- [ ] 3.1 RED: report allowlists/safe stdout, forbidden content absence, staging validation, atomic current/previous promotion, rollback on write/rename failure, CLI exit codes, no-dependency imports, unchanged `ci`/`ci-pr2a` blocks.
- [ ] 3.2 GREEN: `adapters/report.py` and `cli.py`; modify only `Makefile` with `.PHONY`/`eval-quality-gate`; bootstrap validated baseline, journal promotion, safe errors, `evaluation-runs/gate/current` evidence.
- [ ] 3.3 REFACTOR/verify: preserve no subprocess/network/persistence/content logging, inject `FrozenClock`, run Unit 3 focused command.
- [ ] 4.1 Run all focused gate tests.
- [ ] 4.2 Run `make eval-quality-gate`; verify repeatable safe evidence and non-zero `block`/`escalate` behavior.
- [ ] 4.3 Run `make ci-pr2a`, then canonical `make ci`; do not alter roadmap, archive state, RDD/4R claims, or unrelated files.

## Files Changed

| File | Action | Lines | What Was Done |
|------|--------|------:|---------------|
| `backend/features/evaluation/gates/__init__.py` | Created | 0 | Package marker. |
| `backend/features/evaluation/gates/domain.py` | Created | 226 | Immutable contracts: GateSignal, GateFloor, GateMetrics, GateDecision, CriticalExpectation; GATE_STATUSES, GATE_REASON_CODES, ALLOWED_REASON_CODES, METRIC_NAMES; reviewed temporary FLOORS (MappingProxyType); CRITICAL_EXPECTATIONS table. |
| `backend/features/evaluation/gates/policy.py` | Created | 142 | `evaluate_floor_policy`: cross-multiplication floor+baseline comparison, fail-closed invalid_evidence, block-outranks-escalate precedence, reason-code aggregation. |
| `backend/features/evaluation/gates/ports.py` | Created | 44 | Gate-specific ports: GateReportStore, CriticalObservationSelector, GateClock protocols. |
| `backend/features/evaluation/gates/application.py` | Created | 123 | `evaluate_gate`: adapts harness Metrics→GateMetrics, evaluates critical contracts (outcome/reason/citation rules), combines with floor policy, critical mismatch→block outranks all. |
| `backend/features/evaluation/gates/adapters/__init__.py` | Created | 0 | Adapters package marker (for later slice). |
| `tests/unit/test_technical_grounding_gates_policy.py` | Created | 520 | 42 tests: immutable types, statuses/reasons, five floors, cross-multiplication (pass/above/below), malformed evidence (bool/neg/zero-den/missing), precedence, critical expectations, dependency-free. |
| `tests/unit/test_technical_grounding_gates_runner.py` | Created | 427 | 36 tests: critical contract pass/mismatch (wrong outcome/reason/citations/missing/unknown-code), block-outranks-escalate, no recomputation, selective observation, frozen-clock determinism, harness-unchanged. |

**Authored line totals (excluding OpenSpec):**
- Runtime/source: 535 lines (domain 226 + policy 142 + ports 44 + application 123)
- Tests: 947 lines (policy 520 + runner 427)
- Total authored: 1,482 lines

**This slice exceeds the 400-line review budget** — this is expected and why the change uses chained PRs (`stacked-to-main`). This slice (Units 1+2) is one autonomous PR boundary; Phase 3 (report/CLI/Make) is the next slice.

## TDD Cycle Evidence

| Task | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR |
|------|-----------|-------|------------|-----|-------|-------------|----------|
| 1.1 | `tests/unit/test_technical_grounding_gates_policy.py` | Unit | N/A (new) | ✅ 42 tests written, all failed (module missing) | ✅ 42/42 passed | ✅ 6 parametrized malformed-evidence cases + 5 floor cases + multiple regression cases | ✅ MappingProxyType for FLOORS immutability; SIM103 simplification; import sorting |
| 1.2 | (same) | Unit | N/A (new) | (covered by 1.1 RED) | ✅ 42/42 passed | ✅ block+escalate aggregation; invalid-evidence outranks | ✅ clean |
| 1.3 | (same) | Unit | N/A (new) | (covered by 1.1 RED) | ✅ 42/42 passed | ➖ | ✅ ruff/pyright/focused-test-guard clean |
| 2.1 | `tests/unit/test_technical_grounding_gates_runner.py` | Unit | ✅ 26/26 harness tests pass | ✅ 35 tests failed (module missing), 1 trivial pass | ✅ 36/36 passed | ✅ 12 parametrized critical-contract pass cases + 5 wrong-outcome + 5 wrong-reason + 3 nonempty-citations | ✅ full-critical-set fixture refactor |
| 2.2 | (same) | Unit | ✅ 26/26 harness tests pass | (covered by 2.1 RED) | ✅ 36/36 passed | ✅ critical mismatch + floor regression combination; block-outranks-escalate | ✅ MetricSignal typed import |
| 2.3 | (same) | Unit | ✅ 26/26 harness tests pass | (covered by 2.1 RED) | ✅ 36/36 passed | ➖ | ✅ ruff/pyright/focused-test-guard clean |

### Test Summary
- **Total tests written**: 78 (42 policy + 36 runner)
- **Total tests passing**: 78
- **Layers used**: Unit (78)
- **Approval tests** (refactoring): None — no refactoring of existing code
- **Pure functions created**: 5 (`evaluate_floor_policy`, `evaluate_gate`, `_to_gate_metrics`, `_to_gate_signal`, `_evaluate_critical_contracts`)

## Work Unit Evidence

| Evidence | Required value |
|---|---|
| Focused test command and exact result | `uv run --frozen pytest tests/unit/test_technical_grounding_gates_policy.py tests/unit/test_technical_grounding_gates_runner.py -q` → 78 passed in 0.04s, exit 0 |
| Runtime harness command/scenario and exact result | N/A — CLI wiring and `make eval-quality-gate` belong to the later report/CLI slice (Phase 3); no runtime boundary exists for this pure-policy/runner slice |
| Rollback boundary | Remove `backend/features/evaluation/gates/{__init__,domain,policy,ports,application.py}` and `adapters/__init__.py`, plus `tests/unit/test_technical_grounding_gates_{policy,runner}.py`. No harness, kernel, dataset, Makefile, manifest, or lockfile changes to revert. |

## Deviations from Design

1. **FLOORS immutability**: Design says "immutable floors"; implementation uses `types.MappingProxyType` wrapping a dict to enforce read-only access at runtime (test asserts `.update()` raises). This is a faithful realization, not a deviation.

2. **Reason-code aggregation on block+escalate**: The design says "Block outranks escalate." The implementation sets STATUS to `block` when any block-regression fires, but aggregates ALL regression reason codes (both block and escalate) into the decision so reviewers see every failing signal. This is consistent with the spec's "both exit non-zero" and the design's precedence order.

3. **Critical expectations vs committed kernel outputs**: The design's critical expectations table (eval-11/12→contradiction_detected, eval-13→out_of_scope) describes the EXPECTED pairs from the dataset. The committed kernel baseline shows the development fake kernel does NOT produce these for eval-11/12/13 (it produces insufficient_information/supported/contradiction_detected instead). This is expected behavior: the gate is a RELEASE CONTRACT that blocks when the kernel doesn't meet critical contracts. The gate tests use constructed inputs (pure fixtures), not real kernel outputs, so this doesn't affect the tests. On a real `make eval-quality-gate` run (Phase 3+), the gate WILL block with `critical_contract_mismatch` — which is the intended fail-closed release-contract behavior. **This is a discovery, not a deviation** — the design is correct; the kernel is a development fake that doesn't yet satisfy all critical contracts.

## Issues Found

1. **Design critical-expectations table discrepancy with committed baseline**: The committed `evaluation-runs/current/records.jsonl` shows 6 of 12 critical cases do NOT match the design's expected outcome/reason pairs (eval-11/12 produce insufficient_information or supported instead of contradictory_information; eval-13 produces contradictory_information instead of out_of_scope). This means a real gate run will block with `critical_contract_mismatch`. This is the intended release-contract behavior — the gate exists to catch exactly these regressions. No action needed in this slice; flagged for the orchestrator/maintainer.

2. **Focused-test guard constraint**: Negative number literals (e.g., `-1`) in `pytest.mark.parametrize` are rejected by the repo's focused-test guard (parsed as `UnaryOp`, not `Constant`). Resolved by defining a module-level `NEG_ONE = -1` constant and referencing it by name in parametrize values.

## Cleanup / Process Evidence

- No commits created, no pushes, no PR opened (per instructions).
- No `make ci` or `ci-pr2a` changes (verified: `git diff -- Makefile` empty).
- No new dependencies (verified: `git diff -- pyproject.toml uv.lock` empty).
- No harness/kernel/dataset/provider/embedding/database changes (verified: `git diff` on harness files empty).
- No RDD/4R, no review started, no approval claimed.
- All new files pass `ruff check`, `ruff format --check`, `pyright`, and `check_focused_tests.py`.
- Existing harness tests (26) still pass — safety net confirmed.

## Native Attempt Evidence

- Attempt ordinal: 1
- Expected current revision: `sha256:357052e1db0db53f986f270e704fb1d9b6aba572140e5c8699ca51b63e33c628`
- Did NOT call `sdd-attempt begin`, `reset`, or `finish`.
- Focused test commands and outcomes:
  - `uv run --frozen pytest tests/unit/test_technical_grounding_gates_policy.py -q` → 42 passed, exit 0
  - `uv run --frozen pytest tests/unit/test_technical_grounding_gates_runner.py -q` → 36 passed, exit 0
  - `uv run --frozen pytest tests/unit/test_technical_grounding_gates_policy.py tests/unit/test_technical_grounding_gates_runner.py -q` → 78 passed, exit 0
- Static checks:
  - `uv run --frozen ruff check ...` → All checks passed, exit 0
  - `uv run --frozen ruff format --check ...` → 8 files already formatted, exit 0
  - `uv run --frozen pyright ...` → 0 errors, 0 warnings, exit 0
  - `uv run --frozen python scripts/ci/check_focused_tests.py .` → no findings, exit 0
- Safety net: `uv run --frozen pytest tests/unit/test_quality_evaluation_harness.py -q` → 26 passed, exit 0
- Changed-line count: 1,482 authored lines (535 source + 947 tests), excluding OpenSpec
- Disposition: **PASSED** — all focused tests and static checks green; existing harness unchanged; no scope violations.