# Apply Progress: Technical Grounding Safety Gates

Change: `add-technical-grounding-safety-gates`
Project: `opsknowledge`
Mode: Strict TDD (explicit maintainer decision overriding project-level `strict_tdd: false`)
Delivery strategy: `ask-on-risk` resolved to chained PRs
Chain strategy: `stacked-to-main`
Review budget: 400 lines excluding OpenSpec
Native attempt: ordinal 1, expected revision `sha256:357052e1db0db53f986f270e704fb1d9b6aba572140e5c8699ca51b63e33c628`
Native attempt: ordinal 2, expected revision `sha256:9b8fd8453b8a2158e0dfac7f7c4ea7ddc173d04d5520c8cba82ef0c14ffd1dc6`
Native attempt: ordinal 3, expected revision `sha256:feb83a3c3d0136b35965f5cf461464e5dea5fe94913e311ac5c410a011569b9c`

## Slice Boundary

This apply progress merges three autonomous stacked-to-main batches. The
former slice-2 was re-planned into six sub-slices (2A–2F); this file records
the original full slice-2 provenance (kept as audit history) AND the isolated
PR 2A candidate that replaced it.

### Slice 1 — `slice-1-policy-runner` (MERGED in `master` at `b6aa528`)
- Phase 1: Policy and Contracts (tasks 1.1–1.3) — Unit 1
- Phase 2: Runner and Critical Contracts (tasks 2.1–2.3) — Unit 2

### Former Slice 2 — `slice-2-safe-report-opt-in-wiring` (RE-PLANNED, NOT applied as one PR)
The former slice-2 implemented all of report serialization, atomic promotion,
baseline bootstrap, CLI, and Makefile wiring in one 1,535-line batch. It
exceeded the 400-line review budget and was re-planned into sub-slices 2A–2F.
Its red/green TDD provenance is preserved below as audit history. Its bytes
were preserved recoverably outside the candidate (see "Later-work archive").

### PR 2A — `slice-2a-report-core` (THIS BATCH)
- Phase 2 task 3.1 only: core allowlisted gate report serializer
- `report.py` serializer core + the focused tests that prove it
- Later sub-slices 2B–2F are NOT in this candidate; their bytes are archived

Phase 4 (Integration Verification, tasks 4.1–4.3) is a **later slice** and was
NOT implemented. This batch did not perform final Phase 4 verification beyond
the focused evidence needed for this slice.

## Completed Tasks

### Slice 1 (merged)
- [x] 1.1 RED: focused tests for immutable types, allowlisted statuses/reasons, five floors, cross-multiplication, malformed/boolean/negative/zero-denominator evidence, and baseline validation.
- [x] 1.2 GREEN: `backend/features/evaluation/gates/{__init__,domain,policy,ports}.py`; immutable contracts, reviewed floors, immutable baseline comparison, fail-closed precedence.
- [x] 1.3 REFACTOR/verify: gate dependency-free and harness-independent; Unit 1 focused command passes.
- [x] 2.1 RED: critical scenario contracts (eval-11/12, eval-16, eval-15, eval-13, injected failures) for exact outcome/reason pairs, empty citations, no kernel/metric reimplementation, frozen Clock determinism.
- [x] 2.2 GREEN: `backend/features/evaluation/gates/application.py`; consumes `RunSummary.metrics`/`CaseResult`, selects critical observations, emits safe `GateDecision`, block outranks escalate.
- [x] 2.3 REFACTOR/verify: Unit 2 focused command passes; existing evaluation harness remains numbers-only and unchanged.

### Former Slice 2 (re-planned; provenance kept as audit history)
- [x] 3.1 RED (former): report allowlists/safe stdout, forbidden content absence, staging validation, atomic current/previous promotion, rollback on write/rename failure, CLI exit codes, no-dependency imports, unchanged `ci`/`ci-pr2a` blocks.
- [x] 3.2 GREEN (former): `adapters/report.py` and `cli.py`; modify only `Makefile` with `.PHONY`/`eval-quality-gate`; bootstrap validated baseline, journal promotion, safe errors, `evaluation-runs/gate/current` evidence.
- [x] 3.3 REFACTOR/verify (former): preserve no subprocess/network/persistence/content logging, inject `FrozenClock`, run Unit 3 focused command.

