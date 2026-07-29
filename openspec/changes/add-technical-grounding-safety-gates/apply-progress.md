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
Native attempt: ordinal 6, expected revision `sha256:0140b0c961450fb5eb05690533d07a2bbcbff993aded4b4540fd667472bb5967`
Native attempt: ordinal 7, expected revision `sha256:a547400df5c788e02928a257834839da38542c1292a97bbeaa9299a6fd25d9fd`

## Slice Boundary

This apply progress merges six autonomous stacked-to-main batches. The
former slice-2 was re-planned into six sub-slices (2A–2F); this file records
the original full slice-2 provenance (kept as audit history) AND the isolated
PR 2A, PR 2B, PR 2C, PR 2D, and PR 2E candidates that replaced it.

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

### PR 2C — `slice-2c-atomic-promotion` (MERGED in `master` at `42e0b58`)
- Phase 2 task 3.3 only: staging validation, atomic current/previous promotion, rollback, cleanup
- Restores `report.py:146-207` (validation + `_os_replace` + `GateReportAdapter.promote`) and report tests `:441-623` (9 `promote_` tests) from the archive
- GREEN: the 9 restored promotion tests pass against the newly-restored adapter; 2A serializer + 2B safety tests unchanged
- Later sub-slices 2D–2F are NOT in this candidate; their bytes stay archived (baseline source `:209-280`, CLI, Makefile, architecture wiring all excluded)

### PR 2D — `slice-2d-baseline-validation` (MERGED in `master` at `5a088ed`)
- Phase 2 task 3.4 only: baseline-source resolution and validation (immutable baseline bootstrap)
- Restores `report.py:209-280` (`_signal_from_dict`, `_metrics_from_dict`, `bootstrap_baseline`, updated `__all__`) and report tests `:626-751` (`_write_harness_summary` helper + 5 `bootstrap_baseline` tests) from the archive
- GREEN: the 7 restored baseline tests pass against the newly-restored bootstrap code; 2A serializer + 2B safety + 2C promotion tests unchanged (25 total)
- Later sub-slices 2E–2F were NOT in that candidate; their bytes stayed archived (CLI, Makefile, architecture wiring, 2E tests all excluded)

### PR 2E — `slice-2e-gate-cli` (THIS BATCH)
- Phase 2 task 3.5 only: gate CLI orchestration (frozen-clock wiring, safe stdout, exit codes, no-network imports)
- Restores `cli.py` (entire 85-line file) and report tests `:753-930` (7 tests: 4 `run_gate_*` exit-code/stdout + 2 import-guard + 1 deterministic) from the archive
- GREEN: the 8 restored 2E test cases pass against the newly-restored CLI; 2A serializer (3) + 2B safety (6) + 2C promotion (9) + 2D baseline (7) tests unchanged (33 total)
- Later sub-slice 2F is NOT in this candidate; its bytes stay archived (Makefile, architecture wiring `test_technical_grounding_gates.py`, committed gate baseline evidence all excluded)

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

### PR 2C (merged in master at 42e0b58 — isolated slice-2c-atomic-promotion)
- [x] 3.3 (2C) RED staging/atomic/rollback tests; GREEN `report.py:146-207`; REFACTOR cleanup and prior-byte preservation.
  - RED provenance preserved from the former slice-2: the 9 `promote_` tests (3 staging-validation + 3 atomic-promotion + 2 rollback + 1 cleanup) were written first against a missing `GateReportAdapter` and failed (`ImportError: cannot import name 'GateReportAdapter'`) when restored to a master tree that only had the 2A serializer.
  - GREEN: restored `report.py:146-207` (`_validate_report_payload`, `_os_replace` module-level alias, `GateReportAdapter.promote` with staged validation, atomic current/previous promotion, stale-previous removal, rollback on first/second rename failure, staging cleanup) + needed imports (`os`, `shutil`, `dataclass`, `Path`) and `__all__` update. The 9 `promote_` tests pass; 2A serializer (3) and 2B safety (6) tests unchanged (18/18 total).
  - REFACTOR: restored bytes from the verified archive were byte-faithful. Adjustments limited to: (1) re-added `from pathlib import Path` to the test imports (2A had removed it during isolation; the archive's original full file imported `Path` and the 2C block's `tmp_path: Path` annotations require it); (2) `ruff format` applied one canonical boundary fix (added a blank line before the 2C section header, trimmed a trailing blank line at EOF introduced by the archive block boundary). No test logic or production logic altered. `ruff format --check` clean.

### PR 2D (merged in master at 5a088ed — isolated slice-2d-baseline-validation)
- [x] 3.4 (2D) RED baseline-source/validation tests; GREEN `report.py:209-280`; REFACTOR immutable baseline handling.
  - RED provenance preserved from the former slice-2: the 5 `bootstrap_baseline` tests (1 first-run-from-harness + 1 later-run-from-gate + 1 no-source-raises + 1 malformed-harness-raises + 3 parametrized bad-signal rejections) + the `_write_harness_summary` helper were written first against a missing `bootstrap_baseline` and failed (`ImportError: cannot import name 'bootstrap_baseline'`) when restored to a master tree (`42e0b58`) that had only the 2A serializer + 2C promotion adapter.
  - GREEN: restored `report.py:209-280` (`_signal_from_dict` with int/bool/negative/zero-denominator/numerator-exceeds validation, `_metrics_from_dict` with exact key-set validation, `bootstrap_baseline` with gate-snapshot-preferred-then-harness-fallback resolution and malformed/missing rejection) + updated `__all__` (now exports `bootstrap_baseline`) + removed the 2C-era "baseline bootstrap belongs to a later stacked slice" docstring sentence. Re-added `import pytest` (removed by 2A isolation; the 2D parametrized test uses `@pytest.mark.parametrize`). The 7 `bootstrap_baseline` tests pass; 2A serializer (3) + 2B safety (6) + 2C promotion (9) tests unchanged (25/25 total).
  - REFACTOR: restored bytes from the verified archive were byte-faithful. `report.py` (280 lines) is now byte-identical to the archive `report.py.full` (280 lines). The test file (750 lines) is byte-identical to the archive's first 750 lines; the only adjustment is trimming the archive's two trailing blank lines (lines 751-752, which belonged to the 2E boundary and became W292 trailing blanks once 2E was not restored) — the same kind of whitespace-only canonicalization as PR 2B and PR 2C. No test or production logic altered. `ruff format --check` clean (no canonicalization needed beyond the trailing-blank trim).

