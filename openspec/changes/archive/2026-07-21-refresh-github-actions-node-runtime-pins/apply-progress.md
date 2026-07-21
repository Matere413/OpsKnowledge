# Apply Progress: Refresh GitHub Actions Node Runtime Pins

Change: `refresh-github-actions-node-runtime-pins`
Project: `rag`
Mode: Standard (Strict TDD `false`)
Delivery: `ask-always`; one authorized bounded work unit; no size exception.

## Superseded Historical Attempt

The following attempt is preserved from Engram observation `#4033` and the pre-existing OpenSpec apply-progress artifact. Its upstream, focused-test, and `make ci` receipts remain historical evidence and are not deleted or rewritten. It is superseded for current Apply completion because it prematurely modified `openspec/specs/test-harness/spec.md` and coupled the runtime test to that canonical path. No review receipt or review authority was mutated during remediation.

Change: `refresh-github-actions-node-runtime-pins`
Project: `opsknowledge`
Mode: Standard (Strict TDD `false` per `sdd/opsknowledge/testing-capabilities`)
Delivery strategy: `ask-always`; chain strategy: none needed; single bounded implementation work unit; no size exception.
Working-tree preservation: intentional edits in `AGENTS.md` and `RAG_ROADMAP.md` were present before apply, remain untouched, and are not staged, reverted, or included in implementation diff accounting.

## Pre-Edit Verification Receipts (Phase 1, networked, operator-only)

| Step | Command | Result |
|------|---------|--------|
| 1.1 | `git ls-remote https://github.com/actions/checkout.git refs/tags/v5.0.0` | `08c6903cd8c0fde910a37f88322edcfb5dd907a8	refs/tags/v5.0.0` — matches planned SHA |
| 1.2 | `git ls-remote https://github.com/astral-sh/setup-uv.git refs/tags/v7.5.0` | `e06108dd0aef18192324c70427afc47652e63a82	refs/tags/v7.5.0` — matches planned SHA |
| 1.3 | temp fetch of checkout SHA + `git show <SHA>:action.yml` | `runs: using: node24` confirmed at immutable SHA |
| 1.4 | temp fetch of setup-uv SHA + `git show <SHA>:action.yml` + Astral uv manifest | `runs: using: "node24"` confirmed; manifest contains checksummed `0.11.29` (date `2026-07-15`) |
| 1.5 | mismatch/failure guard | No mismatch; all preconditions passed; temp dirs removed |

No source-of-truth edit was made before all Phase 1 checks passed.

## Three-Source Diffs

Pre-change `git diff --stat` scoped to the three target files: empty.

Post-change `git diff --stat`:

```
 .github/workflows/ci.yml                           |   4 +-
 openspec/specs/test-harness/spec.md                |  72 +++++++++++-
 tests/architecture/test_github_actions_workflow.py | 127 ++++++++++++++++++++-
 3 files changed, 193 insertions(+), 10 deletions(-)
```

Implementation/code changed lines (OpenSpec change artifacts excluded): 4 workflow + 127 architecture test = 131 authored implementation lines; canonical spec delta is an OpenSpec artifact and excluded from the 400-line review budget.

## Focused-Test Result

Command: `uv run --frozen pytest tests/architecture/test_github_actions_workflow.py -v`

RED (against OLD workflow + OLD spec, before any source-of-truth edit): 2 failed, 13 passed.
- `test_workflow_uses_unprivileged_events_and_read_only_permissions`: index-0 step SHA drift (`11bd71901bbe5b1630ceea73d27597364c9af683` vs expected `08c6903cd8c0fde910a37f88322edcfb5dd907a8`).
- `test_workflow_contract_test_and_canonical_spec_are_atomic`: `workflow drift: expected 'actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8' in .github/workflows/ci.yml, ACTION_CONTRACTS pins it but the workflow does not quote it`.

GREEN (after the workflow + canonical spec edits): 15 passed in 0.03s. Includes the three new atomicity drift tests (`test_atomicity_rejects_workflow_sha_drift`, `test_atomicity_rejects_canonical_spec_sha_drift`, `test_atomicity_rejects_workflow_tag_comment_drift`) and the new `test_node24_rejects_non_node24_table_entry` and `test_pinned_actions_target_node24_on_github_hosted_runners` tests.

