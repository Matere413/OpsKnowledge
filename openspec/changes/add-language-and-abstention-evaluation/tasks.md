# Tasks: Language and Abstention Evaluation

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | Slice 1: ~150; Slice 2: ~130; Slice 3: ~175; Slice 4: ~145; total ~600 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | Four slices: PR 1 → PR 2 → PR 3 → PR 4; stacked-to-main |
| Delivery strategy | chained PRs |
| Chain strategy | stacked-to-main |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Immutable population and `/30`, `/18`, escape metrics | PR 1 | `uv run --frozen pytest tests/unit/test_quality_evaluation_harness.py` | N/A: domain/application only | `population.py`, `domain.py`, `application.py` and their tests |
| 2 | Nullable routed language and typed provider failures | PR 2 | `uv run --frozen pytest tests/unit/test_quality_evaluation_harness.py -k 'language or failure'` | N/A: in-process kernel boundary | `query/application.py`, `shared/ports.py`, `adapters/kernel.py` and tests |
| 3 | Allowlisted deterministic serialization and history-safe storage | PR 3 | `uv run --frozen pytest tests/unit/test_quality_evaluation_harness.py -k 'report or history or rollback'` | N/A: adapter behavior is unit-tested | `adapters/report.py` and serializer tests |
| 4 | Opt-in CLI promotion, evidence, and boundary proof | PR 4 | `uv run --frozen pytest tests/architecture/test_quality_evaluation_harness.py tests/architecture/test_evaluation_dataset_ci_order.py` | `make eval-quality`; inspect current/previous/history | `cli.py`, `evaluation-runs/`, and architecture tests |

Threat matrix: every design row is explicitly N/A; no threat-specific RED tasks apply.

## Phase 1: Population and Contract Metrics

- [x] 1.1 Create `backend/features/evaluation/population.py` with immutable 34-case `PopulationDefinition`, frozen expectations/escape flags, version/digest, declared in-memory timeout cases, and fail-closed ID/denominator validation.
- [x] 1.2 Modify `backend/features/evaluation/domain.py` and `application.py` to snapshot expected metadata, preserve all five signals, compute language `/30`, abstention `/18`, and exact escape metrics; add focused unit coverage.

## Phase 2: Safe Kernel Observations

- [x] 2.1 Modify `backend/features/query/application.py`, `backend/shared/ports.py`, and `backend/features/evaluation/adapters/kernel.py` so routed language is nullable/observed from evidence, adapters never infer input language, and provider failures remain typed and in-memory; add unit coverage.

## Phase 3: Reports and Evidence Lifecycle

- [x] 3.1 Modify `backend/features/evaluation/adapters/report.py` to enforce exact allowlists, sorted canonical JSONL/text output, shared run identity, and exclusion of protected content; test byte determinism and safe fields.
- [x] 3.2 Implement staged three-file promotion and rollback: snapshot `current/` and `previous/` into immutable `history/{run_id}/`, rotate atomically with backup restoration, and never overwrite/delete history; test failure recovery.

## Phase 4: CLI, Boundaries, and Verification

- [ ] 4.1 Modify `backend/features/evaluation/cli.py` to emit/promote `summary.json`, `records.jsonl`, and `report.txt` through the reviewed replacement while retaining explicit opt-in and non-persistence.
- [ ] 4.2 Update `tests/unit/test_quality_evaluation_harness.py` and `tests/architecture/test_quality_evaluation_harness.py` for lineage, deterministic safety, manifest/mapping authority, rollback history, and unchanged `make ci`/`ci-pr2a`/gate boundaries; verify `make eval-quality`.
