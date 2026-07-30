# Apply Progress: Units 1–2

Change: `add-language-and-abstention-evaluation`
Mode: Standard (`strict_tdd: false`); hybrid OpenSpec + Engram; auto-chain, stacked-to-main, PR 2.
Request: `apply-unit-2-acquire-20260730`; work unit: `unit-2-safe-kernel-observations`; native cap: 200 changed lines.
Native attempt: already active from parent; no acquire, settle, reset, branch, commit, PR, review, or agent operation performed.

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

Remaining: tasks 3.1–3.2 and 4.1–4.2.
