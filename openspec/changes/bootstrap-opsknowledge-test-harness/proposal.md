# Proposal: Bootstrap OpsKnowledge Test Harness

## Intent

Establish the smallest reproducible Python quality harness before runtime work begins. This makes future implementation reviewable through one local and remote contract while preserving the documented architecture, safety, and dependency-governance boundaries.

## Scope

### In Scope
- Python 3.12 packaging via `pyproject.toml`, an exact-pinned development-tool lockfile, and Pytest, Ruff, and Pyright configuration (Pyright inline in `pyproject.toml`).
- Unit and architecture tests for dependency direction, focused-test prohibition, and reconciliation of production dependencies against `governance/direct-dependencies.yaml`.
- A Makefile whose `make ci` restores the frozen lock and runs all available quality, governance, dev-lock vulnerability, and license checks.
- A thin GitHub Actions workflow that invokes `make ci` without duplicating its logic.

### Out of Scope
- Frontend, PostgreSQL, Compose, cloud infrastructure, application features, and broad runtime implementation.
- Direct production dependencies or changes to dependency approvals; development tools remain outside the governance evidence record.
- Integration tests, OpenAPI/client drift, pre-commit hooks, and enabling Strict TDD. Strict TDD is re-evaluated with the next runtime change.

## Capabilities

### New Capabilities
- `test-harness`: Reproducible Python quality, test, and dependency-governance gate exposed through `make ci`.

### Modified Capabilities
- None.

## Approach

Use `uv` with Python 3.12 and a committed lockfile; keep all tooling development-only and exactly pinned in the lock. Add Pytest, Ruff, Pyright, architecture tests, and dev-lock audit/license checks behind Make targets. GitHub Actions remains a thin adapter over `make ci`, preventing local/remote drift.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `pyproject.toml`, `uv.lock`, `.python-version` | New | Packaging, exact development-tool resolution, and inline Pyright configuration. |
| `tests/` | New | Smoke, architecture, and governance reconciliation tests. |
| `Makefile`, `.github/workflows/ci.yml` | New | Single CI contract and thin remote invocation. |
| `governance/direct-dependencies.yaml` | Validated only | No approval or dependency entry changes. |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Dev-lock audit/license findings block CI | Medium | Resolve or explicitly govern findings during implementation; do not weaken checks. |
| Architecture tests initially have no runtime source to inspect | Low | Keep narrow, durable checks and extend them with each runtime change. |

## Rollback Plan

Revert the harness commit as one unit; it adds no runtime behavior, production dependency, data migration, or durable baseline change.

## Dependencies

- Python 3.12 and a GitHub Actions runner capable of invoking `make ci`.

## Success Criteria

- [ ] `make ci` reproduces the locked development environment and exits non-zero for quality or governance failures.
- [ ] GitHub Actions invokes `make ci` successfully without duplicating validation commands.
- [ ] No direct production dependency or dependency-approval record is added.