### PR 2A (this batch — isolated from the former slice 2)
- [x] 3.1 (2A) RED core allowlist/status/metadata tests; GREEN `report.py:1-143`; REFACTOR canonical safe JSON.
  - RED provenance preserved from the former slice-2: the 3 `serialize_gate_report` tests were written first against a missing module and failed (module missing).
  - GREEN provenance preserved: `serialize_gate_report` + helpers implemented; the 3 focused tests passed.
  - REFACTOR: removed later-slice imports (`os`, `shutil`, `dataclass`, `Path`) and later-slice exports from `__all__`; removed unused `import pytest` from the test file; trailing newline added; `ruff format` applied (1 file reformatted). Serializer core remains byte-stable (sort_keys canonical JSON, exact allowlist assertion).

## Remaining Tasks (later slices)

- [ ] 3.2 (2B) RED critical-observation/content-safety tests; GREEN verifies 2A's serializer (no duplicated production hunk); REFACTOR coverage.
- [ ] 3.3 (2C) RED staging/atomic/rollback tests; GREEN `report.py:146-207`; REFACTOR cleanup and prior-byte preservation.
- [ ] 3.4 (2D) RED baseline-source/validation tests; GREEN `report.py:209-280`; REFACTOR immutable baseline handling.
- [ ] 3.5 (2E) RED exit/stdout/no-network tests; GREEN `cli.py`; REFACTOR frozen `Clock` wiring and safe errors.
- [ ] 3.6 (2F) RED Make/CI/boundary tests; GREEN Makefile target and evidence wiring; REFACTOR no `ci`/`ci-pr2a` drift.
- [ ] 4.1 Run all gate focused tests: `uv run --frozen pytest tests/unit/test_technical_grounding_gates_policy.py tests/unit/test_technical_grounding_gates_runner.py tests/unit/test_technical_grounding_gates_report.py tests/architecture/test_technical_grounding_gates.py -q`.
- [ ] 4.2 Run `make eval-quality-gate`; verify repeatable safe evidence and non-zero `block`/`escalate` behavior.
- [ ] 4.3 Run `make ci-pr2a`, then canonical `make ci`; do not alter roadmap, archive state, RDD/4R claims, or unrelated files.

## Later-work archive (recoverable, outside the candidate)

The former slice-2's later-slice bytes (promotion, baseline, CLI, Makefile,
architecture tests, additional report tests, generated evidence) were
preserved recoverably under the pre-approved external temporary root before
removal from the active Git candidate. No later work was lost or silently
rewritten.

- Archive root: `/var/folders/3h/2p5xjx012bq2b7vs3ykb4yfr0000gn/T/opencode/slice-2-later-work-archive-20260728-201441`
- Contents: full byte copies of `report.py`, `cli.py`, both test files, the
  generated gate report, the full tracked `git diff`, and a `MANIFEST.md`.
- SHA256 of archived later-slice files:
  - `files/report.py.full`: `03040265f455018dbdc1e4eee740ccdd05b8b4a0927c9c3f9105ec31f692d2af`
  - `files/cli.py.full`: `6821a451251d2b21a2d728fc69bb6d12d6a5f3c072b3500230299e68305040cb`
  - `files/test_technical_grounding_gates_report.py.full`: `3333bfba676526ab0114c5f27682aa2ad9745c2ef33c019511bee08ce2584b62`
  - `files/test_technical_grounding_gates.py.full`: `7f91aa505c6344f1847179b4a0259eb4c1b5a43f4dc7d23e0e4be5699d704115`
  - `files/gate-current-report.json`: `3d6bab10ea6fa6b0a332bf5a1374ea0698de6911f1fff49c99785905d7a2d12d`
  - `patch/former-slice-2-tracked.diff`: `f84bdf740f97217ba0984370d3867ecaa631461c06d8c2e205a52b2730a7dc6f`
- Restoration: copy each `.full` variant back to its original repo path to
  re-introduce later-slice work.

## Files Changed

### Slice 1 (merged in master at b6aa528)

