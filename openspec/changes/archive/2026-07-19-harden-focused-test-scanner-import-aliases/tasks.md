# Tasks: Harden Focused-Test Scanner Import Aliases

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated implementation/test changed lines | 120–200 |
| Estimated OpenSpec artifact lines | tasks.md: ~45 lines; existing proposal/spec/design excluded |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR/work unit |
| Delivery strategy | ask-always |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Add bounded alias tracking with coupled scanner tests (Reqs 1–3) | PR 1 | `uv run --frozen pytest tests/architecture/test_focused_test_scanner.py` | N/A: scanner is a filesystem/AST guard; focused pytest exercises its real harness | Revert `scripts/ci/check_focused_tests.py` and `tests/architecture/test_focused_test_scanner.py` together |

## Phase 1: RED Tests / Contract Examples

- [x] 1.1 In `tests/architecture/test_focused_test_scanner.py`, add full-tuple failing cases for direct module/callable, annotated, name-chain, positional, and `name=` aliases (Req 1; Scenarios 1–2).
- [x] 1.2 Add RED cases for RHS-before-target order, unconditional invalidation, recognized `if` ambiguity, and exact `ambiguous-dynamic-import-alias` remediation (Req 2; Scenarios 4–5).
- [x] 1.3 Add RED equivalence cases for function/async/class/lambda isolation, unsupported non-grammar forms, duplicate ownership, ordering, and byte-identical repeated scans (Reqs 1–3; Scenarios 3, 6).

## Phase 2: Scanner Implementation

- [x] 2.1 In `scripts/ci/check_focused_tests.py`, add private `AliasKind` environments and source-order assignment classification for direct importlib/callable aliases, annotated assignments, name chains, and definite invalidation.
- [x] 2.2 Implement recognized `if` branch cloning/merging with stable ambiguity findings; preserve `claim()` ownership, existing diagnostic tuples, deduplication, and deterministic sorting.
- [x] 2.3 Push fresh environments for function, async-function, class, and lambda bodies while preserving definition-time traversal; keep traversal, parse/error, resource, exclusion, and exit contracts unchanged.

## Phase 3: Verification

- [x] 3.1 Run the focused scanner suite and confirm all Req 1–3 scenarios pass without changing existing canonical diagnostics.
- [x] 3.2 Run `uv run --frozen pytest` to verify collection independence and scanner regressions, then run canonical `make ci` as the submission gate.
- [x] 3.3 Review the diff for explicit non-goals: no containers, dynamic attributes, closures, interprocedural analysis, workflow/config changes, dependencies, or Actions pins.
