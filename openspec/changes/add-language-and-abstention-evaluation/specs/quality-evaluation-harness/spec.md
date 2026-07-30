# Delta for quality-evaluation-harness

## MODIFIED Requirements

### Requirement: Preserve the Fixed Scenario Set

Each replacement run MUST contain exactly the versioned population, not an append to the active 34-case baseline. Manifest bytes and mapping authority remain unchanged. Injected failures MUST be declared and in-memory only. Prior evidence remains historical.

#### Scenario: Population assembly

- GIVEN a valid manifest, reviewed mapping, replacement population, and prior baseline
- WHEN a run is assembled
- THEN every record belongs to it, no case is appended, and prior evidence is not overwritten

### Requirement: Measure Five Baseline Signals

The harness MUST continue reporting numeric outcome classification, exact citation-set match, language routing, sensitive block, and contradiction detection. It MUST emit numbers only, define no thresholds, and leave the gate's five-signal contract unchanged.

#### Scenario: Gate separation

- GIVEN a completed replacement run
- WHEN its summary is inspected
- THEN the five signals remain numeric and threshold-free, and new metrics do not change gate thresholds or inputs

### Requirement: Keep Evidence Opt-In and Non-Gating

The harness MUST run only through explicit opt-in evaluation, version reviewed evidence under `evaluation-runs/`, retain current/previous baselines plus history, leave `make ci`/`ci-pr2a`, thresholds, and archived gate semantics unchanged, and persist no runtime query state.

#### Scenario: Bounded evidence

- GIVEN `make ci` or `ci-pr2a` runs without explicit evaluation
- WHEN recipes and evidence are inspected
- THEN CI is unchanged, no new floor is applied, and current, previous, and historical evidence remain available
