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
Native attempt: ordinal 4, expected revision `sha256:82a3662fd5a6fb51b7efe5289e853d5cc85bdd4e098fb9da6411b60e3ba1281f`
Native attempt: ordinal 5, expected revision `sha256:0b458e9d4b8a8e6eec5fb4f99cd432e64cf397baa506d981279ad19b2c1615dc`

## Slice Boundary

This apply progress merges five autonomous stacked-to-main batches. The
former slice-2 was re-planned into six sub-slices (2A–2F); this file records
the original full slice-2 provenance (kept as audit history) AND the isolated
PR 2A, PR 2B, and PR 2C candidates that replaced it.

### Slice 1 — `slice-1-policy-runner` (MERGED in `master` at `b6aa528`)
- Phase 1: Policy and Contracts (tasks 1.1–1.3) — Unit 1
- Phase 2: Runner and Critical Contracts (tasks 2.1–2.3) — Unit 2

### Former Slice 2 — `slice-2-safe-report-opt-in-wiring` (RE-PLANNED, NOT applied as one PR)
The former slice-2 implemented all of report serialization, atomic promotion,
baseline bootstrap, CLI, and Makefile wiring in one 1,535-line batch. It
exceeded the 400-line review budget and was re-planned into sub-slices 2A–2F.
Its red/green TDD provenance is preserved below as audit history. Its bytes
were preserved recoverably outside the candidate (see "Later-work archive").

### PR 2A — `slice-2a-report-core` (MERGED in `master` at `3b7eacd`)
- Phase 2 task 3.1 only: core allowlisted gate report serializer
- `report.py` serializer core + the focused tests that prove it
- Later sub-slices 2B–2F are NOT in this candidate; their bytes are archived

### PR 2B — `slice-2b-critical-content-safety` (MERGED in `master` at `5e4b636`)
- Phase 2 task 3.2 only: critical-observation and forbidden-content safety tests
- Test-only slice: restores report tests `:253-440` (6 tests) from the archive
- GREEN verifies 2A’s serializer already emits critical observations and
  forbids content tokens — NO duplicated production hunk
- Later sub-slices 2C–2F are NOT in this candidate; their bytes stay archived

### PR 2C — `slice-2c-atomic-promotion` (THIS BATCH)
- Phase 2 task 3.3 only: staging validation, atomic current/previous promotion, rollback, cleanup
- Restores `report.py:146-207` (validation + `_os_replace` + `GateReportAdapter.promote`) and report tests `:441-623` (9 `promote_` tests) from the archive
- GREEN: the 9 restored promotion tests pass against the newly-restored adapter; 2A serializer + 2B safety tests unchanged
- Later sub-slices 2D–2F are NOT in this candidate; their bytes stay archived (baseline source `:209-280`, CLI, Makefile, architecture wiring all excluded)

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

### PR 2A (merged in master at 3b7eacd — isolated from the former slice 2)
- [x] 3.1 (2A) RED core allowlist/status/metadata tests; GREEN `report.py:1-143`; REFACTOR canonical safe JSON.
  - RED provenance preserved from the former slice-2: the 3 `serialize_gate_report` tests were written first against a missing module and failed (module missing).
  - GREEN provenance preserved: `serialize_gate_report` + helpers implemented; the 3 focused tests passed.
  - REFACTOR: removed later-slice imports (`os`, `shutil`, `dataclass`, `Path`) and later-slice exports from `__all__`; removed unused `import pytest` from the test file; trailing newline added; `ruff format` applied (1 file reformatted). Serializer core remains byte-stable (sort_keys canonical JSON, exact allowlist assertion).

### PR 2B (merged in master at 5e4b636 — isolated slice-2b-critical-content-safety)
- [x] 3.2 (2B) RED critical-observation/content-safety tests; GREEN verifies 2A's serializer (no duplicated production hunk); REFACTOR coverage.
  - RED provenance preserved from the former slice-2: the 6 critical-observation/forbidden-content/citation-ids tests were written first against a missing serializer and failed (module missing) in the original full slice-2 TDD cycle.
  - GREEN: the restored 6 tests pass against 2A's already-merged serializer (`report.py:1-143` unchanged). No production hunk was duplicated or added — this is a test-only slice proving the 2A serializer already emits the allowlisted critical observations and forbids content tokens at the serializer boundary.
  - REFACTOR: restored bytes from the verified archive were byte-faithful; the only adjustment was trimming one trailing blank line (W292) introduced by the archive block boundary; `ruff format --check` clean.