| File | Action | Lines | What Was Done |
|------|--------|------:|---------------|
| `backend/features/evaluation/gates/__init__.py` | Created | 0 | Package marker. |
| `backend/features/evaluation/gates/domain.py` | Created | 226 | Immutable contracts: GateSignal, GateFloor, GateMetrics, GateDecision, CriticalExpectation; GATE_STATUSES, GATE_REASON_CODES, ALLOWED_REASON_CODES, METRIC_NAMES; reviewed temporary FLOORS (MappingProxyType); CRITICAL_EXPECTATIONS table. |
| `backend/features/evaluation/gates/policy.py` | Created | 142 | `evaluate_floor_policy`: cross-multiplication floor+baseline comparison, fail-closed invalid_evidence, block-outranks-escalate precedence, reason-code aggregation. |
| `backend/features/evaluation/gates/ports.py` | Created | 44 | Gate-specific ports: GateReportStore, CriticalObservationSelector, GateClock protocols. |
| `backend/features/evaluation/gates/application.py` | Created | 123 | `evaluate_gate`: adapts harness Metrics→GateMetrics, evaluates critical contracts, combines with floor policy, critical mismatch→block outranks all. |
| `backend/features/evaluation/gates/adapters/__init__.py` | Created | 0 | Adapters package marker. |
| `tests/unit/test_technical_grounding_gates_policy.py` | Created | 520 | 42 tests. |
| `tests/unit/test_technical_grounding_gates_runner.py` | Created | 427 | 36 tests. |

### PR 2A (this batch — isolated candidate)

| File | Action | Lines | What Was Done |
|------|--------|------:|---------------|
| `backend/features/evaluation/gates/adapters/report.py` | Created (truncated from former 280) | 141 | Serializer core only: `serialize_gate_report` + helpers (`_signal_dict`, `_metrics_dict`, `_floors_dict`, `_critical_observations`, `_to_gate_metrics_from_summary`), allowlist constants, `__all__` exporting only `GATE_VERSION`/`SCHEMA_VERSION`/`serialize_gate_report`. Removed later-slice imports (`os`, `shutil`, `dataclass`, `Path`) and later-slice code (promotion, baseline, validation). |
| `tests/unit/test_technical_grounding_gates_report.py` | Created (truncated from former 930) | 247 | 3 focused `serialize_gate_report` tests + shared scaffolding (helpers, allowlist constants, `_ExpectRaise`, `_raises`, metric builders, summary builders). Removed later-slice tests (critical-obs/forbidden/citation, promotion, rollback, baseline, CLI, imports, deterministic). Removed unused `import pytest` (F401). |

**Authored line totals (excluding OpenSpec + generated evidence):**
- PR 2A: 388 total lines (report.py 141 + test 247); 317 non-blank authored lines.
- Under the 400-line hard maintainer threshold. No `size:exception` requested or assumed.

### Removed from the active candidate (archived, not lost)

| File | Former lines | Archive path | Later slice |
|------|------:|---|---|
| `backend/features/evaluation/gates/adapters/report.py` (:144-280) | 136 | `files/report.py.full` | 2C/2D |
| `backend/features/evaluation/gates/cli.py` | 85 | `files/cli.py.full` | 2E |
| `tests/unit/test_technical_grounding_gates_report.py` (:253-930) | 678 | `files/test_technical_grounding_gates_report.py.full` | 2B/2C/2D/2E |
| `tests/architecture/test_technical_grounding_gates.py` | 231 | `files/test_technical_grounding_gates.py.full` | 2F |
| `Makefile` (+9) | 9 | `patch/former-slice-2-tracked.diff` | 2F |
| `evaluation-runs/gate/current/report.json` | 3136 bytes | `files/gate-current-report.json` | generated evidence |

## TDD Cycle Evidence

### Slice 1 (merged)

| Task | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR |
|------|-----------|-------|------------|-----|-------|-------------|----------|
| 1.1 | `tests/unit/test_technical_grounding_gates_policy.py` | Unit | N/A (new) | ✅ 42 tests written, all failed (module missing) | ✅ 42/42 passed | ✅ 6 parametrized malformed-evidence cases + 5 floor cases + multiple regression cases | ✅ MappingProxyType for FLOORS immutability; SIM103 simplification; import sorting |
| 1.2 | (same) | Unit | N/A (new) | (covered by 1.1 RED) | ✅ 42/42 passed | ✅ block+escalate aggregation; invalid-evidence outranks | ✅ clean |
| 1.3 | (same) | Unit | N/A (new) | (covered by 1.1 RED) | ✅ 42/42 passed | ➖ | ✅ ruff/pyright/focused-test-guard clean |
| 2.1 | `tests/unit/test_technical_grounding_gates_runner.py` | Unit | ✅ 26/26 harness tests pass | ✅ 35 tests failed (module missing), 1 trivial pass | ✅ 36/36 passed | ✅ 12 parametrized critical-contract pass cases + 5 wrong-outcome + 5 wrong-reason + 3 nonempty-citations | ✅ full-critical-set fixture refactor |
| 2.2 | (same) | Unit | ✅ 26/26 harness tests pass | (covered by 2.1 RED) | ✅ 36/36 passed | ✅ critical mismatch + floor regression combination; block-outranks-escalate | ✅ MetricSignal typed import |
| 2.3 | (same) | Unit | ✅ 26/26 harness tests pass | (covered by 2.1 RED) | ✅ 36/36 passed | ➖ | ✅ ruff/pyright/focused-test-guard clean |

