# Apply Progress: Units 1–4

Change: `add-language-and-abstention-evaluation`
Mode: Standard (`strict_tdd: false`); hybrid OpenSpec + Engram; ask-on-risk, stacked-to-main, PR 4.
Request: `unit-4-apply-20260730-0408`; work unit: `unit-4-opt-in-cli-boundary-proof`; native cap: 400 changed lines.
Native attempt: parent-provided acquire is active; no acquire, settle, reset, branch, commit, PR, review, or agent operation performed.

## SDD Result Contract
status: success
executive_summary: >-
  Unit 4 tasks 4.1–4.2 are complete. The opt-in CLI promotes the complete
  reviewed three-file bundle with deterministic lineage, safe evidence, and
  rollback-preserving history.
artifacts:
  - `openspec/changes/add-language-and-abstention-evaluation/apply-progress.md`
  - `engram://opsknowledge/observation/4957`
  - `sdd/add-language-and-abstention-evaluation/apply-progress`
next_recommended: sdd-verify
risks:
  - Parent-owned runtime settlement and evidence revision remain pending.
  - Authored accounting is 261 additions+deletions under the 400-line cap;
    generated evaluation evidence is excluded from authored review accounting.
skill_resolution: Standard mode (`strict_tdd: false`); `sdd-apply`,
  `python-backend-mastery`, and `work-unit-commits` loaded; strict-TDD module
  not active.

## Completed
- [x] 1.1 Immutable 34-case population, frozen expectations/flags, version/digest, timeout declarations, fail-closed validation.
- [x] 1.2 Expected metadata snapshot, preserved five baseline signals, `/30`, `/18`, escape metrics, focused tests.
- [x] 2.1 Nullable evidence-observed routed language, typed in-memory provider failures, and focused kernel coverage.

## Unit 1 history (preserved)
Unit 1 changed `population.py`, evaluation `domain.py`/`application.py`, and harness tests; its recorded native accounting was 226 changed lines under the approved 250-line cap. Focused pytest passed 30 tests; targeted Ruff and Pyright passed with zero diagnostics. Runtime harness was N/A because Unit 1 had no external boundary. Population: `language-abstention-v1`, digest `4c6d2364921d5941b5b66cb6374ac654e5248c9e23f4d6368d12645a10d3d1c6`; evidence digest `8a3613c849dd997d0d58d8adc9b761ca3bb4523e9de05936094315cb0352452d`. Rollback left later units untouched.

## Unit 2 changed paths and budget
- `backend/features/query/application.py` — carries nullable `routed_language`, observed only from a single-language evidence set, including typed provider-failure responses.
- `backend/shared/ports.py` — adds nullable routed-language state to the safe response surface.
- `backend/features/evaluation/adapters/kernel.py` — consumes application-observed language and never falls back to case input.
- `backend/features/evaluation/domain.py` — makes `CaseResult.language` nullable to match the safe contract.
- `tests/unit/test_quality_evaluation_harness.py` — proves nullable no-evidence behavior, evidence observation, language isolation, and typed failure outcomes.
- `openspec/changes/add-language-and-abstention-evaluation/tasks.md` — only task 2.1 checkbox changed.

Native working-tree diff including the two SDD artifacts: 152 additions+deletions; implementation/test subset: 112. Both are under the 200-line native slice cap. No Unit 3–4 paths changed.

## Unit 2 Work Unit Evidence
- Focused: `uv run --frozen pytest tests/unit/test_quality_evaluation_harness.py -k 'language or failure'` → 10 passed, 21 deselected.
- Ruff: targeted `uv run --frozen ruff check` → passed.
- Pyright: targeted `uv run --frozen pyright` → 0 errors, 0 warnings, 0 informations.
- Runtime harness: N/A — this slice has only an in-process kernel boundary; no integration or external provider harness exists.
- Rollback boundary: revert the Unit 2 hunks in the four implementation paths and harness tests; restore only `CaseResult.language` to non-nullable while preserving Unit 1 metric/population hunks, and revert only the 2.1 checkbox/progress artifact.
- Evidence digest (ordered implementation/test bytes): `sha256:be5ed7712b08810e1e3b0571b0c73e8a58cf4902e112230ae38facfc33361f54`.

## Unit 3 Work Unit Evidence
- [x] 3.1 Safe allowlists, sorted canonical reports, shared run identity, and protected-content exclusion.
- [x] 3.2 Three-file staging, immutable `history/{run_id}/` snapshots, atomic backup restoration, and failure recovery.
- Changed paths: `backend/features/evaluation/adapters/report.py`, `tests/unit/test_quality_evaluation_harness.py`, this progress file, and task checkboxes only.
- Focused: `uv run --frozen pytest tests/unit/test_quality_evaluation_harness.py -k 'summary or records or human or promotion or report or history or rollback'` → 4 passed, 27 deselected; `uv run --frozen ruff check backend/features/evaluation/adapters/report.py tests/unit/test_quality_evaluation_harness.py` → passed; `uv run --frozen pyright backend/features/evaluation/adapters/report.py tests/unit/test_quality_evaluation_harness.py` → 0 errors, 0 warnings, 0 informations.
- Runtime harness: N/A — no external boundary exists; in-process smoke `uv run --frozen python -c '<three-file promotion>'` → passed. CLI wiring/runtime promotion belongs to Unit 4.
- Rollback boundary: revert the Unit 3 hunks in `report.py` and its focused tests plus only the 3.1/3.2 checkboxes/progress section; preserve Units 1–2 and `evaluation-runs/current/`.
- Native changed-line estimate: 250 additions+deletions including SDD artifacts (227 implementation/test); evidence digest: `sha256:b1324c43f1cb03dcf40c0b2824b033bc81285fefe19f7515e1ca3ba75835d0d6`.