### PR 2C (this batch — isolated slice-2c-atomic-promotion)
- [x] 3.3 (2C) RED staging/atomic/rollback tests; GREEN `report.py:146-207`; REFACTOR cleanup and prior-byte preservation.
  - RED provenance preserved from the former slice-2: the 9 `promote_` tests (3 staging-validation + 3 atomic-promotion + 2 rollback + 1 cleanup) were written first against a missing `GateReportAdapter` and failed (`ImportError: cannot import name 'GateReportAdapter'`) when restored to a master tree that only had the 2A serializer.
  - GREEN: restored `report.py:146-207` (`_validate_report_payload`, `_os_replace` module-level alias, `GateReportAdapter.promote` with staged validation, atomic current/previous promotion, stale-previous removal, rollback on first/second rename failure, staging cleanup) + needed imports (`os`, `shutil`, `dataclass`, `Path`) and `__all__` update. The 9 `promote_` tests pass; 2A serializer (3) and 2B safety (6) tests unchanged (18/18 total).
  - REFACTOR: restored bytes from the verified archive were byte-faithful. Adjustments limited to: (1) re-added `from pathlib import Path` to the test imports (2A had removed it during isolation; the archive's original full file imported `Path` and the 2C block's `tmp_path: Path` annotations require it); (2) `ruff format` applied one canonical boundary fix (added a blank line before the 2C section header, trimmed a trailing blank line at EOF introduced by the archive block boundary). No test logic or production logic altered. `ruff format --check` clean.

## Remaining Tasks (later slices)

- [x] 3.3 (2C) RED staging/atomic/rollback tests; GREEN `report.py:146-207`; REFACTOR cleanup and prior-byte preservation. *(completed in PR 2C — entry retained for traceability)*
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

### PR 2A (merged in master at 3b7eacd — isolated candidate)

| File | Action | Lines | What Was Done |
|------|--------|------:|---------------|
| `backend/features/evaluation/gates/adapters/report.py` | Created (truncated from former 280) | 141 | Serializer core only: `serialize_gate_report` + helpers (`_signal_dict`, `_metrics_dict`, `_floors_dict`, `_critical_observations`, `_to_gate_metrics_from_summary`), allowlist constants, `__all__` exporting only `GATE_VERSION`/`SCHEMA_VERSION`/`serialize_gate_report`. Removed later-slice imports (`os`, `shutil`, `dataclass`, `Path`) and later-slice code (promotion, baseline, validation). |
| `tests/unit/test_technical_grounding_gates_report.py` | Created (truncated from former 930) | 247 | 3 focused `serialize_gate_report` tests + shared scaffolding (helpers, allowlist constants, `_ExpectRaise`, `_raises`, metric builders, summary builders). Removed later-slice tests (critical-obs/forbidden/citation, promotion, rollback, baseline, CLI, imports, deterministic). Removed unused `import pytest` (F401). |

### PR 2B (merged in master at 5e4b636 — isolated slice-2b-critical-content-safety)

| File | Action | Lines | What Was Done |
|------|--------|------:|---------------|
| `tests/unit/test_technical_grounding_gates_report.py` | Modified (appended 2B block) | 247→436 (+189) | Restored byte-faithful critical-observation and forbidden-content safety tests from the verified archive (archive lines 253-440). 6 tests: `records_five_signals_in_baseline_and_observed`, `records_reviewed_floors`, `critical_observations_are_allowlisted_and_selected`, `excludes_non_critical_results`, `contains_no_forbidden_content_tokens`, `citation_ids_only_not_content`. One trailing blank line trimmed (W292). No production code changed. |

### PR 2C (this batch — isolated slice-2c-atomic-promotion)

