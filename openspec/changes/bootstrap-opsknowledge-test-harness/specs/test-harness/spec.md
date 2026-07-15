# Delta for test-harness

## ADDED Requirements

### Requirement: Locked Python Development Environment

`pyproject.toml` MUST require `>=3.12,<3.13`, have empty dependencies, and use a locked `dev` extra; `.python-version` MUST pin `3.12`. Before frozen sync or any quality gate, local `make ci` MUST accept only `uv --version` output exactly equal to `uv 0.11.29`; it MUST then use frozen sync and `uv run --frozen`. On a local version mismatch, it MUST exit non-zero without running a gate and print exactly this two-line template, replacing `<actual>` with the captured version output (or `unavailable`):

```text
ERROR: uv version mismatch; expected 0.11.29, found <actual>.
Remediation: install uv 0.11.29 and rerun make ci.
```

#### Scenario: Locked tool execution

- GIVEN committed lockfile
- WHEN `make ci` runs
- THEN tools use uv-managed environment
- AND stale/incompatible locks exit non-zero

#### Scenario: Local uv version mismatch fails before the gate

- GIVEN local `uv --version` returns a value other than `uv 0.11.29`
- WHEN `make ci` runs
- THEN it emits the prescribed mismatch template with the captured value
- AND it exits non-zero before frozen sync or any quality stage

### Requirement: Deterministic CI Runner Bootstrap

After checkout, use `astral-sh/setup-uv@d4b2f3b6ecc6e67c4457f6d3e41ec42d3d0fcb86 # v5.4.2` with `version: "0.11.29"`, then assert `uv --version` is exactly `uv 0.11.29` before `make ci`. GitHub Actions and local `make ci` MUST enforce the same version equality; the workflow assertion is a prerequisite and `make ci` repeats the local gate. Apply MUST re-verify the SHA or block.

#### Scenario: Clean runner has the selected uv

- GIVEN a clean runner
- WHEN the workflow runs after checkout
- THEN setup installs `0.11.29` and assertion precedes `make ci`
- AND a version mismatch exits non-zero without invoking `make ci`

### Requirement: Ordered, Fail-Closed Quality Gate

`make ci` MUST execute frozen sync, focused guard, Ruff check/format, Pyright, Pytest, audit, then license inventory, stopping at first failure. Findings/tool-service errors MUST fail closed; no retry/suppression/allowlist MAY conceal them. The wrapper MUST preserve output, classify cause, recover only by unchanged re-run.

#### Scenario: Isolated fail-fast proof

- GIVEN recording sentinels in a copied recipe
- WHEN an earlier stage fails
- THEN the log ends there and no later sentinel runs

#### Scenario: Deterministic audit wrapper outcomes

- GIVEN stubs for success, finding, timeout, unavailable service, tool failure
- WHEN the wrapper is tested for each result
- THEN classifications are `success`, `vulnerability_finding`, `vulnerability_service_unavailable`, or `vulnerability_tool_failure`
- AND non-success exits non-zero after one call; rerun proves recovery

### Requirement: Collection-Independent Focused-Test Prohibition

Before Pytest, `make ci` MUST run standalone AST guard over `tests/**/*.py`. It MUST reject skip, skipif, xfail, `.only`, focus forms, aliases; allowlist empty, collection-independent.

#### Scenario: Skipped test cannot bypass the guard

- GIVEN a test uses an aliased prohibited construct
- WHEN `make ci` runs
- THEN the guard fails before Pytest and names file/construct

### Requirement: Production and Test-Tree Dependency Boundaries

Checks MUST reconcile production dependencies with governance, not dev tools. Their reviewed map MUST inspect `langchain` → `langchain`, `llamaindex` → `llama_index`, `redis` → `redis`, `kubernetes` → `kubernetes`; `streaming`, `visualinterpretation`, `email`, `notifier`, `reranking`, `queues`, `microservices` MUST be non-importable declaration exclusions. Map gaps/unresolved aliases MUST fail visibly. Imports MUST name path/dependency; governance unmodified.

#### Scenario: Normalized excluded test import fails

- GIVEN a test imports `llama_index` directly or through a tracked alias
- WHEN architecture checks run
- THEN it names test file and canonical `llamaindex`

#### Scenario: Map or alias cannot bypass review

- GIVEN an excluded policy entry lacks a reviewed map classification or an excluded alias cannot resolve
- WHEN architecture checks initialize or scan
- THEN they fail non-zero, naming it for review

### Requirement: Least-Privilege GitHub Actions Delegation

The workflow MUST use only unprivileged `push`/`pull_request`, read-only `contents`, credential-free checkout; never `pull_request_target`, secrets, or write tokens. Third-party actions MUST use immutable SHA/version comments; no SHA may be invented.

#### Scenario: Workflow boundary review

- GIVEN the workflow is inspected
- WHEN its events, permissions, checkout, and references are evaluated
- THEN it has the required read-only boundary and verified SHA/version comments

### Requirement: License Inventory Is Evidence, Not Compatibility Approval

The gate MUST run `uv run --frozen pip-licenses --from=expression --format=json`, retain output, and make no policy claim.

#### Scenario: Inventory remains non-policy

- GIVEN the license stage succeeds
- WHEN its configuration is reviewed
- THEN it has no compatibility suppression or fabricated approval

### Requirement: Bootstrap Scope and Strict TDD

The harness MUST pass without application source and MUST NOT add runtime, production, or excluded dependencies. Strict TDD stays `false` until a runtime change re-evaluates it.

#### Scenario: Empty source tree passes

- GIVEN no application source exists
- WHEN `make ci` runs
- THEN it exits zero when all checks pass and Strict TDD remains disabled
