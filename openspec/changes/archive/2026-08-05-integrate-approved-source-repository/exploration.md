## Exploration: integrate-approved-source-repository

### Current State

The repository is a clean `master` checkout at `ea85be4`. The current implementation contains a fail-closed corpus boundary, a deterministic query kernel, and the Phase 2 evaluation harness, but it has no `backend/features/indexing/` feature, source-repository adapter, database index, `IndexVersion`, `IndexRun`, or `IndexOperation` implementation.

The existing `backend/features/corpus/adapters/manifest_loader.py` reads the repository-local `evaluation-dataset/manifest.json` and JSON entry/fragment payloads. It validates hashes, safe paths, approval, synthetic classification, development profile, parent references, language matching, OCR metadata, and exhaustive manifest coverage. This is a development-only evaluation fixture loader, not an approved source repository integration. `backend/features/evaluation/adapters/dataset.py` deliberately validates that fixture before loading it and must remain separate from a production-source adapter.

The Phase 3 contract defines the approved entry repository as the source of truth: filenames identify entry, language, and revision; Spanish and English revisions are independent; and repository presence determines current availability. The architecture describes an `Approved Source` outbound adapter and assigns source access to the indexing boundary, but those are target/planned contracts rather than current capabilities.

**Bounded problem:** establish a provider-independent, fail-closed boundary that can enumerate the currently available approved source artifacts and return deterministic, validated source metadata for later ingestion. A first implementation may use a development-only local adapter or fixture, but it must not parse documents, extract OCR, create embeddings, persist an index, or process corporate data.

**Likely responsibilities:**

- Define an immutable source-artifact descriptor and an outbound source-repository port.
- Validate repository-relative paths, safe file access, supported collection/language/revision identity, approval/classification/profile boundaries, and content hashes or equivalent source identity.
- Produce a deterministic repository snapshot/inventory that downstream ingestion can consume without inferring identity from document content.
- Fail closed on malformed names, duplicate identities, unsafe paths, unreadable artifacts, or an incomplete repository scan; a scan failure must never be interpreted as an empty repository.
- Keep the source adapter replaceable so a future approved corporate adapter can satisfy the same contract without entering this change.

**Architectural boundaries:** domain and application code remain provider-independent; filesystem or remote-source access belongs in outbound adapters. The `indexing` feature should own source synchronization orchestration once that feature exists. The `corpus` feature should continue to own normalized entry/fragment provenance and the development synthetic boundary; it should not become a remote-source client. No inbound HTTP/UI or database boundary is required for this first source slice.

**Phase 8 co-prerequisite:** a corporate source adapter is not authorized by this change. Corporate processing remains blocked until identity, authorization, privacy/sensitive screening, controlled provider, and TI gates are documented as passed. The safe first path is development-only synthetic metadata or a contract-only adapter test; it must not access SharePoint/Graph, Entra, managed identity, private endpoints, or corporate documents.

**Explicit exclusions:** PDF parsing, selectable-text extraction, structure-aware chunking, OCR, OCR quality decisions, image interpretation, embeddings, vector storage, PostgreSQL schema, index publication, atomicity, rollback, cleanup, advisory locking, idempotency, scheduled synchronization, administrator controls, corporate SharePoint/Graph integration, and provider egress. Those remain separate Phase 3 or Phase 8 changes.

### Affected Areas

- `backend/features/indexing/` — likely new owner for the source-repository port, source inventory application service, and future synchronization orchestration; the directory does not exist today.
- `backend/features/corpus/{domain.py,application.py}` — may need a small provider-independent source identity/provenance projection, but existing synthetic JSON loading must remain compatible and development-only.
- `backend/features/corpus/adapters/manifest_loader.py` — reference boundary only; do not turn the evaluation-dataset JSON loader into a corporate/source-repository adapter.
- `backend/features/evaluation/adapters/dataset.py` — preserve its validate-before-load behavior and keep evaluation fixtures separate from source discovery.
- `backend/shared/ports.py` — possible location for a narrowly scoped source port only if it is genuinely cross-feature; prefer feature ownership over expanding shared contracts.
- `tests/unit/` and `tests/architecture/` — deterministic tests for filename identity, language/revision independence, safe paths, hashes, duplicate identities, scan failures, and development/corporate denial.
- `governance/direct-dependencies.yaml` and `pyproject.toml` — likely unchanged if the first adapter uses the standard library; Docling is already governed but belongs to the later PDF/OCR ingestion change, not this one.
- `RAG_ROADMAP.md`, `AGENTS.md`, and `docs/architecture/platform-architecture.md` — authority and traceability references only during this exploration; no edits are justified now.