| File | Action | Lines | What Was Done |
|------|--------|------:|---------------|
| `backend/features/evaluation/gates/adapters/report.py` | Modified (appended 2C production block) | 141→217 (+76, -4) | Restored byte-faithful `report.py:146-207` from the verified archive: `_validate_report_payload` (empty/malformed/non-dict/non-allowlist/invalid-status rejection), module-level `_os_replace = os.replace` (monkeypatch seam), `@dataclass(frozen=True, slots=True) GateReportAdapter` with `promote()` (staged validation before I/O, stale-previous removal, atomic current→previous then staged→current, rollback restoring prior current on 2nd-rename failure, staging cleanup on 1st-rename failure and on rollback). Added imports `os`, `shutil`, `dataclass`, `Path`; updated module docstring (promotion now present, baseline still later); `__all__` now exports `GateReportAdapter`. Removed 4 lines: the old 2A-only docstring sentence and the narrow `__all__`. Baseline block (`:209-280`) NOT restored — stays archived for 2D. |
| `tests/unit/test_technical_grounding_gates_report.py` | Modified (appended 2C test block + import) | 436→620 (+184) | Restored byte-faithful `promote_` tests from the verified archive (archive lines 441-623). 9 tests: `test_promote_rejects_empty_payload_before_touching_committed_paths`, `test_promote_rejects_malformed_json_payload`, `test_promote_rejects_payload_missing_allowlisted_keys`, `test_promote_creates_current_on_first_run`, `test_promote_moves_current_to_previous_on_replacement`, `test_promote_replaces_old_previous_on_third_run`, `test_promote_rollback_on_rename_failure_restores_current`, `test_promote_rollback_on_first_rename_failure_leaves_current_intact`, `test_promote_cleans_staging_on_failure`. Re-added `from pathlib import Path` (2C block uses `tmp_path: Path`); `ruff format` applied one boundary fix (blank line before section header + trailing-blank trim). Later tests (`:625+`, baseline/CLI/imports/deterministic) NOT restored — stay archived for 2D/2E. |

**Authored line totals (excluding OpenSpec + generated evidence):**
- PR 2A: 388 total lines (report.py 141 + test 247); 317 non-blank authored lines.
- PR 2B: 190 inserted lines (189 test block + 1 separator blank); 169 non-blank authored lines.
- PR 2C: 268 changed lines (264 insertions + 4 deletions); 204 non-blank authored lines (76 production + 4 docstring/import deletions + 184 test insertions).
- PR 2C is under the 400-line hard maintainer threshold. No `size:exception` requested or assumed.

### Removed from the active candidate (archived, not lost)

| File | Former lines | Archive path | Later slice |
|------|------:|---|---|
| `backend/features/evaluation/gates/adapters/report.py` (:144-280) | 136 | `files/report.py.full` | 2C restored `:146-207`; `:209-280` (baseline) still archived for 2D |
| `backend/features/evaluation/gates/cli.py` | 85 | `files/cli.py.full` | 2E |
| `tests/unit/test_technical_grounding_gates_report.py` (:253-930) | 678 | `files/test_technical_grounding_gates_report.py.full` | 2B restored `:253-440`; 2C restored `:441-623`; `:625-930` (baseline/CLI/imports/deterministic) still archived for 2D/2E |
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

### PR 2A (merged in master at 3b7eacd — isolated slice-2a-report-core)

| Task | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR |
|------|-----------|-------|------------|-----|-------|-------------|----------|
| 3.1 (2A) | `tests/unit/test_technical_grounding_gates_report.py` | Unit | ✅ 92/92 (78 gate slice-1 + 14 harness arch) | ✅ Preserved from former slice-2: the 3 `serialize_gate_report` tests were RED first (module missing) | ✅ 3/3 passed after isolation (serializer core retained; later-slice code removed) | ✅ 3 cases: exact allowlist keys, decision status+reasons, run_id/profile/provider_mode/timestamp/duration — each exercises a distinct serializer field path | ✅ Removed unused `import pytest` (F401); added trailing newline (W292); `ruff format` applied (1 file reformatted); removed later-slice imports/exports from `report.py` `__all__`; serializer byte-stable canonical JSON preserved |

### PR 2B (merged in master at 5e4b636 — isolated slice-2b-critical-content-safety)

| Task | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR |
|------|-----------|-------|------------|-----|-------|-------------|----------|
| 3.2 (2B) | `tests/unit/test_technical_grounding_gates_report.py` | Unit | ✅ 92/92 (78 gate slice-1 + 14 harness arch) | ✅ Preserved from former slice-2: the 6 critical-observation/forbidden-content/citation-ids tests were RED first (module missing) | ✅ 9/9 passed (3 from 2A + 6 restored 2B) against 2A's already-merged serializer — no production hunk added | ✅ 6 cases: five-signal baseline/observed, reviewed floors, allowlisted+selected critical observations, non-critical exclusion, forbidden-token absence, citation-IDs-not-content — each proves a distinct safety property at the serializer boundary | ✅ Trailing blank line trimmed (W292); `ruff format --check` clean; byte-faithful restoration from verified archive |

