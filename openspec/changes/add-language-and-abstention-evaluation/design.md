# Design: Language and Abstention Evaluation

## Technical Approach

Keep the development-only, in-process boundary and replace the 34-case assembly with a reviewed `PopulationDefinition`. It references unchanged manifest bytes and `REVIEWED_MAPPING`, but freezes expected metadata, escape flags, version, and digest. Run it through the fake kernel, calculate three contract metrics beside the unchanged five signals, serialize one allowlisted bundle, and promote it atomically.

## Architecture Decisions

| Decision | Choice | Alternative rejected; rationale |
|---|---|---|
| Run identity | `sha256(UTF-8(canonical_json(fields)))`, lowercase hex; sorted keys and compact separators. Fields are `schema_version`, `contract_version`, `population_version`, `population_digest`, `manifest_digest`, `mapping_digest`, `profile`, `provider_mode`, `timestamp_6`, and `duration_6`. A frozen clock makes identical inputs produce identical report bytes. | Delimited or wall-clock IDs permit collisions or byte drift; legacy IDs remain historical. |
| Reviewed scoring | Expected results are immutable in the snapshot. Corrections create a new version/digest; scoring never reads observations or mutates the prior snapshot. | Runtime re-derivation would rewrite history and invalidate comparisons. |
| Populations | Exactly 34 cases: 32 manifest scenarios (16 `es`, 16 `en`, 16 supported, 16 abstention) plus two declared in-memory `provider-timeout` cases. Language is `/30`: exclude two sensitive and two declared provider-failure cases; `routed_language=None` stays in the denominator with numerator zero and is never replaced by input language. Correct abstention is `/18`: every expected non-supported case, including sensitive/provider failures. Escape denominator is exactly reviewed `escape_required=true` IDs; empty or absent IDs fail closed. | Reusing `/34`, dropping `None`, or inferring escape cases hides safety failures. |
| Escape observable | An escape passes only when the safe response is not `supported` and matches expected outcome/reason, empty citations, and `human expert` escalation. Observe enums, IDs, and booleans only; never parse, log, or persist claim text. | Claim parsing or a new answer-quality dependency is unsafe and out of scope. |
| Evidence lifecycle | Stage three files, snapshot `current/` and `previous/` into immutable `history/{run_id}/` before promotion or rollback, then rotate with backups. | Sidecar/current-only rotation can mix evidence or lose the prior `previous/` bundle. |

## Data Flow

`manifest.json` + validator → population snapshot + mapping digest → safe kernel response → metric calculators → canonical serializers → staged bundle → history snapshot → `current/`.

Safe response exposes nullable `routed_language`; adapters never infer it from the question. Failures stay in memory; missing/extra IDs fail closed.

## File Changes

| File | Action | Description |
|---|---|---|
| `backend/features/evaluation/population.py` | Create | Cases, expectations, escape flags, failures. |
| `backend/features/evaluation/{domain,application}.py` | Modify | Validation, metrics, `None`, identity; retain five formulas. |
| `backend/features/query/application.py`, `backend/shared/ports.py`, `backend/features/evaluation/adapters/kernel.py` | Modify | Safe route state and typed failures. |
| `backend/features/evaluation/adapters/{report,cli}.py` | Modify | Allowlist, bundle, history rotation, rollback. |
| `evaluation-dataset/manifest.json`, `backend/features/evaluation/mapping.py` | Authority | Unchanged inputs; digests enter identity. |
| `evaluation-runs/{current,previous,history}/` | Modify/Create | Legacy and immutable history. |
| `tests/unit/test_quality_evaluation_harness.py`, `tests/architecture/test_quality_evaluation_harness.py` | Modify | Focused proof. |

## Interfaces / Contracts

The allowlist is enforced separately for every output. `summary.json` keys are exactly `schema_version`, `contract_version`, `population_version`, `population_digest`, `replaces_population_version`, `manifest_digest`, `mapping_digest`, `run_id`, `profile`, `provider_mode`, `timestamp`, `duration_seconds`, `total_cases`, `exclusions`, `metrics`, and `contract_metrics`. `metrics` has exactly `outcome_classification`, `citation_exact_match`, `language_routing`, `sensitive_block`, `contradiction_detection`; `contract_metrics` has exactly `language_accuracy`, `correct_abstention`, `unsupported_claim_escape`; each value is integer `{numerator,denominator}`. `records.jsonl` keys are exactly `case_id`, `language`, nullable `routed_language`, `expected_outcome`, `expected_reason_code`, `observed_outcome`, `reason_code`, `escalation`, opaque `citation_ids`, `citations_match`, and population booleans. `report.txt`/stdout contain only fixed labels for `run_id`, versions, profile/provider, timestamp/duration, counts, exclusions, and those eight metric names. No output contains questions, answers, claims, citation content, provider payloads, or free-form errors. Records and metrics are sorted; report lines are fixed.

Promotion validates all three files and their shared `run_id`, snapshots existing bundles to history (same ID only if bytes match), snapshots staged data, then atomically rotates `current → previous`, staged → `current`; failure restores backups. Rollback uses the same path. History is never overwritten or deleted.

## Testing Strategy

| Layer | Focused contract proof |
|---|---|
| Unit | `test_quality_evaluation_harness.py`: populations, nullable routing, immutable expectations, failures, escape observable, run-ID/byte determinism, allowlists, and history/rollback recovery. |
| Architecture | `test_quality_evaluation_harness.py`, `test_evaluation_dataset_ci_order.py`, `test_evaluation_dataset_validator.py`: opt-in, CI, manifest authority. Existing `test_technical_grounding_gates_{policy,runner,report}.py` prove gate seams. |
| Integration/E2E | N/A; only unit and architecture layers exist. |

## Threat Matrix

| Boundary | Applicability | Response / RED test |
|---|---|---|
| Documentation-like paths | N/A — no executable classification | None |
| Git repository selection | N/A — no VCS automation | None |
| Commit state | N/A — no commit automation | None |
| Push state | N/A — no push automation | None |
| PR commands | N/A — no PR automation | None |

## Migration / Rollout

No schema migration. `make ci`, `ci-pr2a`, `eval-quality`, `eval-quality-gate`, `.github/workflows/ci.yml`, and gate implementation remain unchanged. Interactive/hybrid preflight, ask-on-risk, and the 400-line review guard remain in force.

## Open Questions

None blocking.
