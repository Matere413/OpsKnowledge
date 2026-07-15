# Design: Reposition RAG as OpsKnowledge

## Technical Approach

Perform an authorized SDD contract replacement, not a silent weakening: atomically reconcile `AGENTS.md` first, then `RAG_ROADMAP.md`, then architecture in one bounded documentation work unit. A completed unit contains all three aligned edits—there is no completed interval where a lower source contradicts a higher source. Move governance evidence from `architecture/` to `governance/`; architecture narratives remain in `docs/architecture/`. Preserve the modular monolith, provider/TI boundaries, evidence-first flow, and failure semantics; “RAG” remains a technical retrieval term, not the product name.

## Architecture Decisions

| Decision | Options / trade-off | Decision and rationale |
|---|---|---|
| Migration scope | Rewrite architecture vs terminology/boundary migration | Migrate terminology and source examples only. The proposal excludes runtime, dependencies, manifests, lockfiles, and behavior changes. |
| Evidence collections | One generic corpus vs governed collections | Define `runbooks`, `adrs`, and `operational-policies`; require approval, version, classification, and fragment language. This makes the portfolio domain concrete without weakening evidence controls. |
| Governance evidence path | Keep a misleading `architecture/` root vs move the evidence | Move `architecture/direct-dependencies.yaml` to `governance/direct-dependencies.yaml`. The move is byte-for-byte except for an intentional comment-only naming change (header "RAG platform" → "OpsKnowledge platform"); the new checksum is documented in apply-progress. This clarifies ownership; it does not alter dependency policy, approval, schema, or CI behavior. |
| Historical record | Mutate/delete prior artifacts vs relation-backed successor record | Never modify historical content. Create successor links in new artifacts and persist `supersedes` relations: #3226→#3122, #3227→#3125, #3228→#3133, and the new tasks observation→#3134. If relations are unsupported, create a new immutable supersession index. |

## Data Flow

```text
Approved entry (runbook / ADR / policy)
  -> approval + version + classification + language per fragment
  -> query-language filter -> citation-only resolution
  -> canonical outcome -> human-expert escalation when required
```

Synthetic manifest-controlled entries remain development-only and visibly non-corporate; no synthetic fragment enters a corporate index. Corporate sources remain future, controlled/TI-gated sources. English queries receive English fragments only; Spanish queries receive Spanish fragments only—never fallback or cross-language ranking.

## File Changes and Terminology

| File | Action | Planned edit |
|---|---|---|
| `AGENTS.md` | Modify first | Change title; the safety abstention/provider-failure bullets; “Dependency governance”; and “Where to look.” Replace `Consultation App` with `human expert`, domain examples, and every dependency-evidence path. |
| `RAG_ROADMAP.md` | Modify second | Change title, Product boundary, Guiding principles, Phase 0 canonical-source/completion notes, Phase 0–10 labels, cross-phase abstention invariant, Next step, and dependency-evidence path. |
| `docs/architecture/platform-architecture.md` | Modify third | Change title/introduction, overview, data model, flows, module ownership, risk/demo sections, traceability, checklist, and every dependency-evidence reference; preserve planned status/topology. |
| `architecture/direct-dependencies.yaml` → `governance/direct-dependencies.yaml` | Move | Preserve YAML content; update header comment from "RAG platform" to "OpsKnowledge platform" (intentional comment-only naming change); recompute and document the new checksum; remove the old path only after references target the new path. |
| `openspec/changes/reposition-rag-as-portfolio-platform/specs/opsknowledge-domain-contract/spec.md` | Reference | Keep the nine requirements as the delta contract; no runtime interface is introduced. |
| OpenSpec change artifacts | Modify | Update the moved path in `proposal.md`, `specs/**`, this design, and future `tasks.md`, `verify-report.md`, and `supersession-index.md`. |
| `openspec/changes/reposition-rag-as-portfolio-platform/supersession-index.md` and Engram `sdd/reposition-rag-as-portfolio-platform/supersession-index` | Create if needed | Immutable fallback mapping of successor topics/IDs to #3122/#3125/#3133/#3134, reason, and relation-persistence result. |

