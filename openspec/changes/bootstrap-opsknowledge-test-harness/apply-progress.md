# Apply Progress: bootstrap-opsknowledge-test-harness

**Mode**: Standard (Strict TDD disabled — no runner exists; this change establishes it)
**Delivery**: chained PRs, feature-branch-chain; PR2 is split into PR2A (Make/version/order) and PR2B (scanner). No monolithic PR2 exception and no `ci-available` contract.

## Size Exceptions (approved)

### Tracker-only exception
The tracker PR is documentation-only (SDD planning artifacts + apply-progress) with **850 insertions across 7 files** (`git diff --shortstat master...chore/bootstrap-test-harness-tracker`). The user approved a `size:exception` for the tracker PR; it remains draft/no-merge until all child PRs (PR1–PR4) are reviewed and integrated.

### PR1 exception
The user approved a `size:exception` for PR1 because 517 of its 575 changed lines are the generated, indivisible `uv.lock` lockfile. The manifest (`pyproject.toml`, `.python-version`, `.gitignore`) and the generated lockfile are one atomic reproducible unit. PR2A, PR2B, PR3, and PR4 retain focused chained boundaries with no exception.

## Cumulative Task State

### Phase 1: Packaging Surface (PR1) — COMPLETE (7/7, committed)

- [x] 1.1 Create `.python-version` containing exactly `3.12`. — Done.
- [x] 1.2 Create `pyproject.toml` `[project]` with `name = "opsknowledge"`, `version = "0.0.0"`, `requires-python = ">=3.12,<3.13"`, `dependencies = []`. — Done.
- [x] 1.3 Add `[project.optional-dependencies] dev = [...]` with pytest, ruff, pyright, pip-audit, pip-licenses, pyyaml — versions from `uv.lock`, not invented. — Done (pytest==9.1.1, ruff==0.15.21, pyright==1.1.411, pip-audit==2.10.1, pip-licenses==5.5.5, pyyaml==6.0.3).
- [x] 1.4 Add inline `[tool.pyright]`, `[tool.ruff]`, `[tool.pytest.ini_options]`, `[tool.coverage.run]` blocks in `pyproject.toml`. — Done.
- [x] 1.5 Generate `uv.lock` via `uv lock`; commit it; re-running on a clean clone MUST produce an identical file. — Done (41 packages; clean-clone proven from committed branch).
- [x] 1.6 Extend `.gitignore` with `.venv/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `.pyright_cache/`, `.uv-cache/`, `*.egg-info/`, `dist/`, `build/`, `htmlcov/`, `.coverage`. — Done.
- [x] 1.7 Stop and report if local `uv self version --short` ≠ `0.11.29`; do not substitute a different version. — Done.

### Phase 2A: COMPLETE (implemented, not committed)
- [x] `Makefile` gates on complete `uv self version --short == "0.11.29"`, then provides sync/Ruff/Pyright/Pytest order and `ci-pr2a` verification.
- [x] Recipe tests prove exact success and reject mismatched, suffixed, multiline, malformed, unavailable, and command-error `uv self version --short` output before later invocation.
- [x] `make ci` fails closed at the PR2B scanner boundary; PR2A contains no scanner, audit, license, or dependency-boundary implementation.

### Phase 2B: NOT STARTED
- [ ] Implement scanner and its architecture tests; then make `ci` fail closed at the PR3 audit boundary.

### Phase 3: NOT STARTED
- [ ] Complete dependency boundary, audit, license, and fail-fast work; final `make ci` exits zero.

### Phases 4–5: NOT STARTED

## Git Topology (feature-branch-chain)

Topology is defined by **symbolic branch relationships**, not hardcoded PR1 SHAs. Branch names use the branch-pr `type/description` convention. Verify ancestry at any time with the commands below.

```
master (03a67fb)
  └─ chore/bootstrap-test-harness-tracker        [tracker PR targets master; draft/no-merge; size:exception]
       └─ build/bootstrap-test-harness-pr1-packaging   [PR1 PR targets tracker; size:exception]
```

Targeting chain (feature-branch-chain): tracker draft/no-merge targets `master`; PR1 targets tracker; PR2A targets PR1; PR2B targets PR2A; PR3 targets PR2B; PR4 targets PR3. Size exceptions are scoped only to tracker docs and the PR1 generated lockfile; PR2A–PR4 have none.

### Immutable baseline SHAs
| SHA | Role |
|-----|------|
| `c3cc223` | master: first commit — OpsKnowledge project baseline |
| `03a67fb` | master: second commit — governance bootstrap (PR template + issue templates) — CURRENT MASTER TIP |

### Verifiable ancestry commands
```bash
# Prove tracker descends from master (merge-base must equal master tip):
git merge-base master chore/bootstrap-test-harness-tracker

