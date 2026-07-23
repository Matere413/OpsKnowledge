# Delta for evaluation-dataset

## ADDED Requirements

### Requirement: Evaluation Dataset Capability

A new capability `evaluation-dataset` SHALL provide a static, manifest-controlled, dependency-free bilingual synthetic corpus and scenario catalog that later Phase 1/2 changes can consume. The capability defines a manifest, synthetic entries across `runbooks`, `adrs`, and `operational-policies`, scenario records, fragment provenance, and a structural validator. The capability SHALL NOT perform retrieval, embedding, generation, database persistence, corporate ingestion, profile wiring, or Phase 2 measurement; any code path that would do so is out of scope and MUST fail closed at the validator boundary.

#### Scenario: Capability is a static dataset only

- GIVEN the capability is invoked
- WHEN a consumer inspects the artifacts
- THEN the artifacts are versioned repository files plus a structural validator
- AND no runtime calls, network I/O, provider configuration, or database access are introduced

#### Scenario: Capability is bounded to the development synthetic boundary

- GIVEN the dataset is consumed by any later change
- WHEN a consumer inspects classification and approval metadata
- THEN every entry is `classification: synthetic` and `approval: approved`
- AND no path exposes a corporate classification or an unapproved entry

### Requirement: Manifest-Controlled Synthetic Entries

The dataset SHALL include a deterministic manifest that lists every entry, fragment, and scenario with stable identifiers, language, revision, collection type, classification, approval state, content hash, and source fragment references. The manifest MUST be a single document; entries, fragments, and scenarios MUST each carry a stable, unique identifier that is referenced by the manifest and never reused across revisions.

#### Scenario: Stable identifiers are unique

- GIVEN the manifest lists every entry, fragment, and scenario
- WHEN the validator checks identifier uniqueness
- THEN duplicates within the dataset fail closed

#### Scenario: Manifest is exhaustive

- GIVEN an entry, fragment, or scenario file exists on disk
- WHEN the validator checks coverage
- THEN every file is declared in the manifest and every manifest reference resolves to a file
- AND orphan files or dangling references fail closed

#### Scenario: Content hashes match declared bytes

- GIVEN the manifest declares a content hash for an entry or fragment
- WHEN the validator recomputes the hash over the on-disk bytes
- THEN the recomputed hash equals the declared hash
- AND any mismatch fails closed

### Requirement: Three Approved Collection Types

The dataset SHALL cover all three approved collection types — `runbooks`, `adrs`, and `operational-policies` — with at least one synthetic entry per collection, each approved, versioned, language-tagged, and visibly non-corporate.

#### Scenario: All three collections are present

- GIVEN the dataset is validated
- WHEN the validator enumerates collection types
- THEN `runbooks`, `adrs`, and `operational-policies` are each present
- AND each has at least one entry that is approved, versioned, and language-tagged

#### Scenario: Collection types are exhaustive

- GIVEN a scenario or fragment references a collection
- WHEN the validator resolves the reference
- THEN the collection value is exactly one of `runbooks`, `adrs`, or `operational-policies`
- AND any other value fails closed

### Requirement: Approved and Classified Status

Every entry, fragment, and scenario SHALL carry an explicit `approval: approved` status and an explicit `classification: synthetic`. The validator MUST treat unapproved or non-synthetic classification as a fail-closed condition. Synthetic content SHALL never be rewired for corporate consumption; the manifest SHALL mark every entry as `profile: development`.

#### Scenario: Unapproved status is rejected

- GIVEN an entry or scenario declares any status other than `approved`
- WHEN the validator runs
- THEN validation fails closed

#### Scenario: Non-synthetic classification is rejected

- GIVEN an entry or fragment declares a classification other than `synthetic`
- WHEN the validator runs
- THEN validation fails closed

#### Scenario: Development profile is enforced

- GIVEN a manifest entry is not marked `profile: development`
- WHEN the validator runs
- THEN validation fails closed

### Requirement: Language Tagging and Fragment Isolation

Every entry, fragment, and scenario SHALL carry a language tag whose value is exactly `es` or `en`. A fragment's language tag MUST equal the parent entry's language tag. The validator SHALL fail closed on any fragment whose language differs from the parent entry, any evidence set that mixes languages for a single query, and any scenario whose evidence references fragments in a language other than the scenario's query language.

#### Scenario: Fragment language matches parent entry

- GIVEN an entry declares language `es`
- WHEN the validator inspects its fragments
- THEN every fragment declares language `es`
- AND a fragment declaring `en` fails closed

#### Scenario: Mixed-language evidence is rejected