### PR 2E (this batch — isolated slice-2e-gate-cli)
- [x] 3.5 (2E) RED exit/stdout/no-network tests; GREEN `cli.py`; REFACTOR frozen `Clock` wiring and safe errors.
  - RED provenance preserved from the former slice-2: the 7 2E tests (4 `run_gate_*` exit-code/stdout + 2 import-guard parametrized/single + 1 deterministic frozen-clock) were written first against a missing `backend.features.evaluation.gates.cli` and failed (`ModuleNotFoundError: No module named 'backend.features.evaluation.gates.cli'`) when restored to a master tree (`5a088ed`) that had only the 2A serializer + 2C promotion adapter + 2D baseline bootstrap.
  - GREEN: restored `cli.py` (entire 85-line file: `run_gate` orchestration with frozen `Clock`, `run_evaluation` → `bootstrap_baseline` → `evaluate_gate` → `serialize_gate_report` → `GateReportAdapter.promote`, safe stdout writing status+reason_codes only, exit 0 for pass / 1 for block/escalate; `main` wiring with `_PROJECT_ROOT = parents[4]` and `FrozenClock(timestamp=1_700_000_000.0, duration_seconds=0.0)`). Restored report tests `:753-930` (7 tests: `test_run_gate_returns_zero_on_pass`, `test_run_gate_returns_nonzero_on_block`, `test_run_gate_returns_nonzero_on_escalate`, `test_run_gate_stdout_contains_only_safe_fields`, `test_gate_report_and_cli_import_no_forbidden_modules` (2 parametrized cases), `test_gate_cli_uses_no_subprocess_or_network`, `test_run_gate_produces_deterministic_report_across_runs`). The 8 restored 2E test cases pass; 2A serializer (3) + 2B safety (6) + 2C promotion (9) + 2D baseline (7) tests unchanged (33/33 total).
  - REFACTOR: `cli.py` (85 lines) is byte-identical to the archive `cli.py.full` (`sha256:6821a451…`). The test file (931 lines) is byte-identical to the archive's full `test_technical_grounding_gates_report.py.full` (930 lines) EXCEPT for one added type-narrowing guard line (`assert mod.__file__ is not None` at line 891) required by the pyright CI gate (`mod.__file__` is `str | None`; `Path()` requires `StrPath`). This is a necessary type-safety adjustment, not a logic change — the test's intent and assertions are unchanged. `ruff check`/`ruff format --check`/`pyright`/`check_focused_tests.py`/`check_dependency_boundaries.py` all clean.

## Remaining Tasks (later slices)

- [x] 3.3 (2C) RED staging/atomic/rollback tests; GREEN `report.py:146-207`; REFACTOR cleanup and prior-byte preservation. *(completed in PR 2C — entry retained for traceability)*
- [x] 3.4 (2D) RED baseline-source/validation tests; GREEN `report.py:209-280`; REFACTOR immutable baseline handling. *(completed in PR 2D — entry retained for traceability)*
- [x] 3.5 (2E) RED exit/stdout/no-network tests; GREEN `cli.py`; REFACTOR frozen `Clock` wiring and safe errors. *(completed in PR 2E — entry retained for traceability)*
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

### PR 2C (merged in master at 42e0b58 — isolated slice-2c-atomic-promotion)

| File | Action | Lines | What Was Done |
|------|--------|------:|---------------|
| `backend/features/evaluation/gates/adapters/report.py` | Modified (appended 2C production block) | 141→217 (+76, -4) | Restored byte-faithful `report.py:146-207` from the verified archive: `_validate_report_payload` (empty/malformed/non-dict/non-allowlist/invalid-status rejection), module-level `_os_replace = os.replace` (monkeypatch seam), `@dataclass(frozen=True, slots=True) GateReportAdapter` with `promote()` (staged validation before I/O, stale-previous removal, atomic current→previous then staged→current, rollback restoring prior current on 2nd-rename failure, staging cleanup on 1st-rename failure and on rollback). Added imports `os`, `shutil`, `dataclass`, `Path`; updated module docstring (promotion now present, baseline still later); `__all__` now exports `GateReportAdapter`. Removed 4 lines: the old 2A-only docstring sentence and the narrow `__all__`. Baseline block (`:209-280`) NOT restored — stays archived for 2D. |
| `tests/unit/test_technical_grounding_gates_report.py` | Modified (appended 2C test block + import) | 436→620 (+184) | Restored byte-faithful `promote_` tests from the verified archive (archive lines 441-623). 9 tests: `test_promote_rejects_empty_payload_before_touching_committed_paths`, `test_promote_rejects_malformed_json_payload`, `test_promote_rejects_payload_missing_allowlisted_keys`, `test_promote_creates_current_on_first_run`, `test_promote_moves_current_to_previous_on_replacement`, `test_promote_replaces_old_previous_on_third_run`, `test_promote_rollback_on_rename_failure_restores_current`, `test_promote_rollback_on_first_rename_failure_leaves_current_intact`, `test_promote_cleans_staging_on_failure`. Re-added `from pathlib import Path` (2C block uses `tmp_path: Path`); `ruff format` applied one boundary fix (blank line before section header + trailing-blank trim). Later tests (`:625+`, baseline/CLI/imports/deterministic) NOT restored — stay archived for 2D/2E. |

### PR 2D (this batch — isolated slice-2d-baseline-validation)

