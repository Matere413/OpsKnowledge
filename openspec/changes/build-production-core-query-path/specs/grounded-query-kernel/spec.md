# Grounded Query Kernel Specification

## Purpose

Query approved development evidence deterministically. HTTP, UI, sessions, embeddings, live providers, persistence, and corporate processing before Phase 8/TI are out of scope.

## Requirements

### Requirement: Evidence Selection and Ranking

Fragments MUST carry parent provenance, approved version, `synthetic` classification, and `development` profile. Exact language (`en`/`es`) MUST precede ranking/provider input; unsafe/ambiguous metadata MUST fail closed. Ranking SHALL be deterministic and tie-stable.

#### Scenario: Ranked evidence

- GIVEN development contains approved, versioned synthetic English evidence
- WHEN an English query retrieves
- THEN it is eligible in repeatable order

#### Scenario: Exclusion

- GIVEN metadata is unsafe, ambiguous, corporate, or wrong-language
- WHEN retrieval runs
- THEN it is excluded before ranking/provider input

### Requirement: Grounded Prompt and Citations

Provider input SHALL contain only the query, grounding rules, and same-language fragments. History, glossary, support history, model knowledge, and user instructions SHALL NOT be evidence. `supported` citations MUST identify retrieved approved fragments; invalid or missing citations fail closed.

#### Scenario: Valid citations

- GIVEN fragments support a query
- WHEN the provider cites only retrieved fragments
- THEN the result is `supported` with their identifiers

#### Scenario: Invalid citation

- GIVEN output cites an unapproved, unretrieved, or wrong-language fragment
- WHEN citation validation runs
- THEN no `supported` result is returned

### Requirement: Safety Outcomes

Before retrieval/provider, sensitive input MUST return `unavailable` (`sensitive_blocked`). Insufficient, contradictory, and out-of-scope inputs MUST return canonical outcomes; contradiction MUST NOT prefer a revision. Each MUST expose no answer/citations and recommend a human expert where applicable.

#### Scenario: Sensitive block

- GIVEN sensitive input
- WHEN classified
- THEN `unavailable`, no answer/citations, and no provider call

#### Scenario: Abstention is safe

- GIVEN input is insufficient, contradictory, or out of scope
- WHEN outcome classification runs
- THEN corresponding outcome has no answer/citations and recommends a `human expert`

### Requirement: Provider and Side-Effect Safety

The provider MUST remain replaceable; identical fake prompt/configuration MUST produce identical text/citations. Timeout, rate-limit, outage, or other failure MUST return `unavailable`, recommend a human expert, expose no answer/citations, and make no unbounded retry. Text MAY exist only in memory for validation; content MUST NOT be persisted/logged and live providers are forbidden.

#### Scenario: Fake reproducibility

- GIVEN identical prompt and fake-provider configuration
- WHEN fake generation repeats
- THEN text and citation identifiers are identical

#### Scenario: Provider failure

- GIVEN fake provider reports an outage
- WHEN kernel resolves
- THEN `unavailable` has no answer, persistence, logging, or fabricated evidence
