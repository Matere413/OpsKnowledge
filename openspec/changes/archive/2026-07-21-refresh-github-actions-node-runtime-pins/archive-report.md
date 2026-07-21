# Archive Report: Refresh GitHub Actions Node Runtime Pins

**Change**: `refresh-github-actions-node-runtime-pins`
**Date**: 2026-07-21
**Mode**: hybrid
**Status**: success

## Summary

Recovered a partially completed archive, confirmed the canonical `test-harness` spec already reflected the approved delta, and completed the missing archive trail in the existing archive directory without moving files again.

## Recovery Notes

- Archive relocation had already occurred before recovery.
- Canonical spec was synchronized at `openspec/specs/test-harness/spec.md` and matched the approved delta.
- Historical receipts, review lineage, and verification evidence were preserved.

## Source of Truth Updated

- `openspec/specs/test-harness/spec.md`

## Verification

| Command | Result |
|---|---|
| `uv run --frozen pytest tests/architecture/test_github_actions_workflow.py -v` | 13 passed in 0.08s; exit 0 |
| `make ci` | complete; all gates green; `137 passed in 27.91s`; exit 0 |

## Traceability

### Bound review lineage

- `review-c9b0c27988bd2d6c`

### Engram observations

- `#4106` — tasks mirror, reconciled to 10/10
- `#4109` — apply-progress
- `#4114` — verify-report

## Files

- `openspec/specs/test-harness/spec.md` — canonical spec promotion already present and retained
- `openspec/changes/archive/2026-07-21-refresh-github-actions-node-runtime-pins/` — existing archive directory completed with this report

## Notes

- No commit, push, PR, or review lifecycle action was started or finalized.
- Unrelated working-tree edits were preserved.