| File | Action | Lines | What Was Done |
|------|--------|------:|---------------|
| `backend/features/evaluation/gates/adapters/report.py` | Modified (appended 2D production block) | 217→280 (+67, -4) | Restored byte-faithful `report.py:209-280` from the verified archive: `_signal_from_dict` (int/bool/negative/zero-denominator/numerator-exceeds validation), `_metrics_from_dict` (exact key-set validation against METRIC_NAMES), `bootstrap_baseline` (gate-snapshot `current/report.json` preferred on later runs, harness `current/summary.json` fallback on first run, malformed/missing/non-dict/missing-metrics rejection). Updated `__all__` to export `bootstrap_baseline`. Removed 4 lines: the 2C-era "Baseline bootstrap belongs to a later stacked slice and lives in this same module once that slice lands." docstring sentence (baseline now present). `report.py` (280 lines) is now byte-identical to the archive `report.py.full` (280 lines). |
| `tests/unit/test_technical_grounding_gates_report.py` | Modified (appended 2D test block + import) | 620→750 (+130, -0) | Restored byte-faithful `bootstrap_baseline` tests from the verified archive (archive lines 625-751). 5 tests + 1 helper: `_write_harness_summary` helper, `test_bootstrap_baseline_from_harness_snapshot_on_first_run`, `test_bootstrap_baseline_from_gate_snapshot_on_later_run`, `test_bootstrap_baseline_raises_when_no_source`, `test_bootstrap_baseline_raises_on_malformed_harness_summary`, `test_bootstrap_baseline_rejects_zero_denominator_or_negative` (3 parametrized cases: zero-denominator, negative-numerator, numerator-exceeds-denominator). Re-added `import pytest` (removed by 2A isolation; the 2D parametrized test uses `@pytest.mark.parametrize`; the archive's original full file imported `pytest`). Test file (750 lines) is byte-identical to the archive's first 750 lines; the archive's two trailing blank lines (751-752, belonging to the 2E boundary) were trimmed (W292). Later tests (`:753-930`, CLI/imports/deterministic) NOT restored — stay archived for 2E. |

### PR 2E (this batch — isolated slice-2e-gate-cli)

| File | Action | Lines | What Was Done |
|------|--------|------:|---------------|
| `backend/features/evaluation/gates/cli.py` | Created | 85 | Restored byte-faithful `cli.py` from the verified archive (entire file). `run_gate(*, dataset_root, gate_dir, harness_current, clock: FrozenClock) -> int`: orchestrates `run_evaluation` → `bootstrap_baseline` → `evaluate_gate` → `serialize_gate_report` → `GateReportAdapter.promote`, writes safe stdout (`gate: {status}\nreasons: {codes}\n` — status and reason codes only, no content), returns 0 for pass / 1 for block/escalate. `main()`: resolves `dataset_root` from `sys.argv[1]` (default `_PROJECT_ROOT/evaluation-dataset`), `_PROJECT_ROOT = parents[4]`, `gate_dir = evaluation-runs/gate`, `harness_current = evaluation-runs/current`, `FrozenClock(timestamp=1_700_000_000.0, duration_seconds=0.0)`. `if __name__ == "__main__": raise SystemExit(main())`. No subprocess, no shell, no network, no persistence beyond `evaluation-runs/gate/`. Byte-identical to archive `cli.py.full` (`sha256:6821a451…`). |
| `tests/unit/test_technical_grounding_gates_report.py` | Modified (appended 2E test block) | 750→931 (+181, -0) | Restored byte-faithful 2E tests from the verified archive (archive lines 753-930). 7 tests / 8 cases: `test_run_gate_returns_zero_on_pass`, `test_run_gate_returns_nonzero_on_block` (critical mismatch → block), `test_run_gate_returns_nonzero_on_escalate` (language regression → escalate), `test_run_gate_stdout_contains_only_safe_fields` (no forbidden content tokens in stdout), `test_gate_report_and_cli_import_no_forbidden_modules` (2 parametrized cases: report + cli — no http/requests/subprocess/langchain/etc.), `test_gate_cli_uses_no_subprocess_or_network` (AST-level import guard), `test_run_gate_produces_deterministic_report_across_runs` (frozen-clock byte-identical across 2 runs). Test file (931 lines) is byte-identical to archive's full `test_technical_grounding_gates_report.py.full` (930 lines) EXCEPT one added type-narrowing guard (`assert mod.__file__ is not None` at line 891, required by pyright CI gate). No new imports needed (`Any`, `Path`, `pytest`, `json` already present from 2A-2D). 2F arch tests (`test_technical_grounding_gates.py`) NOT restored — stay archived. |

**Authored line totals (excluding OpenSpec + generated evidence):**
- PR 2A: 388 total lines (report.py 141 + test 247); 317 non-blank authored lines.
- PR 2B: 190 inserted lines (189 test block + 1 separator blank); 169 non-blank authored lines.
- PR 2C: 268 changed lines (264 insertions + 4 deletions); 204 non-blank authored lines (76 production + 4 docstring/import deletions + 184 test insertions).
- PR 2D: 201 changed lines (197 insertions + 4 deletions); 172 non-blank authored lines (67 production insertions + 4 docstring deletions + 130 test insertions including 1 `import pytest` re-add).
- PR 2E: 266 authored lines (85 cli.py + 181 test insertions); 232 non-blank authored lines (68 cli.py non-blank + 164 test non-blank). The test insertions are 180 archive bytes + 1 type-narrowing guard line required by pyright.
- PR 2D and PR 2E are each under the 400-line hard maintainer threshold. No `size:exception` requested or assumed.

### Removed from the active candidate (archived, not lost)

| File | Former lines | Archive path | Later slice |
|------|------:|---|---|
| `backend/features/evaluation/gates/adapters/report.py` (:144-280) | 136 | `files/report.py.full` | 2C restored `:146-207`; `:209-280` (baseline) still archived for 2D |
| `backend/features/evaluation/gates/cli.py` | 85 | `files/cli.py.full` | 2E RESTORED (byte-identical) |
| `tests/unit/test_technical_grounding_gates_report.py` (:253-930) | 678 | `files/test_technical_grounding_gates_report.py.full` | 2B restored `:253-440`; 2C restored `:441-623`; 2D restored `:625-751`; 2E restored `:753-930` (complete) |
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

### PR 2C (merged in master at 42e0b58 — isolated slice-2c-atomic-promotion)

| Task | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR |
|------|-----------|-------|------------|-----|-------|-------------|----------|
| 3.3 (2C) | `tests/unit/test_technical_grounding_gates_report.py` | Unit | ✅ 92/92 (78 gate slice-1 + 14 harness arch) + ✅ 9/9 report (2A+2B merged at 5e4b636) | ✅ Preserved from former slice-2: the 9 `promote_` tests were RED first (module missing). Re-confirmed RED on restoration: all 9 failed with `ImportError: cannot import name 'GateReportAdapter'` against master `5e4b636` (2A+2B only) before the production block was restored | ✅ 18/18 passed (3 from 2A + 6 from 2B + 9 restored 2C) after restoring `report.py:146-207` — the adapter implements staged validation, atomic current/previous promotion, rollback, and cleanup | ✅ 9 cases: 3 staging-validation rejections (empty/malformed-json/missing-allowlist-keys — each rejects before touching committed paths), 3 atomic-promotion scenarios (first-run creates current/no-previous, replacement moves current→previous, third-run replaces old previous), 2 rollback scenarios (2nd-rename-failure restores prior current from previous, 1st-rename-failure leaves current intact), 1 staging-cleanup-on-failure — each exercises a distinct promotion/rollback code path via `_os_replace` monkeypatch seam | ✅ Re-added `from pathlib import Path` (removed by 2A isolation, required by 2C `tmp_path: Path` annotations); `ruff format` applied one boundary fix (blank line before section header + trailing-blank trim at EOF); `ruff check`/`ruff format --check`/`pyright`/`check_focused_tests.py`/`check_dependency_boundaries.py` all clean; byte-faithful restoration from revalidated archive |

### PR 2D (merged in master at 5a088ed — isolated slice-2d-baseline-validation)

| Task | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR |
|------|-----------|-------|------------|-----|-------|-------------|----------|
| 3.4 (2D) | `tests/unit/test_technical_grounding_gates_report.py` | Unit | ✅ 92/92 (78 gate slice-1 + 14 harness arch) + ✅ 18/18 report (2A+2B+2C merged at 42e0b58) | ✅ Preserved from former slice-2: the 5 `bootstrap_baseline` tests + `_write_harness_summary` helper were RED first (module missing). Re-confirmed RED on restoration: all 7 failed (5 tests + 3 parametrized = 7 total) with `ImportError: cannot import name 'bootstrap_baseline'` against master `42e0b58` (2A+2B+2C only) before the production block was restored | ✅ 25/25 passed (3 from 2A + 6 from 2B + 9 from 2C + 7 restored 2D) after restoring `report.py:209-280` — the bootstrap resolves gate-snapshot-first then harness-fallback, validating all five signals | ✅ 7 cases: 1 first-run-from-harness (exercises the harness-fallback path with no gate current), 1 later-run-from-gate (exercises the gate-snapshot-preferred path, writes a real serialized report then reads its observed_metrics), 1 no-source-raises (both gate and harness missing), 1 malformed-harness-raises (non-JSON summary.json), 3 parametrized bad-signal rejections (zero-denominator, negative-numerator, numerator-exceeds-denominator — each exercises a distinct `_signal_from_dict` validation branch) — each exercises a distinct baseline resolution/validation code path | ✅ Re-added `import pytest` (removed by 2A isolation, required by 2D `@pytest.mark.parametrize`); trimmed archive trailing blank lines (W292 at 2E boundary); `ruff check`/`ruff format --check`/`pyright`/`check_focused_tests.py`/`check_dependency_boundaries.py` all clean; `report.py` now byte-identical to archive `report.py.full`; byte-faithful restoration from revalidated archive |

### PR 2E (this batch — isolated slice-2e-gate-cli)

| Task | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR |
|------|-----------|-------|------------|-----|-------|-------------|----------|
| 3.5 (2E) | `tests/unit/test_technical_grounding_gates_report.py` | Unit | ✅ 92/92 (78 gate slice-1 + 14 harness arch) + ✅ 25/25 report (2A+2B+2C+2D merged at 5a088ed) | ✅ Preserved from former slice-2: the 7 2E tests were RED first (module missing). Re-confirmed RED on restoration: all 7 failed (5 `run_gate_*` + 2 import-guard) with `ModuleNotFoundError: No module named 'backend.features.evaluation.gates.cli'` against master `5a088ed` (2A+2B+2C+2D only) before `cli.py` was restored. 1 passed (the `report` parametrize case of `test_gate_report_and_cli_import_no_forbidden_modules`, which doesn't need `cli`) | ✅ 8/8 2E cases passed (4 `run_gate_*` + 2 parametrized import-guard + 1 AST import-guard + 1 deterministic) after restoring `cli.py` — the CLI orchestrates frozen-clock evaluation, gate decision, safe serialization, atomic promotion, safe stdout, and correct exit codes. 33/33 total (3 from 2A + 6 from 2B + 9 from 2C + 7 from 2D + 8 from 2E) | ✅ 8 cases: 1 pass-exit-0 (exercises the `decision.status == "pass" → return 0` branch), 2 block/escalate-exit-nonzero (exercises the `return 1` branch with critical-mismatch block and language-regression escalate — each produces a distinct status/reason pair), 1 safe-stdout (exercises the `sys.stdout.write` path — no forbidden content tokens, only status+reasons), 2 parametrized no-forbidden-imports (exercises the import boundary for both report and cli modules — http/requests/subprocess/langchain/etc. absent), 1 AST-level no-subprocess/network (exercises the AST import-walk guard — catches imports pyright/ruff wouldn't flag at runtime), 1 deterministic-frozen-clock (exercises byte-identical output across 2 runs with identical frozen inputs) — each exercises a distinct CLI contract | ✅ Added 1 type-narrowing guard (`assert mod.__file__ is not None` at line 891) required by the pyright CI gate (`mod.__file__` is `str | None`; `Path()` requires `StrPath`) — the test's intent and assertions are unchanged; `cli.py` byte-identical to archive `cli.py.full`; `ruff check`/`ruff format --check`/`pyright`/`check_focused_tests.py`/`check_dependency_boundaries.py` all clean; byte-faithful restoration from revalidated archive |

### Test Summary (combined)
- **Total tests written across all batches**: 162 (42 policy + 36 runner + 33 report-former + 21 arch-former + 6 report-2B + 9 report-2C + 7 report-2D + 8 report-2E)
- **PR 2A focused tests in active candidate**: 3 (serialize_gate_report core)
- **PR 2B focused tests restored**: 6 (critical-observations/forbidden/citation-ids safety proof)
- **PR 2C focused tests restored**: 9 (staging validation + atomic promotion + rollback + cleanup)
- **PR 2D focused tests restored**: 7 (baseline bootstrap: 2 source-resolution + 2 malformed/missing rejection + 3 parametrized bad-signal validation)
- **PR 2E focused tests restored**: 8 (4 run_gate exit-code/stdout + 2 parametrized import-guard + 1 AST import-guard + 1 deterministic frozen-clock)
- **PR 2A+2B+2C+2D+2E focused tests passing**: 33
- **Layers used**: Unit
- **Approval tests** (refactoring): None — no refactoring of existing code
- **Pure functions created**: 8 retained in PR 2A+2C+2D (`serialize_gate_report`, `_signal_dict`, `_metrics_dict`, `_floors_dict`, `_critical_observations`, `_validate_report_payload`, `_signal_from_dict`, `_metrics_from_dict`); `_to_gate_metrics_from_summary` reuses the slice-1 `_to_gate_metrics`; `GateReportAdapter.promote` is the atomic-promotion method (stateful by design — validates staged payload before any committed I/O); `bootstrap_baseline` is the baseline resolver (reads filesystem snapshots — stateful by design, validates all signals before returning); PR 2E adds `run_gate` (orchestrator — stateful by design, runs the full gate pipeline and promotes evidence) and `main` (CLI entry — reads `sys.argv`, resolves paths, constructs `FrozenClock`, delegates to `run_gate`)

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

### PR 2C (merged in master at 42e0b58)

| Evidence | Required value |
|---|---|
| Focused test command and exact result | `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q -k 'promote_'` → 9 passed, 9 deselected in 1.01s, exit 0 (after GREEN). RED before production restore: same command → 9 failed (ImportError: cannot import name 'GateReportAdapter'), exit non-zero. Full file: `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q` → 18 passed in 0.03s, exit 0 (3 from 2A + 6 from 2B + 9 from 2C). |
| Runtime harness command/scenario and exact result | N/A — temp-path adapter slice; no runtime boundary exists for PR 2C alone. The `GateReportAdapter.promote` operates on a caller-supplied `base_dir` (validated in tests via `tmp_path`); the CLI wiring that invokes it (`make eval-quality-gate`) belongs to later stacked slices (2E/2F). The restored tests prove staged validation, atomic current/previous promotion, rollback on rename failure, and staging cleanup against a real filesystem via the `_os_replace` monkeypatch seam. |
| Rollback boundary | Revert the 2C production block in `backend/features/evaluation/gates/adapters/report.py` (remove `_validate_report_payload`, `_os_replace`, `GateReportAdapter`, the `os`/`shutil`/`dataclass`/`Path` imports, and the `GateReportAdapter` `__all__` entry; restore the 2A-only docstring sentence). Revert the 2C test append + `Path` import in `tests/unit/test_technical_grounding_gates_report.py` (back to 436 lines). No baseline code (`:209-280`), Makefile, CLI, harness, kernel, dataset, manifest, lockfile, or dependency changes to revert — all still archived. |

### PR 2D (merged in master at 5a088ed)

| Evidence | Required value |
|---|---|
| Focused test command and exact result | `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q -k bootstrap_baseline` → 7 passed, 18 deselected in 1.03s, exit 0 (after GREEN). RED before production restore: same command → 7 failed (ImportError: cannot import name 'bootstrap_baseline'), 18 deselected, exit non-zero. Full file: `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q` → 25 passed in 0.04s, exit 0 (3 from 2A + 6 from 2B + 9 from 2C + 7 from 2D). |
| Runtime harness command/scenario and exact result | N/A — snapshot-loader slice; no runtime boundary exists for PR 2D alone. `bootstrap_baseline` reads filesystem snapshots (`gate_dir/current/report.json` or `harness_current/summary.json`) supplied by the caller (validated in tests via `tmp_path`); the CLI wiring that invokes it (`make eval-quality-gate`) belongs to later stacked slices (2E/2F). The restored tests prove gate-snapshot-preferred-then-harness-fallback resolution, malformed/missing source rejection, and all five-signal validation (int/bool/negative/zero-denominator/numerator-exceeds) against real filesystem fixtures. |
| Rollback boundary | Revert the 2D production block in `backend/features/evaluation/gates/adapters/report.py` (remove `_signal_from_dict`, `_metrics_from_dict`, `bootstrap_baseline`, the `bootstrap_baseline` `__all__` entry; restore the 2C-era "Baseline bootstrap belongs to a later stacked slice" docstring sentence). Revert the 2D test append + `import pytest` in `tests/unit/test_technical_grounding_gates_report.py` (back to 620 lines). No CLI (`cli.py`), Makefile, architecture wiring, harness, kernel, dataset, manifest, lockfile, dependency, or generated evidence changes to revert — all still archived. |

### PR 2E (this batch)

| Evidence | Required value |
|---|---|
| Focused test command and exact result | `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q -k 'run_gate_ or gate_cli or gate_report_and_cli'` → 8 passed, 25 deselected in 0.06s, exit 0 (after GREEN). RED before CLI restore: same command → 7 failed (ModuleNotFoundError: No module named 'backend.features.evaluation.gates.cli'), 1 passed, 25 deselected, exit non-zero. Full file: `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q` → 33 passed in 0.05s, exit 0 (3 from 2A + 6 from 2B + 9 from 2C + 7 from 2D + 8 from 2E). |
| Runtime harness command/scenario and exact result | `uv run --frozen python -m backend.features.evaluation.gates.cli evaluation-dataset` → exit 1 (non-zero); stdout: `gate: block\nreasons: critical_contract_mismatch`; report promoted atomically to `evaluation-runs/gate/current/report.json` (3136 bytes, 13 allowlisted keys, no forbidden content); deterministic byte-identical across 2 runs (frozen clock `FrozenClock(timestamp=1_700_000_000.0, duration_seconds=0.0)`); `previous/` created on 2nd run. **Expected release block**: the committed development fake kernel does not satisfy eval-11/12/13 critical contracts — the gate blocks fail-closed as designed. Generated `evaluation-runs/gate/` was cleaned up after verification (not a deliverable of this slice; committed gate baseline evidence remains excluded/archived). |
| Rollback boundary | Remove `backend/features/evaluation/gates/cli.py` (delete the 85-line file). Revert the 2E test append in `tests/unit/test_technical_grounding_gates_report.py` (remove lines 751-931, back to 750 lines; remove the `assert mod.__file__ is not None` guard). No Makefile, architecture wiring (`test_technical_grounding_gates.py`), committed gate baseline evidence (`gate-current-report.json`), 2F tests, harness, kernel, dataset, manifest, lockfile, or dependency changes to revert — all still archived/excluded. |

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

### PR 2C (merged in master at 42e0b58)
10. **`Path` import re-added to the test file**: PR 2A removed `from pathlib import Path` during isolation because its 3 serializer tests did not use `Path` (and `import pytest` was removed as F401). The 2C test block uses `tmp_path: Path` annotations in all 9 `promote_` test signatures and in the inner `_failing_replace`/`_always_fail` helper signatures, so `Path` is required. The archive's original full test file imported `Path` (archive line 19); re-adding it restores the original import surface, not a new dependency. This is a necessary import restoration driven by the 2C block's type annotations, consistent with the archive's own import block. Not a design deviation.
11. **`ruff format` boundary fix**: The byte-faithful 2C block restored the archive's single blank-line separator before the section header comment (archive line 437→441). `ruff format` canonicalized this to two blank lines before the module-level section (PEP 8 two-blank rule between the prior 2B function and the 2C comment+function group) and trimmed the trailing blank line at EOF (the archive's line 623 blank, which sat before the 2D block in the original full file and became a trailing blank once 2D was not restored). These are whitespace-only canonicalizations identical in kind to the PR 2B trailing-blank trim; no test or production logic was altered. Faithful to the restoration protocol.

