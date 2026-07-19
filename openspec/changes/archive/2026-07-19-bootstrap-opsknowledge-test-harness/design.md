# Design: Bootstrap OpsKnowledge Test Harness

## Technical Approach

Preserve PR1/PR2A's locked Python/`uv` and fail-fast `make ci`. PR2B is a bytes-and-AST-only strict structural whitelist.

## Architecture Decisions

| Decision | Alternatives / trade-off | Choice and rationale |
|---|---|---|
| Strict whitelist | Detection leaves bypass space | Only repository-evidenced direct pytest shapes pass; other executable pytest/unittest use fails. |
| Scope | `tests/` misses source; environments scan vendor code | First-party `*.py`; only `.git/`, `.venv/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, `.pyright/`, `.cache/` excluded; unknown paths included. |
| Excluded entries | Inspecting skipped content breaks the boundary | Count before `lstat`; error/symlink fails; verified exclusions are never read/enumerated. |
| Bounded scan | Unbounded traversal risks CI exhaustion | Iterative lexical worklist; stop above 100,000 encountered entries, 10,000 Python files, 1 MiB/file, or 64 MiB total bytes. |
| CI boundary | A guard after Pytest is bypassable | Keep PR2A stages/version gate, but compose `make ci` as sync → scanner → Ruff/Pyright → Pytest → failing PR3 audit boundary. |

## Data Flow

```text
make ci → exact uv gate → frozen sync → iterative walk → entry/file/byte limits → AST classifier
                                                                  ├─ diagnostics → non-zero
                                                                  └─ clean → quality stages → PR3 boundary
```

## File Changes

| File | Action | Description |
|---|---|---|
| `scripts/ci/check_focused_tests.py` | Replace | Default-deny structural validator; discard detector/resolver. |
| `tests/architecture/test_focused_test_scanner.py` | Replace | Wholesale equivalence-class suite; detector-era file is superseded evidence. |
| `Makefile` | Modify | Pass worktree root and run guard before Pytest; retain PR3 stub. |
| `openspec/changes/.../design.md` | Modify | This corrected superseding design. |

## Interfaces / Contracts

```python
Diagnostic = tuple[str, int, str, str]
# safe_relative_path, line_or_0, reason_code, remediation
```

The validator visits every finite executable API root globally: pytest/unittest `Import`, import `Call`, `Name`, `Attribute`, `Call`, decorator, annotation, and assignment roots. Only pytest/unittest imports are restricted: canonical `import pytest` passes; pytest `from`/star/alias/dynamic imports and every unittest import/use are `unsupported-test-api`. Owned allowed shapes are `pytest.fixture(scope="session")`, direct `pytest.mark.parametrize`, direct `pytestmark = pytest.mark.ci_recipe` or singleton tuple, and `pytest.MonkeyPatch` annotation. Other executable pytest use is unsupported.

No symbol table/value flow exists. Alias/chained assignment, `getattr`, dunder, subscript, computed/wrapped receiver, and dynamic import reject structurally. Strings/docs and non-pytest `.only`/`.focus` pass. Noncanonical pytestmark assignment/mutation is `pytestmark-mutation`.

`parametrize` owns its direct decorator. Position 0 is string/tuple-of-strings; values and `ids` recursively permit string/number/bool/`None` constants, list/tuple, or any direct `Name` (never resolved/executed/scope-checked). Lambda, call, f-string, comprehension, conditional, attribute, subscript, starred, wrapper, unknown, or other keyword fails once at its first invalid node: `unsupported-parametrize-argument` / “use literal containers or a direct Name”. Validated descendants are handled.

Dynamic-import ownership applies to complete direct calls `__import__`, `importlib.import_module`, or `importlib.__import__` whose positional or `name=` target is exact literal `"pytest"` or `"unittest"`. Syntactic `import importlib as ...` and `from importlib import import_module` forms reject at their import root without alias/value resolution. It reports `unsupported-dynamic-import` / “remove the dynamic import or use canonical import pytest”; children are handled. Other calls and standalone strings/docs are not dynamic-import findings.

Validators claim approved/rejected roots in `handled`; descendants are not reclassified. Unowned executable pytest/unittest references fail. Deduplicate `(path,line,reason,remediation)`; map `unsupported-test-api` and `pytestmark-mutation` to their direct rewrites.

Root is uncounted. One global encounter counter spans the scan invocation. Incrementally consume `scandir`, count before classification, and collect only bounded entries; candidate 100001 stops before metadata. Sort each collected directory batch; process exclusions before descent/Python accounting and push children reverse-lexically. Every entry counts. In-scope Python then checks 10,000 files, 1 MiB, 64 MiB before read/parse. Limits stop; other observable errors fail closed.

Paths are safely relative (else traversal error); AST lines fall back to `0`. Deduplicate all fields and sort path, line, reason, remediation. Remediation is rewrite direct, remove the construct/mutation, or propose a new SDD grammar.

## Testing Strategy

| Layer | Test | Approach |
|---|---|---|
| Whitelist | Each allowed import/decorator/annotation/pytestmark shape | New equivalence-class suite uses only literals/direct Names in its own parametrization. |
| Parametrize | Recursive literals/any direct `Name`/`ids`, plus rejected expressions | Depth-first fixtures assert one stable diagnostic and no Name lookup; no BinOp/lambda/subscript decorator arguments. |
| Dynamic/rejection | Alias/star/from/unittest; direct dynamic import forms and literal import targets | Assert `unsupported-dynamic-import` ownership; ordinary strings pass. |
| Evidence | Repository fixtures/tests | Negative source remains ordinary string fixture content; final root scan proves the replacement suite and all first-party files pass. |
| Filesystem | Excluded entry/subtree and all limits | Mock `lstat`/`scandir`; root uncounted, exclusions count, #100001 pre-classification. |
| Isolation/meta | No runtime execution; no silent grammar broadening | Hostile `conftest.py`; mutation tests remove a category check and must fail. |
| Recipe | Scanner precedes Pytest | Sentinel recipe test; retain PR1/PR2A version tests. |

## Migration / Rollout

Migration is not executed. Preserve/hash revised exploration, proposal, spec, design; regenerate tasks/apply-progress; then restore blocked PR2B files from `f505c81`. Before invoking the new validator on the repository tree, replace `tests/architecture/test_focused_test_scanner.py` wholesale, then migrate local-UV lambdas and `_FAILURE_PREFIXES[...]` decorator values to direct helpers/constants. The old suite is never a future-validator acceptance input; after replacement, rebuild validator/tests and require the full included tree to pass. Keep revised artifacts/tasks; no blanket reset.

Stale staged implementation and apply-progress statements are current-state evidence, not conformance claims. Apply cleans the stale apply-progress claims while implementing regenerated tasks. Engram #3588 grants a size exception only to PR2B; PR2A, PR3, and PR4 have no size exception.

## Open Questions

- [ ] None.