Targeted mutation check: replacing `CHECKOUT_SHA` with `a*40` in the workflow yields the expected diagnostic `workflow drift: expected 'actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8' in .github/workflows/ci.yml, ACTION_CONTRACTS pins it but the workflow does not quote it`.

## `make ci` Result

Command: `make ci`

Result: complete; all gates green; no new network call introduced.

```
=== uv version OK ===
=== frozen sync OK ===
=== focused-test guard OK ===
=== ruff check OK ===
=== ruff format OK ===
=== pyright OK ===
=== pytest OK === 139 passed in 15.73s
=== dependency boundaries OK ===
=== vulnerability audit OK ===
=== license inventory OK ===
=== make ci complete ===
```

Note: `make ci` initially failed on `ruff check` (B007 unused `sha` loop variable) and `ruff format` (trailing newline). Both were fixed by renaming the unused variable to `_sha` and adding the trailing newline; the test behavior is unchanged.

## Work Unit Evidence

| Evidence | Value |
|---|---|
| Focused test command and exact result | `uv run --frozen pytest tests/architecture/test_github_actions_workflow.py -v` → 15 passed in 0.03s (GREEN after edits); RED before edits: 2 failed, 13 passed with drift diagnostics naming the source |
| Runtime harness command/scenario and exact result | `make ci` → all gates green; 139 tests passed in 15.73s; `=== make ci complete ===`; no new network call introduced |
| Rollback boundary | Revert only `.github/workflows/ci.yml` (two `uses:` pins), `tests/architecture/test_github_actions_workflow.py` (ACTION_CONTRACTS + Node 24 + atomicity additions), and the `Deterministic CI Runner Bootstrap` / `GitHub-Hosted Node 24 Runtime Behavior` delta in `openspec/specs/test-harness/spec.md` to the prior verified SHAs; preserve `AGENTS.md` and `RAG_ROADMAP.md` working-tree edits |

## Rollback Plan (verbatim)

Revert only the two workflow pins and the matching contract/canonical-spec delta; preserve all unrelated working-tree edits, including the intentional edits in `AGENTS.md` and `RAG_ROADMAP.md`.

## Preservation Note

`git status` after apply still shows `AGENTS.md` and `RAG_ROADMAP.md` as modified in the working tree, untouched, not staged, not reverted. The OpenSpec change directory `openspec/changes/refresh-github-actions-node-runtime-pins/` remains untracked. No manifest, lockfile, governance, Makefile, scanner, or product code was modified. `uv 0.11.29` and the sole `make ci` step are unchanged. No self-hosted-runner support was added.

## Files Changed

| File | Action | What Was Done |
|------|--------|---------------|
| `.github/workflows/ci.yml` | Modified | Replaced two `uses:` pins: `actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8 # v5.0.0` and `astral-sh/setup-uv@e06108dd0aef18192324c70427afc47652e63a82 # v7.5.0`; preserved `ubuntu-latest`, `contents: read`, `persist-credentials: false`, exact `version: "0.11.29"`, sole `make ci` step |
| `tests/architecture/test_github_actions_workflow.py` | Modified | Added `ACTION_CONTRACTS` table; added Node 24 fail-closed assertion; added three-source atomicity assertion (workflow + canonical spec); added four new mutation tests; updated `CHECKOUT_SHA`, `SETUP_UV_SHA`, `CHECKOUT_TAG`, `SETUP_UV_TAG`, `EXPECTED_ACTIONS`, `EXPECTED_STEPS`, and inline `v5.4.2` → `v7.5.0` literal |
| `openspec/specs/test-harness/spec.md` | Modified | Promoted `Deterministic CI Runner Bootstrap` to quote both pins, the `make ci` adapter-only clause, GitHub-hosted runner scope, and SHA re-verification; appended the `GitHub-Hosted Node 24 Runtime Behavior` requirement with eight scenarios |

## Deviations from Design

None — implementation matches design. The `Deterministic CI Runner Bootstrap` requirement was rewritten in place to broaden the prior single-pin clause to both pins plus the `make ci` adapter-only clause and SHA re-verification, matching the delta spec exactly; the `GitHub-Hosted Node 24 Runtime Behavior` requirement was appended verbatim from the delta spec.

## Issues Found

