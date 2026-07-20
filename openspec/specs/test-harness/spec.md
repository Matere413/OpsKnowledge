# Delta for test-harness

## ADDED Requirements

### Requirement: Locked Python Development Environment

`pyproject.toml` MUST require `>=3.12,<3.13`, have empty dependencies, and use a locked `dev` extra; `.python-version` MUST pin `3.12`. Before frozen sync or any quality gate, local `make ci` MUST execute `uv self version --short` and accept only its complete output exactly equal to `0.11.29`; it MUST then use frozen sync and `uv run --frozen`. `uv -V` and `uv --version` MUST NOT validate the executable because this binary includes build metadata in both; `uv version --short` MUST NOT validate it because it reports the project-package version. On a local version mismatch, it MUST exit non-zero without running a gate and print exactly this two-line template, replacing `<actual>` with the captured output (or `unavailable`):

```text
ERROR: uv version mismatch; expected 0.11.29, found <actual>.
Remediation: install uv 0.11.29 and rerun make ci.
```

#### Scenario: Locked tool execution

- GIVEN committed lockfile
- WHEN `make ci` runs
- THEN tools use uv-managed environment
- AND stale/incompatible locks exit non-zero

#### Scenario: Exact executable version succeeds

- GIVEN `uv self version --short` produces exactly `0.11.29`
- WHEN `make ci` runs
- THEN the executable-version gate succeeds
- AND frozen sync is eligible to run

#### Scenario: Invalid executable-version output fails before the gate

- GIVEN `uv self version --short` is mismatched, suffixed, multiline, malformed, unavailable, or errors
- WHEN `make ci` runs
- THEN it emits the prescribed mismatch template with the captured value
- AND it exits non-zero before frozen sync or any quality stage

### Requirement: Deterministic CI Runner Bootstrap

After checkout, use `astral-sh/setup-uv@d4b2f3b6ecc6e67c4457f6d3e41ec42d3d0fcb86 # v5.4.2` with `version: "0.11.29"`, then assert `uv self version --short` is exactly `0.11.29` before `make ci`. GitHub Actions and local `make ci` MUST enforce the same executable-version equality; the workflow assertion is a prerequisite and `make ci` repeats the local gate. Apply MUST re-verify the SHA or block.

#### Scenario: Clean runner has the selected uv

- GIVEN a clean runner
- WHEN the workflow runs after checkout
- THEN setup installs `0.11.29` and assertion precedes `make ci`
- AND a version mismatch exits non-zero without invoking `make ci`

### Requirement: Ordered, Fail-Closed Quality Gate

`make ci` MUST execute frozen sync, focused guard, Ruff check/format, Pyright, Pytest, audit, then license inventory, stopping at first failure. Findings/tool-service errors MUST fail closed; no retry/suppression/allowlist MAY conceal them. The wrapper MUST preserve output, classify cause, recover only by unchanged re-run.

#### Scenario: Isolated fail-fast proof

- GIVEN recording sentinels in a copied recipe
- WHEN an earlier stage fails
- THEN the log ends there and no later sentinel runs

#### Scenario: Deterministic audit wrapper outcomes

- GIVEN stubs for success, finding, timeout, unavailable service, tool failure
- WHEN the wrapper is tested for each result
- THEN classifications are `success`, `vulnerability_finding`, `vulnerability_service_unavailable`, or `vulnerability_tool_failure`
- AND non-success exits non-zero after one call; rerun proves recovery

### Requirement: Collection-Independent Focused-Test Prohibition