### PR 2D (merged in master at 5a088ed)
12. **`import pytest` re-added to the test file**: PR 2A removed `import pytest` during isolation because its 3 serializer tests used bare `assert` (no `pytest.mark`), making it an F401 unused import. The 2D test block uses `@pytest.mark.parametrize` (archive line 718) for the 3 bad-signal rejection cases, so `pytest` is required. The archive's original full test file imported `pytest` (archive line 22); re-adding it restores the original import surface, not a new dependency. This is a necessary import restoration driven by the 2D block's parametrize decorator, consistent with the archive's own import block and the repo's other gate test files (`test_technical_grounding_gates_policy.py`, `test_technical_grounding_gates_runner.py` both import `pytest`). Not a design deviation.
13. **Trailing-blank trim at 2E boundary**: The byte-faithful 2D block restored the archive's test content through line 750 (the last `bootstrap_baseline` assertion). The archive had two blank lines at 751-752 before the 2E section header at 753. Since 2E was NOT restored in 2D, those trailing blanks became W292 violations. The only adjustment was trimming them — no test logic or content was altered. (PR 2E later restored the 2E block, re-introducing those two blank lines as the PEP 8 two-blank separator before the 2E section header, so the test file is now byte-identical to the archive's full 930 lines except for the 1-line type guard — see PR 2E deviation 15.) `ruff format --check` confirms the file is correctly formatted. Faithful to the restoration protocol.
14. **`report.py` now byte-identical to archive `report.py.full`**: With the 2D production block restored, `report.py` (280 lines) matches the archive's full `report.py.full` (280 lines) byte-for-byte. This means the report adapter module is now complete through the baseline bootstrap — the only remaining archived production code was `cli.py` (2E, now restored). The 2C-era docstring sentence ("Baseline bootstrap belongs to a later stacked slice and lives in this same module once that slice lands.") was removed because the baseline is now present. This is the intended end state for the 2D slice, not a deviation.

