# Tasks: Bootstrap OpsKnowledge Test Harness

## Review Workload Forecast
Engram #3588 grants a size exception only to PR2B; PR2A, PR3, and PR4 have no size exception. Planning remains separate. Report staged, full-worktree, implementation/test, planning, and combined totals independently against `f505c81`.

Final staged/full snapshot against `f505c81`: +1,182/-500 = 1,682 changed lines. Implementation/test: +835/-26 = 861; planning/config: +347/-474 = 821. The staged index and worktree are identical; the prior staged/unstaged overlay discrepancy is resolved.

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: High

### Suggested Work Units
| Unit | Goal | PR | Boundary |
|---|---|---|---|
| 1 | Ordered whitelist replacement | PR2B | Child of PR2A `f505c81`; #3588 only |
| 2 | Bounded scanner and suite | PR2B | Same child; PR2B-only exception |
| 3 | Boundaries, audit, license, fail-fast | PR3 | Child of PR2B; no exception |
| 4 | Thin Actions adapter | PR4 | Child of PR3; no exception |

## Phase 1: Preserve and Migrate Before Scanning
- [x] 1.1 Preserve revised exploration, proposal, spec, design, tasks, and superseded audit history; mark the detector implementation/suite superseded and keep migration history intact.
- [x] 1.2 Before any root scan, replace `tests/architecture/test_focused_test_scanner.py` wholesale with the whitelist-derived suite; do not use the old detector suite as acceptance input.
- [x] 1.3 In `tests/ci/test_local_uv_version.py`, replace the three parametrize lambdas with named module-level helpers and the three `_FAILURE_PREFIXES[...]` decorator subscripts with named constants/direct references.

## Phase 2: Finite Global Whitelist Scanner
- [x] 2.1 Replace `scripts/ci/check_focused_tests.py` wholesale: remove `_bound_names`, resolver/value flow, and detector logic; implement global structural whitelist/default deny with exact handled-root ownership and no semantic resolution.
- [x] 2.2 Enforce only unaliased `import pytest`, session `pytest.fixture`, direct `pytest.mark.parametrize`, direct `pytestmark` ci-recipe value/singleton tuple, and direct `pytest.MonkeyPatch` annotation; reject other pytest/unittest APIs and aliases.
- [x] 2.3 Implement ownership for direct `__import__`, `importlib.import_module`, and `importlib.__import__` calls targeting literal `pytest`/`unittest`; emit `unsupported-dynamic-import`, handle descendants once, and leave ordinary strings/unrelated targets unflagged.
- [x] 2.4 Implement direct `parametrize` grammar, including literal containers and any direct `Name` in value/`ids` positions without lookup; reject lambda, call, f-string, comprehension, conditional, attribute/subscript, starred, wrapper, and unknown expressions.
- [x] 2.5 Implement incremental bounded `scandir`: count entries before metadata, keep root uncounted, allow 100,000 and reject 100,001 before classification, classify fixed exclusions, never enumerate/read excluded subtrees, and preserve unknown paths.
- [x] 2.6 Preserve lexical ordering, 10,000-file, 1 MiB/file, 64 MiB total-byte limits/order, symlink/enumeration/stat/read/decode/parse closure, safe paths, stable reason/remediation mapping, deduplication, and scanner-before-Pytest Makefile ordering.

## Phase 3: Contract Acceptance and Accounting
- [x] 3.1 Add equivalence-class tests for whitelist allowances/rejections, dynamic-import ownership, handled descendants, default-deny APIs, false-positive strings/production calls, and stable diagnostics.
- [x] 3.2 Add total-entry, excluded-entry, incremental enumeration, all file/byte boundary, error, symlink, ordering, and collection-independence tests; prove the complete included tree passes after migrations.
- [x] 3.3 Verify clean pass, PR3-boundary failure, full verification, staged/full three-way accounting, implementation/test versus planning totals, and rollback/fix-forward evidence for `f505c81`.

## Phase 4: Apply Cleanup and Fresh Review
- [x] 4.1 Clean stale current detector/resolver completion claims from `apply-progress.md` while preserving truthful completed history and superseded audit evidence.
- [x] 4.2 Stage proposal/spec/design/tasks consistently, then complete independent fresh 4R review without widening PR2B or adding PR3/PR4 exceptions.
