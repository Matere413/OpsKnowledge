# Tasks: Reframe Roadmap for Direct Corporate Product

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 463 native frozen snapshot; 415 additions across six lifecycle files (plus only bounded correction wording if noted) |
| 400-line budget risk | High |
| Chained PRs recommended | No — current frozen transaction is kept as one documentation delivery under explicit size exception |
| Delivery strategy | exception-ok |
| Chain strategy | size-exception |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: High

The frozen native snapshot measured 463 changed lines: the six SDD artifacts in this change folder account for 415 additions before the two tracked product-documentation files, whose 48-line implementation edit is the only slice under the 400-line budget. The maintainer approved the `size:exception` after the native snapshot was measured, so the frozen transaction stays as one documentation delivery and is NOT split or re-scoped. This record does NOT imply the budget was under 400; the 400-line budget risk is High, and the exception is explicit.

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Reframe roadmap and preserve lineage | Single PR | `git diff --check && make ci` | N/A — documentation-only change | Revert only the allowlisted product-documentation files and the change-folder SDD lifecycle artifacts |

## Phase 1: Ownership and Evidence Preflight

- [x] 1.1 Before apply, inspect `audit-opsknowledge-phase-0-inputs` as the accepted Phase 0/Phase 4 baseline; STOP without edits if ownership or status is unsettled or overlapping.
- [x] 1.2 Read-only verify `git show 12ba6926`, PR #28 evidence, and `openspec/changes/build-minimal-grounded-opsknowledge-core/`; define the implementation allowlist and protected paths.

## Phase 2: Documentation Changes

- [x] 2.1 Modify `RAG_ROADMAP.md` without renumbering history: absorb Phase 1 into planned production core, credit only PR #28’s corpus/ports slice, mark retrieval/prompt/provider/outcome/CLI pending, retain Phase 2/invariants, and make Phase 8 gates parallel prerequisites.
- [x] 2.2 Modify `docs/architecture/platform-architecture.md` minimally: keep all runtime components planned, preserve separate synthetic/demo boundaries, and state corporate processing is blocked until identity, authorization, sensitive screening, controlled provider, and TI gates pass.
- [x] 2.3 Create `openspec/changes/reframe-roadmap-for-direct-corporate-product/phase-1-lineage-closure.md` with `reframed—not complete`, PR #28/`12ba6926` receipt evidence, only the delivered corpus boundary/shared ports/corpus domain-application-loader inventory, and the five pending work areas.

## Phase 3: Verification and Rollback Readiness

- [x] 3.1 Cross-review `RAG_ROADMAP.md`, `docs/architecture/platform-architecture.md`, the closure note, and `AGENTS.md` for consistent gates, safety invariants, Phase 2 retention, and no false completion.
- [x] 3.2 Verify the allowlist: only `RAG_ROADMAP.md`, `docs/architecture/platform-architecture.md`, and the closure note are implementation edits (current-change SDD lifecycle artifacts may also be present); run `git diff --check`, `git diff --stat`, and confirm the 48-line product-documentation edit is under 400, with the maintainer-approved `size:exception` recorded for the 463-line full native snapshot containing 415 additions across the six lifecycle artifacts.
- [x] 3.3 Run `make ci`; verify `git diff --name-only -- AGENTS.md backend web tests governance openspec/changes/build-minimal-grounded-opsknowledge-core openspec/changes/archive` is empty, and confirm rollback never changes PR #28, its receipt, or prior SDD artifacts.
