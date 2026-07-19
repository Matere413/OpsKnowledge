# CI Contributor Guide

Run `make ci` before submitting a change. It is the one canonical local CI gate; GitHub Actions invokes it rather than defining another pipeline.

## Quick path

1. Install the exact required `uv` version: `0.11.29`.
2. Run `make ci` from the repository root.
3. Fix every failure and rerun the complete command. Do not use a subset, selector, skipped stage, or a replacement command as a merge-gate result.

## What the gate guarantees

`Makefile` is the executable source of the ordered, fail-fast gate. The current sequence is:

| Stage | Contributor expectation |
|---|---|
| Tool version | `uv self version --short` must be exactly `0.11.29`; mismatches, suffixes, multiline output, and an unavailable executable fail. |
| Environment | `uv sync --frozen --extra dev` restores the locked development environment. The lockfile is an input to CI, not something CI refreshes. |
| Test policy | The focused-test scanner runs before quality checks and fails on findings or scan uncertainty. |
| Quality and tests | Ruff check and format check, Pyright, then the full non-focused Pytest suite run without contributor-supplied selectors. Pytest configuration excludes only the registered `ci_recipe` marker to prevent recursive Make-target tests. |
| Supply-chain checks | Dependency-boundary reconciliation, vulnerability audit, and license inventory run after Pytest. |

The gate stops at the first failed stage. A successful earlier stage never makes a later failure acceptable.

## Frozen dependencies and `uv`

Keep `uv`, manifests, and lockfiles aligned with the command contract.

- Do not change the configured `uv` version or replace `--frozen` with a resolving command as a convenience fix.
- If an approved dependency change requires a lock refresh, make that refresh part of the same bounded change and then run `make ci`.
- The gate executes `uv` through an argv-only launcher. Treat `UV` as an executable path setting, not shell syntax.

Dependency approval and production-dependency reconciliation are governed by `governance/direct-dependencies.yaml`; that record is evidence, not permission to bypass review.

## Focused-test policy

The policy prohibits focused or runtime-controlled tests outside the scanner's explicitly allowed direct grammar. Do not introduce test API aliases, dynamic test-framework imports, runtime `skip`/`xfail` controls, or mutable `pytestmark` constructs.

The scanner statically examines in-scope Python files and intentionally fails closed for malformed, unreadable, symlinked, or resource-limit-violating input. It excludes only its fixed cache and virtual-environment directories; it does not execute discovered test code.

**Current boundary:** import aliases of `importlib` and direct imports of `import_module` are rejected, but assignment aliases of `importlib.import_module` are not yet detected. Do not rely on that gap: it is the required pre-Phase-1 change `harden-focused-test-scanner-import-aliases` and must be closed before the next implementation PR.

## GitHub Actions adapter

`.github/workflows/ci.yml` is a thin, least-privilege adapter: it checks out without persisted credentials, installs and asserts the same exact `uv` version, then runs only `make ci`.

- Do not add an alternate CI command, extra failure-bypass controls, or a second quality definition to the workflow.
- Action references are pinned to full commit SHAs with release-version comments.
- The workflow's permitted shape, action pins, `uv` version, and canonical `make ci` invocation are governed by `tests/architecture/test_github_actions_workflow.py`. Update the workflow and that contract together when an approved pin-refresh change requires it.
- `refresh-github-actions-node-runtime-pins` is the independent pre-Phase-1 change for the current Actions runtime-pin warning; it is CI/platform hardening, not Phase 9 product observability.

## Reference points

| Need | Authoritative source |
|---|---|
| Ordered command behavior | `Makefile` |
| GitHub Actions adapter and pins | `.github/workflows/ci.yml` and `tests/architecture/test_github_actions_workflow.py` |
| Focused-test scanner behavior | `scripts/ci/check_focused_tests.py` and `tests/architecture/test_focused_test_scanner.py` |
| Dependency approval evidence | `governance/direct-dependencies.yaml` |
