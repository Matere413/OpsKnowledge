# Tasks: Bootstrap OpsKnowledge Test Harness

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Change name | `bootstrap-opsknowledge-test-harness` |
| Language | English |
| Estimated changed lines (range) | 650 – 900 (central ~750) |
| 800-line review budget | **Medium** — central sits at the ceiling; upper bound exceeds it |
| Chained PRs recommended | **Yes** — atomic apply exceeds the 800 budget; the change is decomposable |
| Suggested split | PR1 packaging → PR2A Make/version/order → PR2B focused-test scanner → PR3 boundaries/audit/license/final CI → PR4 GitHub Actions adapter |
| Delivery strategy | `ask-on-risk` → resolved to `feature-branch-chain` |
| Chain strategy | **feature-branch-chain** — resolved and approved by user |
| Strict TDD | **disabled** for this change; re-evaluated with the next runtime change |

Decision needed before apply: No (resolved — feature-branch-chain approved)
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: N/A (active budget is 800)
800-line budget risk: Medium

**WU→PR map** (feature-branch-chain: tracker draft/no-merge targets `master`; PR1 targets tracker; PR2A targets PR1; PR2B targets PR2A; PR3 targets PR2B; PR4 targets PR3. Exceptions are limited to tracker docs and PR1's generated lockfile; PR2A–PR4 have none):

| PR | Targets | Work | Verify |
|----|---------|------|--------|
| Tracker | `master` (draft/no-merge) | SDD planning artifacts | N/A — draft tracker, merges only after all children integrate |
| PR1 | tracker | `pyproject.toml`, `.python-version`, `uv.lock`, `.gitignore` extensions | `uv lock --check` + `uv sync --frozen --extra dev` exit 0 |
| PR2A | PR1 branch | `Makefile` executable-version, sync, quality-stage order, and smoke/recipe tests only | `make ci-pr2a` exits 0; `make ci` fails closed at PR2B scanner boundary |
| PR2B | PR2A branch | `scripts/ci/check_focused_tests.py` and scanner architecture tests | scanner passes valid tests; `make ci` fails closed at PR3 audit boundary |
| PR3 | PR2B branch | `check_dependency_boundaries.py`, `run_vulnerability_audit.py`, license wiring, boundary/audit/fail-fast tests | final `make ci` exits 0 |
| PR4 | PR3 branch | `.github/workflows/ci.yml` pinning `astral-sh/setup-uv@d4b2f3b6ecc6e67c4457f6d3e41ec42d3d0fcb86 # v5.4.2` + assertion + `make ci`; static workflow tests; apply-time SHA re-verification | Static tests pass; apply-time re-fetch confirms SHA and is recorded in verify report |

---

## Phase 1: Packaging Surface (PR1)

Start: only the durable baseline exists. Finish: `pyproject.toml`, `.python-version`, `uv.lock`, extended `.gitignore` tracked; `uv sync --frozen --extra dev` exits 0. Verify: `uv self version --short` → `0.11.29`; `uv lock --check` → 0. Rollback: `git revert` PR1. Trace: "Locked Python Development Environment" (manifest + version), "Bootstrap Scope and Strict TDD" (no app source), "Production and Test-Tree Dependency Boundaries" (empty `[project.dependencies]`).

- [x] 1.1 Create `.python-version` containing exactly `3.12`.
- [x] 1.2 Create `pyproject.toml` `[project]` with `name = "opsknowledge"`, `version = "0.0.0"`, `requires-python = ">=3.12,<3.13"`, `dependencies = []`.
- [x] 1.3 Add `[project.optional-dependencies] dev = [...]` with pytest, ruff, pyright, pip-audit, pip-licenses, pyyaml — versions from `uv.lock`, not invented.
- [x] 1.4 Add inline `[tool.pyright]`, `[tool.ruff]`, `[tool.pytest.ini_options]`, `[tool.coverage.run]` blocks in `pyproject.toml`.
- [x] 1.5 Generate `uv.lock` via `uv lock`; commit it; re-running on a clean clone MUST produce an identical file.
- [x] 1.6 Extend `.gitignore` with `.venv/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `.pyright_cache/`, `.uv-cache/`, `*.egg-info/`, `dist/`, `build/`, `htmlcov/`, `.coverage`.
- [x] 1.7 Stop and report if local `uv self version --short` ≠ `0.11.29`; do not substitute a different version.

---

## Phase 2A: Make, Executable-Version, and Order Contract (PR2A) — COMPLETE (implemented, not committed)

PR2A owns only Make/version/order and smoke/recipe tests. `make ci-pr2a` proves its completed stages; `make ci` fails closed at the unimplemented PR2B scanner. No scanner, audit, license, or dependency-boundary implementation belongs here.

- [x] 2A.1 Create `Makefile` ordered targets and `.PHONY`; `make ci` fails closed at the PR2B scanner boundary; `make ci-pr2a` verifies PR2A stages.
- [x] 2A.2 Implement `check-uv-version`: capture complete `$(UV) self version --short` output and compare literally to `0.11.29`; never use `-V`, `--version`, or `version --short` for executable validation.
- [x] 2A.3 Create smoke, package-marker, fixture, and CI-recipe test scaffolding.
- [x] 2A.4 Test exact `uv self version --short` success plus mismatched, suffixed, multiline, malformed, unavailable, and command-error output; prove no later tool invocation after failure.

## Phase 2B: Focused-Test AST Scanner (PR2B) — NOT STARTED

- [ ] 2B.1 Create `scripts/ci/check_focused_tests.py` and architecture tests for skip, skipif, xfail, `.only`, focus forms, and aliases.
- [ ] 2B.2 Replace the PR2B fail-closed Make target; verify valid scanner passage and audit-boundary failure.

---

## Phase 3: Boundaries, Audit Wrapper, Fail-Fast Proof (PR3)

Start: PR2B merged. Finish: audit, license, dependency-boundary, and fail-fast coverage complete; final `make ci` exits zero. No monolithic PR2 exception is permitted.

- [ ] 3.1 Create `scripts/ci/check_dependency_boundaries.py` with reviewed map: `langchain → langchain`, `llamaindex → llama_index`, `redis → redis`, `kubernetes → kubernetes`; policy-only exclusions (`streaming`, `visualinterpretation`, `email`, `notifier`, `reranking`, `queues`, `microservices`) marked `non_importable: True`.
- [ ] 3.2 Validate at startup that every `excluded` entry has a map classification or `non_importable` marker (fail non-zero + name the entry otherwise); on scan resolve `import`, `from … import …`, `as` aliases, and literal `__import__(...)`; emit `path:line: canonical-distribution`; unresolvable excluded alias MUST fail non-zero.
- [ ] 3.3 Wire `Makefile` boundary stage to `uv run --frozen python scripts/ci/check_dependency_boundaries.py`; record position in `design.md` if not already.
- [ ] 3.4 Create `scripts/ci/run_vulnerability_audit.py` with `AuditResult = "success" | "vulnerability_finding" | "vulnerability_service_unavailable" | "vulnerability_tool_failure"`; accept subprocess seam `(returncode, stdout, stderr, timed_out)`; invoke `uv run --frozen pip-audit --local --strict` exactly once; classify (timeout → unavailable; rc=0 → success; non-zero + finding signature → finding; non-zero + tool/service signature → unavailable or tool-failure per stderr); forward output verbatim; non-zero for every non-success. No retry, no allowlist.
- [ ] 3.5 Wire `Makefile` `audit` stage to the wrapper; non-zero exit stops the gate.
- [ ] 3.6 Wire `license-inventory` to `uv run --frozen pip-licenses --from=expression --format=json` writing to a documented path (e.g. `artifacts/license-inventory.json`); MUST NOT classify, suppress, or assert compatibility.
- [ ] 3.7 Create `tests/architecture/test_dependency_boundaries.py` with table-driven cases: direct `llama_index`, aliased `llama_index as li`, literal `__import__("llama_index")`, `langchain`, `streaming` marker (asserted non-importable), `kubernetes`; assert non-zero + `path:line: canonical`; assert missing map classification fails at startup.
- [ ] 3.8 Create `tests/unit/test_audit_wrapper.py` with one case per `AuditResult` (success; finding via known stderr; unavailable via `timeout=True`; unavailable via service-down signature; tool-failure via unexpected exception trace); assert classification, exactly one seam call, non-zero exit for non-success, rerun after `success` stub returns zero (recovery proof).
- [ ] 3.9 Create `tests/ci/test_ci_fail_fast.py` that copies the `make ci` recipe, substitutes `UV` with a fake whose `self version --short` output is `0.11.29`, and stages one failure per stage (focused-test, Ruff, Pyright, Pytest, audit, license); assert log ends at that stage's sentinel and no later sentinel runs.

---

## Phase 4: GitHub Actions Thin Adapter (PR4)

Start: PR3 merged; local `make ci` is green; no workflow. Finish: `.github/workflows/ci.yml` tracked; static security + assertion tests pass; apply-time SHA re-verification recorded. Verify: `pytest tests/architecture/test_workflow_security.py -q` → 0; `pytest tests/architecture/test_workflow_version_assertion.py -q` → 0; `make ci` end-to-end locally; apply-time re-fetch confirms `astral-sh/setup-uv@v5.4.2` SHA = `d4b2f3b6ecc6e67c4457f6d3e41ec42d3d0fcb86` and is recorded. Rollback: `git revert` PR4. Trace: "Deterministic CI Runner Bootstrap" (pinned SHA + assertion), "Least-Privilege GitHub Actions Delegation", apply-time re-verification.

- [ ] 4.1 Create `.github/workflows/ci.yml` with `on: push` and `on: pull_request` only (no `pull_request_target`); `permissions: contents: read` at top level; no `secrets:`; credential-free `actions/checkout`.
- [ ] 4.2 Pin `astral-sh/setup-uv@d4b2f3b6ecc6e67c4457f6d3e41ec42d3d0fcb86 # v5.4.2` with `with: version: "0.11.29"`; both SHA and version comment present.
- [ ] 4.3 Add a step that runs `uv self version --short`, asserts exact `0.11.29`; on mismatch exit non-zero and do NOT invoke `make ci`.
- [ ] 4.4 Add a single `make ci` step; workflow MUST NOT duplicate Ruff, Pyright, Pytest, audit, or license stages.
- [ ] 4.5 Create `tests/architecture/test_workflow_security.py` (static): triggers = `push`+`pull_request`; `permissions: contents: read`; no `pull_request_target`, no `secrets:`, no credential env vars; `astral-sh/setup-uv` has SHA `d4b2f3b6ecc6e67c4457f6d3e41ec42d3d0fcb86` AND comment `# v5.4.2`; `make ci` is the only project-validation command.
- [ ] 4.6 Apply-time authoritative re-verification (not a tracked test): before commit, re-fetch upstream `astral-sh/setup-uv` tag for v5.4.2, confirm SHA matches, record in verify report; on mismatch STOP and do NOT fall back to a tag reference or guessed SHA.
- [ ] 4.7 Create `tests/architecture/test_workflow_version_assertion.py` (static): a step exists whose command runs `uv self version --short` and `set -e`/fails before the `make ci` step.

---

## Phase 5: Post-Merge Hygiene

Start: PR1–PR4 all merged; `make ci` green; `openspec/config.yaml` still records the pre-harness capability table. Finish: `openspec/config.yaml` reflects the new table; Engram `sdd/rag/testing-capabilities` records the re-evaluation; verify report carries all six proofs; change ready for `sdd-archive`. Verify: `git diff governance/direct-dependencies.yaml` empty; `grep strict_tdd openspec/config.yaml` shows `false`; `make ci` → 0 in the verify report; Engram `mem_search "sdd/rag/testing-capabilities"` returns the latest observation. Rollback: revert Phase 5's `openspec/config.yaml` edit and the Engram upsert; durable baseline was never modified. Trace: "Bootstrap Scope and Strict TDD", durable-baseline preservation, `sdd-archive` readiness.

- [ ] 5.1 Update `openspec/config.yaml` `testing` block: `test_runner.available: true` `command: "make ci"` `framework: "pytest"`; `linter.available: true` `command: "ruff check"`; `formatter.available: true` `command: "ruff format --check"`; `type_checker.available: true` `command: "pyright"`; `unit: true`; `coverage: false`; `apply.tdd: false`; `apply.test_command: "make ci"`.
- [ ] 5.2 Leave `strict_tdd: false` and `testing.strict_tdd: false`; record the decision in Engram `sdd/rag/testing-capabilities` (`topic_key: sdd/rag/testing-capabilities`).
- [ ] 5.3 Confirm `governance/direct-dependencies.yaml` is byte-identical; record `git diff governance/` in the verify report; reconciliation test passes trivially.
- [ ] 5.4 Run `sdd-verify`; verify report MUST include: (a) `make ci` exit 0; (b) apply-time re-verification of `astral-sh/setup-uv` SHA; (c) focused-test guard proof (aliased skip in temp file fails); (d) audit wrapper classification table; (e) dependency-boundary map coverage proof; (f) recipe fail-fast proof (one staged failure per stage).
