# Exploration: Bootstrap OpsKnowledge Test Harness

## Revision History

| Date (UTC) | Revision | Reason |
|---|---|---|
| 2026-07-15 | 1 | Initial exploration. Read-only investigation of the minimal Python / test / quality harness required before any roadmap implementation can start. Confirmed the change must precede all candidate roadmap changes (per Engram #3255). Scoped to packaging, lockfile, Pytest, Ruff, Pyright, architecture tests, `make ci`, dependency-governance reconciliation, and post-harness Strict TDD re-evaluation. Explicitly excludes frontend, PostgreSQL, Compose, cloud infrastructure, application features, and broad runtime implementation. |

## Purpose

Establish the smallest reviewable Python test and quality harness that makes every future OpsKnowledge implementation change safe and reviewable. The harness is the bootstrap gate that `AGENTS.md` (Testing, CI, and OpenAPI) and the roadmap ("Each implementation change must establish the test harness first, then re-evaluate Strict TDD") make non-negotiable. It must:

- introduce reproducible Python packaging and a lockfile without inventing or approving any production dependency
- run Ruff (lint + format), Pyright (type check), and Pytest (unit + architecture tests) from a single `make ci` entry point
- reconcile direct production dependencies against `governance/direct-dependencies.yaml` so unrecorded or `pending`-only entries fail `make ci`
- preserve all durable architecture, safety, evidence, and provider-failure invariants (no runtime, no PostgreSQL, no providers, no FastAPI app, no web client, no Compose, no corporate/Azure integration)
- re-evaluate Strict TDD after the runner exists, with the decision recorded in `openspec/config.yaml` and Engram `sdd/rag/testing-capabilities`

This exploration is read-only. No project file outside the OpenSpec change folder and the Engram observation is created.

---

## Current State

### What the repository actually has today

- **One commit, `c3cc223 chore: establish OpsKnowledge project baseline`, on the default branch `master`.** Tracked files (19) are: `AGENTS.md`, `RAG_ROADMAP.md`, `docs/architecture/platform-architecture.md`, `docs/brand/brand-guide.md`, `docs/prototypes/main-chat/{opendesign-prompt.md, visual-reference/{index.html, brand-spec.md, README.md}, assets/ParticleSphere.tsx}`, `governance/direct-dependencies.yaml`, `openspec/changes/archive/2026-07-15-reposition-rag-as-portfolio-platform/{proposal.md, exploration.md, supersession-index.md, tasks.md, design.md, verify-report.md, specs/opsknowledge-domain-contract/spec.md}`, and `openspec/specs/opsknowledge-domain-contract/spec.md`. `.gitignore` is the only other tracked file. `openspec/config.yaml` is staged as untracked from the prior session and is not yet committed.
- **No Python runtime, no test runner, no manifests, no lockfiles, no `Makefile`, no CI pipeline.** Engram testing baseline #3111 records all eight quality layers (test runner, unit, integration, e2e, coverage, linter, type checker, formatter) as `available: false`. `RAG_ROADMAP.md` Phase 0 completion notes and `AGENTS.md` Testing, CI, and OpenAPI both confirm this is the current state.
- **No `pyproject.toml`, no `uv.lock`, no `package.json`, no `pnpm-lock.yaml`.** `governance/direct-dependencies.yaml` is therefore an evidence-only record: CI cannot reconcile it against anything because no manifest exists yet. This is the bootstrap problem this change resolves.
- **Dependency governance is fully specified but un-enforced.** The yaml records seven `approved` production entries (fastapi, sqlalchemy, psycopg, alembic, pgvector, docling, openai), one `pending` entry (azure-identity), and seven `excluded` entries. It states the reconciliation rule: "for every direct production import found in pyproject.toml / package.json, there MUST be an entry here whose `name` matches and whose `approval.decision` is `approved`. A `decision: pending` entry ... MUST fail CI." The rule needs a `pyproject.toml` to operate on; this change creates that manifest.
- **The OpenSpec change folder convention is established and one archived change exists** (`2026-07-15-reposition-rag-as-portfolio-platform`), with the full proposal / exploration / spec / design / tasks / verify / supersession-index shape. New changes follow the same shape under `openspec/changes/{change-name}/`.
- **Engram state is live**: `sdd-init/rag` (#3374), `sdd/rag/testing-capabilities` (#3111), and the prior `bootstrap-opsknowledge-test-harness` decision is anchored in #3255. The decision instructs the next session to "start a new SDD change named `bootstrap-opsknowledge-test-harness` before roadmap implementation" and "decide repository initial branch/first commit only when explicitly requested."
- **CodeGraph index is initialized at `.codegraph/`** but indexes no Python source because no Python source exists. It is read-only intelligence and is irrelevant to the harness contract; it is not a CI dependency.

### What the AGENTS.md and roadmap invariant hierarchy requires

`AGENTS.md` (highest authority) and `RAG_ROADMAP.md` (second highest) together define the harness boundary. The exact rule, quoted from `AGENTS.md` Testing, CI, and OpenAPI:

> **Bootstrap invariant (future):** when a runtime stack exists, `make ci` SHALL restore locks, reconcile dependency evidence, and run Ruff, Pyright, unit, architecture, integration, OpenAPI/client drift, focused-test prohibition, vulnerability, and license checks.

The roadmap's Phase 0 completion notes and `RAG_ROADMAP.md` §Next step repeat the rule: "Each implementation change must establish the test harness first, then re-evaluate Strict TDD."

The exploration must scope to the **first** implementation change. The very next section of `AGENTS.md` says: "No runtime stack or test runner exists yet. Implementation changes must establish the test harness first, then re-evaluate Strict TDD." This change is that bootstrap.

The instruction hierarchy in `AGENTS.md` puts SDD spec / design artifacts below `AGENTS.md` and the roadmap. The exploration therefore must NOT add a new direct production dependency that the yaml does not approve, MUST NOT introduce any `excluded` dependency (LangChain, LlamaIndex, Redis, queues, Kubernetes, microservices, streaming, visual interpretation, email/Notifier, unevidenced reranking), and MUST NOT cross the prototype / corporate boundary (no Azure integration, no Entra wire-up, no real OpenAI key).

The CI check list from the bootstrap invariant is the acceptance surface for the change. The exploration must surface which of those checks are in scope now (the harness can run them) and which remain future capabilities (because no runtime / OpenAPI artifact / web client exists).

### What already exists vs. what the change must build

| Bootstrap check | Status today | In scope for this change |
|---|---|---|
| `make ci` entry point | absent | **yes** — create |
| `pyproject.toml` (PEP 621) | absent | **yes** — create as packaging surface only |
| Reproducible lockfile | absent | **yes** — create via uv |
| Pytest test runner | absent | **yes** — add as dev tool only |
| Ruff (lint + format) | absent | **yes** — add as dev tool only |
| Pyright (type check) | absent | **yes** — add as dev tool only |
| Architecture tests (import-boundary tests against `domain`/`application` purity, dependency direction, excluded-dep sweep) | absent | **yes** — add as dev-only test path |
| Dependency governance reconciliation | absent | **yes** — `make ci` reconciles `pyproject.toml` direct production deps against `governance/direct-dependencies.yaml` |
| Unit tests | absent | **yes** — at least one demonstrative unit test so the runner is real |
| Vulnerability scan | absent (no lockfile) | **partial** — `pip-audit` against the dev lockfile only; production vulnerability scan stays future because no production deps are introduced |
| License scan | absent | **partial** — `pip-licenses` over the dev lockfile as proof; production license scan stays future |
| Focused-test prohibition (ban on `.only` / `pytest.skip` outside approved contexts) | absent | **yes** — add as a small lint-style architecture test |
| Integration tests | absent | **out of scope** — require a runtime, which the next change establishes |
| OpenAPI / client drift | absent | **out of scope** — no FastAPI app, no web client, no OpenAPI artifact yet (per `AGENTS.md` §OpenAPI future bootstrap acceptance gate) |
| PostgreSQL / Compose / Docker | absent | **out of scope** — explicitly excluded from this change |
| FastAPI / SQLAlchemy / pgvector / Docling / OpenAI | absent | **out of scope** — these are the next bounded changes' concern; introducing them now would cross the prototype/corporate boundary unprovably and would invent production dependency approvals |

### Skill resolution for the exploration

- `sdd-explore` — read; used as the contract for this phase and the persistence rules.
- `_shared/sdd-phase-common.md` — read; used for retrieval and persistence rules.
- `_shared/openspec-convention.md` — read; used to determine the file path and write rules.
- `cognitive-doc-design` — read; applied for the artifact's progressive disclosure (purpose → current state → affected areas → approaches → recommendation → risks → readiness).
- `python-backend-mastery` — read; used to anchor the packaging and Pytest/Ruff/Pyright choices on established patterns (Pytest fixtures, `pyproject.toml` `[project.optional-dependencies]` separation of dev vs. prod deps, Pydantic-friendly venv). The skill is centered on FastAPI/SQLAlchemy/Pydantic implementation, none of which is in this change, but the **packaging and dev-tooling** rules transfer.
- `go-testing` — read; **not applicable**. The RAG project is Python; this skill encodes Go (`t.TempDir`, `teatest`, table-driven Go) and would conflict if applied.

---

## Affected Areas

The change introduces a small set of new files inside the change folder and one canonical set of new files at the repository root. It does NOT modify any existing file in the durable baseline (`AGENTS.md`, `RAG_ROADMAP.md`, `docs/architecture/platform-architecture.md`, `governance/direct-dependencies.yaml`, `openspec/specs/`, `openspec/config.yaml`).

| File / artifact | New / Modified | Role |
|---|---|---|
| `openspec/changes/bootstrap-opsknowledge-test-harness/proposal.md` | New | Bounded SDD proposal for the harness |
| `openspec/changes/bootstrap-opsknowledge-test-harness/exploration.md` | New (this file) | Read-only investigation, persisted for audit |
| `openspec/changes/bootstrap-opsknowledge-test-harness/specs/test-harness/spec.md` | New | Delta spec — Harness requirements and scenarios |
| `openspec/changes/bootstrap-opsknowledge-test-harness/design.md` | New | Technical design: toolchain versions, project layout, `make ci` command contract, dependency-reconciliation script |
| `openspec/changes/bootstrap-opsknowledge-test-harness/tasks.md` | New | Task plan with line-count forecast and chained-PR plan |
| `openspec/changes/bootstrap-opsknowledge-test-harness/verify-report.md` | New (during sdd-verify) | Evidence `make ci` ran end-to-end |
| `pyproject.toml` | New (root) | PEP 621 packaging, dev-tool extras, Ruff/Pyright/Pytest config, NO direct production dependencies |
| `uv.lock` | New (root) | Reproducible lockfile generated by `uv` |
| `Makefile` | New (root) | `make ci` orchestrator — single entry point |
| `tests/` | New (root) | Unit and architecture test discovery root |
| `tests/conftest.py` | New | Shared Pytest fixtures (e.g. project root resolution, dependency-governance loader) |
| `tests/unit/test_smoke.py` | New | At least one demonstrative unit test (proves the runner works) |
| `tests/architecture/test_dependency_direction.py` | New | Architecture test: production code (none yet) does not import excluded deps or dev-only tooling |
| `tests/architecture/test_dependency_governance.py` | New | Architecture test: reconciles `pyproject.toml` direct prod deps against `governance/direct-dependencies.yaml` |
| `tests/architecture/test_focused_test_prohibition.py` | New | Architecture test: no `pytest.mark.skip` or `pytest.mark.only` outside a documented allowlist |
| `tests/architecture/__init__.py` | New | Empty package marker (test discovery) |
| `tests/unit/__init__.py` | New | Empty package marker (test discovery) |
| `pyrightconfig.json` (or `[tool.pyright]` in `pyproject.toml`) | New | Pyright config, strict mode, `pythonVersion` matching the dev runtime |
| `.python-version` | New | Pin for `uv python pin` / `pyenv` consistency |
| `.github/CODEOWNERS` | New (optional) | Codifies AGENTS.md as the contributor contract owner (small, low-risk addition) — *defer to apply if user asks* |
| `.github/workflows/ci.yml` | New (optional) | CI that runs `make ci` on push/PR — *defer to apply if user asks* |
| `governance/direct-dependencies.yaml` | **NOT modified** | Evidence file stays intact; this change adds no production dependency |
| `openspec/config.yaml` | **NOT modified** | Strict TDD re-evaluation is recorded **after** the runner exists; this change proposes a re-evaluation in a small follow-up edit, not a self-contradicting edit |
| `openspec/specs/opsknowledge-domain-contract/spec.md` | **NOT modified** | The active domain contract stays intact |
| `AGENTS.md`, `RAG_ROADMAP.md`, `docs/architecture/platform-architecture.md` | **NOT modified** | All durable baseline content is preserved |
| Engram `sdd/rag/testing-capabilities` (#3111) | Updated (during apply / verify) | Records the new capabilities and the re-evaluated Strict TDD decision |

### Excluded surfaces (intentionally NOT touched)

- Backend runtime, FastAPI app, SQLAlchemy models, Alembic migrations, pgvector, Docling wiring, OpenAI / Azure OpenAI client.
- Frontend, React, Vite, TypeScript, OpenAPI artifact, generated client.
- PostgreSQL, Docker Compose, image manifests, infrastructure-as-code.
- Entra ID wire-up, Managed Identity, Key Vault, Bicep, any TI-gated value.
- The `excluded:` list in `governance/direct-dependencies.yaml` (LangChain, LlamaIndex, Redis, queues, Kubernetes, microservices, streaming, visual interpretation, email/Notifier, unevidenced reranking).
- The `pending:` entry (azure-identity) — this change does not import it.
- `.codegraph/`, `.atl/`, `docs/prototypes/`, `docs/brand/` — all out of scope.

---

## Approaches

This section compares three packaging / runner / governance strategies. The recommendation is at the end.

### Approach A — `uv` + `pyproject.toml` + standard Pytest / Ruff / Pyright + `make ci` reconciliation (RECOMMENDED)

**Stack**: `uv` for environment and lockfile management; `pyproject.toml` as the single manifest; `pytest` as the test runner; `ruff` (lint + format) and `pyright` (strict) as the quality tools; `pip-audit` and `pip-licenses` as dev-lockfile-only vulnerability and license checks; a small Python `make ci` target that orchestrates them; a custom Python module under `tests/architecture/` that reconciles `pyproject.toml` direct production dependencies against `governance/direct-dependencies.yaml`.

**Why this wins**:

- `uv` is a single, fast, reproducible tool already standard in modern Python monorepos; it produces `uv.lock` directly and resolves environments from a `pyproject.toml` `requires-python` pin.
- All four core tools (Pytest, Ruff, Pyright, `uv`) are MIT-licensed, no-network-by-default-friendly, and not in the `excluded:` list.
- This stack is the **only** stack that lets the change satisfy the bootstrap-invariant CI list (Ruff, Pyright, unit, architecture, focused-test prohibition, vulnerability, license) **without introducing a single direct production dependency**. All tooling lives under `[project.optional-dependencies] dev` in `pyproject.toml`; the `direct-dependencies.yaml` reconciliation script reads only `[project.dependencies]` (production) and verifies the match.
- `make ci` is a `Makefile` target, which the bootstrap invariant already names; the Makefile stays small (one file, one target, calls a Python orchestrator).
- Architecture tests are written in plain Pytest, with no extra dependency, so they cannot introduce an ungoverned import.

**Pros**:

- Minimal surface: 1 manifest, 1 lockfile, 1 Makefile, ~5 test files, 1 Pyright config, 1 Python-version pin. Total new tracked lines ≈ 350–550.
- The reconciliation script is a plain Python test that uses only the standard library (`tomllib`, `pathlib`, `yaml` is a dev-only import, see risk below) — keeps the governance test honest without smuggling governance logic into the production path.
- Easy rollback: a single `git revert` of the change's commit removes the entire harness.
- Sets a clear pattern: every future bounded change adds a feature module and its tests, not new dev-tooling.

**Cons**:

- `pyyaml` is needed by the governance test. It MUST live under `[project.optional-dependencies] dev` (dev tool, not production), so it does NOT appear in `governance/direct-dependencies.yaml` (per the file's explicit rule: "Do not record dev-only, test-only, lint, or type-check tools here").
- `pip-audit` and `pip-licenses` introduce a one-time risk that they may surface advisories on transitive dev deps. The script should fail loudly so the apply phase can decide whether to suppress or upgrade. A pre-flight advisory check on the chosen tool versions is required during the design phase.
- The Makefile introduces a small build-tool choice. It is not in any `excluded:` list, and it is the bootstrap-invariant entry point, so it is justified.

**Effort**: Low–Medium. Most of the work is in the design and the verification run; the implementation is small.

### Approach B — `poetry` + `pyproject.toml` + `tox` for matrix + `pre-commit` (REJECTED for first change)

**Stack**: `poetry` for env + lockfile, `tox` for matrix testing across Python versions, `pre-commit` for lint hooks.

**Why this is rejected for THIS change**: it adds two extra tools (`tox`, `pre-commit`) without improving the bootstrap invariant's required checks (Ruff, Pyright, unit, architecture, focused-test prohibition, vulnerability, license). `tox` is useful when multiple Python versions must be supported, but the active Python version is not yet pinned by the durable baseline; deferring version matrix to a later change is safer. `pre-commit` duplicates the local vs. CI parity that `make ci` already enforces. Adding both now would grow the change to ~700–900 lines and exceed the 800-line review budget. A follow-up change can add them if a matrix is needed.

**Pros**: multi-version matrix; pre-commit local enforcement.

**Cons**: 700–900 line forecast is at or over the active 800-line budget; two extra toolchains to govern; no incremental value for the first change.

### Approach C — `nox` + `pyproject.toml` + hand-rolled `bash` `make ci` (REJECTED)

**Stack**: `nox` for orchestrating `make ci` sessions; hand-rolled bash reconciliation in the Makefile.

**Why this is rejected**: `nox` overlaps with `make ci`'s role; replacing `make` with `nox` violates the bootstrap invariant, which names `make ci` as the entry point. Hand-rolled bash reconciliation is harder to test than a Python `tests/architecture/test_dependency_governance.py` and tends to drift from the yaml schema. Both choices add complexity without value.

**Pros**: `nox` is more Pythonic.

**Cons**: violates the named entry point; bash reconciliation is hard to test; no incremental value.

---

## Recommendation

**Recommend Approach A: `uv` + `pyproject.toml` + standard Pytest / Ruff / Pyright + `make ci` + a Python governance-reconciliation architecture test.**

### Concrete shape of the change

- **`pyproject.toml`** — PEP 621, Python 3.12 (latest stable as of 2026-07), `[project]` has `name = "opsknowledge"`, `requires-python = ">=3.12,<3.13"`, `dependencies = []` (empty by design — no production deps), `[project.optional-dependencies] dev = [...]` with the dev toolchain. `[tool.ruff]`, `[tool.pytest.ini_options]`, `[tool.pyright]` live inline.
- **`uv.lock`** — generated by `uv lock` from the dev extras; reproducible; committed.
- **`.python-version`** — `"3.12"` for `uv python pin` consistency.
- **`Makefile`** — single target `ci` (plus `lock`, `test`, `lint`, `typecheck`, `audit` as helpers). `make ci` runs: `uv sync --frozen` → `ruff check` → `ruff format --check` → `pyright` → `pytest` (unit + architecture) → `pip-audit` (dev lockfile) → `pip-licenses` (dev lockfile). Exit non-zero on any failure.
- **`tests/conftest.py`** — adds the project root to `sys.path` if needed; provides a `pyproject_text` and `governance_yaml` fixture.
- **`tests/unit/test_smoke.py`** — at least one demonstrative unit test (e.g. asserts the project root resolves to a directory containing `AGENTS.md` and `RAG_ROADMAP.md`). Proves the runner is real.
- **`tests/architecture/test_dependency_direction.py`** — asserts that no file under any future `src/opsknowledge/` (which does not yet exist; the test is a stub that passes) imports anything in the `excluded:` list. Today, the test passes trivially because there is no source. The intent is to lock the direction now so future implementation changes cannot smuggle LangChain / LlamaIndex / Redis / etc. in.
- **`tests/architecture/test_dependency_governance.py`** — parses `pyproject.toml` `[project.dependencies]`, parses `governance/direct-dependencies.yaml`, asserts: (a) every entry in `pyproject.toml` matches a `decision: approved` entry in the yaml, (b) no `pending` entry appears in `pyproject.toml`, (c) no `excluded` entry appears in `pyproject.toml`. Today, with `dependencies = []`, all three assertions pass trivially. The intent is to fail the build the moment a future change adds an unapproved prod dep.
- **`tests/architecture/test_focused_test_prohibition.py`** — scans `tests/` for `pytest.mark.only`, `pytest.mark.skip(reason=...)` outside an explicit allowlist, and `@pytest.mark.xfail` outside an allowlist. Fails on any match. Today, the smoke test does not use any of these markers; the test passes.
- **`tests/unit/__init__.py`**, **`tests/architecture/__init__.py`** — empty package markers.
- **`.gitignore` (root)** — adds `.venv/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `.pyright_cache/`, `.uv-cache/`, `*.egg-info/`, `dist/`, `build/`, `.tox/` (for future), `htmlcov/`, `.coverage` (for future). All local / generated; none enter the durable baseline.
- **`openspec/changes/bootstrap-opsknowledge-test-harness/specs/test-harness/spec.md`** — delta spec for the harness, with Given/When/Then scenarios for: packaging, lockfile reproducibility, Ruff, Pyright, Pytest unit, Pytest architecture, focused-test prohibition, dependency-governance reconciliation, vulnerability scan, license scan, and the `make ci` exit-code contract. Follows the `sdd-spec` skill template and the openspec-convention.md `## ADDED Requirements` shape.
- **`openspec/changes/bootstrap-opsknowledge-test-harness/design.md`** — technical design: toolchain versions, project layout, the `make ci` command contract, the governance-reconciliation algorithm, the failure modes, and the Strict TDD re-evaluation plan.
- **`openspec/changes/bootstrap-opsknowledge-test-harness/tasks.md`** — task plan grouped by phase (harness, dev tools, governance, verification, re-evaluation), with the line-count forecast and the chained-PR plan presented under the active `ask-always` strategy.
- **Engram `sdd/rag/testing-capabilities`** — updated at the verify phase with the new capability table, the re-evaluated Strict TDD decision (the recommendation is `strict_tdd: false` for the harness change itself, and `strict_tdd: true` re-evaluated for future runtime changes once a runtime exists, but that re-evaluation is a separate concern and is described, not imposed, here).

### Why Approach A wins on the four criteria

- **Minimal**: ~350–550 new tracked lines, well under the 800-line review budget. No chained PRs are required.
- **Honest about production deps**: by writing `dependencies = []` in `[project]` and putting the entire toolchain in `[project.optional-dependencies] dev`, the change does not introduce a single direct production dependency. The governance reconciliation test is honest from day one: it has nothing to reconcile yet, and it will fail the build the moment a future change adds an unapproved prod dep.
- **Aligned with the instruction hierarchy**: the change preserves every AGENTS.md and roadmap invariant (no excluded dep, no production dep, no corporate wire-up, no streaming, no Redis, no LangChain, no LlamaIndex, no Kubernetes, no TI-gated value, no synthetic corpus exception triggered, no email/Notifier, no visual interpretation, no Azure, no OpenAI key).
- **Reversible**: a single `git revert` of the harness commit removes the entire change. The durable baseline (`AGENTS.md`, `RAG_ROADMAP.md`, platform-architecture, governance yaml, OpenSpec specs) is untouched, so revert cannot leave the durable baseline in an inconsistent state.

### Why no other change is required first

- The harness is **independent of the prototype / corporate boundary**: it introduces no provider, no synthetic corpus, no profile wiring. It is safe to run from the default `master` branch in any environment.
- The harness is **independent of the modular monolith shape**: it does not create `backend/`, `web/`, `compose/`, or any feature module. The monorepo tree remains a planning reference, not a filesystem claim, until a future change creates it.
- The harness is **independent of the OpenAPI future bootstrap gate**: the OpenAPI artifact path (`apps/api/openapi/openapi.json`) and the client path (`apps/web/src/api/generated.ts`) remain future bootstrap acceptance gates. The harness does not produce them and does not check them.

### What the follow-up proposal must do

The bounded proposal that follows this exploration should:

1. Lock the recommended stack: `uv`, `pyproject.toml`, `pytest`, `ruff`, `pyright`, `Makefile`, `pip-audit`, `pip-licenses`, `pyyaml` (dev only).
2. Lock the Python version (3.12) — this is the first project-wide version pin and should be confirmed with the user under the instruction hierarchy.
3. Lock the test architecture: `tests/unit/`, `tests/architecture/`, the three architecture tests, the focused-test prohibition.
4. Lock the `make ci` command contract with the exact invocation order and the exact failure semantics.
5. Lock the dependency-governance reconciliation algorithm in a way that any future change can extend without rewriting the test.
6. Confirm the active review budget (800) and forecast the actual line count at the tasks phase. Under `ask-always`, the proposal must present the chained-PR plan to the user if the forecast exceeds 800, but the central forecast (~450) is comfortably under and chained PRs are not strictly required.
7. Re-evaluate Strict TDD after the harness exists. The recommendation is `strict_tdd: false` for the harness change (the harness is itself a TDD-neutral setup change), and `strict_tdd: true` to be re-evaluated for the next bounded change that introduces a runtime. The proposal should record this plan but should NOT mark `strict_tdd: true` today, because no runtime exists to write tests against.
8. Stay within scope: no production dependency, no runtime, no PostgreSQL, no Compose, no FastAPI app, no web client, no corporate Azure integration, no TI-gated value, no synthetic corpus ingestion, no excluded dependency, no email/Notifier, no streaming, no visual interpretation, no unevidenced reranking.

---

## Open Decisions for the Follow-up Proposal

The bounded proposal must confirm these with the user before it is written. They are not invented by this exploration.

1. **Python version** — confirm 3.12 (the latest stable that `uv` supports and that has the cleanest `pyright --strict` + `tomllib` + PEP 621 story). The user may prefer 3.11 for compatibility.
2. **Tooling versions** — confirm the chosen `uv`, `ruff`, `pyright`, `pytest`, `pip-audit`, `pip-licenses`, `pyyaml` versions. The user may have a preferred pin.
3. **Make vs. invoke vs. task runner** — `make` is named in the bootstrap invariant. Confirm `make` (preferred) vs. `invoke` vs. a Python `__main__`. `make` is recommended.
4. **CI provider** — the bootstrap invariant names the CI checks but not the provider. The change does NOT need to add `.github/workflows/ci.yml` today (that is a future change with its own SDD lifecycle). Confirm deferral.
5. **`.gitignore` scope** — confirm the local-only additions (`.venv/`, `__pycache__/`, `.pytest_cache/`, etc.) are added in the same change or a follow-up. Same change is recommended for atomicity.
6. **Strict TDD re-evaluation timing** — re-evaluate in this change's verify phase (recorded in Engram and a follow-up `openspec/config.yaml` edit) or in a separate bounded change. The recommendation is **record the plan in this change's verify phase** but do NOT enable Strict TDD today; the next bounded change (the runtime bootstrap) re-enables it.
7. **Pre-commit hooks** — defer to a follow-up change. Confirm deferral.
8. **`pyrightconfig.json` vs. inline `[tool.pyright]`** — recommend inline `[tool.pyright]` in `pyproject.toml` to keep the manifest count to one. Confirm.

---

## Review Workload Forecast

| Field | Value |
|---|---|
| Change name | `bootstrap-opsknowledge-test-harness` |
| This exploration artifact | Engram topic `sdd/bootstrap-opsknowledge-test-harness/explore` (English) + `openspec/changes/bootstrap-opsknowledge-test-harness/exploration.md` (English) |
| Active review budget | **`review_budget_lines: 800`** (selected at session preflight) |
| Delivery strategy | `ask-always` (selected at session preflight) |
| Estimated changed lines in follow-up proposal / spec / design / tasks | 350–550. Central case ≈ 450. |
| 800-line budget risk | **Low** — upper bound (550) is well under the active 800-line budget. Chained PRs are NOT required by the budget rule. |
| Chained PRs recommended | **Not required**. The change is atomic by design and naturally reviewable in one PR. Under `ask-always`, the user may still ask for a chained split, but the central case does not need one. |
| 400-line default guard | The change stays above the default 400-line guard; the active budget is 800 (per session preflight), so the guard is satisfied. |
| Verification plan | `make ci` exit zero; `governance/direct-dependencies.yaml` unchanged; `openspec/specs/opsknowledge-domain-contract/spec.md` unchanged; `AGENTS.md` / `RAG_ROADMAP.md` / `docs/architecture/platform-architecture.md` unchanged; Engram `sdd/rag/testing-capabilities` updated with the new capability table and the re-evaluated Strict TDD decision. |

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| `pyyaml` is needed for the governance test and could be mis-classified as production | Low | High | `pyyaml` is added under `[project.optional-dependencies] dev`, NOT `[project.dependencies]`. The governance test reconciles only `[project.dependencies]` against the yaml; the dev extra is not in scope for the file. The dev classification is asserted in the apply phase. |
| `pip-audit` or `pip-licenses` finds advisories or license issues on transitive dev deps | Medium | Low | The dev-only advisories do not affect production (no production deps). The `make ci` failure is loud, so the apply phase can decide to suppress, upgrade, or pin. The design phase will pre-flight a chosen-version check. |
| The Python 3.12 pin becomes stale or conflicts with a future corporate runtime | Low | Low | The pin lives in `pyproject.toml` and `.python-version`; both are easily changed by a follow-up bounded change. The pin is the first project-wide version pin and is the user's call (see Open Decisions). |
| The `make ci` order grows over time and becomes a hidden contract | Medium | Medium | The `make ci` recipe is a single Makefile target with explicit subcommands; the design phase records the contract. Future additions go through a bounded change that updates both the Makefile and the design doc. |
| Architecture tests are written today but pass trivially (no source exists), and a future change silently weakens them | Low | Medium | The architecture tests assert specific structures (no `pytest.mark.only`, no excluded dep, no unapproved prod dep). A future change that weakens them must justify the change in its own SDD proposal; the durable baseline is the contract. |
| The follow-up proposal adds a direct production dependency "for convenience" | Medium | High | The proposal is the right place to raise that question, and `AGENTS.md` requires a new SDD change for every excluded dependency or any direct production dep. The apply phase refuses any `git diff` that adds a `[project.dependencies]` entry without a matching `decision: approved` yaml entry. |
| The user wanted a different runner (e.g. `nox`, `tox`, `hatch`) | Low | Medium | The exploration presents three approaches and recommends `uv` + `pytest` + `ruff` + `pyright` + `make`. The user can pick a different toolchain; the proposal will then rewrite the design. |
| The OpenSpec `openspec/config.yaml` re-evaluation of Strict TDD is mis-applied to the harness change | Medium | Medium | The harness change updates `openspec/config.yaml` only AFTER `make ci` has run end-to-end (in the verify phase), and only to record the re-evaluation; the recommendation is `strict_tdd: false` for the harness change itself, with a separate decision for the next bounded runtime change. |
| `ruff format` re-formats the existing `docs/` markdown and creates a giant diff | Low | Low | Ruff formats Python only. Markdown and YAML are out of Ruff's scope. The exploration confirms this. |
| `.gitignore` additions are incomplete and generated files leak into future commits | Low | Low | The additions follow the standard Python dev-tool ignore list. A follow-up bounded change can add or remove entries. |

---

## Ready for Proposal

**Yes, with explicit preconditions.** The bounded proposal that follows this exploration should:

1. **Ask the user to confirm the eight open decisions** (Python version, tool versions, Make vs. invoke, CI provider deferral, .gitignore scope, Strict TDD timing, pre-commit deferral, pyright config placement).
2. **Forecast the 800-line review budget** explicitly in `tasks.md`. Central case ≈ 450 lines. Chained PRs are NOT required; under `ask-always` the user may still ask for a split.
3. **Lock the `make ci` command contract** with the exact invocation order and exit-code semantics, recorded in `design.md`.
4. **Lock the governance-reconciliation algorithm** so a future change can extend it without rewriting the test.
5. **Stay within scope**: no production dependency, no runtime, no PostgreSQL, no Compose, no FastAPI app, no web client, no corporate Azure integration, no TI-gated value, no synthetic corpus ingestion, no excluded dependency, no email/Notifier, no streaming, no visual interpretation, no unevidenced reranking.
6. **Re-evaluate Strict TDD** in the verify phase and record the decision in Engram `sdd/rag/testing-capabilities` and `openspec/config.yaml`. The recommendation is `strict_tdd: false` for the harness change; the next bounded change (runtime bootstrap) re-enables it.
7. **Preserve the durable baseline**: `AGENTS.md`, `RAG_ROADMAP.md`, `docs/architecture/platform-architecture.md`, `governance/direct-dependencies.yaml`, `openspec/specs/opsknowledge-domain-contract/spec.md` are NOT modified.
8. **Reference the prior decisions**: this change follows `define-rag-platform-architecture` (#3161, #3162, #3163, #3194) and the OpsKnowledge domain contract (#3226, #3227, #3228, #3229). It does not supersede any prior change.

**Implications for later phases**:

- After this change is archived, the next bounded changes (`build-minimal-grounded-opsknowledge-core` and similar) can introduce a single direct production dependency each, with the governance test failing the build if the dep is not in the yaml as `decision: approved`. The first such change is the one that adds FastAPI / SQLAlchemy / psycopg / pgvector / Docling / OpenAI as the runtime stack.
- Strict TDD re-evaluation belongs to the **next** bounded change (the runtime bootstrap), not this one.
- OpenAPI artifact and client drift checks belong to a **later** bounded change (the FastAPI app bootstrap), not this one.
- The `make ci` orchestrator is extensible: future checks (e.g. `bandit` for Python security lint, `mypy` as a Pyright alternative, `pytest-cov` for coverage) can be added by future bounded changes that justify them.

**Do not start the proposal until the user confirms the eight open decisions.** This is a change that introduces the first project-wide version pin (Python 3.12) and the first build-tool choice (Make); both are user-callable.

---

## Cross-References

- Project context: Engram #3374 (sdd-init/rag).
- Testing baseline: Engram #3111 (sdd/rag/testing-capabilities).
- Prior decision anchoring this change: Engram #3255 (session summary: "Defer `bootstrap-opsknowledge-test-harness` to the next session before starting roadmap implementation").
- Roadmap: `RAG_ROADMAP.md` (full file read; Phase 0 completion notes and §Next step require this change before implementation).
- Contributor contract: `AGENTS.md` (full file read; §Testing, CI, and OpenAPI names the bootstrap invariant).
- Architecture reference: `docs/architecture/platform-architecture.md` (full file read; §Monorepo tree and §OpenAPI future bootstrap define the targets but do not require them in this change).
- Dependency governance: `governance/direct-dependencies.yaml` (full file read; this change introduces no direct production dependency, so the file is preserved verbatim).
- OpenSpec convention: `openspec/specs/opsknowledge-domain-contract/spec.md` (full file read; the active domain contract is preserved).
- OpenSpec change-folder convention: `openspec/changes/archive/2026-07-15-reposition-rag-as-portfolio-platform/{exploration,proposal,design,tasks,verify-report,supersession-index}.md` (read as a template for the new change).
- Skill resolution: `sdd-explore` (read), `_shared/sdd-phase-common.md` (read), `_shared/openspec-convention.md` (read), `cognitive-doc-design` (read), `python-backend-mastery` (read), `go-testing` (read; not applicable).

## Skill Resolution

- `sdd-explore` — read; used as the contract for the explore phase and the persistence rules.
- `_shared/sdd-phase-common.md` — read; used for retrieval and persistence rules.
- `_shared/openspec-convention.md` — read; used to determine the file path and write rules.
- `cognitive-doc-design` — read; applied for the artifact's progressive disclosure (purpose → current state → affected areas → approaches → recommendation → risks → readiness).
- `python-backend-mastery` — read; applied for packaging and dev-tooling patterns. The skill's primary scope (FastAPI / SQLAlchemy / Pydantic implementation) is out of scope for this change, but the **packaging and `[project.optional-dependencies]` separation** rules transfer directly.
- `go-testing` — read; **not applicable**. The RAG project is Python; the skill encodes Go patterns (`t.TempDir`, `teatest`, table-driven Go) and would conflict if applied.
