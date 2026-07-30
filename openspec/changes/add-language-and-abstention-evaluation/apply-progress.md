# Apply Progress: Unit 1

Change: `add-language-and-abstention-evaluation`
Mode: Standard (`strict_tdd: false`); hybrid OpenSpec + Engram; PR 1 stacked-to-main.
Request: `apply-unit-1-20260729`; revision `sha256:1d03e1ccb11bc693894a0364583b8db1e4d1205507c64f1fbb24b12ba4694644`.

## Completed
- [x] 1.1 Immutable 34-case population, frozen expectations/flags, version/digest, timeout declarations, fail-closed validation.
- [x] 1.2 Expected metadata snapshot, preserved five baseline signals, `/30`, `/18`, escape metrics, focused tests.

## Changed paths and budget
`backend/features/evaluation/population.py` (created, 89 lines); `backend/features/evaluation/domain.py` (+49/-0); `backend/features/evaluation/application.py` (+34/-10); `tests/unit/test_quality_evaluation_harness.py` (+18/-0); `openspec/changes/add-language-and-abstention-evaluation/tasks.md` (1.1/1.2 checkboxes only); `openspec/changes/add-language-and-abstention-evaluation/apply-progress.md`. Implementation diff: native accounting reports 226 changed lines, under the maintainer-approved 250-line cap.

## Evidence
- Focused: `uv run --frozen pytest tests/unit/test_quality_evaluation_harness.py` → 30 passed.
- Static: targeted Ruff and Pyright → both passed.
- Runtime harness: N/A — Unit 1 has no external runtime boundary; domain/application are in-process and covered by focused tests.
- Population: version `language-abstention-v1`; digest `4c6d2364921d5941b5b66cb6374ac654e5248c9e23f4d6368d12645a10d3d1c6`; frozen smoke produced 34 cases/results and contract denominators `/30`, `/18`, `/18`.
- Evidence digest (implementation/test bytes, ordered paths): `8a3613c849dd997d0d58d8adc9b761ca3bb4523e9de05936094315cb0352452d`.
- Rollback boundary: revert only the four implementation/test paths and Unit 1 checkbox changes; later units remain untouched.

Remaining: Units 2–4 (tasks 2.1, 3.1–3.2, 4.1–4.2).
