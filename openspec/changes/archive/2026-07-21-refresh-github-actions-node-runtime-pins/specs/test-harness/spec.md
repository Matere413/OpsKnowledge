# Delta for test-harness

## MODIFIED Requirements

### Requirement: Deterministic CI Runner Bootstrap

After checkout, use `astral-sh/setup-uv@e06108dd0aef18192324c70427afc47652e63a82 # v7.5.0` with `version: "0.11.29"`, then assert `uv self version --short` is exactly `0.11.29` before `make ci`. The pinned `actions/checkout` MUST be `actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8 # v5.0.0` with `persist-credentials: false`. GitHub Actions and local `make ci` MUST enforce the same executable-version equality; the workflow assertion is a prerequisite and `make ci` repeats the local gate. Apply MUST re-verify both SHAs with `git ls-remote` against the named tags (`refs/tags/v5.0.0` and `refs/tags/v7.5.0`) or block. The contract is the sole `make ci` adapter for GitHub-hosted `ubuntu-latest` runners; self-hosted runners are out of scope and receive no support guarantee.
(Previously: pinned `astral-sh/setup-uv@d4b2f3b6ecc6e67c4457f6d3e41ec42d3d0fcb86 # v5.4.2` with `version: "0.11.29"`, asserted `uv self version --short` is exactly `0.11.29` before `make ci`, and applied SHA re-verification only against the single `setup-uv` tag.)

#### Scenario: Clean runner has the selected uv

- GIVEN a clean GitHub-hosted `ubuntu-latest` runner
- WHEN the workflow runs after checkout
- THEN `actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8 # v5.0.0` checks out with `persist-credentials: false`
- AND `astral-sh/setup-uv@e06108dd0aef18192324c70427afc47652e63a82 # v7.5.0` installs `0.11.29`
- AND the exact-version assertion precedes `make ci`
- AND a version mismatch exits non-zero without invoking `make ci`

#### Scenario: Workflow and executable contract remain consistent

- GIVEN the workflow and `tests/architecture/test_github_actions_workflow.py` contain the approved pin and runner invariants
- WHEN either source drifts
- THEN the executable contract test MUST fail closed under Pytest
- AND it MUST identify the violated workflow-to-contract expectation

## ADDED Requirements

### Requirement: GitHub-Hosted Node 24 Runtime Behavior

The pinned `actions/checkout@v5.0.0` and `astral-sh/setup-uv@v7.5.0` MUST run on the Node 24 JavaScript runtime when executed on GitHub-hosted `ubuntu-latest` runners; the workflow MUST contain no `pull_request_target`, `workflow_run`, secrets, or write tokens and MUST invoke `make ci` as its sole CI step. The contract test MUST fail closed if any pinned action resolves to a non-Node-24 runtime, if a tracked contract assertion drifts from the workflow, if either pinned SHA or its release-tag comment is missing or altered, or if a tracked runner event, permission, or step invariant is broken. Self-hosted runners are explicitly out of scope and receive no support guarantee.

#### Scenario: Pinned actions target Node 24 on GitHub-hosted runners

- GIVEN the workflow references `actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8 # v5.0.0` and `astral-sh/setup-uv@e06108dd0aef18192324c70427afc47652e63a82 # v7.5.0`
- WHEN the contract test inspects each pin's declared JavaScript runtime
- THEN both pins MUST declare Node 24
- AND a pin that resolves to a non-Node-24 runtime causes the contract test to fail closed

#### Scenario: Workflow and contract drift is rejected

- GIVEN the workflow and focused contract test quote the approved SHA/tag pair
- WHEN either executable source quotes a different SHA, tag, or release comment
- THEN Pytest MUST fail closed before `make ci` runs
- AND the failure MUST name the drifted executable source and expected value

#### Scenario: Runner event, permission, and step invariants hold

- GIVEN the workflow is reviewed for least-privilege shape
- WHEN the contract test asserts events, permissions, and steps
- THEN only unprivileged `push`/`pull_request` events are allowed
- AND only read-only `contents` permission is set
- AND `persist-credentials: false` is preserved on the `actions/checkout` step
- AND no `pull_request_target`, `workflow_run`, secrets, or write tokens are present
- AND the sole CI step is `make ci`

#### Scenario: SHA re-verification is required

- GIVEN Apply updates the pinned SHAs
- WHEN verification runs before merge
- THEN `git ls-remote https://github.com/actions/checkout.git refs/tags/v5.0.0` MUST return `08c6903cd8c0fde910a37f88322edcfb5dd907a8`
- AND `git ls-remote https://github.com/astral-sh/setup-uv.git refs/tags/v7.5.0` MUST return `e06108dd0aef18192324c70427afc47652e63a82`
- AND a mismatched SHA causes Apply to block until both pins are re-resolved or reverted

#### Scenario: Exact uv 0.11.29 is preserved

- GIVEN `astral-sh/setup-uv@v7.5.0` is pinned with `version: "0.11.29"`
- WHEN the workflow runs on a clean GitHub-hosted `ubuntu-latest` runner
- THEN `uv self version --short` is exactly `0.11.29` before `make ci`
- AND any other output is rejected non-zero without invoking `make ci`

#### Scenario: Self-hosted runners are explicitly out of scope

- GIVEN the contract covers only GitHub-hosted `ubuntu-latest` runners
- WHEN the contract test evaluates the workflow
- THEN no assertion, runner label, or support guarantee is made for self-hosted runners
- AND the sole supported runner label remains `ubuntu-latest`

#### Scenario: Rollback is bounded to the pin refresh

- GIVEN the change updates only the two pinned Actions and their three coupled references
- WHEN rollback is required
- THEN only the two pin updates and their matching contract/spec delta are reverted to the prior verified SHAs
- AND unrelated working-tree edits (including the intentional edits in `AGENTS.md` and `RAG_ROADMAP.md`) are preserved

## ADDED Requirements

### Requirement: SDD and OpenSpec Promotion Boundaries

The workflow and executable contract test MUST remain consistent and fail closed under Pytest. SDD Verify MUST map the implementation to this active delta. OpenSpec Archive alone MUST synchronize this approved delta into the canonical `test-harness` specification; before archive, the canonical specification MUST remain unchanged intentionally. After archive, focused tests and `make ci` MUST remain independently runnable regardless of OpenSpec path relocation. Runtime tests MUST NOT read canonical or change-local OpenSpec files.

#### Scenario: Verification and archive have distinct authority

- GIVEN Apply changes only the workflow and executable contract test
- WHEN SDD Verify and OpenSpec Archive run
- THEN Verify checks this active delta, while only Archive updates the canonical specification
- AND the canonical specification remains unchanged before Archive

#### Scenario: Runtime tests are path-independent

- GIVEN the change-local or canonical OpenSpec files are moved, absent, or relocated
- WHEN focused runtime tests or `make ci` run after implementation
- THEN they MUST NOT read those specification files
- AND their result MUST depend only on implementation and executable contract inputs