### PR 2E (this batch)
15. **Type-narrowing guard added for pyright CI gate**: The archived 2E test `test_gate_cli_uses_no_subprocess_or_network` (archive line 891) contains `tree = ast.parse(Path(mod.__file__).read_text(encoding="utf-8"))`. `mod.__file__` is typed `str | None` (per `typeshed`), and `Path()` requires `StrPath` — pyright reports `reportArgumentType` on this expression. At HEAD `5a088ed` (2D state, 750-line test file), this line did not exist, so pyright was 0 errors. The 2E restoration introduced 2 pyright errors (the full-repo `pyright` that `make ci` runs reported them), which would fail the CI gate. The minimal intent-preserving fix is adding `assert mod.__file__ is not None` immediately before the `Path()` call — this narrows the type for pyright without changing the test's behavior or assertions (if `__file__` were `None`, the test would fail anyway). This is a necessary type-safety adjustment required by the CI gate, the same category as the trailing-blank trims in prior PRs (tooling-required canonicalizations). The test file (931 lines) is byte-identical to the archive's full `test_technical_grounding_gates_report.py.full` (930 lines) EXCEPT for this 1 added line. `cli.py` (85 lines) is fully byte-identical to the archive `cli.py.full`. Not a design deviation — the test's intent (AST-level import guard against subprocess/network modules) is unchanged.
16. **Generated `evaluation-runs/gate/` cleaned up after runtime verification**: The runtime harness scenario (`uv run --frozen python -m backend.features.evaluation.gates.cli evaluation-dataset`) produced `evaluation-runs/gate/current/report.json` (3,136 bytes) and `evaluation-runs/gate/previous/` on the 2nd run. This generated evidence was used to verify the CLI's end-to-end behavior (exit 1, safe stdout, deterministic, atomic promotion) and then removed — it is NOT a deliverable of the 2E slice. The committed gate baseline evidence (`gate-current-report.json` in the archive) remains excluded per the prompt. The rollback boundary does not include generated runtime artifacts.

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