### PR 2C (this batch — isolated slice-2c-atomic-promotion)

| Task | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR |
|------|-----------|-------|------------|-----|-------|-------------|----------|
| 3.3 (2C) | `tests/unit/test_technical_grounding_gates_report.py` | Unit | ✅ 92/92 (78 gate slice-1 + 14 harness arch) + ✅ 9/9 report (2A+2B merged at 5e4b636) | ✅ Preserved from former slice-2: the 9 `promote_` tests were RED first (module missing). Re-confirmed RED on restoration: all 9 failed with `ImportError: cannot import name 'GateReportAdapter'` against master `5e4b636` (2A+2B only) before the production block was restored | ✅ 18/18 passed (3 from 2A + 6 from 2B + 9 restored 2C) after restoring `report.py:146-207` — the adapter implements staged validation, atomic current/previous promotion, rollback, and cleanup | ✅ 9 cases: 3 staging-validation rejections (empty/malformed-json/missing-allowlist-keys — each rejects before touching committed paths), 3 atomic-promotion scenarios (first-run creates current/no-previous, replacement moves current→previous, third-run replaces old previous), 2 rollback scenarios (2nd-rename-failure restores prior current from previous, 1st-rename-failure leaves current intact), 1 staging-cleanup-on-failure — each exercises a distinct promotion/rollback code path via `_os_replace` monkeypatch seam | ✅ Re-added `from pathlib import Path` (removed by 2A isolation, required by 2C `tmp_path: Path` annotations); `ruff format` applied one boundary fix (blank line before section header + trailing-blank trim at EOF); `ruff check`/`ruff format --check`/`pyright`/`check_focused_tests.py`/`check_dependency_boundaries.py` all clean; byte-faithful restoration from revalidated archive |

### Test Summary (combined)
- **Total tests written across all batches**: 147 (42 policy + 36 runner + 33 report-former + 21 arch-former + 6 report-2B + 9 report-2C)
- **PR 2A focused tests in active candidate**: 3 (serialize_gate_report core)
- **PR 2B focused tests restored**: 6 (critical-observations/forbidden/citation-ids safety proof)
- **PR 2C focused tests restored**: 9 (staging validation + atomic promotion + rollback + cleanup)
- **PR 2A+2B+2C focused tests passing**: 18
- **Layers used**: Unit
- **Approval tests** (refactoring): None — no refactoring of existing code
- **Pure functions created**: 6 retained in PR 2A+2C (`serialize_gate_report`, `_signal_dict`, `_metrics_dict`, `_floors_dict`, `_critical_observations`, `_validate_report_payload`); `_to_gate_metrics_from_summary` reuses the slice-1 `_to_gate_metrics`; `GateReportAdapter.promote` is the atomic-promotion method (stateful by design — validates staged payload before any committed I/O)

## Work Unit Evidence

### Slice 1 (merged)

| Evidence | Required value |
|---|---|
| Focused test command and exact result | `uv run --frozen pytest tests/unit/test_technical_grounding_gates_policy.py tests/unit/test_technical_grounding_gates_runner.py -q` → 78 passed in 0.04s, exit 0 |
| Runtime harness command/scenario and exact result | N/A — CLI wiring and `make eval-quality-gate` belong to the later report/CLI slice (Phase 3); no runtime boundary exists for this pure-policy/runner slice |
| Rollback boundary | Remove `backend/features/evaluation/gates/{__init__,domain,policy,ports,application.py}` and `adapters/__init__.py`, plus `tests/unit/test_technical_grounding_gates_{policy,runner}.py`. No harness, kernel, dataset, Makefile, manifest, or lockfile changes to revert. |

### PR 2A (merged)

| Evidence | Required value |
|---|---|
| Focused test command and exact result | `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q -k serialize_gate_report` → 3 passed in 0.03s, exit 0 |
| Runtime harness command/scenario and exact result | N/A — pure serializer slice; `make eval-quality-gate`, CLI, promotion, and baseline bootstrap belong to later stacked slices (2C–2F). No runtime boundary exists for PR 2A. |
| Rollback boundary | Remove `backend/features/evaluation/gates/adapters/report.py` and `tests/unit/test_technical_grounding_gates_report.py`. No Makefile, CLI, harness, kernel, dataset, manifest, lockfile, or dependency changes to revert (Makefile diff reverted to HEAD; later-slice files removed from candidate and archived). |

