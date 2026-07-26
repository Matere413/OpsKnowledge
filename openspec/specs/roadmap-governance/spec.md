# Delta for Roadmap Governance

## ADDED Requirements

### Requirement: Direct-to-Corporate Roadmap Representation

The roadmap `RAG_ROADMAP.md` MUST present a direct-to-corporate path that absorbs Phase 1 history without claiming a working runtime exists. Phase 1 numeric history, archived artifacts, and Engram lineage SHALL remain discoverable; the in-scope implementation footprint SHALL be described as planned, not delivered.

#### Scenario: Roadmap absorbed Phase 1

- GIVEN `RAG_ROADMAP.md` is updated by this change
- WHEN a reader inspects the Phase 1 section
- THEN Phase 1 is labeled absorbed into the production-core path
- AND no claim that retrieval, prompt, provider, outcome, or CLI runtime is delivered appears

#### Scenario: Phase 0 wording remains unchanged

- GIVEN `audit-opsknowledge-phase-0-inputs` owns Phase 0 input wording
- WHEN this change edits the roadmap
- THEN Phase 0 wording owned by the audit change is not duplicated or rewritten

### Requirement: PR #28 Receipt and Pending Inventory

The closure note `phase-1-lineage-closure.md` MUST cite PR #28 and merge `12ba6926`, record the fail-closed synthetic corpus boundary, shared hexagonal ports, and corpus domain/application/loader as the only delivered scope, and MUST list retrieval, prompt, provider, outcome, and CLI as pending. PR #28, its receipt, and prior SDD artifacts MUST NOT be rewritten, re-archived, or deleted.

#### Scenario: Bounded delivery credit

- GIVEN the closure note exists
- WHEN a reader cross-references the merge `12ba6926`
- THEN only the corpus boundary, shared ports, and corpus domain/application/loader are credited
- AND retrieval, prompt, provider, outcome, and CLI appear as pending

#### Scenario: Historical evidence preserved

- GIVEN PR #28 and prior SDD artifacts exist
- WHEN this change is applied or rolled back
- THEN PR #28, its receipt, and prior SDD artifacts are unchanged
- AND no `openspec/changes/archive/` entry for them is modified

### Requirement: Phase 2 and Cross-Phase Safety Invariants

Phase 2 evaluation assets and the cross-phase safety invariants in `RAG_ROADMAP.md` and `AGENTS.md` SHALL remain required. This change MUST NOT relax, remove, or silently rephrase them.

#### Scenario: Phase 2 retained

- GIVEN the roadmap is reframed
- WHEN a reader locates Phase 2
- THEN its evaluation objective, expected outputs, and pending inputs are still present

#### Scenario: Safety invariants preserved

- GIVEN `AGENTS.md` lists non-negotiable safety invariants
- WHEN the roadmap and architecture documents are diffed
- THEN each invariant is referenced or preserved verbatim

### Requirement: Corporate Processing Prerequisite Gates

No corporate data processing SHALL be represented as available until identity, authorization, privacy/sensitive screening, controlled provider, and TI gates are all documented as passed. The roadmap MUST position Phase 8 gates as a co-prerequisite of Phases 3–5.

#### Scenario: Gates block corporate processing

- GIVEN any of identity, authorization, privacy screen, controlled provider, or TI gates is unmet
- WHEN the roadmap is read
- THEN the corporate path is shown as blocked
- AND the unmet gate is named

#### Scenario: Synthetic and demo boundaries stay separate

- GIVEN the development synthetic fixture and the public-OpenAI demo risk
- WHEN the roadmap is read
- THEN they are described as two separate validation-only concerns
- AND neither authorizes corporate processing

### Requirement: Documentation-Only Scope Enforcement

The implementation edit of this change SHALL be limited to three product-documentation files: `RAG_ROADMAP.md`, `docs/architecture/platform-architecture.md`, and the new `phase-1-lineage-closure.md` note. Current-change SDD planning and lineage artifacts inside `openspec/changes/reframe-roadmap-for-direct-corporate-product/` (proposal, design, spec, tasks, exploration, closure note) MAY be created or updated as lifecycle artifacts of this change and do not count as implementation edits. The change MUST NOT modify runtime code, manifests, lockfiles, tests, CI gates, provider configuration, corporate data references, `AGENTS.md`, prior Phase 1 SDD artifacts, archive entries, or receipt/history files. The 48-line product-documentation implementation edit stays below the 400-line review budget; the full native frozen transaction snapshot is 463 changed lines, including 415 added lines across the six SDD lifecycle artifacts, and a maintainer-approved `size:exception` keeps it as one documentation delivery without splitting or re-scoping.

#### Scenario: Allowlist respected

- GIVEN the change is applied
- WHEN the working tree is diffed
- THEN the only implementation edits are `RAG_ROADMAP.md`, `docs/architecture/platform-architecture.md`, and `phase-1-lineage-closure.md`
- AND current-change SDD planning/lineage artifacts in `openspec/changes/reframe-roadmap-for-direct-corporate-product/` MAY also appear as added or modified lifecycle artifacts
- AND no runtime, manifest, lockfile, test, `AGENTS.md`, prior Phase 1 SDD, archive, or receipt/history file is touched

#### Scenario: Budget guard

- GIVEN the product-documentation implementation edit is computed
- WHEN `git diff --stat` is run on the three allowed implementation files
- THEN their combined changed lines are below 400
- AND the maintainer-approved `size:exception` is recorded for the 463-line full native snapshot that additionally contains 415 added lines across the six SDD lifecycle artifacts
