# Tasks: Technical Grounding Safety Gates

## Review Workload Forecast

| Unit | Runtime/source | Tests | Baseline evidence | Makefile/docs | OpenSpec artifacts | Authored subtotal |
|---|---:|---:|---:|---:|---:|---:|
| 1 Policy/contracts | 170–220 | 150–190 | 0 | 0 | 0 | 320–410 |
| 2 Runner/contracts | 100–140 | 100–140 | 0 | 0 | 0 | 200–280 |
| 3 Report/CLI/wiring | 170–230 | 160–220 | 30–50 | 8–15 | 0 | 368–515 |
| **Total** | **440–590** | **410–550** | **30–50** | **8–15** | **~40–60** | **888–1,205** |

OpenSpec artifact lines are excluded from the 400-line threshold.

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|---|---|---|---|---|---|
| 1 | Immutable domain contracts and fail-closed floors | Pending | `uv run --frozen pytest tests/unit/test_technical_grounding_gates_policy.py -q` | N/A — pure policy | Remove new `gates/{__init__,domain,policy,ports}.py` and its test |
| 2 | Runner and whole-answer critical contracts | Pending | `uv run --frozen pytest tests/unit/test_technical_grounding_gates_runner.py -q` | N/A — CLI wiring follows | Remove new `gates/application.py` and runner test |
| 3 | Safe atomic evidence, CLI, Make target, baseline | Pending | `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py tests/architecture/test_technical_grounding_gates.py -q` | `make eval-quality-gate` | Revert gate report/CLI, Make target, gate evidence, and tests |

## Phase 1: Policy and Contracts

- [x] 1.1 RED: create focused tests for immutable types, allowlisted statuses/reasons, five floors, cross-multiplication, malformed/boolean/negative/zero-denominator evidence, and baseline validation.
- [x] 1.2 GREEN: add `backend/features/evaluation/gates/{__init__,domain,policy,ports}.py`; implement immutable contracts, reviewed floors, immutable baseline comparison, and fail-closed precedence.
- [x] 1.3 REFACTOR/verify: keep the gate dependency-free and harness-independent; run the Unit 1 focused command.

## Phase 2: Runner and Critical Contracts

- [x] 2.1 RED: test `scenario.eval-11/12`, `eval-16`, `eval-15`, `eval-13`, and both injected failures for exact outcome/reason pairs, empty citations, no kernel/metric reimplementation, and frozen `Clock` determinism.
- [x] 2.2 GREEN: add `backend/features/evaluation/gates/application.py`; consume `RunSummary.metrics`/`CaseResult`, select critical observations, emit safe `GateDecision`, and make `block` outrank `escalate`.
- [x] 2.3 REFACTOR/verify: run the Unit 2 focused command and confirm the existing evaluation harness remains numbers-only and unchanged.

## Phase 3: Safe Report and Opt-In Wiring

- [ ] 3.1 RED: test report allowlists/safe stdout, forbidden content absence, staging validation, atomic current/previous promotion, rollback on write/rename failure, CLI exit codes, no-dependency imports, and unchanged `ci`/`ci-pr2a` blocks.
- [ ] 3.2 GREEN: add `adapters/report.py` and `cli.py`; modify only `Makefile` with `.PHONY`/`eval-quality-gate`; bootstrap validated baseline, journal promotion, safe errors, and `evaluation-runs/gate/current` evidence (no `previous` until replacement).
- [ ] 3.3 REFACTOR/verify: preserve no subprocess/network/persistence/content logging, inject `FrozenClock`, and run the Unit 3 focused command.

## Phase 4: Integration Verification

- [ ] 4.1 Run all focused gate tests: `uv run --frozen pytest tests/unit/test_technical_grounding_gates_policy.py tests/unit/test_technical_grounding_gates_runner.py tests/unit/test_technical_grounding_gates_report.py tests/architecture/test_technical_grounding_gates.py -q`.
- [ ] 4.2 Run `make eval-quality-gate`; verify repeatable safe evidence and non-zero `block`/`escalate` behavior.
- [ ] 4.3 Run `make ci-pr2a`, then canonical `make ci`; do not alter roadmap, archive state, RDD/4R claims, or unrelated harness/kernel/dataset files.