### PR 2C (merged in master at 42e0b58)
8. **Worktree environment required `--extra dev` sync, not `--all-groups`.** The fresh git worktree's `uv sync --frozen` (and `--all-groups`) did not install the `pytest`/`ruff`/`pyright` dev tooling because `dev` is a PEP 621 `[project.optional-dependencies]` extra, not a PEP 735 dependency group. The correct restore command is `uv sync --frozen --extra dev`. This is an environment-setup note for future worktree-based apply batches, not an implementation issue. The main checkout's venv already had the tooling; only the fresh worktree needed the explicit `--extra dev` flag.

### PR 2D (merged in master at 5a088ed)
9. **None.** The 2D block is a byte-faithful restoration of already-written, already-RED-proven tests and production code. The only adjustments were re-adding `import pytest` (required by the 2D parametrize decorator, removed by 2A isolation) and trimming the archive's two trailing blank lines at the 2E boundary (W292). All 7 restored tests pass against the newly-restored `bootstrap_baseline`, confirming gate-snapshot-preferred-then-harness-fallback resolution, malformed/missing source rejection, and all five-signal validation. `report.py` is now byte-identical to the archive `report.py.full`.

### PR 2E (this batch)
10. **Pyright `reportArgumentType` on `mod.__file__` (resolved).** The archived 2E test `test_gate_cli_uses_no_subprocess_or_network` passes `mod.__file__` (typed `str | None`) to `Path()`, which requires `StrPath`. At HEAD `5a088ed` (2D state) pyright was 0 errors because this line didn't exist yet; the 2E restoration introduced 2 pyright errors that would fail `make ci`. Resolved by adding a 1-line `assert mod.__file__ is not None` type-narrowing guard before the `Path()` call — the test's intent and assertions are unchanged. The former slice-2 apply-progress claimed "pyright 0 errors" for the full 930-line test file; that claim was inaccurate for the current pyright version/typeshed (the `mod.__file__: str | None` annotation is stricter now). This is a real type-safety fix, not a cosmetic adjustment. See Deviation 15 for details.

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

### PR 2C (merged in master at 42e0b58)
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

