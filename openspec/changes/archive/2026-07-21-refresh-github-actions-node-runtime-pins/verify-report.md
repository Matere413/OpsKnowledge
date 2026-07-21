```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:6ecf22c980463b8869b44a322b33a0fe841ccc0fa7d9582fea04f184673be033
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 3/3
scenarios: 11/11
test_command: uv run --frozen pytest tests/architecture/test_github_actions_workflow.py -v
test_exit_code: 0
test_output_hash: sha256:a29c5c49d2d811c9c095b368dda0ceced803c9fbbdb934ab5c166dd5d6324278
build_command: make ci
build_exit_code: 0
build_output_hash: sha256:cf46cc987f2d24ba32ed0354b7d080a84c6cc4182cdb048fc139553bb2f6ead8
```

# Verification Report: GitHub Actions Node Runtime Pins

**Change**: `refresh-github-actions-node-runtime-pins`
**Mode**: Standard (Strict TDD inactive)
**Verdict**: PASS WITH WARNINGS

The bound staged candidate passed the native post-apply review gate, focused executable contract test, canonical `make ci` gate, and current upstream pin/runtime checks. The active delta is satisfied; Archive remains the sole canonical-spec promotion authority.

## Authority and Candidate

| Check | Result |
|---|---|
| Native dispatcher | `apply: all_done`; `tasks: 10/10`; `reviewGate: allow`; `nextRecommended: verify`; no blocked reasons |
| Bound review lineage | `review-c9b0c27988bd2d6c` |
| Authority revision | `sha256:ad47625325eceafd3bc12a5e72426cc988483b47b224634e506413784542cfb3` |
| Post-apply gate | `allow` — authoritative transaction and content-bound artifacts match |
| Candidate tree | `028fca5530dc62cabc6a776bff2f2a069f86f83b` |
| Canonical spec before Archive | Unchanged from HEAD/index (`c2c89f254e78a77b34f4e069f51a1617d525680c`) |
| Staged candidate hygiene | `git diff --cached --check` passed; native authority validates the full staged target |

## Completeness

| Metric | Value |
|---|---:|
| Tasks total | 10 |
| Tasks complete | 10 |
| Tasks incomplete | 0 |
| Active-delta requirements | 3 |
| Active-delta scenarios | 11 |

## Runtime Evidence

| Evidence | Command / check | Result |
|---|---|---|
| Focused contract | `uv run --frozen pytest tests/architecture/test_github_actions_workflow.py -v` | 13 passed in 0.25s; exit 0 |
| Canonical gate | `make ci` | 137 passed in 72.22s; Ruff, format, Pyright, dependency, audit, and license gates passed; exit 0 |
| Checkout tag | `git ls-remote https://github.com/actions/checkout.git refs/tags/v5.0.0` | `08c6903cd8c0fde910a37f88322edcfb5dd907a8` |
| setup-uv tag | `git ls-remote https://github.com/astral-sh/setup-uv.git refs/tags/v7.5.0` | `e06108dd0aef18192324c70427afc47652e63a82` |
| Immutable action metadata | Current immutable `action.yml` retrieval | Both actions declare `node24` |
| uv manifest | Current Astral `v1/uv.ndjson` retrieval | One `0.11.29` record with SHA-256 for every artifact |

Coverage is not configured as a repository threshold; it is not available from the canonical gate.

## Spec Compliance Matrix

