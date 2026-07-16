# Design: Bootstrap OpsKnowledge Test Harness

## Technical Approach

Create a Python 3.12 development-only gate for `test-harness`. `uv.lock` is the resolution authority; local and remote validation share ordered `make ci`, which first requires `uv self version --short` to equal exactly `0.11.29`. GitHub Actions supplies and verifies the same deterministic prerequisite, then delegates its only project-validation command to `make ci`. No runtime, production dependency, provider, database, or web surface is created.

## Architecture Decisions

| Decision | Alternatives / trade-off | Choice and rationale |
|---|---|---|
| Environment binding | Frozen resolution does not pin the `uv` executable | Before every local `make ci` gate, require complete `uv self version --short` output exactly `0.11.29`; then use `uv sync --frozen --extra dev` and `uv run --frozen`. Installed-binary evidence shows both `uv -V` and `uv --version` include build metadata; `uv version --short` is project metadata. A mismatch prints the prescribed two-line remediation and stops before sync. |
| CI bootstrap | Ambient/latest uv is nondeterministic | After existing checkout, use `astral-sh/setup-uv@d4b2f3b6ecc6e67c4457f6d3e41ec42d3d0fcb86 # v5.4.2`, `version: "0.11.29"`, then assert the same exact `uv self version --short` output before `make ci`, which repeats the local assertion. GitHub's authoritative Astral tag resolves to this verified commit; apply re-verifies it. |
| Focused-test guard | A Pytest check is collection-skippable | Run `uv run --frozen python scripts/ci/check_focused_tests.py` before Pytest. Its AST resolver rejects prohibited forms and aliases across `tests/**/*.py`; allowlist empty. |
| Fail-fast proof | Manual observation is weak | `tests/ci/test_ci_fail_fast.py` copies the recipe, substitutes `UV ?= uv` sentinels, and proves every selected failure stops later stages. |
| Audit availability | Retry/suppression weakens the gate | `scripts/ci/run_vulnerability_audit.py` invokes `uv run --frozen pip-audit --local --strict` once, forwards output, and reports `success`, `vulnerability_finding`, `vulnerability_service_unavailable`, or `vulnerability_tool_failure`. All non-successes fail; recovery is the same command after restoration. |
| Dependency boundary | Distribution/import names diverge | `scripts/ci/check_dependency_boundaries.py` owns a reviewed normalized map: `langchain`/`langchain`, `llamaindex`/`llama_index`, `redis`/`redis`, `kubernetes`/`kubernetes`; policy-only exclusions are explicitly marked non-importable. Map omissions and unresolved excluded aliases fail visibly. |
| License posture | An allowlist invents approval | `pip-licenses` emits inventory evidence only. |
| Workflow security | Tags/default tokens are mutable/broad | Preserve existing `push`/`pull_request`, read-only permissions, credential-free checkout, no secrets/`pull_request_target`, and immutable version-commented action pins. |

## Data Flow

```text
local make ci -> exact uv self version --short assertion -> frozen sync -> focused guard -> Ruff -> Pyright
checkout -> setup-uv 0.11.29 -> uv self version --short assertion -> make ci
pyproject.toml + uv.lock -> frozen sync -> focused guard -> Ruff -> Pyright
  -> Pytest -> audit wrapper -> license inventory
```

The workflow's setup/assertion are prerequisites, not project validation. `Makefile` uses one fail-fast recipe and stage labels; its first stage compares complete `uv self version --short` output literally, rejects mismatch, suffix, multiline, malformed, unavailable, and command-error output, and emits the specified two-line remediation. The AST dependency scanner first validates complete policy-map coverage, resolves direct/imported/assigned aliases and literal dynamic imports, then emits `path:line: canonical-distribution`; unresolved excluded aliases are errors.

## File Changes

| File | Action | Description |
|---|---|---|
| `pyproject.toml`, `.python-version`, `uv.lock` | Create | Empty production set, Python 3.12, locked dev tools. |
| `Makefile`, `scripts/ci/check_focused_tests.py`, `scripts/ci/check_dependency_boundaries.py`, `scripts/ci/run_vulnerability_audit.py` | Create | Exact local uv assertion with deterministic remediation, then ordered locked gate and fail-closed helpers. |
| `.github/workflows/ci.yml` | Create | Existing secure adapter plus pinned uv bootstrap/assertion and `make ci`. |
| `tests/{unit,architecture,ci}/` | Create | Guard, dependency-map, audit-wrapper, and fail-fast tests. |
| `governance/direct-dependencies.yaml` | Validate only | Evidence remains unchanged. |

## Interfaces / Contracts

```python
EXCLUDED_IMPORT_ROOTS: dict[str, tuple[str, ...]]
# {"llamaindex": ("llama_index",), ...}

AuditResult = Literal[
    "success", "vulnerability_finding",
    "vulnerability_service_unavailable", "vulnerability_tool_failure",
]
```

`make ci` accepts only complete `uv self version --short` output `0.11.29`; mismatch, suffixed, multiline, malformed, unavailable, or command-error output emits the specified two-line error with captured `<actual>` (or `unavailable`) and returns non-zero before its first gate. The guard and dependency scanner return non-zero with stable path/line evidence. The audit wrapper accepts a subprocess seam for tests, calls it once, forwards output, and returns non-zero for every non-success classification.

## Testing Strategy

| Layer | What | Approach |
|---|---|---|
| Unit | Focus aliases; map normalization/coverage | Temporary files and table-driven fixtures, including `llama_index`. |
| Unit | Audit outcomes | Stub subprocess: success, finding, timeout, unavailable service, unexpected failure; assert classification, one call, non-zero, and success rerun. |
| CI recipe | Local executable-version parity, ordering/bootstrap | Stub `uv self version --short` for exact success and mismatch, suffixed, multiline, malformed, unavailable, and command-error output; assert exact remediation and no later invocation on failure. Static workflow test checks setup SHA/comment, selected version, `uv self version --short` assertion-before-`make ci`, and existing security boundary. |

## Migration / Rollout

No migration required. Apply re-verifies the action pin; if it cannot, it stops rather than using a tag or guessed SHA. Roll back by reverting the atomic harness commit. Strict TDD stays disabled until the next runtime change.

## Open Questions

- [ ] None.