### Former Slice 2 (audit history — provenance preserved)

| Task | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR |
|------|-----------|-------|------------|-----|-------|-------------|----------|
| 3.1 | `tests/unit/test_technical_grounding_gates_report.py` | Unit | ✅ 92/92 (78 gate slice-1 + 14 harness arch) | ✅ 33 tests failed (modules missing) | ✅ 33/33 passed | ✅ 3 parametrized bad-baseline cases + 7 allowlist-key assertions + 5 promotion scenarios + 3 rollback scenarios | ✅ `_ExpectRaise` context manager + `_raises` helper (repo guard forbids `pytest.raises`); named constants for dict parametrize |
| 3.1 | `tests/architecture/test_technical_grounding_gates.py` | Architecture | ✅ 92/92 | ✅ 7 tests failed (Makefile target + adapter missing) | ✅ 21/21 passed | ✅ ci + ci-pr2a order assertions + 11 forbidden-module parametrized cases | ✅ `pytest.fail`→`assert` (repo guard) |
| 3.2 | (same) | Unit/Arch | ✅ 92/92 | (covered by 3.1 RED) | ✅ 54/54 passed (33 report + 21 arch) | ✅ baseline bootstrap from harness vs gate snapshot; deterministic report across runs | ✅ `_PROJECT_ROOT parents[4]` fix (gate cli is one dir deeper than harness cli) |
| 3.3 | (same) | Unit/Arch | ✅ 92/92 | (covered by 3.1 RED) | ✅ 54/54 passed | ➖ | ✅ ruff/pyright/focused-test-guard/dependency-boundaries clean; runtime harness `make eval-quality-gate` confirms fail-closed block |

### PR 2A (this batch — isolated slice-2a-report-core)

| Task | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR |
|------|-----------|-------|------------|-----|-------|-------------|----------|
| 3.1 (2A) | `tests/unit/test_technical_grounding_gates_report.py` | Unit | ✅ 92/92 (78 gate slice-1 + 14 harness arch) | ✅ Preserved from former slice-2: the 3 `serialize_gate_report` tests were RED first (module missing) | ✅ 3/3 passed after isolation (serializer core retained; later-slice code removed) | ✅ 3 cases: exact allowlist keys, decision status+reasons, run_id/profile/provider_mode/timestamp/duration — each exercises a distinct serializer field path | ✅ Removed unused `import pytest` (F401); added trailing newline (W292); `ruff format` applied (1 file reformatted); removed later-slice imports/exports from `report.py` `__all__`; serializer byte-stable canonical JSON preserved |

### Test Summary (combined)
- **Total tests written across all batches**: 132 (42 policy + 36 runner + 33 report-former + 21 arch-former)
- **PR 2A focused tests in active candidate**: 3 (serialize_gate_report core)
- **PR 2A focused tests passing**: 3
- **Layers used**: Unit
- **Approval tests** (refactoring): None — no refactoring of existing code
- **Pure functions created**: 5 retained in PR 2A (`serialize_gate_report`, `_signal_dict`, `_metrics_dict`, `_floors_dict`, `_critical_observations`); `_to_gate_metrics_from_summary` reuses the slice-1 `_to_gate_metrics`

## Work Unit Evidence

### Slice 1 (merged)

| Evidence | Required value |
|---|---|
| Focused test command and exact result | `uv run --frozen pytest tests/unit/test_technical_grounding_gates_policy.py tests/unit/test_technical_grounding_gates_runner.py -q` → 78 passed in 0.04s, exit 0 |
| Runtime harness command/scenario and exact result | N/A — CLI wiring and `make eval-quality-gate` belong to the later report/CLI slice (Phase 3); no runtime boundary exists for this pure-policy/runner slice |
| Rollback boundary | Remove `backend/features/evaluation/gates/{__init__,domain,policy,ports,application.py}` and `adapters/__init__.py`, plus `tests/unit/test_technical_grounding_gates_{policy,runner}.py`. No harness, kernel, dataset, Makefile, manifest, or lockfile changes to revert. |

