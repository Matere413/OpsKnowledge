## Exploration: harden-focused-test-scanner-import-aliases

### Current State
The focused-test scanner in `scripts/ci/check_focused_tests.py` parses Python source with `ast` and fails closed for prohibited pytest/unittest usage and selected dynamic imports. `_Policy._dynamic_import()` recognizes only the canonical dotted spellings `__import__`, `importlib.import_module`, and `importlib.__import__`. Direct imports, `importlib` module aliases, and `from importlib import import_module` aliases are therefore detected when written in those supported shapes.

The exact gap is assignment aliasing of the callable attribute, for example `importlib; load = importlib.import_module; load('pytest')` (and equivalent annotated or chained direct assignments). The assignment is currently traversed generically, but no alias state is retained; the later call's spelling is just `load`, so the scanner emits no `unsupported-dynamic-import` diagnostic. This creates a fail-open path for dynamically importing prohibited test APIs. Existing focused scanner tests cover direct and import-statement aliases, but not assignment aliases.

### Affected Areas
- `scripts/ci/check_focused_tests.py` — `_Policy` owns the AST policy and dynamic-import recognition; it needs narrowly scoped alias state and assignment handling.
- `tests/architecture/test_focused_test_scanner.py` — equivalence-class tests are the established coverage surface for allowed/rejected source shapes and should add assignment-alias cases, including expected diagnostic line behavior.
- `openspec/config.yaml` — confirms the hybrid artifact convention, frozen pytest command, and bounded/reversible SDD rules; no configuration change is indicated.
- `RAG_ROADMAP.md` — establishes this as the immediate required pre-Phase-1 CI-hardening change, independent from the GitHub Actions runtime-pin change.

### Approaches
1. **Bounded callable-alias tracking** — track names assigned directly from recognized `importlib.import_module` (and, if retained by the existing policy, recognized `importlib.__import__`) expressions, including simple `Assign` and `AnnAssign` forms; treat calls through those names exactly like canonical dynamic imports.
   - Pros: closes the known gap with a small AST-local change; preserves current diagnostics and fail-closed intent; easy to test and independently revert.
   - Cons: requires explicit decisions about chained aliases, multiple targets, and reassignment; does not model arbitrary Python data flow.
   - Effort: Low

2. **General import/data-flow resolver** — build a broader symbol table for imports, assignments, attributes, scopes, and rebinding before classifying calls.
   - Pros: more complete coverage of alias and rebinding variants.
   - Cons: disproportionate complexity for a CI guard; introduces scope/order semantics and new false-positive/false-negative risks; harder to review and maintain before runtime code exists.
   - Effort: High

3. **Require canonical imports in source only** — add a textual or AST rule rejecting assignment aliases without teaching the scanner to recognize their later calls.
   - Pros: superficially simple.
   - Cons: changes the policy shape rather than reliably detecting prohibited behavior; risks rejecting harmless code while still leaving other dynamic-call paths unclear; does not directly satisfy the known detection gap.
   - Effort: Medium

### Recommendation
Use bounded callable-alias tracking in `_Policy`, limited to direct and annotated assignment expressions whose value is the recognized `importlib.import_module` attribute (plus any already-supported dynamic-import callable that the implementation intentionally preserves). Propagate simple name-to-name aliases only when they are syntactically unambiguous, and classify literal `pytest`/`unittest` targets through those names with the existing `unsupported-dynamic-import` diagnostic and remediation. Add focused equivalence tests for direct assignment, annotated assignment, chained aliasing if supported, unrelated assignments, and non-target module names. Do not introduce a general resolver, modify the policy message, or touch application/runtime code.

The bounded scope is independently reversible, directly addresses the roadmap blocker, and keeps implementation risk below the 400-line review budget. Verification should use the focused architecture test module first, then the canonical `make ci` gate as required by `AGENTS.md`.

### Risks
- Alias tracking can become unsound if reassignment, scope boundaries, or arbitrary expressions are treated as equivalent to direct aliases; the implementation should explicitly limit supported shapes and test unsupported shapes fail closed or remain outside the claimed contract.
- Adding aliases without marking assignment subtrees as handled could produce duplicate or differently-owned diagnostics; preserve the visitor's existing `handled`/`claim` ownership behavior.
- The scanner is itself loaded dynamically by tests, so changes must remain standard-library/AST-only and preserve Python 3.12 compatibility.
- The separate `refresh-github-actions-node-runtime-pins` change must remain out of scope; no workflow, manifest, roadmap, or runtime changes are needed for this scanner fix.

### Ready for Proposal
Yes. The gap, affected files, bounded approach, and acceptance-test direction are sufficiently clear for `sdd-propose`. Proposal scope should remain limited to focused-test scanner assignment aliases and their architecture tests; design/spec/tasks should decide the precise supported alias forms before implementation.
