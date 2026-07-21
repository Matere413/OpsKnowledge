# Phase 0 Roadmap Reconciliation Specification

## Purpose

Define the documentation contract for reconciling Phase 0 with the current OpsKnowledge boundary. This change updates roadmap wording only; it MUST NOT create data, alter runtime behavior, or weaken governing safety and prototype/corporate invariants.

## Requirements

### Requirement: Current Phase 0 Input and Dataset Balance

Phase 0 SHALL identify one current required input: a manifest-controlled, versioned, approved, language-tagged, visibly non-corporate, development-only synthetic sample spanning `runbooks`, `adrs`, and `operational-policies`. The initial bilingual evaluation slice SHALL target 50% answerable/grounded cases and 50% abstention/safety cases with Spanish/English parity.

#### Scenario: Synthetic sample is the immediate prerequisite

- GIVEN a reader reviews Phase 0 pending inputs
- WHEN the current prerequisite is identified
- THEN only the governed synthetic bilingual sample is required now
- AND no corporate material is implied or invented

#### Scenario: Balanced bilingual slice is explicit

- GIVEN Phase 0 describes expected evaluation coverage
- WHEN a reviewer checks the dataset target
- THEN answerable/grounded and abstention/safety cases are each 50%
- AND equivalent Spanish and English coverage is required

### Requirement: Controlled References and Evidence Boundaries

Phase 0 SHALL describe historical corporate metrics, historical Q&A/support reports, and corporate glossaries as optional future controlled references, never as prerequisites or answer evidence. Such references MUST NOT override citation-only evidence, abstention, language isolation, or the synthetic development-only boundary.

#### Scenario: Unavailable corporate inputs do not block progress

- GIVEN corporate metrics, Q&A reports, or glossaries are unavailable
- WHEN Phase 0 completion is assessed
- THEN the Phase 0 foundation remains actionable
- AND no replacement corporate data is fabricated

#### Scenario: Historical reference is not evidence

- GIVEN a future controlled historical reference is available
- WHEN roadmap wording describes its use
- THEN it is limited to evaluation or later impact measurement
- AND it cannot serve as answer evidence or automatic ground truth

### Requirement: Roadmap Consistency and Phase 4 Placement

The reconciled roadmap SHALL use consistent wording for objective, scope, pending inputs, expected outputs, candidate list, completion/next-step language, and the Phase 4 candidate list. Phase 0 SHALL not retain a terminology-map candidate; terminology query expansion SHALL be assigned to Phase 4 as `add-approved-terminology-query-expansion` and remain query-understanding-only, never evidence.

#### Scenario: Candidate sequencing is unambiguous

- GIVEN a reviewer compares Phase 0 and Phase 4
- WHEN candidate changes and next steps are checked
- THEN evaluation-dataset work follows the reconciled Phase 0 foundation
- AND terminology query expansion appears only in Phase 4

#### Scenario: Documentation-only scope is preserved

- GIVEN this change is reviewed for implementation impact
- WHEN its affected artifacts are inspected
- THEN only roadmap documentation is reconciled
- AND no dataset, runtime, corporate-data intake, or non-roadmap product artifact is created
- AND normal SDD planning, verification, and archive artifacts remain permitted
