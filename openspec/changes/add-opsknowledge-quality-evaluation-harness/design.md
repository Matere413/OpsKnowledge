# Design: OpsKnowledge Quality Evaluation Harness

## Technical Approach

Add a dependency-free `evaluation` feature that validates the manifest, loads the unchanged 32 scenarios and corpus, validates a reviewed question map, then executes 34 cases through the existing `resolve_query`/`LexicalRetriever`/`FakeProvider` boundary. The kernel, dataset, provider contracts, and `make ci` remain unchanged. Invalid runs execute zero cases and cannot promote evidence.

## Architecture Decisions

| Decision | Choice | Alternatives rejected | Rationale |
|---|---|---|---|
| Feature boundary | `backend/features/evaluation` with domain, application, inbound CLI, and outbound adapters | Changes to `query` or `corpus` | Preserves the feature-organized hexagonal monolith and keeps this delta independently removable. |
| Dataset gate | Call `scripts.ci.validate_evaluation_dataset.validate` before loading or executing; then use existing `load_corpus` | Duplicate rules or subprocess validation | Reuses the dataset authority without external process behavior. |
| Question input | A reviewed tuple of 32 `(scenario_id, language, question, reviewed=True)` rows in `mapping.py` | Dataset fields or generated questions | Keeps question text outside ground truth; missing, duplicate, extra, unreviewed, or language-mismatched rows fail closed. |
| Failure pair | Two in-memory cases, exact IDs `injected-provider-failure-es` and `...-en`, both using typed `ProviderFailure("provider-timeout")` | Dataset edits or live simulation | Exercises typed `unavailable` without persistence, network, or corpus mutation. |
| Baseline retention | `evaluation-runs/current/` and `evaluation-runs/previous/`; promote only after complete safe serialization | Unbounded run history or mutable pointers | Version is carried by `run_id`; atomic staging and rename retain at most two reviewed baselines. |

## Data Flow

```text
CLI → validate profile/dataset/mapping → load Corpus + scenarios
    → assemble 32 base + 2 injected cases
    → kernel adapter (LexicalRetriever + FakeProvider)
    → safe case results → metrics → JSON/JSONL/human writer
```

`domain.py` owns immutable cases/results and metric formulas. `ports.py` defines `Clock`, case-executor, validator, and report-store protocols. `adapters/dataset.py` reads only manifest-listed scenario JSON; `adapters/kernel.py` wraps the unchanged kernel and records routed language without content. `adapters/clock.py` provides `SystemClock` and `FrozenClock`. `adapters/report.py` allowlists serialization and promotes baselines. `cli.py` uses `argparse`; no subprocess or shell evaluation occurs inside the feature.

## File Changes

| File | Action | Description |
|---|---|---|
| `backend/features/evaluation/{__init__,domain,ports,mapping,application,cli}.py` | Create | Contracts, reviewed map, runner, metrics, and CLI. |
| `backend/features/evaluation/adapters/{__init__,dataset,kernel,clock,report}.py` | Create | Dataset/kernel/clock/report adapters. |
| `tests/unit/test_quality_evaluation_harness.py` | Create | Runner, mapping, determinism, metrics, provider failure, and safe-output tests. |
| `tests/architecture/test_quality_evaluation_harness.py` | Create | CLI/Makefile/dependency-boundary contracts. |
| `Makefile` | Modify | Add opt-in `eval-quality` only; preserve `ci` byte/order membership. |
| `evaluation-runs/current/*` | Create | One reviewed safe baseline; `previous` is created on first replacement. |

## Interfaces / Contracts

Safe summary/JSONL records contain only IDs, enums, versions, timestamp, booleans, counts, rates, profile, and duration: `run_id`, `case_id`, `language`, expected/observed outcome and reason, citation **IDs**, match flags, and metric counts. They never contain question/answer/citation content, claim text, or provider payloads. `run_id` hashes manifest/catalog hashes, mapping digest, contract versions, provider mode, profile, and `Clock` timestamp. `FrozenClock` makes repeated runs byte-identical; durations use injected monotonic readings. Denominators are explicit: outcome and citation / 34; language routing / retrieval cases; sensitive block / sensitive cases; contradiction detection / contradictory cases. Rates are numeric and threshold-free.

## Testing Strategy

| Layer | What to test | Approach |
|---|---|---|
| Unit | Validation gate, 34-case assembly, mapping, language isolation, typed failure, formulas, determinism, allowlist, retention rollback | Spies prove zero calls on invalid input; canaries prove content never serializes. |
| Architecture | `make eval-quality` exists, uses frozen `UV_RUN`, and `ci` is unchanged; no new dependency or persistence port | Static Makefile/import/source contracts. |
| Integration/E2E | N/A | Current testing configuration has no integration or E2E layer; the runner is entirely in-process. |

## Threat Matrix

| Boundary | Applicability | Safe/failure behavior and RED test |
|---|---|---|
| Documentation-like paths | N/A — no executable-file classification | No test. |
| Git repository selection | N/A — no Git operation | No test. |
| Commit state | N/A — no commit operation | No test. |
| Push state | N/A — no push operation | No test. |
| PR commands | N/A — no PR automation | No test. |

The shell boundary is limited to the existing `$(UV_RUN) run --frozen python -m ...` recipe; fixed argv, validated paths, non-zero safe failure, and no baseline promotion are covered by the architecture contract.

## Migration / Rollout

No migration required. Work units target approximately 130/140/90 authored lines (contracts+mapping, runner+kernel, report+CLI/Makefile); tasks must re-count against 400 lines and ask before chaining. Rollback removes only this feature, tests, target, and baselines; dataset, kernel, dependencies, `make ci`, and runtime state remain untouched.

## Open Questions

None; thresholds and broader Phase 2 metrics remain explicitly deferred to their later SDD changes.