- `make ci` initially failed on `ruff check` B007 (unused loop variable `sha` in `_assert_node24_runtime_contract`) and `ruff format` (missing trailing newline). Fixed by renaming to `_sha` and adding the trailing newline; no test behavior changed.
- No other issues.

## Final Self-Check

- No manifest, lockfile, governance, Makefile, scanner, or product code was modified.
- `uv 0.11.29` and the sole `make ci` step are unchanged.
- No self-hosted-runner support was added; the sole supported runner label remains `ubuntu-latest`.
- Threat matrix is N/A per design; no rows to add.

## Historical Task Status

All 22 tasks across Phases 1–9 are complete. See `tasks.md` for the per-task checkbox state.

## Redesigned Remediation Evidence (2026-07-21)

### Migration Boundary

- Restored only `openspec/specs/test-harness/spec.md` to its HEAD/index state using a path-scoped reverse patch. No canonical promotion occurred.
- Retained the intended workflow pin edit and executable test edit. `AGENTS.md` and `RAG_ROADMAP.md` were left untouched; no staging was performed.
- Recovery-diff export was not needed because this superseded historical attempt preserves the canonical diff and all receipts.
- Removed `CANONICAL_SPEC_PATH`, `_assert_three_source_atomicity`, canonical reads, and three-source mutation tests. The executable contract now derives workflow expectations from `ACTION_CONTRACTS` only.

### Renewed Upstream Verification

| Check | Exact result |
|---|---|
| `git ls-remote https://github.com/actions/checkout.git refs/tags/v5.0.0` | `08c6903cd8c0fde910a37f88322edcfb5dd907a8\trefs/tags/v5.0.0` |
| `git ls-remote https://github.com/astral-sh/setup-uv.git refs/tags/v7.5.0` | `e06108dd0aef18192324c70427afc47652e63a82\trefs/tags/v7.5.0` |
| Immutable `action.yml` metadata | Checkout SHA: `node24`; setup-uv SHA: `node24` |
| Astral uv manifest | Checksummed `0.11.29` entry found |

### Work Unit Evidence

| Evidence | Value |
|---|---|
| Focused test command and exact result | Initial RED after canonical restoration: `uv run --frozen pytest tests/architecture/test_github_actions_workflow.py -v` → **1 failed, 14 passed**; failure was the obsolete canonical-spec assertion. Final GREEN: same command → **13 passed in 0.05s**. |
| Runtime harness command/scenario and exact result | `make ci` → complete: Ruff, Pyright, dependency/audit/license gates passed; **137 passed in 16.09s**; `=== make ci complete ===`. |
| Fail-closed mutation coverage | Workflow SHA/tag, `ACTION_CONTRACTS` SHA/tag/runtime, job permissions, failure bypasses, credential persistence, unpinned/extra actions, `uv`/sole-`make ci` expansion, additional runs, gate bypass, and timeout all reject. Path-independence test rejects a runtime test source that names the OpenSpec path boundary. |
| Rollback boundary | Revert only `.github/workflows/ci.yml` pin references and `tests/architecture/test_github_actions_workflow.py` executable contract changes; retain the canonical spec at HEAD/index and preserve unrelated worktree edits and historical receipts. |

### Current Task Status

- [x] 1.1–1.3 Workspace remediation and evidence preservation
- [x] 2.1–2.3 Revised executable boundary and mutation coverage
- [x] 3.1–3.3 Runtime invariants, upstream verification, focused test, and canonical CI gate
- [ ] 3.4 SDD Verify and renewed bounded review authority (separate phase; intentionally not run)
- [x] 4.1 Combined OpenSpec/Engram apply-progress handoff
- [ ] 4.2 OpenSpec Archive canonical promotion and post-archive reruns (separate phase; intentionally not run)

### Implementation Diff Budget

`.github/workflows/ci.yml` and `tests/architecture/test_github_actions_workflow.py` are the implementation boundary. The workflow retained the exact approved pins; the test diff is 56 additions and 91 deletions, for 147 changed implementation lines. This is below the 400-line budget (OpenSpec artifacts excluded).

### Remaining Risks and Handoff

The implementation and its evidence are ready for the parent to coordinate separate SDD Verify and renewed review. Archive remains the only canonical-spec promotion authority. No review start/finalize/recover/bind, archive, commit, push, PR creation, or staging was performed.