- GIVEN a scenario with language `en` references both an `en` and an `es` fragment as evidence
- WHEN the validator runs
- THEN validation fails closed

#### Scenario: Evidence language matches query language

- GIVEN a scenario declares query language `es`
- WHEN the validator inspects the evidence set
- THEN every referenced fragment declares language `es`
- AND an `en` fragment in the evidence set fails closed

### Requirement: Revision and Provenance Metadata

Every entry SHALL declare a revision string and a content hash; every fragment SHALL declare a parent entry reference, a fragment identifier, and a content hash. A scenario's evidence references MUST point to a declared fragment identifier that exists under a declared parent entry. The validator SHALL fail closed on missing parent references, fragment identifiers that do not exist, or revision strings that contradict the manifest.

#### Scenario: Fragment provenance is traceable

- GIVEN a scenario references a fragment
- WHEN the validator resolves the reference
- THEN the fragment exists, has a parent entry declared in the manifest, and the parent entry is approved
- AND a missing or unapproved parent fails closed

#### Scenario: Revision metadata is consistent

- GIVEN the manifest declares a revision for an entry
- WHEN the validator compares it to the entry's declared revision
- THEN both values match
- AND any drift fails closed

### Requirement: Scenario Catalog of Exactly 32 Scenarios

The dataset SHALL include exactly 32 scenarios, organized as 16 bilingual semantic pairs. Each pair SHALL contain one `es` and one `en` scenario that share the same case type, the same expected outcome classification, the same safety classification, and the same evidence shape. The validator SHALL fail closed if the scenario count is not exactly 32, if the number of `es` scenarios is not 16, if the number of `en` scenarios is not 16, or if any bilingual pair is missing a counterpart in the opposite language.

#### Scenario: Scenario count is exactly 32

- GIVEN the dataset is validated
- WHEN the validator counts scenarios
- THEN the count equals 32
- AND any other count fails closed

#### Scenario: Sixteen bilingual pairs are present

- GIVEN the dataset is validated
- WHEN the validator groups scenarios by case type and expected outcome
- THEN each group contains exactly two scenarios — one `es` and one `en` — for 16 groups
- AND a group missing its counterpart fails closed

#### Scenario: Pair parity holds across language

- GIVEN an `es` scenario and an `en` scenario are declared as a pair
- WHEN the validator compares their case type, expected outcome, and safety classification
- THEN all three match
- AND any drift fails closed

### Requirement: 50/50 Grounded Versus Abstention Balance

The dataset SHALL contain exactly 16 scenarios whose expected outcome is a grounded, supported answer and exactly 16 scenarios whose expected outcome is an abstention or safety case. The validator SHALL fail closed on any deviation from this 50/50 split, including rounding, missing categories, or duplicate outcomes.

#### Scenario: Grounded count is exactly 16

- GIVEN the dataset is validated
- WHEN the validator counts scenarios whose expected outcome is a grounded outcome
- THEN the count equals 16
- AND any other count fails closed

#### Scenario: Abstention count is exactly 16

- GIVEN the dataset is validated
- WHEN the validator counts scenarios whose expected outcome is an abstention or safety outcome
- THEN the count equals 16
- AND any other count fails closed

#### Scenario: Every scenario declares an expected outcome

- GIVEN the dataset is validated
- WHEN the validator inspects each scenario
- THEN every scenario declares exactly one expected outcome drawn from the six-state taxonomy
- AND a missing or duplicate outcome fails closed

### Requirement: Outcome and Claim Expectations

Each scenario SHALL declare its expected outcome as exactly one of the six states defined by the OpsKnowledge domain contract: `supported`, `insufficient_information`, `contradictory_information`, `out_of_scope`, `unavailable`, or `session_expired`. Each scenario SHALL declare the expected claim or abstention reason and the expected evidence references; a scenario with expected outcome `supported` MUST list the evidence fragments that justify it. The dataset MUST NOT include any literal generated gold answer, paraphrase of a model output, or prose that could be read as authoritative answer text; the only expected answer content is the outcome label, the evidence references, the claim expectation, and the abstention reason.

#### Scenario: Outcome is from the six-state taxonomy

- GIVEN a scenario declares an expected outcome
- WHEN the validator validates the value
- THEN the value is one of the six declared states
- AND any other value fails closed

#### Scenario: Supported scenarios declare evidence

- GIVEN a scenario's expected outcome is `supported`
- WHEN the validator inspects the scenario
- THEN it references at least one approved, language-matched fragment whose parent entry is approved
- AND missing evidence fails closed

#### Scenario: No literal gold answers