Unit 3 handoff remaining: tasks 4.1–4.2.

## Unit 4 Work Unit Evidence
- [x] 4.1 Reviewed opt-in CLI promotion now sends the complete `summary.json`, `records.jsonl`, and `report.txt` bundle through `ReportAdapter`; direct writes to `current/` were removed. Run identity and summary lineage include the reviewed population, replacement label, manifest digest, mapping digest, frozen timestamp, and frozen duration.
- [x] 4.2 Added behavior-first CLI, deterministic-safety, manifest/mapping-authority, complete-bundle rollback, and unchanged CI/gate-boundary proof.
- Changed paths: `backend/features/evaluation/cli.py`, `backend/features/evaluation/application.py`, `backend/features/evaluation/domain.py`, `backend/features/evaluation/population.py`, `tests/unit/test_quality_evaluation_harness.py`, `tests/architecture/test_quality_evaluation_harness.py`, `evaluation-runs/current/`, `evaluation-runs/previous/`, `evaluation-runs/history/`, this progress file, and task checkboxes only. No Makefile, gate implementation, dataset, or mapping authority bytes changed.
- Focused behavior-first RED: `uv run --frozen pytest tests/unit/test_quality_evaluation_harness.py -k 'cli or history_rollback'` initially reported 2 failed, 1 passed, 31 deselected against the pre-Unit-4 implementation. GREEN after implementation: the same command reported 3 passed, 31 deselected.
- Focused tests: `uv run --frozen pytest tests/unit/test_quality_evaluation_harness.py tests/architecture/test_quality_evaluation_harness.py tests/architecture/test_evaluation_dataset_ci_order.py` → 62 passed, exit 0.
- Runtime harness: `make eval-quality` → exit 0; frozen run ID `61fc720912802afd4c91c8812feb3e8c06c2c008e53c74d464a31e09624274c0`; current contains all three files, previous retains the former 34-case baseline, and `history/61fc720912802afd4c91c8812feb3e8c06c2c008e53c74d464a31e09624274c0/{current,staged}` retains both snapshots. No external provider, database, HTTP, or runtime query state was used.
- Runtime output: baseline signals `10/34`, `0/4`, `20/34`, `9/34`, `2/2`; contract metrics `7/18`, `18/30`, `7/18` in deterministic report order. This is measurement evidence only; no thresholds or CI semantics changed.
- Changed-line accounting: `261` authored additions+deletions excluding generated evaluation evidence, below the 400-line native cap. The complete working-tree snapshot delta is `495` lines, including `234` generated `evaluation-runs/` additions+deletions; generated evidence is excluded from authored review accounting.
- Rollback boundary: revert the Unit-4 hunks in `cli.py`, the lineage fields/identity inputs in `application.py`/`domain.py`/`population.py`, the two Unit-4 test sections, the replacement `evaluation-runs/` bundle/history, and only the 4.1/4.2 task/progress updates. Preserve Units 1–3 implementation, prior evidence, gate files, dataset, mapping, and Makefile.
- Diagnosis: the CLI previously promoted only `summary.json` and then wrote `records.jsonl`/`report.txt` directly, bypassing three-file validation and history rotation; `RunSummary` also left lineage fields unset. The bounded fix routes one complete bundle through the reviewed adapter and carries immutable lineage metadata into the report.
- Harness disposition: PASS. The real opt-in command completed successfully; the architecture boundary tests prove `make ci`, `ci-pr2a`, and `eval-quality-gate` remain unchanged/outside the opt-in target. No integration or E2E layer exists for this in-process development harness.
- Cleanup evidence: no `.staging-*` or `.previous-backup-*` directories remain after promotion; the immutable history directory remains intentionally retained.
- Process evidence: the executor did not acquire, reset, finish, settle, or otherwise mutate native runtime authority; the parent-owned token/request/objective remained untouched. No commit, branch, PR, native review, or agent launch was performed.
- Evidence revision: not exposed to the executor; parent-owned runtime settlement remains pending. Evidence digest (ordered changed Python implementation/test bytes: `cli.py`, `application.py`, `domain.py`, `population.py`, architecture test, unit test): `sha256:aa55427b44a1f6bde49b5a84de7dbdc73845b30e64b60fa8b116b2853680a006`.

Remaining: none for Unit 4; verification/settlement remains parent-owned.