### PR 2B (merged)

| Evidence | Required value |
|---|---|
| Focused test command and exact result | `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q -k 'critical_observations or forbidden or citation_ids'` → 3 passed, 6 deselected in 0.03s, exit 0. Full file: `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q` → 9 passed in 0.02s, exit 0. |
| Runtime harness command/scenario and exact result | N/A — test-only safety-proof slice; no runtime boundary exists. The restored tests prove critical observations and forbidden content absence at the serializer boundary without adding production behavior. |
| Rollback boundary | Revert the 189-line test append to `tests/unit/test_technical_grounding_gates_report.py` (back to 247 lines). No production code, Makefile, CLI, harness, kernel, dataset, manifest, lockfile, or dependency changes to revert. |

### PR 2C (this batch)

| Evidence | Required value |
|---|---|
| Focused test command and exact result | `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q -k 'promote_'` → 9 passed, 9 deselected in 1.01s, exit 0 (after GREEN). RED before production restore: same command → 9 failed (ImportError: cannot import name 'GateReportAdapter'), exit non-zero. Full file: `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q` → 18 passed in 0.03s, exit 0 (3 from 2A + 6 from 2B + 9 from 2C). |
| Runtime harness command/scenario and exact result | N/A — temp-path adapter slice; no runtime boundary exists for PR 2C alone. The `GateReportAdapter.promote` operates on a caller-supplied `base_dir` (validated in tests via `tmp_path`); the CLI wiring that invokes it (`make eval-quality-gate`) belongs to later stacked slices (2E/2F). The restored tests prove staged validation, atomic current/previous promotion, rollback on rename failure, and staging cleanup against a real filesystem via the `_os_replace` monkeypatch seam. |
| Rollback boundary | Revert the 2C production block in `backend/features/evaluation/gates/adapters/report.py` (remove `_validate_report_payload`, `_os_replace`, `GateReportAdapter`, the `os`/`shutil`/`dataclass`/`Path` imports, and the `GateReportAdapter` `__all__` entry; restore the 2A-only docstring sentence). Revert the 2C test append + `Path` import in `tests/unit/test_technical_grounding_gates_report.py` (back to 436 lines). No baseline code (`:209-280`), Makefile, CLI, harness, kernel, dataset, manifest, lockfile, or dependency changes to revert — all still archived. |

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

### PR 2A (merged)
7. **`__all__` narrowed to serializer exports**: The former `report.py` exported `GateReportAdapter` and `bootstrap_baseline`, which belong to later slices (2C, 2D). PR 2A's `__all__` exports only `GATE_VERSION`, `SCHEMA_VERSION`, and `serialize_gate_report`. Later slices will re-add the promotion/baseline exports when their code lands in the same module. Faithful to the re-planned boundary, not a design deviation.
8. **Unused scaffolding retained in the test file**: `_ExpectRaise`, `_raises`, `_gate_metrics_regression`, `_gate_metrics_escalate_only`, `_BAD_*`, `FORBIDDEN_CONTENT_TOKENS`, `ALLOWED_OBSERVATION_KEYS`, `_write_harness_summary`-adjacent constants are defined but not called by the 3 PR 2A tests. They are kept because the revised tasks artifact assigns them to the PR 2A test boundary (`:1-252`) and later slices (2B–2E) reuse them. Module-level unused functions/constants are not ruff errors (only unused imports are F401). The single unused import (`pytest`) was removed.

### PR 2B (merged)
9. **Byte-faithful restoration with one trailing-blank trim**: The 2B block was restored verbatim from the verified archive (byte-identical to archive lines 253-440). The archive block ended with a blank line that became a trailing blank at EOF (W292); ruff flagged it. The only adjustment was trimming that single trailing `\n` — no test logic or content was altered. Faithful to the restoration protocol, not a deviation.

### PR 2C (this batch)
10. **`Path` import re-added to the test file**: PR 2A removed `from pathlib import Path` during isolation because its 3 serializer tests did not use `Path` (and `import pytest` was removed as F401). The 2C test block uses `tmp_path: Path` annotations in all 9 `promote_` test signatures and in the inner `_failing_replace`/`_always_fail` helper signatures, so `Path` is required. The archive's original full test file imported `Path` (archive line 19); re-adding it restores the original import surface, not a new dependency. This is a necessary import restoration driven by the 2C block's type annotations, consistent with the archive's own import block. Not a design deviation.
11. **`ruff format` boundary fix**: The byte-faithful 2C block restored the archive's single blank-line separator before the section header comment (archive line 437→441). `ruff format` canonicalized this to two blank lines before the module-level section (PEP 8 two-blank rule between the prior 2B function and the 2C comment+function group) and trimmed the trailing blank line at EOF (the archive's line 623 blank, which sat before the 2D block in the original full file and became a trailing blank once 2D was not restored). These are whitespace-only canonicalizations identical in kind to the PR 2B trailing-blank trim; no test or production logic was altered. Faithful to the restoration protocol.

