# Design: Minimal Grounded OpsKnowledge Core

## Technical Approach

Implement a stdlib-first hexagonal slice. `cli.py` loads manifest-listed `development`/`approved`/`synthetic` records, screens the question, detects language, retrieves by keyword overlap, applies fail-closed outcomes, and calls a provider for supported evidence. Embeddings, databases, HTTP, sessions, OCR interpretation, and reranking remain excluded. CI keeps the validator; runtime loading independently fails closed.

## Architecture Decisions

| Decision | Choice | Alternatives / rationale |
|---|---|---|---|---|
| Retrieval | Normalized-token overlap, stable score/ID ordering, and mandatory language/provenance filters. | Embeddings add egress, dependency, and nondeterminism without Phase 1 value. |
| Answer boundary | The provider may produce an internal answer for citation validation, but the CLI returns **no answer text**: only the spec’s safe fields (`outcome`, fragment-ID citations, escalation, profile, reason code). | Returning content contradicts the approved JSON contract. A later UI/output change must amend it. Logs are separate and never contain question, answer, citation content, tokens, secrets, or provider payloads. |
| Provider | `Generate` outbound protocol; `OpenAIProvider` is the production adapter and a deterministic fake is test-only. | No calls on screening, session signal, empty/contradictory evidence, or unsupported outcomes; timeout/rate-limit/outage maps to `unavailable` with one bounded attempt. |
| Session signal | `--session-expired` is an explicit compatibility input that returns `session_expired`, human-expert escalation, and no provider call. | No session object, clock, storage, or lifecycle is introduced; real expiry belongs to the future session feature. |

## Data Flow

```text
argv/profile → manifest loader → sensitive screen → language filter
    → deterministic retrieval → outcome/citation gate → Generate port
    → internal citation validation → safe JSON stdout
                                      └→ safe JSON log events only
```

The loader rejects non-development profiles, non-synthetic/unapproved records, invalid parents, mixed languages, and unlisted paths. Supported output requires every citation to be an approved, language-matched retrieved fragment. Other safety/provider paths abstain and recommend a human expert. No state is written.

## File Changes

| File | Action | Description |
|---|---|---|
| `backend/shared/ports.py` | Create | `Retrieve`/`Generate` ports and safe logging protocol. |
| `backend/features/corpus/{domain.py,application.py,adapters/manifest_loader.py}` | Create | Fragment model, loading policy, and manifest adapter. |
| `backend/features/query/{domain.py,application.py,adapters/openai_provider.py,cli.py}` | Create | Screening, retrieval, outcomes, provider, and CLI. |
| `tests/unit/test_opsknowledge_core.py`, `tests/architecture/test_opsknowledge_core_cli.py` | Create | Safety, grounding, provider, boundary, and subprocess tests. |
| `pyproject.toml`, `uv.lock` | Modify | Include `backend` in Pyright and add pinned approved `openai`. |
| `governance/direct-dependencies.yaml` | Verify only | Reuse approved `openai`; reconciliation remains required. No new CI stage. |

## Interfaces / Contracts

```python
class Generate(Protocol):
    def generate(self, question: str, evidence: tuple[Fragment, ...], language: str) -> GeneratedAnswer: ...
```

`GeneratedAnswer` contains internal text plus citation IDs; `SafeResponse` omits text. `python -m backend.features.query.cli QUESTION` emits a JSON object; invalid startup/arguments use stderr and non-zero exit. `--profile` defaults to `development`; `--session-expired` is the sole compatibility signal.

## Testing Strategy

| Layer | What to test | Approach |
|---|---|---|
| Unit | Profile denial, screening order, language isolation, deterministic retrieval, six outcomes, citation allow-list, provider failure, and content-free logs. | Pytest with fake provider and temporary roots. |
| Process/architecture | One JSON stdout object, safe stderr/logs, malformed argv, and `--session-expired` without provider access. | Subprocess invocation; inspect streams and fake call count. |
| CI | Dataset/dependency contracts and backend quality. | Existing `make ci` stages. |

## Threat Matrix

CLI is an argv-only process boundary; it adds no HTTP routing, shell composition, executable classification, repository selection, or VCS/PR automation.

| Boundary | Minimum adversarial cases | Applicability | Design response | Planned RED tests |
|---|---|---|---|---|
| Documentation-like paths | `requirements.txt`, Markdown, shell-like names | N/A — manifest paths are data, not executable classification. | No execution or classification boundary is added. | None; corpus-path tests are outside this matrix. |
| Git repository selection | `git -C`, relative, absolute paths | N/A — no Git selector or repository operation. | No repository authority is accepted. | None. |
| Commit state | staged, `commit -a`, empty index | N/A — no commit/index operation. | No commit mutation is performed. | None. |
| Push state | tracking branch, first push, refspec | N/A — no push/refspec operation. | No remote/ref resolution is performed. | None. |
| PR commands | `--head`, environment prefix, composed commands | N/A — no PR or command composition. | No VCS command is constructed or executed. | None. |

Task traceability for `tasks.md`: T1 corpus; T2 screen/log boundary; T3 language/retrieval/citations/outcomes; T4 provider failure; T5 CLI/session signal; T6 tests/dependency/CI. Keep each invariant attached to its task’s RED tests.

## Migration / Rollout

No migration required. Development-only local rollout; no corporate/Azure wiring. Revert backend, tests, and dependency changes without touching the dataset or domain contract.

## Open Questions

None. Omitted CLI answer text is intentional.