### PR 2D (merged in master at 5a088ed)
- No commits created, no pushes, no PR opened (per instructions).
- No `make ci` or `ci-pr2a` changes (verified: `git diff --name-only 42e0b58` shows only `report.py` and the report test file; Makefile untouched).
- No new dependencies (verified: `git diff -- pyproject.toml uv.lock` empty).
- No CLI/Makefile/architecture-wiring/generated-evidence changes (verified: only 2 files changed; `cli.py`, `Makefile`, architecture test `test_technical_grounding_gates.py`, generated `gate-current-report.json`, and 2E tests (`:753-930`) all remained archived — NOT restored).
- No harness/kernel/dataset/provider/embedding/database changes (verified: `git diff` on harness files empty).
- No RDD/4R, no review started, no approval claimed, no roadmap update, no archive.
- The 2 modified files pass `ruff check`, `ruff format --check`, `pyright`, `check_focused_tests.py`, and `check_dependency_boundaries.py`.
- Existing gate + harness tests (92) still pass — safety net confirmed.
- Full report test file (25) passes — 2A serializer (3) + 2B safety (6) + 2C promotion (9) + 2D baseline (7) all green together.
- Archive revalidated: all 6 archive file SHA256 hashes match the MANIFEST (`report.py.full` `03040265…`, `cli.py.full` `6821a451…`, `test_technical_grounding_gates_report.py.full` `3333bfba…`, `test_technical_grounding_gates.py.full` `7f91aa50…`, `gate-current-report.json` `3d6bab10…`, `former-slice-2-tracked.diff` `f84bdf74…`). Archive bytes intact; no later work lost or silently rewritten.
- Applied in the MAIN checkout (no worktree created); the main venv already had all tooling.

### PR 2E (this batch)
- No commits created, no pushes, no PR opened (per instructions).
- No `make ci` or `ci-pr2a` changes (verified: `git diff --name-only 5a088ed` shows only `cli.py` (new) and the report test file; Makefile untouched).
- No new dependencies (verified: `git diff -- pyproject.toml uv.lock` empty).
- No Makefile/architecture-wiring/committed-gate-baseline-evidence/2F-tests changes (verified: only 2 files changed; `Makefile`, architecture test `test_technical_grounding_gates.py`, generated/committed `gate-current-report.json`, and 2F tests all remain archived/excluded — NOT restored). Generated `evaluation-runs/gate/` from the runtime verification was cleaned up (not a deliverable).
- No harness/kernel/dataset/provider/embedding/database changes (verified: `git diff` on harness files empty).
- No RDD/4R, no review started, no approval claimed, no roadmap update, no archive.
- The 2 changed files pass `ruff check`, `ruff format --check`, `pyright` (full repo, 0 errors), `check_focused_tests.py`, and `check_dependency_boundaries.py`.
- Existing gate + harness tests (92) still pass — safety net confirmed.
- Full report test file (33) passes — 2A serializer (3) + 2B safety (6) + 2C promotion (9) + 2D baseline (7) + 2E CLI (8) all green together. Full gate suite (policy + runner + report) = 111 passed.
- Runtime harness `uv run --frozen python -m backend.features.evaluation.gates.cli evaluation-dataset` → exit 1, `gate: block / reasons: critical_contract_mismatch`, report promoted atomically (3136 bytes, 13 allowlisted keys, no forbidden content), deterministic byte-identical across 2 runs, `previous/` created on 2nd run. Generated evidence cleaned up after verification.
- Archive revalidated: all 6 archive file SHA256 hashes match the MANIFEST (`report.py.full` `03040265…`, `cli.py.full` `6821a451…`, `test_technical_grounding_gates_report.py.full` `3333bfba…`, `test_technical_grounding_gates.py.full` `7f91aa50…`, `gate-current-report.json` `3d6bab10…`, `former-slice-2-tracked.diff` `f84bdf74…`). Archive bytes intact; no later work lost or silently rewritten.
- Applied in the MAIN checkout (no worktree created); the main venv already had all tooling.

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

### PR 2C (merged in master at 42e0b58)
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

### PR 2D (merged in master at 5a088ed)
- Attempt ordinal: 6
- Expected current revision: `sha256:0140b0c961450fb5eb05690533d07a2bbcbff993aded4b4540fd667472bb5967`
- Work unit: `slice-2d-baseline-validation`
- Did NOT call `sdd-attempt begin`, `reset`, or `finish`.
- Focused test commands and outcomes:
  - RED (before production restore): `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q -k bootstrap_baseline` → 7 failed (ImportError: cannot import name 'bootstrap_baseline'), 18 deselected in 1.15s, exit non-zero — genuine RED: all 7 tests (5 tests + 3 parametrized = 7 total) reference production code that does not exist on master `42e0b58` (2A+2B+2C only).
  - GREEN (after restoring `report.py:209-280`): `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q -k bootstrap_baseline` → 7 passed, 18 deselected in 1.03s, exit 0.
  - Full file: `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q` → 25 passed in 0.04s, exit 0 (3 from 2A + 6 from 2B + 9 from 2C + 7 from 2D).
- Static checks:
  - `uv run --frozen ruff check backend/features/evaluation/gates/adapters/report.py tests/unit/test_technical_grounding_gates_report.py` → All checks passed!, exit 0
  - `uv run --frozen ruff format --check backend/features/evaluation/gates/adapters/report.py tests/unit/test_technical_grounding_gates_report.py` → 2 files already formatted, exit 0
  - `uv run --frozen pyright backend/features/evaluation/gates/adapters/report.py tests/unit/test_technical_grounding_gates_report.py` → 0 errors, 0 warnings, 0 informations, exit 0
  - `uv run --frozen python scripts/ci/check_focused_tests.py .` → no findings, exit 0
  - `uv run --frozen python scripts/ci/check_dependency_boundaries.py .` → no findings, exit 0
- Safety net: `uv run --frozen pytest tests/unit/test_technical_grounding_gates_policy.py tests/unit/test_technical_grounding_gates_runner.py tests/architecture/test_quality_evaluation_harness.py -q` → 92 passed in 0.12s, exit 0
- Runtime harness: N/A — snapshot-loader slice; `bootstrap_baseline` reads filesystem snapshots (`gate_dir/current/report.json` or `harness_current/summary.json`) supplied by the caller (tested via `tmp_path`). The CLI/Makefile wiring that invokes it belongs to later stacked slices (2E/2F). No runtime boundary exists for PR 2D alone.
- Archive revalidation: all 6 archive file SHA256 hashes re-checked and match the MANIFEST (`report.py.full` `03040265…`, `cli.py.full` `6821a451…`, `test_technical_grounding_gates_report.py.full` `3333bfba…`, `test_technical_grounding_gates.py.full` `7f91aa50…`, `gate-current-report.json` `3d6bab10…`, `former-slice-2-tracked.diff` `f84bdf74…`). Archive bytes intact.
- Changed-line count: 201 authored lines (197 insertions + 4 deletions; 67 production + 4 docstring deletions + 130 test insertions including 1 `import pytest` re-add), excluding OpenSpec + generated evidence. 172 non-blank authored lines. Under the 400-line hard maintainer threshold; no `size:exception` requested or assumed.
- Scope verification: only 2 files changed (`backend/features/evaluation/gates/adapters/report.py`, `tests/unit/test_technical_grounding_gates_report.py`). No CLI (`cli.py`), Makefile, architecture wiring (`test_technical_grounding_gates.py`), generated evidence (`gate-current-report.json`), 2E tests (`:753-930`), harness, kernel, dataset, manifest, or lockfile changes. CLI/Makefile/arch/2E-tests/generated-evidence all remained archived — NOT restored (per PR 2D boundary).
- Byte-fidelity: production block restored byte-faithful from archive `report.py:209-280`; `report.py` (280 lines) is now byte-identical to the archive `report.py.full` (280 lines). Test block restored byte-faithful from archive `:625-751`; test file (750 lines) is byte-identical to the archive's first 750 lines. Adjustments limited to: (1) re-added `import pytest` (removed by 2A isolation, required by 2D `@pytest.mark.parametrize`, present in the archive's original import block); (2) trimmed archive trailing blank lines at the 2E boundary (W292). No test or production logic altered.
- Content revision hash (PR 2D non-OpenSpec authored content): `sha256:299989764b947e52f3bfc79d83d099c93574afcab33e8a884df38468083b90a0`
- Disposition: **PASSED** — 7 restored baseline tests green (RED re-confirmed before GREEN); 2A+2B+2C tests unchanged (25 total green); static checks clean; safety net (92) green; archive integrity revalidated; line count 201 ≤ 400; no out-of-scope restoration.