Mapping: `Dental Design Guidance RAG`/`RAG Platform` → `OpsKnowledge`; dental guides → approved technical entries; SharePoint clinical guides → future corporate approved sources; synthetic PDFs → synthetic technical entries; technicians/support/clinical teams → `reader`/`contributor`/`reviewer`/`admin`; Consultation App → human expert. Preserve these exact outcomes: `supported`, `insufficient_information`, `contradictory_information`, `out_of_scope`, `unavailable`, `session_expired`.

Rename only domain-specific candidate labels: P0 `define-dental-guidance-domain-and-corpus` → historical/superseded and new contract; `build-consultation-evaluation-dataset` → `build-opsknowledge-evaluation-dataset`; P1 `build-minimal-grounded-dental-rag` → `build-minimal-grounded-opsknowledge-core`; P2 RAG/clinical labels → OpsKnowledge/technical; P3 SharePoint-guide/PDF labels → approved-source/document labels; P6 `expose-rag-application-services` → `expose-opsknowledge-application-services`; P7 technician/clinical labels → reader/reviewer; P9 RAG/five-technician labels → OpsKnowledge/five-user. P4, P5, P8, and generic P10 labels remain unless they contain those terms; `integrate-dental-design-software` becomes `integrate-approved-operations-tool`.

## Requirement Traceability

| Spec | Authoritative sources | Planned edits |
|---|---|---|
| 1 Identity | AGENTS hierarchy; roadmap Product boundary; architecture overview | titles, boundary, terminology map |
| 2 Collections | AGENTS prototype boundary; roadmap Product boundary; architecture data model | collection governance and entry metadata |
| 3 Separation | AGENTS prototype/corporate; roadmap invariant 1; architecture demo gate | synthetic/corporate wording and denial claims |
| 4 Language | AGENTS safety; roadmap Phase 4; architecture query flow | fragment-level isolation |
| 5 Roles | AGENTS authorization; roadmap Phases 0/8; architecture governance | four-role mapping and expert boundary |
| 6 Citations/escalation | AGENTS safety; roadmap invariants 3–5; architecture query flow | human-expert outcome wording |
| 7 Outcomes | AGENTS provider/sessions; roadmap Phase 7; architecture failure rules | six-state canonical list, unchanged |
| 8 Sensitive screen | AGENTS security; roadmap Phase 8; architecture gate ordering | technical-domain examples only |
| 9 Supersession | AGENTS hierarchy; roadmap Phase 0; architecture traceability | bidirectional links and retained history |

## Testing and Rollout

No runtime test harness exists and this workspace is not a Git repository. Verify by filesystem/content inspection: assert `governance/direct-dependencies.yaml` exists and `architecture/direct-dependencies.yaml` does not; search LIVE authority/governance files (AGENTS.md, RAG_ROADMAP.md, docs/architecture/platform-architecture.md, governance/direct-dependencies.yaml) for the old path as a live reference — it must return zero matches. Historical/provenance artifacts in `openspec/changes/` may intentionally mention the old path as migration context and are excluded from the live-reference check. Then inspect AGENTS, roadmap, and architecture in authority order; search live scope for dental/Consultation-App terms (allow historical/supersession links); compare all nine OpsKnowledge requirement rows; confirm the exact taxonomy, collections, language isolation, roles, and no runtime/manifest/lockfile changes. Persist relation links using `engram_mem_compare(... relation: supersedes)`; otherwise write the immutable index. Roll back using safe order (never delete sole evidence before verified restoration): (1) create `architecture/`; (2) copy current `governance/direct-dependencies.yaml` to `architecture/direct-dependencies.yaml`; (3) restore the former header comment if reverting the product migration; (4) verify expected pre-move checksum `b8a8f9bd5c4eb04145bc01cd388e3b3b2b22f3c4743d5fc4b5152af7d9bcc519` (only if the comment change is also reverted); (5) retarget all references to `architecture/direct-dependencies.yaml`; (6) only then remove `governance/`.

Forecast: 680–930 changed lines: AGENTS ~50, roadmap ~340–510, architecture ~260–360, OpenSpec/path move ~30, plus index. Against the active **800-line** budget, risk is High at the upper estimate. **Delivery decision resolved: size:exception.** The maintainer explicitly approved a single atomic review unit for the 680–930-line forecast. The workspace is NOT a Git repository; no branches, PRs, or chained-PR base branches apply. The original forecast recommended chained PRs (`ask-always`), but the maintainer resolved the decision by approving `size:exception` — one atomic delivery, no chain strategy.
