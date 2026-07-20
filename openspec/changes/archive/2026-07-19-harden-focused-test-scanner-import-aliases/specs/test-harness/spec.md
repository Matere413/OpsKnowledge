# Delta for test-harness

## ADDED Requirements

### Requirement: Bounded Dynamic-Import Alias Grammar

The focused-test scanner MUST extend its existing structural whitelist with a finite, closed grammar for direct aliases of recognized dynamic-import callables. It MUST recognize direct `importlib` module aliases and direct callable aliases, including equivalent simple or annotated assignments and syntactically unambiguous name-to-name chains. Calls through a tracked callable alias with a literal target `"pytest"` or `"unittest"` MUST produce the existing `unsupported-dynamic-import` reason and remediation. The scanner MUST NOT infer general Python data flow.

#### Scenario: Direct callable and module aliases are rejected

- GIVEN `loader = importlib.import_module` or `import importlib as imports; loader = imports.import_module`
- WHEN `loader("pytest")` or `loader(name="unittest")` is scanned
- THEN the scanner returns `unsupported-dynamic-import` with the existing actionable diagnostic

#### Scenario: Supported alias forms are equivalent

- GIVEN a direct, annotated, or syntactically unambiguous name-to-name alias of a recognized callable
- WHEN it dynamically imports a literal `pytest` or `unittest` target
- THEN it is rejected identically to the canonical callable spelling

#### Scenario: Closed grammar does not resolve arbitrary expressions

- GIVEN a container alias, dynamic attribute, `getattr`, subscript, computed expression, wrapper, closure, or interprocedural call
- WHEN the scanner encounters the form
- THEN it MUST NOT claim semantic resolution; unsupported or ambiguous syntax remains fail-closed under the existing scanner policy

### Requirement: Definite Rebinding and Conditional Ambiguity

Tracked aliases MUST be invalidated after an unconditional, unambiguous reassignment that establishes a different value. If recognized conditional control flow leaves a tracked name potentially bound to multiple origins, the scanner MUST fail closed with a stable diagnostic rather than silently dropping tracking. Assignment handling MUST preserve existing finding ownership so one source construct does not create duplicate findings.

#### Scenario: Definite reassignment removes tracking

- GIVEN `loader = importlib.import_module` followed by unconditional `loader = safe_loader`
- WHEN `loader("pytest")` is scanned
- THEN the former alias MUST NOT cause a dynamic-import finding

#### Scenario: Conditional reassignment fails closed

- GIVEN a recognized conditional form may leave `loader` bound to either the tracked callable or another value
- WHEN a sensitive literal call through `loader` is scanned
- THEN the scanner MUST return a stable fail-closed ambiguity diagnostic

### Requirement: Isolated Alias Environments and Stable Findings

Alias state MUST be isolated per module, function, class, and lambda lexical environment; aliases MUST NOT cross those boundaries or become closure resolution. Findings MUST retain safe repository-relative paths, available line numbers, stable reasons and remediation, deterministic ordering, and deduplication. Existing traversal, resource limits, parse/error fail-closed behavior, collection independence, and zero/non-zero exit contracts MUST remain unchanged.

#### Scenario: Lexical environments do not inherit aliases

- GIVEN a module, function, class, or lambda defines an alias in another lexical environment
- WHEN the inner environment calls the same name
- THEN the call is not resolved using the outer alias

#### Scenario: Repeated findings are deterministic

- GIVEN a stable tree containing repeated and distinct alias violations
- WHEN the scan runs twice
- THEN both results are sorted, deduplicated, line-aware when available, and byte-for-byte equivalent

## REMOVED Requirements

None. Existing scanner safety, resource, determinism, and collection-independent contracts remain in force.

## RENAMED Requirements

None.

### Explicit Non-Goals

This change MUST NOT add container aliases, dynamic attributes, closures, interprocedural analysis, general data-flow resolution, workflow/configuration changes, GitHub Actions runtime pins, application Phase 1 work, or dependencies.
