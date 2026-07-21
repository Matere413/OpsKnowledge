# Design: Refresh GitHub Actions Node Runtime Pins

## Technical Approach

Apply changes only the CI workflow and its executable architecture test. The active delta governs Apply and Verify; Archive alone promotes it to the canonical `test-harness` spec. The offline test derives workflow expectations from `ACTION_CONTRACTS`, never OpenSpec paths. Preserve Node 24, both exact SHA/tag pins, least privilege, `uv 0.11.29`, and the sole `make ci` command.

## Architecture Decisions

| Decision | Choice | Alternative rejected | Rationale |
|---|---|---|---|
| Pin evidence | Checkout `08c6903cd8c0fde910a37f88322edcfb5dd907a8 # v5.0.0`; setup-uv `e06108dd0aef18192324c70427afc47652e63a82 # v7.5.0` | Tags or unverified SHAs | Immutable pins and readable provenance; Apply re-verifies tags and upstream `action.yml` Node 24 metadata. |
| Executable boundary | Test maps workflow `uses` values and tag comments to `ACTION_CONTRACTS`; every runtime is `node24` | Canonical/change-local spec reads or CI network access | Tests stay deterministic and survive OpenSpec relocation while rejecting workflow/contract drift. |
| Lifecycle authority | Apply edits two implementation files; Verify maps them to the active delta; Archive updates canonical spec | Apply-time three-source atomicity | Prevents premature promotion and keeps runtime behavior independent of documentation location. |

## Data Flow

    Apply: upstream tag + action.yml ──> workflow + ACTION_CONTRACTS
                                           │
    active delta ── SDD Verify ───────────┤──> focused pytest / make ci
                                           │
                              OpenSpec Archive ──> canonical spec

Apply runs both required `git ls-remote` checks, fetches each immutable SHA in a temporary directory, and requires `action.yml` `runs.using == node24`; it also confirms setup-uv's authoritative manifest has checksummed `0.11.29`. Any mismatch, fetch, parse, or metadata failure blocks Apply before editing. CI performs no network lookup and reads no canonical or change-local OpenSpec file.

## File Changes

| File | Action | Description |
|---|---|---|
| `.github/workflows/ci.yml` | Modify | Keep only the approved pins, `ubuntu-latest`, `contents: read`, credential-free checkout, exact uv assertion, and sole `make ci`. |
| `tests/architecture/test_github_actions_workflow.py` | Modify | Make `ACTION_CONTRACTS` the workflow-to-contract source; remove canonical-path/three-source assertions and add path-independence mutations. |

No Apply edit: canonical spec, index/review authority, proposal, delta, tasks, or apply-progress.

## Interfaces / Contracts

`ACTION_CONTRACTS[action] = (sha, tag, "node24")`. Workflow expectations are constructed from this table; a missing/changed SHA, release comment, runtime, event, permission, checkout credential setting, uv version/order, extra action/run block, or non-sole `make ci` fails closed with expected-source diagnostics. No self-hosted support is added.

## Testing Strategy

| Layer | What to Test | Approach |
|---|---|---|
| Architecture | Contract/workflow consistency, Node 24, least privilege, uv and sole gate | RED mutations for SHA/tag/runtime, permissions, commands, and OpenSpec-path absence; focused Pytest is path-independent. |
| Apply evidence | Upstream tag/SHA, `action.yml`, uv manifest | Required networked verification before edits; retain receipts. |
| Canonical gate | Repository contract after artifact relocation | Run focused test and `make ci`; neither reads OpenSpec. |

## Threat Matrix

| Boundary | Applicability | Design response / RED tests |
|---|---|---|
| Documentation-like paths | N/A | No executable classification. |
| Git repository selection | N/A | Operator uses fixed repository; no repository-selection logic. |
| Commit state | N/A | No commit automation. |
| Push state | N/A | No push automation. |
| PR commands | N/A | No PR command integration. |

## Migration / Rollout

From the current workspace, preserve all historical upstream/focused/`make ci` receipts but mark prior Apply evidence superseded: it included premature canonical-spec work and canonical-coupled tests. Restore **only** the premature `openspec/specs/test-harness/spec.md` worktree edit; retain unrelated edits and the two intended implementation files. Amend Apply to remove canonical coupling, repeat upstream verification, then obtain renewed review before any merge. SDD Verify maps the renewed implementation to the active delta; only Archive later promotes it.

## Rollback

Before Archive, revert only the two implementation files to their prior verified pins and withdraw/amend the active delta; do not touch unrelated worktree changes or historical receipts. After Archive, use a new bounded SDD change for canonical reversal.

## Review Workload Forecast

- Implementation forecast: workflow ~4 and test ~55–85 changed lines; <400 lines excluding OpenSpec artifacts.
- Decision needed before apply: No
- Chained PRs recommended: No
- 400-line budget risk: Low
- Execution is interactive; delivery is `ask-always`. Re-evaluate if actual implementation exceeds budget.

## Open Questions

None.
