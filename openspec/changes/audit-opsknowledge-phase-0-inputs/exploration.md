## Exploration: Audit OpsKnowledge Phase 0 Inputs and Candidate Changes

### Current State

The product repositioning is complete and authoritative: OpsKnowledge is a bilingual technical knowledge platform over approved, versioned `runbooks`, `adrs`, and `operational-policies`. The corporate product may use only controlled approved sources; the development prototype may use visibly non-corporate, manifest-controlled synthetic technical entries. The test-harness bootstrap is archived and complete, while application runtime and corporate integrations do not yet exist.

Phase 0 still describes several inputs using the former support-history-oriented framing. The live contract explicitly states that support history and glossary content are never answer evidence. The repositioning artifacts preserve the need for measurable evaluation assets, but do not authorize inventing or acquiring unavailable corporate data. Therefore, Phase 0 should now establish synthetic portfolio/demo evaluation assets and record historical operational evidence as optional or later evidence, rather than making it a product-implementation prerequisite.

### Evidence Matrix

| Item | Current evidence | Disposition | Rationale / required wording direction |
|---|---|---|---|
| Historical support baseline metrics | `RAG_ROADMAP.md` Phase 0, lines 68–90; Phase 9, lines 474–479 | **must be replaced/reworded** | Reframe as optional corporate impact evidence, unavailable for the prototype, and not a prerequisite for Phase 1. Phase 9 already says wider impact measurement follows the pilot and baseline availability. Do not request or fabricate corporate metrics. |
| Historical question/support-answer report | `RAG_ROADMAP.md` Phase 0, lines 74–81; `AGENTS.md` lines 29–35; `openspec/specs/opsknowledge-domain-contract/spec.md` lines 59–67 | **must be replaced/reworded** | Replace the mandatory historical report with an optional, access-controlled evaluation reference set if legitimately available. It must never be answer evidence or automatic ground truth; synthetic scenario cases are the current Phase 0 asset. |
| Existing bilingual glossary | `RAG_ROADMAP.md` Phase 0 lines 77–78; Phase 4 lines 247–255; domain contract lines 39–47 and 59–67 | **must be replaced/reworded** | No corporate glossary should be assumed. Build a reviewed terminology map from the synthetic approved collections when needed; use it only for query understanding/expansion, never evidence. Corporate glossary intake belongs with controlled source governance and later retrieval work. |
| Initial approved entry sample | `RAG_ROADMAP.md` Phase 0 lines 73, 88–90; architecture lines 14–17, 229–233; domain contract lines 19–37 | **still required now** | Required to make evaluation and the Phase 1 grounded core concrete. The immediate sample must be manifest-controlled synthetic technical entries, visibly non-corporate, versioned, approved within the demo contract, language-tagged, and isolated from any corporate index. A corporate sample is not available and must not be invented. |

### Affected Areas

- `RAG_ROADMAP.md` — Phase 0 pending inputs, objective, scope, expected outputs, candidate ordering, and Next step need precise synthetic/corporate wording.
- `AGENTS.md` — establishes the higher-authority rule that support history and glossary entries are never answer evidence and separates synthetic demo assets from corporate inputs.
- `docs/architecture/platform-architecture.md` — defines the approved collections, synthetic source classification, fragment language, and planned prototype/corporate boundary.
- `openspec/specs/opsknowledge-domain-contract/spec.md` — canonical current domain contract for collection governance, bilingual isolation, citation-only evidence, and supersession.
- `openspec/changes/archive/2026-07-15-reposition-rag-as-portfolio-platform/` — archived repositioning evidence confirms the migration was documentary, with runtime behavior deferred.
- `openspec/changes/archive/2026-07-19-bootstrap-opsknowledge-test-harness/` — confirms the test harness is complete and available for future evaluation/runtime changes.

### Candidate Change Assessment

1. **`build-opsknowledge-evaluation-dataset` remains correctly scoped, with a narrower immediate boundary**
   - Pros: supplies representative supported, ambiguous, contradictory, out-of-scope, and unanswerable cases; enables measurable safety work without corporate data; follows the repositioning contract.
   - Cons: historical support reports cannot be treated as ground truth; synthetic cases require explicit provenance and review; it must not become a disguised corporate-data intake.
   - Effort: Medium

2. **`add-approved-domain-terminology-map` remains conceptually valid but should be renamed/reworded**
   - Pros: supports bilingual query understanding and consistent terminology over the approved technical collections; aligns with Phase 4's non-evidence glossary rule.
   - Cons: “domain” and “existing glossary” imply a corporate source that is not available; terminology must not influence answer evidence or cross-language retrieval.
   - Effort: Low

### Recommendation

Keep `build-opsknowledge-evaluation-dataset` as the next substantive Phase 0 change, explicitly limited first to synthetic portfolio/demo collections and reviewed scenarios. Retain the terminology-map change after the dataset (or make it a small dependent work unit), but rename it to something such as `add-approved-collection-terminology-map` and state that it is derived from reviewed synthetic/approved entries when no corporate glossary exists. Reword the four pending inputs rather than deleting them: only the synthetic initial entry sample is a current prerequisite; historical reports and corporate glossary material are optional or later controlled evidence.

The roadmap should also stop saying “real support history” is required to complete the current Phase 0 foundation. A precise replacement is: “Convert the agreed product boundary and controlled synthetic collection sample into a reproducible evaluation foundation; retain any legitimately available historical support evidence as optional, access-controlled reference data for later impact measurement.”

### Risks

- Treating historical support answers as ground truth would violate the current citation/evidence contract and could reintroduce the superseded support-oriented product framing.
- Calling synthetic entries “approved corporate entries” would collapse the prototype/corporate boundary; all sample assets need explicit synthetic classification and development-only enforcement.
- A terminology map could accidentally become retrieval evidence or enable cross-language fallback unless its query-understanding-only role remains explicit.
- Requiring unavailable corporate metrics or reports could block Phase 1 unnecessarily and encourage fabricated evidence.
- The current `openspec/config.yaml` records `engram_project: opsknowledge` while the requested artifact project is `rag`; this is a persistence-configuration mismatch that should be preserved as context, not silently corrected during this read-only exploration.

### Ready for Proposal

No. The audit is ready to inform a bounded proposal, but the roadmap wording and candidate slug/scope need an explicit maintainer decision before proposal creation—especially whether the terminology-map rename is accepted and whether historical evidence is labeled optional or deferred to Phase 9.
