# Language and Abstention Evaluation Specification

## Purpose

Define a contract for routing, correct abstention, and unsupported-claim escape.

## Requirements

### Requirement: Replacement Population

The evaluator SHALL replace—not append—the 34-case baseline with a reviewed versioned population. Runs SHALL identify both versions; evidence is immutable. Expected results MUST NOT change for scoring.

#### Scenario: Lineage

- GIVEN a reviewed replacement population and 34-case evidence
- WHEN a new baseline is accepted
- THEN only the replacement is current, its version is identifiable, and prior evidence remains

### Requirement: Contract Metrics

Each metric SHALL expose numerator/denominator. Language accuracy uses routing-reached cases, excluding sensitive blocks/provider failures. Correct abstention requires expected outcome, reason code, empty citations, and human-expert recommendation. Unsupported-claim escape requires no unsupported claim plus its abstention contract. Other denominators are named; zero MUST fail closed.

#### Scenario: Contracts and exclusions

- GIVEN eligible, screened, provider-failure, abstention, and unsupported-claim cases
- WHEN metrics are computed
- THEN named populations and exclusions define denominators, and wrong abstention contracts or emitted unsupported claims are not counted

### Requirement: Safe Evidence

Reports SHALL be deterministic for identical inputs and clock state, with ordered serialization. They MAY contain only IDs, enums, versions, timestamps, booleans, counts, and rates; they MUST exclude question, answer, citation content, claims, and provider payloads. Runtime state MUST NOT persist.

#### Scenario: Deterministic reports

- GIVEN identical replacement inputs, a frozen clock, and protected text in execution data
- WHEN the evaluator runs twice and reports
- THEN outputs match byte-for-byte and protected text is absent

### Requirement: Development Boundary

The evaluator MUST use only the manifest-controlled development synthetic corpus and deterministic in-process fake-provider kernel. It MUST NOT use live providers, embeddings, persistence, HTTP, UI, corporate data, or excluded dependencies. It SHALL be opt-in, non-gating, and outside `make ci` and `ci-pr2a`.

#### Scenario: Closed boundary

- GIVEN a contributor does not explicitly invoke the evaluation
- WHEN `make ci` or `ci-pr2a` runs
- THEN it is not required and no external or corporate capability is invoked

### Requirement: Corrections and Rollback

Corrections SHALL address only failures demonstrated by replacement cases and MUST preserve safety, mapping non-authority, thresholds, and CI membership. Rollback SHALL restore the prior baseline without deleting history or changing archived gate semantics.

#### Scenario: Rollback history

- GIVEN a replacement baseline is rolled back
- WHEN the rollback completes
- THEN the prior baseline is active, replacement evidence remains retained, and gate thresholds and CI membership remain unchanged