### PR 2A (this batch)

| Evidence | Required value |
|---|---|
| Focused test command and exact result | `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q -k serialize_gate_report` → 3 passed in 0.03s, exit 0 |
| Runtime harness command/scenario and exact result | N/A — pure serializer slice; `make eval-quality-gate`, CLI, promotion, and baseline bootstrap belong to later stacked slices (2C–2F). No runtime boundary exists for PR 2A. |
| Rollback boundary | Remove `backend/features/evaluation/gates/adapters/report.py` and `tests/unit/test_technical_grounding_gates_report.py`. No Makefile, CLI, harness, kernel, dataset, manifest, lockfile, or dependency changes to revert (Makefile diff reverted to HEAD; later-slice files removed from candidate and archived). |

### Former Slice 2 (audit history)

| Evidence | Required value |
|---|---|
| Focused test command and exact result | `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py tests/architecture/test_technical_grounding_gates.py -q` → 54 passed in 0.13s, exit 0 |
| Runtime harness command/scenario and exact result | `make eval-quality-gate` → exit 1 (non-zero); stdout: `gate: block / reasons: critical_contract_mismatch`; report promoted to `evaluation-runs/gate/current/report.json` (3136 bytes, 13 allowlisted keys, no forbidden content); deterministic byte-identical across 2 runs (frozen clock); `previous/` created on 2nd run. **Expected release block**: the committed development fake kernel does not satisfy eval-11/12/13 critical contracts — the gate blocks fail-closed as designed. This is the intended release-contract behavior, NOT an implementation failure. |
| Rollback boundary | Revert `Makefile` diff (remove `.PHONY` entry + `eval-quality-gate` target). Remove `backend/features/evaluation/gates/adapters/report.py`, `backend/features/evaluation/gates/cli.py`, `tests/unit/test_technical_grounding_gates_report.py`, `tests/architecture/test_technical_grounding_gates.py`, and `evaluation-runs/gate/`. No harness, kernel, dataset, policy, runner, manifest, lockfile, or dependency changes to revert. |

## Deviations from Design

### Slice 1 (merged)
1. **FLOORS immutability**: Design says "immutable floors"; implementation uses `types.MappingProxyType` wrapping a dict to enforce read-only access at runtime. Faithful realization.
2. **Reason-code aggregation on block+escalate**: Design says "Block outranks escalate." STATUS is `block` when any block-regression fires, but ALL regression reason codes are aggregated. Consistent with spec "both exit non-zero."
3. **Critical expectations vs committed kernel outputs**: The design's critical expectations table describes EXPECTED pairs. The committed development fake kernel does NOT produce these for eval-11/12/13. The gate WILL block with `critical_contract_mismatch` on a real run — intended fail-closed release-contract behavior. Discovery, not deviation.

### Former Slice 2 (audit history)
4. **`_ExpectRaise` context manager instead of `pytest.raises`**: The repo's focused-test guard forbids `pytest.raises` (flags it as `unsupported-test-api`). A plain `_ExpectRaise` class provides equivalent semantics without pytest-API coupling. Faithful to the repo's existing `_raises` pattern (slice 1), extended to a context manager for rollback tests that need post-raise state assertions.
5. **`_PROJECT_ROOT = parents[4]`**: The gate `cli.py` lives one directory deeper (`gates/cli.py`) than the harness `cli.py` (`evaluation/cli.py`), so `parents[4]` resolves to the project root instead of `parents[3]`. This is correct path arithmetic, not a deviation.
6. **`_os_replace` module-level indirection**: `os.replace` is referenced via a module-level `_os_replace` alias so tests can monkeypatch it to inject rename failures. This enables the rollback tests without subprocess or mocking frameworks. Consistent with the design's "inject write/rename failures" testing strategy.

