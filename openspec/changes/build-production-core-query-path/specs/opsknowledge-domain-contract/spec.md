# Delta for OpsKnowledge Domain Contract

## MODIFIED Requirements

### Requirement: Citation-Only Evidence and Escalation

Every claim SHALL cite a current approved entry; conversation history, glossary, support history, and model knowledge SHALL NEVER be evidence. `supported` answers SHALL carry valid citations. The kernel MUST expose no answer/citations for `insufficient_information` or `contradictory_information`; both SHALL recommend a `human expert`.
(Previously: escalation was required, but the kernel’s no-answer/no-citation abstention boundary was not explicit.)

#### Scenario: Insufficient abstention

- GIVEN no approved fragment matches
- WHEN resolution completes
- THEN `insufficient_information`, no answer/citations, and a `human expert` recommendation

#### Scenario: Contradictory abstention

- GIVEN approved sources contradict
- WHEN resolution completes
- THEN `contradictory_information`, no answer, and a `human expert` recommendation

### Requirement: Six-State Outcome Taxonomy

The system SHALL classify resolved queries into `supported`, `insufficient_information`, `contradictory_information`, `out_of_scope`, `unavailable`, or `session_expired`. This kernel SHALL implement the first five; a later session capability SHALL own `session_expired`. Provider failure SHALL return `unavailable`, no answer, and a `human expert` recommendation; persistence is outside this kernel.
(Previously: the core contract did not defer `session_expired` to the later session capability.)

#### Scenario: Provider outage

- GIVEN provider is unavailable
- WHEN kernel resolution completes
- THEN `unavailable`, no answer, and a `human expert` recommendation

#### Scenario: Session expiry is deferred

- GIVEN no session capability exists
- WHEN it resolves a query
- THEN it never returns `session_expired`
