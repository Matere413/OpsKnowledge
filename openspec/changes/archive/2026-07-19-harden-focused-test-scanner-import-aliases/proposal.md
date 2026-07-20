# Proposal: Harden Focused-Test Scanner Import Aliases

## Intent

Close a fail-open path in the focused-test guard: direct assignment aliases of dynamic-import callables can import `pytest` or `unittest` without producing a diagnostic. The primary outcome is preventing incomplete CI coverage; bounded false positives are mitigated by a closed grammar.

## Scope

### In Scope
- Recognize direct callable aliases such as `loader = importlib.import_module` and direct `importlib` module aliases.
- Invalidate tracked aliases after unconditional, unambiguous reassignment; reject recognized conditional ambiguity.
- Isolate module, function, class, and lambda alias environments; add focused equivalence-class tests.

### Out of Scope
- Container aliases, dynamic attributes, closures, interprocedural analysis, or general data-flow resolution.
- GitHub Actions runtime pins, application Phase 1 work, workflow/configuration changes, and new dependencies.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `test-harness`: extend the focused-test dynamic-import grammar to cover direct assignment aliases and specified alias ambiguity.

## Approach

Add AST-local alias state to `_Policy` in `scripts/ci/check_focused_tests.py`. Track only direct importlib module and callable assignment forms in each isolated lexical environment. Resolve calls through a tracked alias using the existing `unsupported-dynamic-import` diagnostic. Invalidate definite rebinding; fail closed only for ambiguity in the documented closed grammar. Do not infer unsupported Python semantics.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `scripts/ci/check_focused_tests.py` | Modified | Bounded alias tracking and ambiguity handling. |
| `tests/architecture/test_focused_test_scanner.py` | Modified | Alias, rebinding, scope, and ambiguity equivalence tests. |
| `openspec/specs/test-harness/spec.md` | Modified later | Delta requirement after this proposal. |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| False negatives from unsupported forms | Medium | Explicit closed grammar; fail closed for recognized ambiguity. |
| False positives from rebinding/scope | Low | Definite invalidation and isolated lexical environments. |
| Scope expansion | Low | Exclude general data-flow and keep independent change boundary. |

## Rollback Plan

Revert the scanner and focused-test-suite changes together, restoring prior canonical/import-statement detection without changing CI workflow or application code.

## Dependencies

- Existing `test-harness` specification and focused scanner test suite.

## Success Criteria

- [ ] Supported direct callable/module alias forms importing literal `pytest` or `unittest` fail with `unsupported-dynamic-import`.
- [ ] Definite reassignment removes alias tracking; specified conditional ambiguity fails closed.
- [ ] Aliases never cross module, function, class, or lambda boundaries.
- [ ] Focused tests and canonical `make ci` pass; implementation remains within the 400-line code review budget.