- GIVEN the dataset is reviewed for answer text
- WHEN the validator scans scenario records
- THEN no field contains a literal generated reference answer, paraphrase, or model-style completion
- AND any such field fails closed

### Requirement: Contradiction Cases Use Paired Synthetic Revisions

Scenarios whose expected outcome is `contradictory_information` SHALL be constructed from two paired synthetic revisions of the same entry, where each revision is independently approved and language-tagged and the contradiction is visible in the manifest. The validator SHALL fail closed if a contradiction scenario references only a single revision, references revisions that are not both approved, or relies on entries that are not synthetic.

#### Scenario: Contradiction uses paired revisions

- GIVEN a scenario with expected outcome `contradictory_information`
- WHEN the validator inspects the evidence references
- THEN exactly two revisions of the same parent entry are referenced
- AND both revisions are approved, language-matched, and synthetic
- AND any other shape fails closed

#### Scenario: Contradiction is language-isolated

- GIVEN an `es` contradiction scenario and its `en` counterpart
- WHEN the validator compares their revisions
- THEN each references revisions in its own declared language
- AND a cross-language revision reference fails closed

### Requirement: OCR Uncertainty Cases Use Provenance-Marked Text

Scenarios that exercise OCR uncertainty SHALL reference fragments that originate from extracted OCR text, where each fragment declares an OCR provenance marker, a source reference, and a quality indicator. The dataset MUST NOT include, describe, or imply image content; the only OCR-related data is the extracted text plus provenance metadata.

#### Scenario: OCR fragments declare provenance

- GIVEN a scenario exercises OCR uncertainty
- WHEN the validator inspects its evidence fragments
- THEN each fragment declares `provenance: ocr`, a source reference, and a quality indicator
- AND a missing marker fails closed

#### Scenario: No image content is represented

- GIVEN the dataset is reviewed
- WHEN the validator scans for image content
- THEN no entry, fragment, or scenario references an image, screenshot, photograph, or visual interpretation
- AND any such reference fails closed

### Requirement: Prompt Override and Unanswerable Cases

Scenarios that exercise prompt override, out-of-scope, or unanswerable behavior SHALL declare the override intent or the abstention reason explicitly and SHALL NOT include any evidence that would resolve the question. The validator SHALL fail closed if a prompt-override scenario includes resolvable evidence, if an out-of-scope scenario declares evidence at all, or if an unanswerable scenario declares a supported outcome.

#### Scenario: Prompt override has no resolvable evidence

- GIVEN a scenario declares a prompt-override case type
- WHEN the validator inspects the evidence set
- THEN the evidence set is empty
- AND non-empty evidence fails closed

#### Scenario: Out-of-scenario declares no evidence

- GIVEN a scenario declares an out-of-scope case type
- WHEN the validator inspects the evidence set
- THEN the evidence set is empty
- AND any evidence fails closed

#### Scenario: Unanswerable scenario abstains

- GIVEN a scenario declares an unanswerable case type
- WHEN the validator inspects the expected outcome
- THEN the expected outcome is one of `insufficient_information`, `out_of_scope`, or `unavailable`
- AND any other outcome fails closed

### Requirement: Sensitive Identifier Cases Are Obviously Fictitious

Scenarios that exercise sensitive data screening SHALL use obviously fictitious synthetic identifiers that are visibly not real, such as placeholder names, reserved example domains, or test-only patterns. The dataset MUST NOT include real names, real domains, real customer identifiers, or any value that could be confused with production data. The validator SHALL fail closed if a sensitive case references a non-obviously-fictitious identifier or omits the fictitious marker.

#### Scenario: Fictitious markers are present

- GIVEN a scenario exercises sensitive screening
- WHEN the validator inspects the identifiers
- THEN every identifier carries an explicit `fictitious: true` marker or is drawn from a reserved example domain
- AND missing markers fail closed

#### Scenario: Production-looking identifiers are rejected

- GIVEN a sensitive case references an identifier that could plausibly be a real production value
- WHEN the validator runs
- THEN validation fails closed

### Requirement: Dependency-Free Structural Validator

The dataset SHALL ship with a structural validator that runs without network access, without database access, without provider configuration, and without any new production dependency. The validator SHALL be invokable by `make ci`, SHALL return zero on a fully valid dataset, and SHALL return non-zero with a stable, safe diagnostic for every documented failure mode. Diagnostics MUST include a safe repository-relative path or identifier, a stable reason code, and a concrete remediation hint; diagnostics MUST NOT include scenario content, evidence text, or model-style answer text.