## Issues Found

### Slice 1 (merged)
1. **Design critical-expectations table discrepancy with committed baseline**: 6 of 12 critical cases do NOT match the design's expected outcome/reason pairs. A real gate run blocks with `critical_contract_mismatch` — intended release-contract behavior. Flagged for the orchestrator/maintainer.
2. **Focused-test guard constraint**: Negative number literals in `pytest.mark.parametrize` are rejected (parsed as `UnaryOp`). Resolved by module-level `NEG_ONE = -1` constant.

### Former Slice 2 (audit history)
3. **Focused-test guard forbids `pytest.raises` AND dict literals in parametrize**: Resolved by `_ExpectRaise` context manager + `_raises` boolean helper, and named module-level constants (`_BAD_ZERO_DEN`, `_BAD_NEG_NUM`, `_BAD_EXCEED`) for parametrize values.
4. **Initial gate baseline blocks fail-closed**: `make eval-quality-gate` exits non-zero with `critical_contract_mismatch` because the development fake kernel does not satisfy eval-11/12/13 critical contracts. This is the EXPECTED release block — the gate is a release contract that blocks when the kernel doesn't meet critical contracts. The baseline is recorded as a fail-closed gate result, not a weakening of policy. Distinguished from implementation failure: all 132 focused tests pass, static checks are clean, and the runtime harness produces the correct safe report with the correct block decision.
5. **Runtime-generated `evaluation-runs/previous/`**: Running `make eval-quality` (harness) for comparison created a harness `previous/`. Cleaned up — not part of this slice's deliverable. The gate `evaluation-runs/gate/current/` is the intended initial baseline.

### PR 2A (merged)
6. **None.** The serializer core isolates cleanly. The only lint fix required was removing the unused `import pytest` (the 3 focused tests use bare `assert`, no `pytest.mark`) and adding a trailing newline.

### PR 2B (merged)
7. **None.** The 2B block is a byte-faithful restoration of already-written, already-RED-proven tests. The only adjustment was trimming one trailing blank line (W292) introduced by the archive block boundary. All 6 restored tests pass against the unchanged 2A serializer, confirming the serializer already emits allowlisted critical observations and forbids content tokens.

### PR 2C (this batch)
8. **Worktree environment required `--extra dev` sync, not `--all-groups`.** The fresh git worktree's `uv sync --frozen` (and `--all-groups`) did not install the `pytest`/`ruff`/`pyright` dev tooling because `dev` is a PEP 621 `[project.optional-dependencies]` extra, not a PEP 735 dependency group. The correct restore command is `uv sync --frozen --extra dev`. This is an environment-setup note for future worktree-based apply batches, not an implementation issue. The main checkout's venv already had the tooling; only the fresh worktree needed the explicit `--extra dev` flag.

## Cleanup / Process Evidence

### PR 2A (merged)
- No commits created, no pushes, no PR opened (per instructions).
- No `make ci` or `ci-pr2a` changes (verified: `Makefile` reverted to HEAD; `git diff -- Makefile` empty).
- No new dependencies (verified: `git diff -- pyproject.toml uv.lock` empty).
- No harness/kernel/dataset/provider/embedding/database changes (verified: `git diff` on harness files empty).
- No RDD/4R, no review started, no approval claimed, no roadmap update, no archive.
- All new files pass `ruff check`, `ruff format --check`, `pyright`, `check_focused_tests.py`, and `check_dependency_boundaries.py`.
- Existing gate + harness tests (92) still pass — safety net confirmed.
- Later-slice work preserved recoverably under the pre-approved external temp root; no later work lost or silently rewritten.