Before Pytest, `make ci` MUST run a standalone source-policy scan over first-party `*.py` files beneath the repository root. The fixed, version-controlled exclusion set is `.git/`, `.venv/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, `.pyright/`, and `.cache/`; these are control, environment, or tool-cache paths, including generated dependencies under `.venv/`. No `vendor/` or generated-source directory currently exists in this repository; adding one requires a separately reviewed, version-controlled exclusion-set change. Unknown paths, including arbitrary `vendor/`, `generated/`, or test directories, remain in scope. For every encountered entry, the scanner MUST obtain enough metadata to classify its path against the fixed set, then MUST NOT enumerate or read an excluded subtree. It MUST fail closed for an observable lstat/stat/classification error on that encountered excluded entry; it makes no claim about errors inside content it deliberately does not traverse. The scanner MUST enumerate only that root and MUST NOT import project modules, collect with Pytest, load plugins or configuration, or execute tests. Symlinks and errors in either scope or excluded paths MUST fail closed; exclusions MUST NOT be caller-selectable or used to hide first-party tests.

The policy is a strict structural whitelist, not a Python-semantics interpreter. It evaluates every executable structural pytest/unittest API use in included first-party Python. An executable structural use is only an AST import or import call, or a `Name`, `Attribute`, `Call`, decorator, annotation, or assignment root whose direct syntax references canonical `pytest` or `unittest` API spellings; ordinary strings, docstrings, comments, and unrelated normal imports are not API uses. For pytest/unittest imports specifically, the only permitted import is `import pytest` with no alias; `from pytest import ...`, star/aliased imports, every `unittest` import, and dynamic imports are rejected. The only permitted direct forms are: `pytest.fixture` as a decorator with the repository's literal `scope="session"`; `pytest.mark.parametrize` as a decorator with the exact argument grammar below; `pytest.mark.ci_recipe` as the direct `pytestmark` value (or the direct flat singleton tuple used by current scanner fixtures); and `pytest.MonkeyPatch` only as a direct annotation reference. No runtime pytest API is permitted: `pytest.skip`, `pytest.xfail`, and `pytest.skipif` are all rejected, as are all unittest APIs. `pytest.raises` is not in the current repository evidence and is therefore rejected unless a future spec amendment adds it. Unknown marks, decorators, assertion helpers, fixtures, receivers, and pytest/unittest references fail closed. The whitelist MUST reject aliases, assignments of pytest objects, chained aliases, aliases of `getattr`, `getattr`, `__dict__`/dunder access, subscripts, computed receivers, wrappers, dynamic import strings, focus/only/skip/skipif/xfail forms, unknown marks, and unresolved or mutation-shaped expressions. No semantic alias/value resolution is allowed. Recognized dynamic import calls MUST use the stable reason `unsupported-dynamic-import`: this includes a direct call to `__import__`, a direct canonical `importlib.import_module` or `importlib.__import__` call, only when its import-target argument is the exact literal `"pytest"` or `"unittest"`. Ordinary standalone strings and documentation remain outside this rule.

For `pytest.mark.parametrize`, the only accepted shape is a direct decorator call whose receiver is exactly `pytest.mark`, whose attribute is exactly `parametrize`, and whose arguments are limited to: a string or tuple of strings for the parameter-name argument; flat or nested list/tuple literals containing only strings, numbers, booleans, `None`, and other such literal containers; any direct AST `Name` reference in value or `ids` positions, without checking its definition, scope, or value; and the keyword `ids` with one of those same literal values or a direct `Name`. Direct `Name` values are references only: the scanner MUST NOT resolve or execute them. Lambda expressions, calls, comprehensions, conditionals, f-strings, attribute/subscript/computed expressions, starred elements, wrappers, and any other expression are rejected with `unsupported-parametrize-argument`. Existing lambdas in `tests/ci/test_local_uv_version.py` MUST be replaced by named module-level helper references, and current `_FAILURE_PREFIXES[...]` decorator values MUST be replaced by direct named constants, as an implementation migration; the scanner does not validate those names.

The existing `tests/architecture/test_focused_test_scanner.py` is superseded detector evidence, not a future-whitelist compatibility requirement. It MUST be replaced wholesale by a suite derived from the whitelist's equivalence classes; the replacement suite MUST use grammar-compatible literals and direct `Name` references in its own parametrization and MUST NOT construct fixtures with `BinOp` or other rejected expressions inside parametrize arguments. During migration, the superseded file MAY fail the future whitelist; after replacement, the complete included first-party Python tree MUST pass the whitelist.

`pytestmark` MUST have no assignment or mutation in the accepted grammar beyond the direct `pytest.mark.ci_recipe` value and the explicitly accepted flat singleton tuple. Plain/annotated/augmented assignment, method mutation, subscript/slice assignment or deletion, and named-expression (`:=`) mutation MUST fail closed. The scanner MUST NOT claim to detect arbitrary behavior hidden behind Python semantics.

The scanner MUST use iterative directory traversal and MUST enforce reviewed resource limits of at most 1 MiB per in-scope Python file, 64 MiB total bytes read across the scan, 10,000 in-scope Python files, and exactly 100,000 encountered filesystem entries globally per one scan invocation. Directory enumeration MUST consume `scandir` incrementally, count and check each returned entry before metadata classification, and MUST NOT materialize an unbounded `sorted(os.scandir(...))`. For each directory, it MAY collect only the entries already obtained before the limit/error boundary, then sort that bounded collection deterministically before processing it; an enumeration error fails closed. The repository root itself is not an encountered entry. Each directory entry returned while traversing an included directory counts once, including directories, non-Python files, symlinks, and entries later identified as excluded. The counter MUST be checked before metadata classification of the candidate entry: entry 100,000 is allowed to proceed through classification and the applicable exclusion/symlink/file checks; candidate entry 100,001 MUST fail closed before further classification or traversal. Exclusion classification and subtree skipping occur after the encounter-limit check and before any descent or Python byte accounting. Exceeding any limit MUST stop the scan, return non-zero, and emit a stable resource-limit diagnostic with the safe path when available. These limits protect CI predictability for this repository and MUST NOT be described as general denial-of-service immunity.

The scan MUST fail closed for a non-directory or symlink root, any observed symlink entry, traversal/enumeration/stat/read/decode failure, and syntax/parse failure. It MUST assume a stable tree for the duration of the scan and MUST NOT claim protection against concurrent mutation or TOCTOU races.

Each finding MUST contain a safe repository-relative path, line when available, stable rejected-construct/reason code, and concrete remediation: rewrite to an allowed direct spelling, remove the focused construct, or propose a separately reviewed SDD grammar. Findings MUST be sorted deterministically and deduplicated. A false positive is an intentional safety tradeoff: developers MUST apply the direct-syntax remediation or seek a future contract change; the scanner MUST NOT silently broaden its grammar.

The guard MUST return zero only when the complete scan succeeds and produces no prohibited or ambiguous form, and non-zero for every finding or scan failure. The Makefile MUST invoke it before Pytest and preserve fail-fast ordering. PR2B advances `make ci` to the PR3 audit boundary; Engram #3588 grants a size exception only to PR2B; PR2A, PR3, and PR4 have no size exception. That delivery evidence is not a runtime behavior requirement.

#### Scenario: Skipped test cannot bypass the guard

- GIVEN any repository Python file uses a direct prohibited marker or an alias, indirection, `getattr`, mutation, computed/starred container, wrapper, or unknown marker-sensitive expression
- WHEN `make ci` runs
- THEN the guard fails before Pytest with the safe path, available line, stable reason, and direct-syntax remediation

#### Scenario: Allowed direct syntax passes

- GIVEN current repository tests use only direct `import pytest`, `pytest.fixture(scope="session")`, `pytest.mark.parametrize`, `pytest.mark.ci_recipe`, and `pytest.MonkeyPatch` annotation forms
- WHEN the complete scan runs
- THEN it exits zero and reports no finding

#### Scenario: Strict whitelist rejects unsupported test APIs

- GIVEN a first-party test uses an aliased/star import, any unittest import, `pytest.raises`, an unknown mark, a pytest-object assignment, or a computed/wrapped receiver
- WHEN the guard scans
- THEN it fails closed with `unsupported-test-api` and remediation to use an explicitly allowed direct form or propose a spec amendment

#### Scenario: Parametrize accepts direct Names without semantic checks

- GIVEN a direct `pytest.mark.parametrize` decorator uses string/tuple names, literal flat or nested containers, and any direct AST `Name` in value or `ids` positions
- WHEN the guard scans
- THEN it accepts the decorator without checking definition, scope, value, or executing the Names

#### Scenario: Parametrize rejects executable or computed arguments

- GIVEN a direct parametrize call contains a lambda, call, f-string, comprehension, conditional, attribute/subscript, starred element, wrapper, or unsupported expression
- WHEN the guard scans
- THEN it fails closed with `unsupported-parametrize-argument` and remediation to use literals or a direct approved Name

#### Scenario: Current lambda migration is explicit

- GIVEN `tests/ci/test_local_uv_version.py` still passes a lambda or `_FAILURE_PREFIXES[...]` subscript to a parametrize decorator
- WHEN the implementation is reviewed against this contract
- THEN it fails the migration requirement; direct named helper/constant references are required instead

#### Scenario: Superseded detector suite is replaced wholesale

- GIVEN `tests/architecture/test_focused_test_scanner.py` contains the prior detector-oriented parametrization or BinOp-built fixtures
- WHEN the whitelist migration is evaluated
- THEN that file is treated as superseded evidence and replaced wholesale by equivalence-class tests using grammar-compatible literals/direct Names

#### Scenario: Whitelist migration completes on the included tree

- GIVEN the superseded detector suite has been replaced and the local UV lambdas/subscripts have been migrated to named helpers/constants
- WHEN the complete included first-party tree is scanned
- THEN the whitelist passes with no unsupported-parametrize or other whitelist findings

#### Scenario: Dynamic imports fail only in executable sensitive forms

- GIVEN included first-party executable syntax calls `__import__`, canonical `importlib.import_module`/`importlib.__import__` with positional or `name=` exact literal target `"pytest"` or `"unittest"`, or uses syntactic `importlib` aliases/import-from `import_module`
- WHEN the guard scans
- THEN it fails with `unsupported-dynamic-import`, while ordinary standalone strings and unrelated dynamic import targets do not fail under this reason

#### Scenario: Runtime controls are never allowed

- GIVEN any included first-party executable function body contains direct or indirect `pytest.skip(...)`, `pytest.xfail(...)`, or `pytest.skipif(...)`
- WHEN the guard scans
- THEN it fails closed with `prohibited-runtime-control` or `unsupported-test-api`; no context-sensitive exception is made

#### Scenario: Ordinary strings are not test API references

- GIVEN production code, documentation, or a test fixture string contains the text `pytest.mark.skip` or `unittest.skip`
- WHEN the guard scans and the text is not an executable structural pytest/unittest API use
- THEN it reports no finding for that string alone

#### Scenario: First-party scope and fixed exclusions

- GIVEN a prohibited construct exists in first-party Python, while `.venv/`, `.git/`, a cache, or an unknown `vendor/` directory contains Python files
- WHEN the guard scans the repository root
- THEN it classifies each encountered entry, reports the first-party file, scans the unknown directory, and does not enumerate or read the fixed exclusions

#### Scenario: Excluded entry classification fails closed

- GIVEN lstat/stat/classification fails for an encountered fixed-exclusion entry
- WHEN the guard scans
- THEN it exits non-zero with a stable diagnostic; it does not claim to inspect failures inside a subtree it did not traverse

#### Scenario: Exclusions cannot hide tests

- GIVEN a caller requests an extra exclusion or places a first-party test under an unlisted directory
- WHEN the guard runs
- THEN the request is ignored or rejected, the test remains in scope, and observed symlink/error conditions fail non-zero

#### Scenario: Finite focus grammar avoids production false positives

- GIVEN direct `pytest.mark.only`, `pytest.only`, `unittest.skipIf`, or an alias/computed receiver in an executable structural decorator/call/assignment/annotation position, plus an unrelated production `obj.only()` call
- WHEN the guard scans
- THEN it rejects the listed direct or ambiguous structural API form and does not flag the unrelated production call

#### Scenario: Runtime control calls are rejected in all function bodies

- GIVEN a fixture/helper/async function body contains direct `pytest.skip(...)` or `pytest.xfail(...)`
- WHEN the guard scans
- THEN it fails non-zero with the runtime-control diagnostic; `pytest.skipif(...)` is not treated as a supported runtime form

#### Scenario: Pytestmark mutation categories fail closed

- GIVEN `pytestmark` is assigned, annotated, augmented, mutated by method call, subscript/slice-assigned, subscript/slice-deleted, or targeted by a named expression
- WHEN the guard scans
- THEN it fails non-zero with one stable mutation/unsupported diagnostic and remediation

#### Scenario: Alias chains do not become semantic resolution

- GIVEN a prohibited marker/runtime call is reached through chained aliases, an alias of `getattr`, or a computed receiver
- WHEN the guard scans
- THEN it rejects the ambiguous syntax fail-closed without resolving values or executing code

#### Scenario: Resource limits are deterministic

- GIVEN an in-scope Python file is exactly 1 MiB and the scan remains within 64 MiB and 10,000 files
- WHEN the guard scans iteratively
- THEN traversal completes without recursion-depth failure

#### Scenario: Resource limit boundary fails closed

- GIVEN a file exceeds 1 MiB, total reads exceed 64 MiB, or the 10,000-file limit is exceeded
- WHEN the guard scans
- THEN it stops with a stable resource-limit diagnostic and exits non-zero

#### Scenario: Directory enumeration is incremental and bounded

- GIVEN deterministic `scandir` mocks yield entries incrementally and the global count reaches 100,000
- WHEN the guard enumerates a directory
- THEN it counts before classification, sorts only entries already collected for that directory, and rejects candidate 100,001 without unbounded materialization

#### Scenario: Encountered-entry limit boundary is deterministic

- GIVEN deterministic traversal mocks return 100,000 entries beneath included directories, followed by a candidate 100,001st entry
- WHEN the guard scans
- THEN entry 100,000 is classified normally, while the 100,001st entry fails before lstat/stat classification or traversal with a stable safe remediation

#### Scenario: Excluded entries consume the encounter budget

- GIVEN deterministic traversal returns excluded and included entries in a stable order
- WHEN the guard scans
- THEN each returned entry consumes one encounter, exclusion is checked only after that accounting, and excluded subtrees consume no further entries because they are not traversed

#### Scenario: Collection independence

- GIVEN `conftest.py`, a plugin, or configuration would raise if imported or executed
- WHEN the guard scans the root
- THEN its result depends only on filesystem bytes/metadata and AST parsing, without importing, collection, configuration, or test execution

#### Scenario: Filesystem and parse uncertainty fails closed

- GIVEN the root is invalid or an observed symlink, traversal/stat/read/decode/parse fails, or the tree changes concurrently
- WHEN the guard runs
- THEN an observed error produces a non-zero result and stable diagnostic; the contract makes no TOCTOU guarantee for concurrent mutation

#### Scenario: Deterministic actionable diagnostics

- GIVEN multiple files contain repeated and distinct prohibited forms
- WHEN the guard runs twice over the same stable tree
- THEN findings are identical, repository-relative, line-aware when possible, sorted, and deduplicated

### Requirement: Production and Test-Tree Dependency Boundaries

Checks MUST reconcile production dependencies with governance, not dev tools. Their reviewed map MUST inspect `langchain` → `langchain`, `llamaindex` → `llama_index`, `redis` → `redis`, `kubernetes` → `kubernetes`; `streaming`, `visualinterpretation`, `email`, `notifier`, `reranking`, `queues`, `microservices` MUST be non-importable declaration exclusions. Map gaps/unresolved aliases MUST fail visibly. Imports MUST name path/dependency; governance unmodified.

#### Scenario: Normalized excluded test import fails

- GIVEN a test imports `llama_index` directly or through a tracked alias
- WHEN architecture checks run
- THEN it names test file and canonical `llamaindex`

#### Scenario: Map or alias cannot bypass review

- GIVEN an excluded policy entry lacks a reviewed map classification or an excluded alias cannot resolve
- WHEN architecture checks initialize or scan
- THEN they fail non-zero, naming it for review

### Requirement: Least-Privilege GitHub Actions Delegation

The workflow MUST use only unprivileged `push`/`pull_request`, read-only `contents`, credential-free checkout; never `pull_request_target`, secrets, or write tokens. Third-party actions MUST use immutable SHA/version comments; no SHA may be invented.

#### Scenario: Workflow boundary review

- GIVEN the workflow is inspected
- WHEN its events, permissions, checkout, and references are evaluated
- THEN it has the required read-only boundary and verified SHA/version comments

### Requirement: License Inventory Is Evidence, Not Compatibility Approval

The gate MUST run `uv run --frozen pip-licenses --from=expression --format=json`, retain output, and make no policy claim.

#### Scenario: Inventory remains non-policy

- GIVEN the license stage succeeds
- WHEN its configuration is reviewed
- THEN it has no compatibility suppression or fabricated approval

### Requirement: Bootstrap Scope and Strict TDD

The harness MUST pass without application source and MUST NOT add runtime, production, or excluded dependencies. Strict TDD stays `false` until a runtime change re-evaluates it.

#### Scenario: Empty source tree passes

- GIVEN no application source exists
- WHEN `make ci` runs
- THEN it exits zero when all checks pass and Strict TDD remains disabled

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