### PR 2A (this batch)
7. **`__all__` narrowed to serializer exports**: The former `report.py` exported `GateReportAdapter` and `bootstrap_baseline`, which belong to later slices (2C, 2D). PR 2A's `__all__` exports only `GATE_VERSION`, `SCHEMA_VERSION`, and `serialize_gate_report`. Later slices will re-add the promotion/baseline exports when their code lands in the same module. Faithful to the re-planned boundary, not a design deviation.
8. **Unused scaffolding retained in the test file**: `_ExpectRaise`, `_raises`, `_gate_metrics_regression`, `_gate_metrics_escalate_only`, `_BAD_*`, `FORBIDDEN_CONTENT_TOKENS`, `ALLOWED_OBSERVATION_KEYS`, `_write_harness_summary`-adjacent constants are defined but not called by the 3 PR 2A tests. They are kept because the revised tasks artifact assigns them to the PR 2A test boundary (`:1-252`) and later slices (2B–2E) reuse them. Module-level unused functions/constants are not ruff errors (only unused imports are F401). The single unused import (`pytest`) was removed.

## Issues Found

### Slice 1 (merged)
1. **Design critical-expectations table discrepancy with committed baseline**: 6 of 12 critical cases do NOT match the design's expected outcome/reason pairs. A real gate run blocks with `critical_contract_mismatch` — intended release-contract behavior. Flagged for the orchestrator/maintainer.
2. **Focused-test guard constraint**: Negative number literals in `pytest.mark.parametrize` are rejected (parsed as `UnaryOp`). Resolved by module-level `NEG_ONE = -1` constant.

### Former Slice 2 (audit history)
3. **Focused-test guard forbids `pytest.raises` AND dict literals in parametrize**: Resolved by `_ExpectRaise` context manager + `_raises` boolean helper, and named module-level constants (`_BAD_ZERO_DEN`, `_BAD_NEG_NUM`, `_BAD_EXCEED`) for parametrize values.
4. **Initial gate baseline blocks fail-closed**: `make eval-quality-gate` exits non-zero with `critical_contract_mismatch` because the development fake kernel does not satisfy eval-11/12/13 critical contracts. This is the EXPECTED release block — the gate is a release contract that blocks when the kernel doesn't meet critical contracts. The baseline is recorded as a fail-closed gate result, not a weakening of policy. Distinguished from implementation failure: all 132 focused tests pass, static checks are clean, and the runtime harness produces the correct safe report with the correct block decision.
5. **Runtime-generated `evaluation-runs/previous/`**: Running `make eval-quality` (harness) for comparison created a harness `previous/`. Cleaned up — not part of this slice's deliverable. The gate `evaluation-runs/gate/current/` is the intended initial baseline.

### PR 2A (this batch)
6. **None.** The serializer core isolates cleanly. The only lint fix required was removing the unused `import pytest` (the 3 focused tests use bare `assert`, no `pytest.mark`) and adding a trailing newline.

## Cleanup / Process Evidence

### PR 2A (this batch)
- No commits created, no pushes, no PR opened (per instructions).
- No `make ci` or `ci-pr2a` changes (verified: `Makefile` reverted to HEAD; `git diff -- Makefile` empty).
- No new dependencies (verified: `git diff -- pyproject.toml uv.lock` empty).
- No harness/kernel/dataset/provider/embedding/database changes (verified: `git diff` on harness files empty).
- No RDD/4R, no review started, no approval claimed, no roadmap update, no archive.
- All new files pass `ruff check`, `ruff format --check`, `pyright`, `check_focused_tests.py`, and `check_dependency_boundaries.py`.
- Existing gate + harness tests (92) still pass — safety net confirmed.
- Later-slice work preserved recoverably under the pre-approved external temp root; no later work lost or silently rewritten.

### Former Slice 2 (audit history)
- No commits created, no pushes, no PR opened (per instructions).
- No `make ci` or `ci-pr2a` changes (verified: `git diff -- Makefile` shows only `.PHONY` line + new target; `ci`/`ci-pr2a` blocks byte-identical).
- No new dependencies (verified: `git diff -- pyproject.toml uv.lock` empty).
- No harness/kernel/dataset/provider/embedding/database changes (verified: `git diff` on harness files empty).
- No RDD/4R, no review started, no approval claimed, no roadmap update, no archive.
- All new files pass `ruff check`, `ruff format --check`, `pyright`, `check_focused_tests.py`, and `check_dependency_boundaries.py`.
- Existing gate + harness tests (92) still pass — safety net confirmed.
- Runtime harness `make eval-quality-gate` produces correct fail-closed block with safe atomic evidence.

## Native Attempt Evidence

