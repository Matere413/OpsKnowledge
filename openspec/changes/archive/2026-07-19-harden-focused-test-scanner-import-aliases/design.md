# Design: Harden Focused-Test Scanner Import Aliases

## Technical Approach

Extend `_Policy` in `scripts/ci/check_focused_tests.py` with a bounded, AST-local alias environment. It recognizes only direct `importlib` module aliases, direct dynamic-import callable aliases, annotated equivalents, and unambiguous `Name`-to-`Name` chains required by the delta spec. Existing canonical-call detection, `claim()` ownership, set-based findings, and tree traversal remain authoritative.

## Architecture Decisions

| Decision | Choice | Alternatives / rationale |
|---|---|---|
| Alias representation | Stack of isolated environments: `Name -> module/callable/ambiguous` classification. | Python runtime evaluation or symbol-table resolution is rejected: this guard must remain syntactic, bounded, and dependency-free. |
| Statement semantics | Scan each assignment RHS in the current environment, then classify/invalidate direct `Name` targets. | Pre-updating state is rejected because it violates Python statement order; general data-flow is out of scope. |
| Ambiguity | Merge the two branches of a recognized `if`; divergent classifications become `ambiguous`. A sensitive literal call through that name emits `ambiguous-dynamic-import-alias` with fixed remediation. | Silently dropping state is fail-open; modelling loops, `try`, `match`, or arbitrary expressions is rejected as general flow analysis. |
| Scope | Push an empty environment for function, async-function, class, and lambda executable bodies; do not inherit aliases. | Closure/nonlocal/global resolution is rejected by the explicit non-goals. Definition-time decorators, annotations, defaults, bases, and keywords retain their enclosing traversal context. |

`module` denotes direct `importlib`; `callable` denotes `import_module`, `__import__`, or a direct alias of either. A direct `Name` assignment copies a known classification. Any other unconditional direct-name reassignment invalidates the prior classification. Existing `import importlib as alias` rejection remains unchanged, while its alias is recorded so later direct chains are understood.

## Data Flow

```text
AST statements (source order)
  -> current lexical environment
  -> assignment classification / definite invalidation
  -> call resolver
  -> claim() -> set[Diagnostic] -> sorted scan_file()/scan_tree() result

if statement -> clone pre-state -> visit body / else -> equal merge or ambiguous name
scope boundary -> fresh environment -> body -> discard environment
```

Only a resolved callable plus literal positional target or `name=` target of `pytest`/`unittest` emits the existing `unsupported-dynamic-import` diagnostic and remediation. An ambiguous tracked name at the same sensitive-call shape emits the new stable ambiguity diagnostic. `claim()` marks the owned construct before child traversal; the diagnostic set and existing final sorting deduplicate and order results deterministically with repository-relative paths and line numbers.

## File Changes

| File | Action | Description |
|---|---|---|
| `scripts/ci/check_focused_tests.py` | Modify | Add environment stack, ordered assignment/conditional/scope visitors, and bounded call resolution. |
| `tests/architecture/test_focused_test_scanner.py` | Modify | Add RED equivalence, invalidation, scope, ambiguity, ordering, and determinism cases. |
| `openspec/changes/harden-focused-test-scanner-import-aliases/design.md` | Create | This design artifact. |

**Implementation blast radius:** two Python files; no CI workflow, dependencies, runtime code, or Actions pin changes. **Forecast:** approximately 120–200 implementation-code changed lines (including tests), below the 400-line review budget. OpenSpec artifacts are excluded from that estimate (this design: approximately 670 words).

## Interfaces / Contracts

```python
AliasKind = Literal["importlib-module", "dynamic-import-callable", "ambiguous"]
Environment = dict[str, AliasKind]
```

This is private `_Policy` state, not a public API. It preserves the existing `Diagnostic = tuple[str, int, str, str]` contract. New reason/remediation strings are constants and asserted exactly by tests.

## Testing Strategy

| Layer | What to Test | Approach |
|---|---|---|
| Unit (RED first) | Direct, annotated, module, and name-chain aliases; positional and `name=` literals | Extend `_scan` parameterized cases; assert full tuples and existing reason/remediation. |
| Unit (RED first) | RHS-before-target order, unconditional reassignment, and `if` branch ambiguity | Assert invalidated aliases do not report; ambiguous sensitive calls report one fixed tuple. |
| Unit (RED first) | Function/async/class/lambda isolation; repeated findings | Assert no outer resolution, sorted/deduplicated byte-identical scans. |
| Regression | Traversal limits, parse/decode failures, exclusions, exit behavior | Retain existing scanner tests and run `uv run --frozen pytest`, then canonical `make ci`. |

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file classification, or process-integration boundary changes. Existing filesystem traversal/resource behavior is preserved, not redesigned.

## Migration / Rollout

No migration required. Roll back by reverting the scanner and its tests together. Containers, dynamic attributes, `getattr`, subscripts, closures, interprocedural/general data-flow analysis, workflow/configuration work, dependencies, and GitHub Actions pin refresh remain out of scope.

## Open Questions

None.
