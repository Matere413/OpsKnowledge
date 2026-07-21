# Tasks: Refresh GitHub Actions Node Runtime Pins

## Review Workload Forecast

| Field | Value |
|---|---|
| Estimated implementation lines (OpenSpec excluded) | 60–100 |
| 400-line budget risk | Low |
| Chained PRs recommended | No unless implementation exceeds 400 lines |
| Suggested split | Single bounded implementation work unit |
| Delivery strategy | ask-always |
| Chain strategy | pending until budget is exceeded |

Decision needed before apply: Yes
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|---|---|---|---|---|---|
| 1 | Remediate canonical coupling, refresh executable contract, verify and document evidence | PR 1 | `uv run --frozen pytest tests/architecture/test_github_actions_workflow.py -v` | `make ci` | Workflow and executable test only; preserve unrelated edits and receipts |

## Phase 1: Workspace Remediation and Evidence Preservation

- [x] 1.1 Mark prior Apply tasks/evidence as a superseded attempt; preserve all historical receipts and do not delete or rewrite them.
- [x] 1.2 If needed, export the canonical-spec diff as recovery evidence outside the repository; do not edit `apply-progress.md` yet. (Not needed: the preserved historical receipt records the prior diff.)
- [x] 1.3 Restore only `openspec/specs/test-harness/spec.md` to its HEAD/index state; retain `.github/workflows/ci.yml`, the executable test, and unrelated edits.

## Phase 2: RED Tests for the Revised Boundary

- [x] 2.1 Add failing path-independence mutations proving the executable test passes/fails without canonical or change-local OpenSpec files.
- [x] 2.2 Add failing drift coverage for SHA/tag/runtime, `ACTION_CONTRACTS`, Node 24, least privilege, exact uv/order, and sole `make ci`.
- [x] 2.3 Remove `CANONICAL_SPEC_PATH`, `_assert_three_source_atomicity`, canonical reads, and all three-source mutation tests from `tests/architecture/test_github_actions_workflow.py`.

## Phase 3: GREEN Implementation and Verification

- [x] 3.1 Preserve exact checkout/setup-uv SHA-plus-tag pins, `ubuntu-latest`, `persist-credentials: false`, Node 24, read-only permissions, `uv 0.11.29`, and sole `make ci` in `.github/workflows/ci.yml` and `ACTION_CONTRACTS`.
- [x] 3.2 Rerun both `git ls-remote` tag checks, immutable `action.yml` Node 24 checks, and the checksummed uv manifest verification; block on mismatch.
- [x] 3.3 Run focused pytest, then `make ci`; record exact results and fail-closed mutation coverage.

## Phase 4: Evidence Continuity and Archive Handoff

- [x] 4.1 Update `apply-progress.md` only after implementation by preserving prior evidence as a superseded attempt and appending redesigned evidence, migration receipts, rollback boundary, and review authority.

## Post-Apply Handoff

- SDD Verify checks the completed implementation against the active delta after every Apply task is complete.
- OpenSpec Archive alone promotes the approved delta into the canonical specification.
- After Archive, rerun focused pytest and `make ci` and record the post-archive results in the archive report.