### PR 2B (merged)
- No commits created, no pushes, no PR opened (per instructions).
- No `make ci` or `ci-pr2a` changes (verified: `git diff -- Makefile` empty; only the test file changed).
- No new dependencies (verified: `git diff -- pyproject.toml uv.lock` empty).
- No production code changes (verified: `git diff --stat HEAD` shows only the test file, +189 insertions, 0 deletions).
- No harness/kernel/dataset/provider/embedding/database changes (verified: `git diff` on harness files empty).
- No RDD/4R, no review started, no approval claimed, no roadmap update, no archive.
- The modified test file passes `ruff check`, `ruff format --check`, `pyright`, `check_focused_tests.py`, and `check_dependency_boundaries.py`.
- Existing gate + harness tests (92) still pass — safety net confirmed.
- Archive revalidated: all 6 archive file hashes match the MANIFEST; no later work lost or silently rewritten.

### PR 2C (this batch)
- No commits created, no pushes, no PR opened (per instructions).
- No `make ci` or `ci-pr2a` changes (verified: `git diff --name-only master` shows only `report.py` and the report test file; Makefile untouched).
- No new dependencies (verified: `git diff -- pyproject.toml uv.lock` empty).
- No baseline/CLI/Makefile/architecture-wiring changes (verified: only 2 files changed; baseline `report.py:209-280`, `cli.py`, `Makefile`, architecture test, and generated evidence all remain archived — NOT restored).
- No harness/kernel/dataset/provider/embedding/database changes (verified: `git diff` on harness files empty).
- No RDD/4R, no review started, no approval claimed, no roadmap update, no archive.
- The 2 modified files pass `ruff check`, `ruff format --check`, `pyright`, `check_focused_tests.py`, and `check_dependency_boundaries.py`.
- Existing gate + harness tests (92) still pass — safety net confirmed.
- Full report test file (18) passes — 2A serializer (3) + 2B safety (6) + 2C promotion (9) all green together.
- Archive revalidated: all 6 archive file SHA256 hashes match the MANIFEST in this file (`report.py.full`, `cli.py.full`, `test_technical_grounding_gates_report.py.full`, `test_technical_grounding_gates.py.full`, `gate-current-report.json`, `former-slice-2-tracked.diff`). Archive bytes intact; no later work lost or silently rewritten.
- Worktree created at `RAG-worktrees/slice-2c-atomic-promotion` (branch `slice-2c-atomic-promotion`, stacked-to-main from `master` `5e4b636`); environment restored via `uv sync --frozen --extra dev`.

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

### PR 2A (merged)
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

### PR 2B (merged)
- Attempt ordinal: 4
- Expected current revision: `sha256:82a3662fd5a6fb51b7efe5289e853d5cc85bdd4e098fb9da6411b60e3ba1281f`
- Work unit: `slice-2b-critical-content-safety`
- Did NOT call `sdd-attempt begin`, `reset`, or `finish`.
- Focused test commands and outcomes:
  - `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q -k 'critical_observations or forbidden or citation_ids'` → 3 passed, 6 deselected in 0.03s, exit 0
  - `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q` → 9 passed in 0.02s, exit 0
- Static checks:
  - `uv run --frozen ruff check tests/unit/test_technical_grounding_gates_report.py` → All checks passed, exit 0
  - `uv run --frozen ruff format --check tests/unit/test_technical_grounding_gates_report.py` → 1 file already formatted, exit 0
  - `uv run --frozen pyright tests/unit/test_technical_grounding_gates_report.py` → 0 errors, 0 warnings, 0 informations, exit 0
  - `uv run --frozen python scripts/ci/check_focused_tests.py .` → no findings, exit 0
  - `uv run --frozen python scripts/ci/check_dependency_boundaries.py .` → no findings, exit 0
- Safety net: `uv run --frozen pytest tests/unit/test_technical_grounding_gates_policy.py tests/unit/test_technical_grounding_gates_runner.py tests/architecture/test_quality_evaluation_harness.py -q` → 92 passed in 0.12s, exit 0
- Runtime harness: N/A — test-only safety-proof slice; no runtime boundary exists.
- Archive revalidation: all 6 archive file SHA256 hashes match the MANIFEST (`report.py.full`, `cli.py.full`, `test_technical_grounding_gates_report.py.full`, `test_technical_grounding_gates.py.full`, `gate-current-report.json`, `former-slice-2-tracked.diff`). Archive bytes intact.
- Changed-line count: 190 authored lines (189 test block insertions + 1 separator blank), excluding OpenSpec + generated evidence. Under the 400-line hard maintainer threshold; no `size:exception` requested or assumed.
- Production code: unchanged (verified: `git diff --stat HEAD` shows only the test file; 0 production files modified).
- Disposition: **PASSED** — 6 restored safety tests green against 2A's unchanged serializer; static checks clean; safety net (92) green; archive integrity revalidated; line count 190 ≤ 400; no production hunk duplicated.