### PR 2A (this batch)
- Attempt ordinal: 3
- Expected current revision: `sha256:feb83a3c3d0136b35965f5cf461464e5dea5fe94913e311ac5c410a011569b9c`
- Work unit: `slice-2a-report-core`
- Did NOT call `sdd-attempt begin`, `reset`, or `finish`.
- Focused test commands and outcomes:
  - `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q -k serialize_gate_report` → 3 passed in 0.03s, exit 0
  - `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q` → 3 passed in 0.02s, exit 0
- Static checks:
  - `uv run --frozen ruff check backend/features/evaluation/gates/adapters/report.py tests/unit/test_technical_grounding_gates_report.py` → All checks passed, exit 0
  - `uv run --frozen ruff format --check backend/features/evaluation/gates/adapters/report.py tests/unit/test_technical_grounding_gates_report.py` → 2 files already formatted, exit 0
  - `uv run --frozen pyright backend/features/evaluation/gates/adapters/report.py tests/unit/test_technical_grounding_gates_report.py` → 0 errors, 0 warnings, exit 0
  - `uv run --frozen python scripts/ci/check_focused_tests.py .` → no findings, exit 0
  - `uv run --frozen python scripts/ci/check_dependency_boundaries.py .` → no findings, exit 0
- Safety net: `uv run --frozen pytest tests/unit/test_technical_grounding_gates_policy.py tests/unit/test_technical_grounding_gates_runner.py tests/architecture/test_quality_evaluation_harness.py -q` → 92 passed in 0.11s, exit 0
- Runtime harness: N/A — pure serializer slice; `make eval-quality-gate` and CLI belong to later stacked slices (2C–2F).
- Changed-line count: 388 authored lines (report.py 141 + test 247), excluding OpenSpec + generated evidence. Under the 400-line hard maintainer threshold; no `size:exception` requested or assumed.
- Content revision hash (PR 2A non-OpenSpec authored content): `sha256:599b0dcab89a19e098dc79300d010474813537e36b11fb1644a11b28b19141bc`
- Disposition: **PASSED** — 3 focused serializer tests green; static checks clean; safety net (92) green; active candidate contains only PR 2A + OpenSpec bookkeeping; later-slice work archived recoverably; line count 388 ≤ 400.

### Former Slice 2 (audit history)
- Attempt ordinal: 2
- Expected current revision: `sha256:9b8fd8453b8a2158e0dfac7f7c4ea7ddc173d04d5520c8cba82ef0c14ffd1dc6`
- Work unit: `slice-2-safe-report-opt-in-wiring`
- Did NOT call `sdd-attempt begin`, `reset`, or `finish`.
- Focused test commands and outcomes:
  - `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q` → 33 passed, exit 0
  - `uv run --frozen pytest tests/architecture/test_technical_grounding_gates.py -q` → 21 passed, exit 0
  - `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py tests/architecture/test_technical_grounding_gates.py -q` → 54 passed, exit 0
  - `uv run --frozen pytest tests/unit/test_technical_grounding_gates_policy.py tests/unit/test_technical_grounding_gates_runner.py tests/unit/test_technical_grounding_gates_report.py tests/architecture/test_technical_grounding_gates.py -q` → 132 passed, exit 0
- Static checks:
  - `uv run --frozen ruff check ...` → All checks passed, exit 0
  - `uv run --frozen ruff format --check ...` → 4 files already formatted, exit 0
  - `uv run --frozen pyright ...` → 0 errors, 0 warnings, exit 0
  - `uv run --frozen python scripts/ci/check_focused_tests.py .` → no findings, exit 0
  - `uv run --frozen python scripts/ci/check_dependency_boundaries.py .` → no findings, exit 0
- Safety net: `uv run --frozen pytest tests/unit/test_technical_grounding_gates_policy.py tests/unit/test_technical_grounding_gates_runner.py tests/architecture/test_quality_evaluation_harness.py -q` → 92 passed, exit 0
- Runtime harness: `make eval-quality-gate` → exit 1 (expected fail-closed block: `critical_contract_mismatch`); report promoted atomically; deterministic across runs; no forbidden content
- Changed-line count: 1,535 authored lines (365 source + 1,161 tests + 9 Makefile), excluding OpenSpec + generated evidence
- Disposition: **RE-PLANNED** — the 1,535-line batch exceeded the 400-line budget; re-planned into sub-slices 2A–2F. Its red/green provenance and bytes are preserved as audit history and in the recoverable archive.