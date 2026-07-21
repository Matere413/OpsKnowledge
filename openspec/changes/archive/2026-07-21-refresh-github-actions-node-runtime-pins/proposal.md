# Proposal: Refresh GitHub Actions Node Runtime Pins

## Intent

Remove the impending Node 20 runner-runtime risk from the GitHub-hosted CI adapter without changing the canonical CI gate or the exact `uv 0.11.29` tool contract. Phase 1 remains blocked until this change is verified and archived.

## Scope

### In Scope
- Pin `actions/checkout` to v5.0.0 (`08c6903cd8c0fde910a37f88322edcfb5dd907a8`) and `astral-sh/setup-uv` to v7.5.0 (`e06108dd0aef18192324c70427afc47652e63a82`).
- Preserve SHA-plus-tag comments, `ubuntu-latest`, `persist-credentials: false`, exact `uv 0.11.29`, and the sole `make ci` invocation.
- During Apply, modify only the workflow and its executable contract test. The change-local `test-harness` delta remains normative through Apply and Verify.
- Archive alone promotes the approved delta into `openspec/specs/test-harness/spec.md`.

### Out of Scope
- Self-hosted-runner support or guarantees.
- Canonical-spec modification during Apply or Verify; three-source atomicity assertions during Apply.
- Scanner changes, manifests, lockfile, governance, Makefile, product code, and `uv` changes.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `test-harness`: deterministic CI bootstrap pins and GitHub-hosted Node 24 runtime behavior change.

## Approach

Use the smallest verified Node 24 transition: checkout v5.0.0 and setup-uv v7.5.0. v5.0.0 explicitly uses Node 24; v7.5.0 resolves from Astral's version manifest with checksummed `uv 0.11.29`. Apply re-verifies the pins and changes only `.github/workflows/ci.yml` and `tests/architecture/test_github_actions_workflow.py`. The executable test checks workflow-to-test consistency; SDD Verify checks the implementation against the change-local delta. Archive is the sole canonical-spec promotion boundary.

Apply must rerun:

- `git ls-remote https://github.com/actions/checkout.git refs/tags/v5.0.0`
- `git ls-remote https://github.com/astral-sh/setup-uv.git refs/tags/v7.5.0`

Evidence: [checkout v5.0.0](https://github.com/actions/checkout/releases/tag/v5.0.0), [setup-uv v7.5.0](https://github.com/astral-sh/setup-uv/releases/tag/v7.5.0), and [Astral uv manifest](https://raw.githubusercontent.com/astral-sh/versions/main/v1/uv.ndjson).

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `.github/workflows/ci.yml` | Modified | Replace two SHA/tag pins only. |
| `tests/architecture/test_github_actions_workflow.py` | Modified | Align exact pins and assert Node 24 GitHub-hosted behavior. |
| `openspec/changes/refresh-github-actions-node-runtime-pins/specs/test-harness/spec.md` | Normative | Governs Apply and Verify; archive promotes it. |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| `uv 0.11.29` resolution changes | Low | Verify manifest evidence and run workflow-relevant tests plus `make ci`. |
| Workflow/test drift | Medium | Fail closed in the executable contract test; Verify checks the active delta. |
| Premature canonical promotion | Low | Do not edit the canonical spec until OpenSpec archive. |

## Rollback Plan

Before archive, revert only `.github/workflows/ci.yml` and `tests/architecture/test_github_actions_workflow.py` to the prior verified pins; withdraw or amend the active delta through SDD, leaving the canonical spec unchanged. After archive, use a new bounded SDD change to reverse the promoted canonical requirement. Preserve unrelated working-tree edits.

## Dependencies

- GitHub-hosted `ubuntu-latest` runner supporting Node 24.

## Success Criteria

- [ ] Both pinned actions run on Node 24 on GitHub-hosted `ubuntu-latest`.
- [ ] `uv self version --short` remains exactly `0.11.29` before `make ci`.
- [ ] The focused workflow test and `make ci` pass; Verify accepts the implementation against the active delta.
- [ ] OpenSpec archive is the only operation that promotes the approved delta; Phase 1 stays blocked until archive.
