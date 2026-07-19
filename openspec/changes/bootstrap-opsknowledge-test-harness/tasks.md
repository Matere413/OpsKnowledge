# Tasks: Bootstrap OpsKnowledge Test Harness

## Review Workload Forecast

| Field | Value |
|---|---|
| Estimated PR3 changed lines | 350–650 |
| 800-line budget risk | Medium |
| Chained PRs recommended | Yes — existing feature-branch-chain |
| Suggested split | PR3 audit/boundary/fail-fast → PR4 Actions adapter |
| Delivery strategy | ask-always |
| Chain strategy | feature-branch-chain |

Decision needed before apply: No — resolved by Engram #3658 for PR3 only.
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: Medium

PR3 has a maintainer-approved `size:exception` (Engram #3658) for this slice only. The session review budget remains 800 changed lines. PR4 has no exception and remains out of scope.

### Suggested Work Units

| Unit | Goal | Likely PR | Boundary |
|---|---|---|---|
| 1 | Complete audit, dependency-boundary, license, and fail-fast stages | PR3 | Base = PR2B branch; #3658 exception only |
| 2 | Add least-privilege GitHub Actions adapter and static checks | PR4 | Base = PR3 branch; no exception |

## Phase 1: Completed Foundation and PR2 Slices

- [x] 1.1 Preserve proposal/spec/design history and PR1/PR2A/PR2B delivery evidence; keep Strict TDD disabled.
- [x] 1.2 Complete PR1 packaging and locked `uv` environment (`.python-version`, `pyproject.toml`, `uv.lock`, `.gitignore`).
- [x] 1.3 Complete PR2A `Makefile` version gate, frozen sync, ordered Ruff/Pyright/Pytest stages, and recipe tests.
- [x] 1.4 Complete PR2B whitelist scanner, migration, equivalence-class tests, bounded traversal tests, and PR2B verification/review evidence.

## Phase 2: PR3 Core Implementation (Complete)

- [x] 2.1 Create `scripts/ci/check_dependency_boundaries.py` with the reviewed distribution map, production-manifest/governance reconciliation, and explicit non-importable exclusions; fail on map gaps.
- [x] 2.2 Scan first-party imports and literal dynamic imports, resolve approved aliases, and emit safe `path:line:canonical-distribution` findings without changing governance.
- [x] 2.3 Create `scripts/ci/run_vulnerability_audit.py` with one bounded `pip-audit` call, stable success/finding/unavailable/tool-failure classifications, and unchanged-rerun recovery only.
- [x] 2.4 Extend `Makefile` after Pytest with dependency-boundary, audit, and `license-inventory` stages; preserve output and stop on first failure.

## Phase 3: PR3 Verification (Complete)

- [x] 3.1 Add `tests/architecture/test_dependency_boundaries.py` for direct, chained aliases, dynamic, excluded, invalid-root, symlink, map, and governance cases, including empty/whitespace risk-level rejection.
- [x] 3.2 Add `tests/unit/test_audit_wrapper.py` for all classifications, argv-safe configured-UV execution, output/exit propagation, and recovery rerun.
- [x] 3.3 Extend `tests/ci/test_local_uv_version.py` with PR3-stage fail-fast sentinels; verify final `make ci` exits zero.

## Phase 4: PR4 Workflow Adapter (Complete)

- [x] 4.1 Create `.github/workflows/ci.yml` with pinned `astral-sh/setup-uv` SHA, read-only permissions, credential-free checkout, exact `uv self version --short`, and one `make ci` step.
- [x] 4.2 Add static workflow tests under `tests/architecture/` and re-fetch/re-verify the setup-uv SHA at apply time; record evidence in the final verification report.
