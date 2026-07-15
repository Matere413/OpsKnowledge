# OpsKnowledge Domain Contract

## Purpose

OpsKnowledge is a bilingual technical knowledge platform over approved, versioned runbooks, ADRs, and operational policies. The six-state outcome taxonomy, citation-only evidence, sensitive screening, atomic query persistence, advisory-locked indexes, safe JSON logs, demo/corporate separation, dependency exclusions, and corporate TI gates are product behavior.

## Requirements

### Requirement: OpsKnowledge Identity

The system SHALL be identified as **OpsKnowledge** across contributor-facing artifacts. OpsKnowledge is not generic document chat, not a clinical/patient system, and not patient-specific analysis.

#### Scenario: Consistent naming

- GIVEN a contributor reads roadmap, architecture, and AGENTS
- WHEN they look up the name
- THEN files use "OpsKnowledge" and dental terminology is absent from live scope

### Requirement: Approved Versioned Collections

The system SHALL organize evidence into three approved, versioned collections: `runbooks`, `adrs`, `operational-policies`. Each entry MUST carry a version, approval status, and synthetic classification when not corporate. Unapproved or unversioned content SHALL NOT be reachable.

#### Scenario: Evidence is approved and versioned

- GIVEN a query is in scope
- WHEN retrieval selects evidence
- THEN every fragment is approved, versioned, classified

### Requirement: Corpus Separation

Synthetic, non-corporate content SHALL stay separate from any corporate collection. A development profile MAY load synthetic manifest-controlled documents; CI SHALL fail if synthetic corpora are wired outside `development`. Corporate MVP MUST NOT cross-load.

#### Scenario: Non-development startup fails

- GIVEN synthetic manifest documents are configured
- WHEN startup occurs outside `development`
- THEN startup fails

### Requirement: Bilingual Fragment Isolation

Every evidence fragment SHALL be tagged with language. Retrieval SHALL filter fragments to query language: English considers only English fragments; Spanish only Spanish. A bilingual approved entry MAY exist, but each fragment within it SHALL still be filtered to the query language.

#### Scenario: Wrong-language fragment

- GIVEN an English query
- WHEN a Spanish fragment is evaluated
- THEN it is excluded

### Requirement: Role Contract

The system SHALL recognize four example roles: `reader`, `contributor`, `reviewer`, `admin`. Protected use cases are deny-by-default; authorization SHALL run before identified records are returned.

#### Scenario: Role denial blocks protected use case

- GIVEN a `reader` requests a protected operation
- WHEN authorization evaluates the request
- THEN it is denied and audited; no identified record is returned

### Requirement: Citation-Only Evidence and Escalation

Every claim SHALL cite a current approved entry; conversation history, glossary, support history, and model knowledge SHALL NEVER be evidence. `supported` answers SHALL carry valid citations. `insufficient_information` and `contradictory_information` SHALL escalate to a `human expert`.

#### Scenario: Insufficient evidence escalates

- GIVEN no approved fragment satisfies the evidence rules
- WHEN resolution completes
- THEN it returns `insufficient_information` recommending a `human expert`

### Requirement: Six-State Outcome Taxonomy

The system SHALL classify every resolved query into one of: `supported`, `insufficient_information`, `contradictory_information`, `out_of_scope`, `unavailable`, `session_expired`. Provider failure and persistence failure SHALL resolve to `unavailable`, persist no answer, and recommend a `human expert`. Session inactivity SHALL resolve to `session_expired`. No ad-hoc statuses.

#### Scenario: Outage resolves to unavailable

- GIVEN the generation or embedding provider is unavailable
- WHEN resolution completes
- THEN it returns `unavailable` and persists no answer

### Requirement: Sensitive Screening

The system SHALL run a high-confidence sensitive screen before embedding, generation, or storage. A matching payload SHALL be blocked; only the blocking event SHALL be logged; no content, citation, or token SHALL be persisted.

#### Scenario: Sensitive payload blocked

- GIVEN a payload triggers the sensitive screen
- WHEN the resolution path processes it
- THEN it is blocked and only the blocking event is logged

### Requirement: Dental-Contract Supersession

Dental-domain contracts SHALL be marked superseded by OpsKnowledge. Superseded artifacts MUST stay reachable as audit history, MUST NOT be deleted, and MUST be linked from roadmap, architecture, and AGENTS.

#### Scenario: Dental artifact visible as superseded

- GIVEN a reader queries the prior dental contract
- WHEN they retrieve the artifact
- THEN it is present, marked superseded, and linked to the OpsKnowledge replacement