### PR 2E (this batch)
- Attempt ordinal: 7
- Expected current revision: `sha256:a547400df5c788e02928a257834839da38542c1292a97bbeaa9299a6fd25d9fd`
- Work unit: `slice-2e-gate-cli`
- Did NOT call `sdd-attempt begin`, `reset`, or `finish`.
- Focused test commands and outcomes:
  - RED (before CLI restore): `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q -k 'run_gate_ or gate_cli or gate_report_and_cli'` → 7 failed (ModuleNotFoundError: No module named 'backend.features.evaluation.gates.cli'), 1 passed, 25 deselected in 0.09s, exit non-zero — genuine RED: all 7 2E tests that reference `cli` fail against master `5a088ed` (2A+2B+2C+2D only; `cli.py` does not exist). The 1 pass is the `report` parametrize case of `test_gate_report_and_cli_import_no_forbidden_modules` (doesn't need `cli`).
  - GREEN (after restoring `cli.py`): `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q -k 'run_gate_ or gate_cli or gate_report_and_cli'` → 8 passed, 25 deselected in 0.06s, exit 0.
  - Full file: `uv run --frozen pytest tests/unit/test_technical_grounding_gates_report.py -q` → 33 passed in 0.05s, exit 0 (3 from 2A + 6 from 2B + 9 from 2C + 7 from 2D + 8 from 2E).
- Static checks:
  - `uv run --frozen ruff check backend/features/evaluation/gates/cli.py tests/unit/test_technical_grounding_gates_report.py` → All checks passed!, exit 0
  - `uv run --frozen ruff format --check backend/features/evaluation/gates/cli.py tests/unit/test_technical_grounding_gates_report.py` → 2 files already formatted, exit 0
  - `uv run --frozen pyright` (full repo, as `make ci` runs) → 0 errors, 0 warnings, 0 informations, exit 0 (after adding the 1-line `assert mod.__file__ is not None` type-narrowing guard at test line 891)
  - `uv run --frozen python scripts/ci/check_focused_tests.py .` → no findings, exit 0
  - `uv run --frozen python scripts/ci/check_dependency_boundaries.py .` → no findings, exit 0
- Safety net: `uv run --frozen pytest tests/unit/test_technical_grounding_gates_policy.py tests/unit/test_technical_grounding_gates_runner.py tests/architecture/test_quality_evaluation_harness.py -q` → 92 passed in 0.12s, exit 0
- Runtime harness: `uv run --frozen python -m backend.features.evaluation.gates.cli evaluation-dataset` → exit 1 (non-zero); stdout: `gate: block\nreasons: critical_contract_mismatch`; report promoted atomically to `evaluation-runs/gate/current/report.json` (3136 bytes, 13 allowlisted keys, no forbidden content); deterministic byte-identical across 2 runs (frozen clock); `previous/` created on 2nd run. **Expected release block**: the committed development fake kernel does not satisfy eval-11/12/13 critical contracts — the gate blocks fail-closed as designed. Generated `evaluation-runs/gate/` cleaned up after verification (not a deliverable of this slice).
- Archive revalidation: all 6 archive file SHA256 hashes re-checked and match the MANIFEST (`report.py.full` `03040265…`, `cli.py.full` `6821a451…`, `test_technical_grounding_gates_report.py.full` `3333bfba…`, `test_technical_grounding_gates.py.full` `7f91aa50…`, `gate-current-report.json` `3d6bab10…`, `former-slice-2-tracked.diff` `f84bdf74…`). Archive bytes intact.
- Changed-line count: 266 authored lines (85 cli.py + 181 test insertions), excluding OpenSpec + generated evidence. 232 non-blank authored lines (68 cli.py non-blank + 164 test non-blank). Under the 400-line hard maintainer threshold; no `size:exception` requested or assumed.
- Scope verification: only 2 files changed (`backend/features/evaluation/gates/cli.py` (new), `tests/unit/test_technical_grounding_gates_report.py` (appended 2E block)). No Makefile, architecture wiring (`test_technical_grounding_gates.py`), committed gate baseline evidence (`gate-current-report.json`), 2F tests, harness, kernel, dataset, manifest, or lockfile changes. Makefile/arch/2F-tests/committed-evidence all remain archived/excluded — NOT restored (per PR 2E boundary).
- Byte-fidelity: `cli.py` (85 lines) restored byte-faithful from archive `cli.py.full` — byte-identical (`sha256:6821a451…`). Test block restored byte-faithful from archive `:753-930`; test file (931 lines) is byte-identical to archive's full `test_technical_grounding_gates_report.py.full` (930 lines) EXCEPT one added type-narrowing guard line (`assert mod.__file__ is not None` at line 891, required by the pyright CI gate). No test or production logic altered.
- Content revision hash (PR 2E non-OpenSpec authored content): `sha256:d71e2e987631e3f72149e17f766aef5a21785a1e3f6cc9409f4513aa1c3380b2`
- Disposition: **PASSED** — 8 restored 2E test cases green (RED re-confirmed before GREEN); 2A+2B+2C+2D tests unchanged (33 total green); static checks clean (incl. full-repo pyright 0 errors after type guard); safety net (92) green; runtime harness confirms safe block/exit-1/deterministic/atomic-promotion; archive integrity revalidated; line count 266 ≤ 400; no out-of-scope restoration.

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