| Requirement | Scenario | Covering runtime evidence | Result |
|---|---|---|---|
| Deterministic CI Runner Bootstrap | Clean runner has the selected uv | Focused contract: workflow pins, credentials, exact uv assertion/order, and sole gate; `make ci` passed | ✅ COMPLIANT |
| Deterministic CI Runner Bootstrap | Workflow and executable contract remain consistent | Focused drift/rejection tests passed | ✅ COMPLIANT |
| GitHub-Hosted Node 24 Runtime Behavior | Pinned actions target Node 24 | Focused Node 24 mutation test passed; immutable upstream `action.yml` checks passed | ✅ COMPLIANT |
| GitHub-Hosted Node 24 Runtime Behavior | Workflow and contract drift is rejected | Focused SHA/tag and workflow mutation tests passed | ✅ COMPLIANT |
| GitHub-Hosted Node 24 Runtime Behavior | Runner event, permission, and step invariants hold | Focused least-privilege, credential, extra-action, timeout, and sole-gate mutation tests passed | ✅ COMPLIANT |
| GitHub-Hosted Node 24 Runtime Behavior | SHA re-verification is required | Both required `git ls-remote` commands returned the exact approved SHA/tag pairs | ✅ COMPLIANT |
| GitHub-Hosted Node 24 Runtime Behavior | Exact uv 0.11.29 is preserved | Focused exact-version/order and gate-bypass mutation tests; `make ci` passed | ✅ COMPLIANT |
| GitHub-Hosted Node 24 Runtime Behavior | Self-hosted runners are explicitly out of scope | Focused exact runner/job contract passed; workflow has only `ubuntu-latest` | ✅ COMPLIANT |
| GitHub-Hosted Node 24 Runtime Behavior | Rollback is bounded to the pin refresh | Staged candidate inspection and native content-bound candidate validation passed; canonical spec remains unchanged | ✅ COMPLIANT |
| SDD and OpenSpec Promotion Boundaries | Verification and archive have distinct authority | Native dispatcher and canonical-spec HEAD/index equality passed | ✅ COMPLIANT |
| SDD and OpenSpec Promotion Boundaries | Runtime tests are path-independent | `test_contract_is_path_independent` passed; source does not name OpenSpec and `make ci` passed | ✅ COMPLIANT |

**Compliance summary**: 11/11 scenarios compliant.

## Correctness

| Requirement | Status | Evidence |
|---|---|---|
| Deterministic CI Runner Bootstrap | ✅ Implemented | Exact checkout/setup-uv SHA-plus-tag pins, read-only credentials, uv `0.11.29` assertion before the only `make ci` step. |
| GitHub-Hosted Node 24 Runtime Behavior | ✅ Implemented | `ACTION_CONTRACTS` records both Node 24 runtimes; executable mutations fail closed for drift and least-privilege violations. |
| SDD and OpenSpec Promotion Boundaries | ✅ Implemented | Runtime test derives its contract from `ACTION_CONTRACTS`, does not read OpenSpec, and canonical spec has not changed. |

## Design Coherence

| Decision | Followed? | Notes |
|---|---|---|
| Immutable SHA/tag pins and upstream metadata | ✅ Yes | Exact tag/SHA and Node 24 checks passed. |
| Offline executable boundary via `ACTION_CONTRACTS` | ✅ Yes | Test source has no OpenSpec path dependency and passed path-independence coverage. |
| Apply/Verify/Archive authority separation | ✅ Yes | Implementation is limited to workflow/test behavior; canonical spec equals HEAD/index before Archive. |
| Bounded rollback | ✅ Yes | Reported boundary is workflow/test pin contract only; unrelated staged content remains preserved in the authority-bound candidate. |

## Canonical Verification Evidence

The following bytes are preserved verbatim as the preimage for `evidence_revision`:

```text
lineage_id=review-c9b0c27988bd2d6c
authority_revision=sha256:ad47625325eceafd3bc12a5e72426cc988483b47b224634e506413784542cfb3
review_gate=allow
review_candidate_tree=028fca5530dc62cabc6a776bff2f2a069f86f83b
focused_command=uv run --frozen pytest tests/architecture/test_github_actions_workflow.py -v
focused_exit=0
focused_output_hash=sha256:a29c5c49d2d811c9c095b368dda0ceced803c9fbbdb934ab5c166dd5d6324278
build_command=make ci
build_exit=0
build_output_hash=sha256:cf46cc987f2d24ba32ed0354b7d080a84c6cc4182cdb048fc139553bb2f6ead8
checkout_tag=08c6903cd8c0fde910a37f88322edcfb5dd907a8 refs/tags/v5.0.0
setup_uv_tag=e06108dd0aef18192324c70427afc47652e63a82 refs/tags/v7.5.0
checkout_runtime=node24
setup_uv_runtime=node24
uv_manifest=checksummed-0.11.29
canonical_spec_preimage=unchanged
```

## Issues Found

**CRITICAL**: None.

**WARNING**:
- The current Engram `tasks` mirror (#4106) is stale at 10/12 and lists Verify/Archive as unchecked, while the authoritative OpenSpec task artifact and native dispatcher report 10/10 complete. The file artifact and dispatcher govern this verification; refresh the stale historical mirror only through the normal artifact synchronization path.

**SUGGESTION**:
- Archive next only after the orchestrator accepts this report; archive should promote the active delta and rerun the focused test plus `make ci` as specified.

## Next Step

`sdd-archive` — after review of this PASS WITH WARNINGS report. Do not alter the implementation, canonical spec, review authority, or staged candidate before the archive handoff.