### Approaches

1. **Contract plus development-only local source inventory** — define a provider-neutral source descriptor/port and implement a safe local adapter that enumerates a controlled synthetic source fixture without interpreting file contents.
   - Pros: provides executable proof of identity, naming, path, hash, and fail-closed behavior; preserves the corporate boundary; creates a clean seam for later ingestion and corporate adapters; can remain dependency-free.
   - Cons: requires a deliberate fixture format because the current evaluation dataset is JSON rather than the Phase 3 PDF naming contract; does not yet prove corporate connectivity or document extraction.
   - Effort: Medium

2. **Contract-only source port and domain metadata** — establish interfaces and validation rules without a filesystem adapter, fixture, or scan implementation.
   - Pros: smallest and safest change; avoids choosing a local fixture representation before product questions are answered.
   - Cons: leaves no executable source-discovery behavior; pushes path, hash, duplicate, and scan-failure proof into a later change; may provide too little value for a change named repository integration.
   - Effort: Low

3. **Corporate SharePoint/Graph source adapter now** — connect the approved-source boundary directly to the future corporate repository.
   - Pros: tests the eventual source system early.
   - Cons: violates the explicit TI and Phase 8 sequencing boundary; introduces corporate data processing, remote permissions, managed identity/network decisions, and new dependencies before their SDD gates; creates a large and difficult rollback boundary.
   - Effort: High — not viable for this change

### Recommendation

Use Approach 1, bounded to **source metadata discovery and deterministic inventory**. The proposal should define the source descriptor and port, make the source of truth and filename identity rules explicit, and add a development-only local adapter or synthetic source fixture that proves safe enumeration and fail-closed diagnostics without reading document semantics. Keep `evaluation-dataset/` as a separate test/evaluation corpus unless the product owner explicitly approves a new fixture representation.

The implementation should be split conceptually into two reversible slices if the task forecast approaches the 800-line review budget: (A) provider-independent descriptor, validation policy, and port; (B) development local adapter plus deterministic inventory tests. A later change can consume the inventory for PDF/OCR ingestion, and separate later changes can own atomic publication and rollback. A corporate Graph/SharePoint adapter requires its own approved change after the Phase 8/TI gates.

**Open product questions before proposal:**

- Is the first accepted source adapter a local development filesystem fixture, or should this change remain contract-only until a governed source sample exists?
- Is the filename grammar exactly `<entry-id>_ESP_REV_<revision>.pdf` / `<entry-id>_EN_REV_<revision>.pdf`, or may an approved source provide an equivalent metadata contract? Which characters and revision forms are valid?
- Where does approval and classification come from for each source artifact: repository metadata, a sidecar/manifest, or a trusted adapter configuration? What is authoritative when they disagree?
- Should the source snapshot expose opaque bytes and hashes only, or also source timestamps/ETags? Timestamps must not become content identity unless explicitly governed.
- Does this change own only current inventory, or also an explicit add/modify/remove diff? The safer boundary is inventory here and synchronization/index lifecycle in the next slice.
- What is the required behavior when one artifact cannot be read: reject the complete snapshot, quarantine the artifact, or return a safe rejected-artifact report without treating the repository as complete?

### Risks

- Reusing the JSON evaluation manifest as the approved source repository would conflate test fixtures with the Phase 3 source-of-truth contract and could hide filename/language/revision errors.
- Treating a failed or partial scan as an empty repository could incorrectly revoke every current document in a later index operation; completeness must be explicit and fail closed.
- Independent Spanish and English revisions can be incorrectly deduplicated if identity is modeled as only `entry-id` and revision without language.
- Approval/classification metadata may be ambiguous at the source boundary; accepting untrusted file names or content as proof of approval would weaken the corporate safety invariant.
- Adding Docling, remote SDKs, or database wiring in this slice would broaden the change into extraction, corporate integration, or index lifecycle work and increase dependency and review risk.
- Corporate source access before Phase 8 identity, authorization, privacy, controlled-provider, and TI gates would violate the roadmap even if the adapter is technically replaceable.

### Ready for Proposal

Yes, conditionally. The repository evidence is sufficient to draft a bounded proposal for source metadata discovery and deterministic inventory. Before proposal, resolve the source fixture/contract choice, metadata authority, filename grammar, scan-failure semantics, and whether inventory-to-diff belongs here or in the next synchronization slice. Do not include PDF/OCR extraction, atomic publication, rollback, or corporate SharePoint/Graph integration in that proposal.