# Prove tracker tip is ancestor of PR1 (merge-base must equal tracker tip):
git merge-base chore/bootstrap-test-harness-tracker build/bootstrap-test-harness-pr1-packaging

# Prove PR1 diff vs tracker contains exactly the four implementation files:
git diff --stat chore/bootstrap-test-harness-tracker...build/bootstrap-test-harness-pr1-packaging

# Prove tracker diff size (for size:exception verification):
git diff --shortstat master...chore/bootstrap-test-harness-tracker
```

PR1's SHA is intentionally not recorded here — it is set by the final rebase onto tracker tip and verified via the ancestry commands above. Recording it would create a rebase loop.

## Verification (PR1, from final committed state)

- `uv self version --short` → `0.11.29` ✅ (`uv -V` and `uv --version` include build metadata; `uv version --short` reports the project package version and none is the gate command.)
- `uv lock --check` → exit 0 ✅
- `uv sync --frozen --extra dev` → exit 0 (39 packages) ✅
- Dev tools run from frozen env: `ruff 0.15.21`, `pyright 1.1.411`, `pytest 9.1.1` ✅
- Clean-clone reproducibility: cloned PR1 branch to temp dir outside repo, `rm uv.lock && uv lock` → byte-identical ✅; `uv sync --frozen --extra dev` in clone → exit 0 ✅; temp clone cleaned up.
- PR1 diff vs tracker: exactly `.gitignore` (+15/-1), `.python-version` (+1), `pyproject.toml` (+43), `uv.lock` (+517) = 575 insertions, 1 deletion; 517 are generated lockfile (approved PR1 size:exception).
- Working tree clean ✅
- No PR2 work present ✅
- No runtime/production dependencies added (`[project.dependencies]` empty) ✅

## Governance Bootstrap (committed on master at `03a67fb`)

- `.github/PULL_REQUEST_TEMPLATE.md`: linked-issue section, exactly-one type checkbox with label mapping, summary, changes table, test plan, contributor checklist.
- `.github/ISSUE_TEMPLATE/bug_report.yml`: YAML form, auto-labels `bug` + `status:needs-review`.
- `.github/ISSUE_TEMPLATE/feature_request.yml`: YAML form, auto-labels `enhancement` + `status:needs-review`.
- See Engram #3417 (`governance/github-collaboration`) for the decision record.

## Publish Preflight Status

- Remote: `https://github.com/Matere413/OpsKnowledge.git` — EMPTY (no commits, no branches)
- gh auth: logged in as Matere413 (keyring), scopes: repo, workflow, read:org, gist ✅
- Governance files: committed locally on master ✅
- Labels still MISSING in remote: `status:approved`, `status:needs-review`, `type:*` — must be created before PRs pass automated checks
- Approved issue: none — must be created and approved before PRs can link it
- No git remote configured locally (no `origin`)

## Environment configuration
- uv: `0.11.29` at `~/.local/bin/uv` (upgraded from 0.11.21 via GitHub release tarball; previous backed up to `~/.local/bin/uv.bak-0.11.21`).
- python3.12: 3.12.13 at `/opt/homebrew/opt/python@3.12/bin/python3.12`.
- No unrelated global configuration altered. Git config not modified.

## Files changed (PR1 scope)

| File | Action | Lines | Description |
|------|--------|-------|-------------|
| `.python-version` | Created | +1 | Pins `3.12` for uv-managed interpreter selection. |
| `pyproject.toml` | Created | +43 | Project `opsknowledge` 0.0.0, `requires-python = ">=3.12,<3.13"`, empty `dependencies`, exact-pinned `dev` extra, inline tool config. |
| `uv.lock` | Created | +517 | Generated lockfile: 41 packages under uv 0.11.29; reproducible from clean clone. Machine-generated, indivisible. |
| `.gitignore` | Modified | +14/-1 | Appended Python dev-env ignore patterns. |
| **Total** | | **575** | **517 generated lockfile + 58 authored** — approved size:exception |

## Deviations from Design
None — implementation matches design.

## Historical Audit

The tracker and PR1 branches went through multiple local rebases during topology remediation and governance restacking. All intermediate SHAs are unreachable from current branch tips. The final compacted history contains: master (2 commits), tracker (1 commit ahead of master), PR1 (1 commit ahead of tracker). No intermediate SHAs are presented as review commits.

## Resume / Next Steps
- PR1 implementation complete, verified, committed on `build/bootstrap-test-harness-pr1-packaging`.
- PUBLICATION still blocked: needs remote labels, approved issue, and `origin` remote.
- PR2A is implemented locally on `build/bootstrap-test-harness-pr2a-make-gate`; do not commit, push, or change topology in this documentation update.
- Next implementation after PR2A publication: PR2B scanner; then PR3 completes audit/license and the final successful `make ci`.
- Tracker `chore/bootstrap-test-harness-tracker` (draft/no-merge) merges to `master` only after all child PRs integrate.
