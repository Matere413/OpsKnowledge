# Tasks: Minimal Grounded OpsKnowledge Core

## Review Workload Forecast

| Field | Value |
|---|---|
| Estimated changed lines | 520–680 authored lines, excluding OpenSpec artifacts |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 corpus boundary; PR 2 query safety/provider; PR 3 CLI/dependency wiring |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|---|---|---|---|---|---|
| 1 | Corpus loading and boundary | PR 1 | `uv run --frozen pytest tests/unit/test_opsknowledge_core.py -k corpus` | `python -m backend.features.query.cli --profile production "status"` must fail closed | Revert `backend/features/corpus/` and corpus tests |
| 2 | Screening, retrieval, outcomes, provider | PR 2 | `uv run --frozen pytest tests/unit/test_opsknowledge_core.py -k "screen or retrieval or provider"` | N/A: in-process fake-provider scenarios are the runtime boundary | Revert `backend/shared/ports.py`, query domain/application/provider, related tests |
| 3 | CLI, dependency wiring, integration | PR 3 | `uv run --frozen pytest tests/architecture/test_opsknowledge_core_cli.py` | `python -m backend.features.query.cli "approved operational status"` emits one safe JSON object | Revert `cli.py`, `pyproject.toml`, `uv.lock`, subprocess tests |

## Phase 1: Foundation and Corpus Boundary

- [x] 1.1 **RED:** Add loader tests for non-development profile, non-synthetic/unapproved manifest records, invalid parents, mixed languages, and unlisted paths; assert safe fail-closed diagnostics and no retrieval exposure.
- [x] 1.2 **GREEN:** Create `backend/features/corpus/{domain.py,application.py,adapters/manifest_loader.py}` with immutable fragments and independent development/approved/synthetic manifest validation.
- [x] 1.3 Create `backend/shared/ports.py` protocols for retrieval, generation, and safe JSON logging without persistence interfaces.

## Phase 2: Query Safety and Grounding

- [ ] 2.1 **RED:** Add unit cases for screening-before-retrieval/provider, content-free logs, English/Spanish isolation, deterministic overlap ordering, empty/contradictory/out-of-scope outcomes, and citation allow-list rejection.
- [ ] 2.2 **GREEN:** Implement `backend/features/query/{domain.py,application.py}` with high-confidence screening, language-filtered retrieval, deterministic five/six-state rules, internal citation validation, and safe responses without answer text.
- [ ] 2.3 **RED:** Add fake-provider tests for timeout, rate limit, outage/non-success, bounded single attempt, no fabricated citations, and no calls on blocked/session/unsupported paths.
- [ ] 2.4 **GREEN:** Implement `backend/features/query/adapters/openai_provider.py` plus deterministic test fake; map provider failures to `unavailable` with human-expert escalation.

## Phase 3: CLI, Verification, and Dependency Wiring

- [ ] 3.1 **RED:** Add subprocess tests in `tests/architecture/test_opsknowledge_core_cli.py` for one safe JSON object, malformed arguments, startup denial, help residual-risk notice, content-free stderr/logs, and `--session-expired` without provider access.
- [ ] 3.2 **GREEN:** Create `backend/features/query/cli.py`; wire profile, deterministic overrides, sole compatibility `--session-expired`, safe stdout/stderr, and no session/persistence behavior.
- [ ] 3.3 Modify `pyproject.toml`/`uv.lock` to include `backend` in Pyright and the approved pinned `openai`; verify `governance/direct-dependencies.yaml` requires no new entry.
- [ ] 3.4 Run focused tests, `uv run --frozen ruff check .`, `uv run --frozen pyright`, and `make ci`; confirm all spec scenarios and the five threat-matrix N/A rows remain unimplemented.