### PR 2C (this batch)
- Attempt ordinal: 5
- Expected current revision: `sha256:0b458e9d4b8a8e6eec5fb4f99cd432e64cf397baa506d981279ad19b2c1615dc`
- Work unit: `slice-2c-atomic-promotion`
- Did NOT call `sdd-attempt begin`, `reset`, or `finish`.
- Focused test commands and outcomes:
  - RED (before production restore): `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q -k 'promote_'` → 9 failed (ImportError: cannot import name 'GateReportAdapter'), 9 deselected in 0.11s, exit non-zero — genuine RED: all 9 tests reference production code that does not exist on master `5e4b636` (2A+2B only).
  - GREEN (after restoring `report.py:146-207`): `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q -k 'promote_'` → 9 passed, 9 deselected in 1.01s, exit 0.
  - Full file: `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q` → 18 passed in 0.03s, exit 0 (3 from 2A + 6 from 2B + 9 from 2C).
- Static checks:
  - `uv run --frozen ruff check backend/features/evaluation/gates/adapters/report.py tests/unit/test_technical_grounding_gates_report.py` → All checks passed!, exit 0
  - `uv run --frozen ruff format --check backend/features/evaluation/gates/adapters/report.py tests/unit/test_technical_grounding_gates_report.py` → 2 files already formatted, exit 0 (after `ruff format` applied 1 boundary fix to the test file)
  - `uv run --frozen pyright backend/features/evaluation/gates/adapters/report.py tests/unit/test_technical_grounding_gates_report.py` → 0 errors, 0 warnings, 0 informations, exit 0
  - `uv run --frozen python scripts/ci/check_focused_tests.py .` → no findings, exit 0
  - `uv run --frozen python scripts/ci/check_dependency_boundaries.py .` → no findings, exit 0
- Safety net: `uv run --frozen pytest tests/unit/test_technical_grounding_gates_policy.py tests/unit/test_technical_grounding_gates_runner.py tests/architecture/test_quality_evaluation_harness.py -q` → 92 passed in 0.11s, exit 0
- Runtime harness: N/A — temp-path adapter slice; `GateReportAdapter.promote` operates on a caller-supplied `base_dir` (tested via `tmp_path`). The CLI/Makefile wiring that invokes it belongs to later stacked slices (2E/2F). No runtime boundary exists for PR 2C alone.
- Archive revalidation: all 6 archive file SHA256 hashes re-checked and match the MANIFEST in this file (`report.py.full` `03040265…`, `cli.py.full` `6821a451…`, `test_technical_grounding_gates_report.py.full` `3333bfba…`, `test_technical_grounding_gates.py.full` `7f91aa50…`, `gate-current-report.json` `3d6bab10…`, `former-slice-2-tracked.diff` `f84bdf74…`). Archive bytes intact.
- Changed-line count: 268 authored lines (264 insertions + 4 deletions; 76 production + 4 docstring/import + 184 test insertions + 1 `Path` import), excluding OpenSpec + generated evidence. 204 non-blank authored lines. Under the 400-line hard maintainer threshold; no `size:exception` requested or assumed.
- Scope verification: only 2 files changed (`backend/features/evaluation/gates/adapters/report.py`, `tests/unit/test_technical_grounding_gates_report.py`). No baseline source (`:209-280`), CLI, Makefile, architecture wiring, harness, kernel, dataset, manifest, or lockfile changes. Baseline/CLI/Makefile/arch all remain archived — NOT restored (per PR 2C boundary).
- Byte-fidelity: production block restored byte-faithful from archive `report.py:146-207`; test block restored byte-faithful from archive `:441-623`. Adjustments limited to: (1) re-added `from pathlib import Path` (removed by 2A isolation, required by 2C annotations, present in the archive's original import block); (2) `ruff format` canonical whitespace at the 2B→2C boundary and EOF. No test or production logic altered.
- Disposition: **PASSED** — 9 restored promotion tests green (RED re-confirmed before GREEN); 2A+2B tests unchanged (18 total green); static checks clean; safety net (92) green; archive integrity revalidated; line count 268 ≤ 400; no out-of-scope restoration.

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