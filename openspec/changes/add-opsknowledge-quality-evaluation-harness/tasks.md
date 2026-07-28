# Tasks: OpsKnowledge Quality Evaluation Harness

## Review Workload Forecast

| Field | Value |
|---|---|
| Estimated changed lines (OpenSpec planning excluded) | ~490 total: Unit 1 ~155, Unit 2 ~180, Unit 3 ~155; exceeds 400: Yes |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | Three work units; chain pending |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units

| Unit | Goal / estimate | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|---|---|---|---|---|---|
| 1 | Contracts, mapping, gate, clock (~155) | Commit/PR 1; pending | `uv run --frozen pytest tests/unit/test_quality_evaluation_harness.py -k "validation or mapping or determinism"` | N/A — CLI not wired | Remove evaluation contracts/adapters and unit tests |
| 2 | 34-case runner, kernel, metrics (~180) | Commit/PR 2; pending | `uv run --frozen pytest tests/unit/test_quality_evaluation_harness.py -k "population or provider or metrics"` | N/A — CLI not wired | Remove runner/kernel files and tests |
| 3 | Reports, CLI, Make target, baseline (~155) | Commit/PR 3; pending | `uv run --frozen pytest tests/unit/test_quality_evaluation_harness.py tests/architecture/test_quality_evaluation_harness.py` | `make eval-quality` on `evaluation-dataset` | Remove report/CLI, target, architecture tests, and evidence |

## Phase 1: Foundation and RED Contracts

- [x] 1.1 RED: In `tests/unit/test_quality_evaluation_harness.py`, prove invalid integrity/language/count/profile and missing/duplicate/extra/unreviewed/mismatched mappings fail closed with zero calls (~35 lines).
- [x] 1.2 GREEN: Create `backend/features/evaluation/{__init__,domain,ports,mapping}.py` and `adapters/{__init__,dataset}.py` with immutable results, validator-before-`load_corpus`, and 32 reviewed ES/EN rows (~120 lines).
- [x] 1.3 RED: Test 32 unchanged cases plus exact injected IDs, base-byte preservation, frozen identity/order/bytes, and no wall-clock reads (~25 lines).
- [x] 1.4 GREEN: Create `adapters/clock.py` with `Clock`, `SystemClock`, `FrozenClock`, stable inputs, and injected monotonic duration (~35 lines).

## Phase 2: Kernel Runner and Metrics

- [x] 2.1 RED: Test language isolation, mapping-as-input-only, typed ES/EN `provider-timeout` → `unavailable`, no fabricated evidence/external calls, and five numeric threshold-free formulas (~55 lines).
- [x] 2.2 GREEN: Create `application.py` and `adapters/kernel.py`; use development `resolve_query`, `LexicalRetriever`/`FakeProvider`, assemble 34 cases, and record language without content (~125 lines).
- [x] 2.3 GREEN: Complete `domain.py` denominators: outcome/citation `/34`, language/retrieval, sensitive/sensitive, contradiction/contradictory (~25 lines).

## Phase 3: Safe Reports and Opt-In Wiring

- [ ] 3.1 RED: Canary-test allowlisted JSON/JSONL/human output, no question/answer/citation/claim/provider content, incomplete-promotion rejection, and atomic current/previous retention (~45 lines).
- [ ] 3.2 RED: Add architecture tests for fixed `UV_RUN` argv, validated paths, non-zero failure/no promotion, no new dependencies/providers/embeddings/persistence/HTTP/auth/UI/corporate/external services, unchanged `ci`, and RDD disabled per #1892 (~35 lines).
- [ ] 3.3 GREEN: Create `adapters/report.py` and `cli.py`, add only opt-in `eval-quality`, and commit one reviewed safe `evaluation-runs/current/*`; create `previous` only on replacement (~110 lines).

## Phase 4: Verification Evidence

- [ ] 4.1 Run focused unit/architecture tests; record evidence for all seven scenarios; add no integration/E2E layer.
- [ ] 4.2 Run `make eval-quality`; verify 34 records, five numeric metrics, deterministic safe output, bounded baselines, no thresholds/state.
- [ ] 4.3 Run unchanged `make ci`; verify membership/order and do not initiate RDD review or enablement.
