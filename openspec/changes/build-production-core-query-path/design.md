# Design: Deterministic Grounded Query Kernel

## Technical Approach

Build an in-process query application service over the `load_corpus` snapshot. Extend each `Fragment` with an immutable parent-entry provenance projection copied from the validated `Entry`; never parse revision data from identifiers. A stdlib lexical adapter implements the `Retrieve` port, failing closed on missing/unsafe metadata and filtering language, approval, classification, and profile before deterministic token-overlap ranking. The application pipeline screens sensitive and out-of-scope/override inputs, routes `en`/`es`, retrieves evidence, applies insufficient/contradiction rules, builds an evidence-only prompt, invokes an injected `Generate`, and allow-lists returned citation IDs. The result uses the existing content-free `SafeResponse`; generated text exists only inside the application during validation.

## Architecture Decisions

| Decision | Choice | Rejected alternative and rationale |
|---|---|---|
| Provenance | Add frozen `EntryProvenance` metadata to `Fragment` (`logical_entry_id`, `revision`, `collection`, language, approval, classification, profile). | Retaining the full `Entry` exposes parent content unnecessarily; parsing IDs is unsafe when naming changes. |
| Retrieval | `LexicalRetriever` uses normalized stdlib tokens, mandatory pre-ranking metadata filters, score descending, then fragment-ID ascending ties. | Embeddings, reranking, and external libraries are out of scope and add nondeterminism/egress. |
| Safety boundary | Application rules decide sensitive, out-of-scope, insufficient, and contradictory outcomes before generation; differing revisions of one logical entry are conservatively contradictory and never auto-prefer the latest. | Letting the provider classify or repair evidence could produce unsupported claims. Semantic conflict scoring is deferred to Phase 2. |
| Provider contract | Add immutable `GroundedPrompt`/prompt-evidence types and typed `ProviderFailure` to `backend/shared/ports.py`; inject only a deterministic fake adapter. | Live OpenAI/Azure adapters, retries, persistence, and HTTP would cross this change’s prototype/Phase 8 boundary. |

## Data Flow

```text
Corpus snapshot → metadata filter → lexical rank → selected fragments
Question → sensitive/scope screen → language route ───────────────────────┐
                                                                           ↓
                         insufficient / contradiction ─────────────── SafeResponse
                                                                           ↓
                 GroundedPrompt (question + rules + same-language evidence)
                                                                           ↓
                         Generate → citation allow-list → SafeResponse
```

No history, glossary, support history, model knowledge, or user instructions are represented as evidence. Empty/low-overlap evidence returns `insufficient_information`; ambiguous language and explicit scope/override rules return `out_of_scope`; invalid/missing citations and provider failures return `unavailable`. These paths contain no answer or citations and recommend a human expert where required. Sensitive blocking uses `unavailable` with reason `sensitive_blocked` and makes no retrieval/provider call.

## File Changes

| File | Action | Description |
|---|---|---|
| `backend/features/corpus/domain.py` | Modify | Add frozen parent provenance projection to `Fragment`. |
| `backend/features/corpus/application.py` | Modify | Populate and validate the projection from resolved `Entry` metadata. |
| `backend/shared/ports.py` | Modify | Add prompt-boundary value objects and typed provider failure; preserve safe logging and no persistence port. |
| `backend/features/query/domain.py` | Create | Language, outcome/reason constants, and query-result policy types. |
| `backend/features/query/application.py` | Create | Screening, routing, retrieval orchestration, contradiction/outcome rules, prompt invocation, and citation validation. |
| `backend/features/query/prompt.py` | Create | Evidence-only prompt construction with immutable selected-fragment records. |
| `backend/features/query/adapters/lexical_retriever.py` | Create | Deterministic `Retrieve` implementation over `Corpus`. |
| `backend/features/query/adapters/fake_provider.py` | Create | Reproducible `Generate` adapter with configurable response or typed failure. |
| `tests/unit/test_opsknowledge_core.py` | Modify | Assert parent provenance remains immutable and explicit. |
| `tests/unit/test_grounded_query_kernel.py` | Create | Kernel safety, determinism, prompt, citation, and provider contract tests. |
| `pyproject.toml` | Modify | Set Pyright coverage to `backend` and `tests`; add no dependency or lockfile change. |

## Interfaces / Contracts

```python
@dataclass(frozen=True, slots=True)
class GroundedPrompt:
    question: str
    language: str
    evidence: tuple[PromptEvidence, ...]

class Generate(Protocol):
    def generate(self, prompt: GroundedPrompt) -> GeneratedAnswer: ...

class ProviderFailure(Exception):
    reason_code: str
```

`resolve_query(...) -> SafeResponse` is side-effect free and never returns `session_expired`; that state belongs to the later session feature.

## Testing Strategy

| Layer | What to Test | Approach |
|---|---|---|
| Unit | Provenance, language isolation, stable ties, screen ordering, all five kernel outcomes, contradiction abstention, prompt boundary, citation allow-list, fake reproducibility/failure, and content-free logs. | Pytest fixtures with immutable fragments, spies, and deterministic fake configuration; no live provider. |
| Integration | N/A — no HTTP, database, or external provider exists in this slice. | In-process application/adapter contract tests remain unit tests. |
| E2E | N/A — CLI/UI is a later inbound-adapter change. | — |

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file classification, or process-integration boundary.

## Migration / Rollout

No migration required. Roll out only as an in-process development synthetic-corpus capability for automated evaluation; Phase 2 metrics, baselines, and thresholds remain out of scope. No production profile, corporate data, live provider, network, persistence, or new dependency is introduced. Revert query modules, tests, port changes, and the provenance projection without changing the dataset or historical artifacts.

## Open Questions

- [ ] Phase 2 should replace or validate the conservative multi-revision contradiction proxy with explicit semantic conflict labels; this does not block the fail-closed kernel.