#### Scenario: Validator runs without external dependencies

- GIVEN the validator is invoked
- WHEN the environment is inspected
- THEN no network, database, provider, or filesystem traversal outside the dataset directory occurs
- AND any external call fails closed

#### Scenario: Valid dataset returns zero

- GIVEN a manifest, entries, fragments, and scenarios that satisfy every requirement
- WHEN the validator runs to completion
- THEN the exit code is zero and no finding is reported

#### Scenario: Diagnostics are safe and actionable

- GIVEN the validator reports a finding
- WHEN the diagnostic is reviewed
- THEN it contains a safe path or identifier, a stable reason code, and a remediation hint
- AND it does not contain scenario content, evidence text, or generated answer text

### Requirement: Fail-Closed Behavior for Documented Violations

The validator SHALL fail closed for every documented integrity and isolation violation: malformed or non-synthetic data, invalid source references, invalid fragment provenance, duplicate identifiers, mixed-language evidence, parity failure between language pairs, balance or count deviation, missing or extra files relative to the manifest, and OCR or sensitive-identifier metadata gaps. Each failure mode SHALL map to a stable reason code so consumers can distinguish them.

#### Scenario: Malformed data fails closed

- GIVEN a manifest entry, scenario, or fragment is missing a required field or carries a value of the wrong type
- WHEN the validator runs
- THEN it fails closed with a stable reason code naming the field and the safe path

#### Scenario: Invalid references fail closed

- GIVEN a scenario references a fragment identifier, parent entry, or revision that does not exist
- WHEN the validator runs
- THEN it fails closed with a stable reason code naming the missing reference

#### Scenario: Duplicate identifiers fail closed

- GIVEN two entries, fragments, or scenarios share the same stable identifier
- WHEN the validator runs
- THEN it fails closed with a stable reason code naming both occurrences

#### Scenario: Mixed-language evidence fails closed

- GIVEN a scenario's evidence set contains fragments in more than one language
- WHEN the validator runs
- THEN it fails closed with a stable reason code naming the offending fragment

#### Scenario: Parity failure fails closed

- GIVEN a bilingual pair does not share the same case type, expected outcome, or safety classification
- WHEN the validator runs
- THEN it fails closed with a stable reason code naming the pair

#### Scenario: Count or balance deviation fails closed

- GIVEN the scenario count, language split, or grounded/abstention split deviates from the documented targets
- WHEN the validator runs
- THEN it fails closed with a stable reason code naming the actual and expected values

### Requirement: Explicit Prohibitions

The dataset and validator SHALL NOT include, configure, or wire any of the following: literal generated gold answers as authoritative answer text, runtime retrieval, runtime embedding, runtime generation, database seeding, database persistence, corporate ingestion, profile wiring, or Phase 2 metrics, baseline reports, or release thresholds. The validator SHALL treat any such wiring as a fail-closed condition. These prohibitions are non-negotiable and inherited from the cross-phase safety invariants; they apply for the entire lifetime of the dataset and any later change that consumes it.

#### Scenario: No runtime wiring

- GIVEN a reviewer inspects the dataset and validator
- WHEN they search for provider calls, network clients, database drivers, or profile configuration
- THEN none are present
- AND any such wiring fails closed

#### Scenario: No corporate ingestion path

- GIVEN a reviewer inspects how the dataset is loaded
- WHEN they trace every entry point
- THEN no path loads the dataset under a corporate classification or outside the development profile
- AND any such path fails closed

#### Scenario: No Phase 2 measurement

- GIVEN a reviewer inspects the dataset and validator
- WHEN they search for metrics, baseline reports, evaluator commands, or release thresholds
- THEN none are present
- AND any such artifact fails closed

### Requirement: Testable Without Runtime Capabilities

Every requirement in this spec SHALL be testable using only the dataset files, the validator, and the existing dependency-free test harness. Tests SHALL NOT rely on retrieval, embedding, generation, database state, provider configuration, network access, or any capability that does not exist in the repository at the time the change is verified. The test plan SHALL use deterministic fixtures and SHALL assert both happy-path and documented-failure behaviors of the validator.

#### Scenario: Tests use the validator and fixtures

- GIVEN the test plan is executed
- WHEN tests run
- THEN they use the validator, the dataset files, and deterministic fixtures only
- AND they do not require retrieval, embedding, generation, database, network, or provider state

#### Scenario: Tests assert fail-closed behaviors

- GIVEN the test plan is executed
- WHEN a documented violation is introduced in a fixture
- THEN the validator reports the matching stable reason code
- AND the test passes only when the diagnostic is exact
