# Proposal: Technical Grounding Safety Gates

## Intent

Phase 2 has a kernel and numbers-only harness, but no release contract for technical-grounding regressions. Add a separate opt-in capability before `add-language-and-abstention-evaluation`; that change owns expanded language and abstention evaluation.

## Scope

### In Scope
- A dependency-free policy with stable codes: `language_routing` and `sensitive_block` require `100%` and regressions `escalate`; `outcome_classification` (`9/34`), `citation_exact_match` (`10/34`), and `contradiction_detection` (`0/4`) are current reviewed floors and failures `block`.
- Whole-answer checks for critical contradiction, sensitive, prompt-override, out-of-scope, and injected provider-failure scenarios; checks assert kernel outputs and do not reimplement kernel behavior.
- An opt-in runner/CLI and `make eval-quality-gate`, allowlisted reports in `evaluation-runs/gate/current` and `previous`, atomic promotion, non-zero `block`/`escalate`, and Strict TDD for policy, runner, and focused tests.

### Out of Scope
- Harness/dataset/kernel/corpus/provider changes, new metrics/cases, or floor tightening (future reviewed change).
- `make ci`/`ci-pr2a` changes, corporate/live-provider paths, extra persistence, or excluded dependencies.
- RDD/4R, roadmap completion, and archive before verification.

## Capabilities

### New Capabilities
- `technical-grounding-safety-gates`: Thresholds, contracts, safe reports, and evidence.

### Modified Capabilities
- None. `quality-evaluation-harness` remains numbers-only and unchanged.

## Approach

Add `backend/features/evaluation/gates/` for policy, runner, and safe reports. Reuse harness runner and `compute_metrics`; compare signals and critical outputs without reimplementation. `escalate` exits non-zero and records its safe code in the allowlisted report, with no separate record. Preserve the synthetic boundary, safe logging, replaceable providers, whole-answer blocking, and zero dependencies. Later phases archive the spec only after verification; the roadmap remains untouched.

**Initial delivery-size warning:** policy, runner, report, wiring, tests, and baseline evidence may approach or exceed 400 authored lines. Tasks must forecast work units; this proposal does not decide PR splitting.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/features/evaluation/gates/`, `cli.py` | New/Modified | Gate implementation. |
| `Makefile`, `tests/` | Modified/New | Opt-in target and tests. |
| `evaluation-runs/gate/` | New | Atomic evidence. |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Floors are mistaken for quality targets. | Med | Label them temporary; tighten only through review. |
| Rules drift or exceed capacity. | Med/High | Assert outputs only; forecast work units. |

## Rollback Plan

Remove gate modules, command, tests, and evidence; leave harness, dataset, kernel, baselines, roadmap, and canonical specs unchanged.

## Dependencies

- Kernel, harness, dataset, `ReportAdapter`, and `Clock`. No new dependency; RDD remains disabled under issue #1892.

## Success Criteria

- [ ] The gate fails closed with stable safe codes; baseline floors are explicitly temporary, not strong-quality targets.
- [ ] Language/sensitive regressions escalate at `100%`; `block`/`escalate` exit non-zero and remain allowlisted.
- [ ] Evidence promotes atomically; `make ci` and `ci-pr2a` are unchanged; focused Strict TDD tests pass without boundary violations.
