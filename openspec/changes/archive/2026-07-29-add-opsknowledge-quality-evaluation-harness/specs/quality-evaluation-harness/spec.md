# Quality Evaluation Harness Specification

## Purpose

Provide a reproducible, development-only Phase 2 harness for the in-process grounded-query kernel, without changing dataset semantics or a release gate.

## Requirements

### Requirement: Validate Before Execution

The harness MUST validate the manifest-controlled dataset before execution. Any validation error MUST fail closed with a reason and zero executed scenarios.

#### Scenario: Validation gates execution

- GIVEN the catalog is valid or has an integrity, language, count, or profile violation
- WHEN the harness starts
- THEN a valid catalog proceeds, while an invalid catalog invokes neither kernel nor provider

### Requirement: Preserve the Fixed Scenario Set

Each run MUST contain exactly 32 unchanged dataset scenarios plus exactly two in-memory cases labeled `injected-provider-failure-es` and `injected-provider-failure-en`. The pair MUST NOT edit or persist in the base dataset.

#### Scenario: Exact population is assembled

- GIVEN a valid catalog and failure injection
- WHEN a run is assembled
- THEN it contains exactly 34 records, with the original dataset bytes unchanged

### Requirement: Keep Question Mapping Non-Authoritative

The harness MUST use a reviewed, harness-owned ES/EN mapping from scenario IDs to deterministic questions. Mapping text is input only, never answer ground truth; outcomes and evidence references remain dataset metadata. Missing, duplicate, unreviewed, or language-mismatched mappings MUST fail closed.

#### Scenario: Reviewed mapping resolves only its scenario

- GIVEN every base ID has a reviewed question in its declared language
- WHEN inputs are resolved
- THEN each question maps only to that scenario and no mapping text becomes an answer expectation

### Requirement: Use Only the Development Kernel Boundary

Execution MUST use only the `development` profile, existing in-process kernel, lexical retrieval, and fake-provider boundary. It MUST NOT use new dependencies, live providers, embeddings, persistence, HTTP, auth, UI, corporate data, or external services. The injected pair MUST preserve typed `unavailable` semantics and never fabricate evidence.

#### Scenario: Provider failure stays local and typed

- GIVEN the development profile and an injected ES or EN provider failure
- WHEN the fake-provider boundary raises its typed failure
- THEN the kernel records `unavailable` with its reason and no fabricated evidence, without external calls

### Requirement: Measure Five Baseline Signals

The harness MUST report numeric counts/rates for outcome classification, exact citation-set match, language routing, sensitive block, and contradiction detection. It MUST emit numbers only and define no release thresholds.

#### Scenario: Five measurements are complete

- GIVEN all 34 records finish
- WHEN results are summarized
- THEN each measurement has numeric values and no threshold decision

### Requirement: Make Runs Deterministic

The harness MUST inject a deterministic `Clock`, derive run identity from stable inputs and clock state, and serialize repeatable output for identical dataset, mapping, kernel, and provider inputs.

#### Scenario: Repeated frozen runs match

- GIVEN identical inputs and frozen clock state
- WHEN the run executes twice
- THEN identity, ordering, metrics, and serialized output match byte-for-byte without wall-clock reads

### Requirement: Expose Safe Reports Only

The harness MUST produce an allowlisted JSON summary, JSONL scenario records, and concise human output. Allowed fields are IDs, enums, versions, timestamps, booleans, counts, and rates; outputs MUST exclude question/answer/citation content, claim text, and provider payloads.

#### Scenario: Safe serialization excludes content

- GIVEN protected text exists in an input, answer, citation, claim, or provider payload
- WHEN any report or human output is produced
- THEN that text is absent and only allowlisted fields remain

### Requirement: Keep Evidence Opt-In and Non-Gating

The harness MUST run only through opt-in `make eval-quality`, version reviewed evidence under `evaluation-runs/`, retain current and previous baselines, leave `make ci` ordering and membership unchanged, and persist no runtime query state.

#### Scenario: Opt-in evidence stays bounded

- GIVEN `make ci` runs without opting in, or a newer reviewed baseline replaces the current one
- WHEN the recipe/evidence is inspected
- THEN CI remains unchanged and current plus previous safe baselines remain without thresholds or runtime state
