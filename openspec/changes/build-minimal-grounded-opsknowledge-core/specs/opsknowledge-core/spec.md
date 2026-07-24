# OpsKnowledge Core Specification

## Purpose

The `opsknowledge-core` capability is a development-only CLI that resolves a free-text question over the manifest-controlled synthetic corpus loaded from `evaluation-dataset/`. It proves that Phase 1 can answer strictly from approved same-language evidence, abstain with human-expert guidance when evidence is missing, contradictory, out of scope, or unavailable, and never expose a sensitive or provider-failure path to any model. This capability is the Phase 1 slice of the OpsKnowledge platform; it does not introduce HTTP, sessions, databases, durable persistence, embeddings, OCR interpretation, reranking, or corporate/Azure integrations.

## Requirements

### Requirement: Development-Only Synthetic Corpus Boundary

The core SHALL run only when the active profile is `development`. The corpus loader SHALL consume entries from `evaluation-dataset/` whose manifest declares `classification: synthetic`, `approval: approved`, and `profile: development`. Any other classification, approval state, or profile SHALL cause the loader to fail closed at startup. The capability SHALL NOT provide a corporate ingestion or classification path; no path may load, expose, or reference a non-synthetic or non-development entry.

#### Scenario: Startup outside development profile fails closed

- GIVEN the active profile is not `development`
- WHEN the core starts
- THEN initialization fails with a safe diagnostic and the CLI does not run

#### Scenario: Non-synthetic entry is rejected

- GIVEN the manifest references an entry whose `classification` is not `synthetic`
- WHEN the corpus loader runs
- THEN the loader fails closed and no entry reaches retrieval

### Requirement: Free-Text CLI Entry Point

The core SHALL expose a CLI that accepts a single free-text question, the active profile, and optional deterministic overrides. The CLI SHALL print exactly one structured response per invocation and SHALL NOT open a server, persist the question, persist the answer, or establish a session.

#### Scenario: CLI resolves a question

- GIVEN the development profile is active and a question is provided
- WHEN `python -m backend.features.query.cli "..."` runs
- THEN it prints a single structured response and exits

### Requirement: High-Confidence Sensitive Screening

The core SHALL run a high-confidence sensitive screen against the question text before retrieval and before any provider call. A matching payload SHALL be blocked; only the blocking event (profile, reason code, safe path) SHALL be emitted; the question text, answer text, citations, and provider payload SHALL NEVER be logged or persisted. A residual-detection-risk notice SHALL be present in CLI help text.

#### Scenario: Sensitive payload is blocked

- GIVEN the question matches the sensitive screen
- WHEN the CLI processes it
- THEN retrieval and provider calls do not run, the response is `unavailable`, and only the blocking event is logged

#### Scenario: Rejected text is not persisted

- GIVEN the sensitive screen blocked a payload
- WHEN the process is inspected
- THEN no log, file, or downstream artifact contains the question text

### Requirement: Language-Filtered Retrieval

Retrieval SHALL detect the query language and SHALL consider only fragments whose language tag matches the query language. A fragment whose language differs from the query SHALL be excluded. Retrieval SHALL be deterministic: same input, profile, and corpus revision SHALL produce the same evidence set.

#### Scenario: Wrong-language fragment is excluded

- GIVEN an English query and a Spanish fragment exists in the corpus
- WHEN retrieval runs
- THEN the Spanish fragment is not in the evidence set

#### Scenario: Retrieval is deterministic

- GIVEN the same question, profile, and corpus revision
- WHEN the CLI runs twice
- THEN the evidence set and outcome are identical

### Requirement: Grounded Generation With Citations

Generation prompts SHALL contain ONLY approved, same-language fragments selected by retrieval. The model output SHALL be accepted as `supported` only if every cited fragment is approved, language-matched, and present in the retrieved set. Unsupported, out-of-scope, contradictory, or out-of-language cases SHALL be resolved by deterministic rule, not by the model.

#### Scenario: Supported answer cites only approved fragments

- GIVEN a question is grounded in approved fragments
- WHEN the CLI runs
- THEN the response outcome is `supported` and every citation points to an approved, language-matched fragment

#### Scenario: Insufficient evidence abstains

- GIVEN no approved same-language fragment satisfies the question
- WHEN the CLI runs
- THEN the outcome is `insufficient_information` and the response recommends a `human expert`

#### Scenario: Contradictory evidence abstains

- GIVEN retrieval surfaces two approved, same-language revisions of one entry that contradict each other
- WHEN the CLI runs
- THEN the outcome is `contradictory_information` and the response recommends a `human expert`

#### Scenario: Out-of-scope question abstains

- GIVEN the question matches an out-of-scope case type and the evidence set is empty
- WHEN the CLI runs
- THEN the outcome is `out_of_scope` and the response recommends a `human expert`

### Requirement: Provider Failure Returns Unavailable

The generation provider SHALL sit behind an outbound port with a deterministic fake adapter. Timeout, rate limit, outage, or any non-success response SHALL resolve the query to `unavailable`, recommend a `human expert`, make no further provider call, and persist no answer or question text. The capability SHALL NOT fabricate citations, fragments, or outcomes to recover from a failure.

#### Scenario: Provider timeout resolves to unavailable

- GIVEN the generation provider times out
- WHEN the CLI processes the question
- THEN the response is `unavailable`, no further provider call is made, and no answer is persisted

#### Scenario: Provider outage is not retried beyond bounded attempt

- GIVEN the generation provider is unavailable
- WHEN the CLI processes the question
- THEN the response is `unavailable` and at most the bounded retry budget was used

### Requirement: Session Expired Outcome

The core SHALL classify a question as `session_expired` only when an explicit session-expiry signal is present in the CLI invocation; otherwise the six-state outcome set collapses to the remaining five for this Phase 1 slice. The response SHALL recommend a `human expert` and SHALL persist nothing.

#### Scenario: Session-expired signal resolves to session_expired

- GIVEN the CLI is invoked with an explicit session-expired signal
- WHEN the CLI runs
- THEN the outcome is `session_expired`, the response recommends a `human expert`, and nothing is persisted

### Requirement: No Answer Persistence in This Slice

The core SHALL NOT persist the question, answer, citations, provider payload, or model output. The CLI response is the only durable artifact of an invocation, and it SHALL carry only safe fields (outcome, citations by reference, escalation guidance, profile, reason code).

#### Scenario: No durable state is written

- GIVEN a CLI invocation completes
- WHEN the working tree and logs are inspected
- THEN no file, database row, or log line contains the question, answer, or provider payload

### Requirement: Safe JSON and Logging Boundaries

The CLI SHALL emit a single JSON object with safe fields only: `outcome`, `citations` (by fragment identifier), `escalation` (human-expert guidance or none), `profile`, and `reason_code`. Logs SHALL be JSON and SHALL contain only safe fields (timestamps, profile, outcome, reason code, durations, attempt counts). Question text, answer text, citations content, tokens, secrets, and provider payloads SHALL NEVER appear in logs or CLI output.

#### Scenario: CLI output is safe and structured

- GIVEN a CLI invocation completes
- WHEN the JSON output is parsed
- THEN it contains only the safe fields and no question or answer text

#### Scenario: Logs never contain content

- GIVEN the CLI has been exercised across all outcomes
- WHEN the log stream is inspected
- THEN no entry contains question text, answer text, citation content, tokens, secrets, or provider payload
