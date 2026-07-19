# Exploration: PR2B focused-test prohibition contract redesign

## Current State

PR2B is staged, uncommitted, and intentionally preserved as review evidence: 692 changed lines against `f505c81` (scanner, architecture tests, Makefile/apply-progress/tasks updates). The current scanner uses lexical import/assignment alias resolution, static and selected dynamic `getattr`, recursive `pytestmark` containers, generic `.only`/`.focus` matching, and `lstat`/`scandir` traversal. Repeated fresh reviews still found bypass classes: aliases of `getattr`, `pytestmark.append`/`+=`, starred and open-ended expressions, local/annotated alias edge cases, and filesystem TOCTOU between pathname checks and reads/descent. The current design therefore claims a bounded model but remains too close to semantic reconstruction of Python.

The contract needs to be closed by syntax, not by an expanding list of aliases. The guard is a collection-independent source policy: it must parse files without importing or executing them, report prohibited constructs and scanner errors, and fail closed on syntax or filesystem uncertainty. It is not a sound semantic theorem for arbitrary Python.

## Affected Areas

- `scripts/ci/check_focused_tests.py` — replace the current resolver-heavy policy with a conservative syntactic recognizer and an explicitly bounded filesystem contract.
- `tests/architecture/test_focused_test_scanner.py` — reduce broad semantic examples and add contract-level acceptance scenarios for allowed syntax, rejected dynamic syntax, diagnostics, collection independence, and traversal limitations.
- `Makefile` — retain ordering/fail-fast wiring; only adjust the scanner invocation if the revised contract changes its interface.
- `openspec/changes/bootstrap-opsknowledge-test-harness/{design.md,specs,tasks.md,apply-progress.md}` — must be revised in the next SDD phases, not in this exploration, to remove semantic-completeness claims and align acceptance criteria.
- `f505c81` — recommended rebuild baseline; the staged PR2B implementation should not be incrementally patched further.

## Approaches

1. **Conservative closed AST policy (recommended)** — permit only explicitly safe node shapes and reject suspicious/dynamic forms. Recognize direct canonical spellings only (for example `pytest.mark.skip`, `unittest.skip`, bare prohibited names, and direct call/decorator targets), while rejecting alias-dependent targets, all `getattr` in policy-sensitive positions, assignment-derived marker aliases, mutation (`append`, augmented assignment), starred/unbounded containers, calls used as marker values unless directly recognized, and unresolved/dynamic expressions. Unknown syntax is an error, not an allow.
   - Pros: finite grammar; auditable and testable; no claim to resolve arbitrary Python; materially reduces bypass surface and implementation size.
   - Cons: false positives for harmless indirection; developers must rewrite to direct syntax or add a reviewed future contract change.
   - Effort: Medium.

2. **Continue bounded alias/value resolution** — expand the resolver for every newly discovered alias, mutation, scope, and expression form.
   - Pros: fewer false positives for ordinary Python.
   - Cons: open-ended semantic emulation, recurring bypasses, larger review surface, and no honest completeness boundary.
   - Effort: High; reject.

3. **Runtime collection/import inspection** — ask pytest what it would collect and inspect runtime markers.
   - Pros: closer to runtime semantics for supported plugins.
   - Cons: violates collection independence, executes project code/plugins, is environment-dependent, and can be skipped or altered by configuration.
   - Effort: Medium; reject.

## Recommendation

Adopt Approach 1 and define the prohibition as a **closed source grammar**:

- Safe means a node is in the small documented allow-set. Canonical direct forms are checked without resolving imports or assignments. Any alias, `getattr` (static or dynamic), computed attribute, call/decorator wrapper not explicitly recognized, mutation, starred element, unpacking, subscript, comprehension, conditional, lambda, or unknown expression in a marker-sensitive position is rejected with a stable diagnostic such as `unsupported-dynamic-focused-test-syntax`.
- Eliminate import/assignment alias resolution from the contract. If a future need justifies aliases, it must be a new SDD change with a separately bounded grammar; it is not part of PR2B.
- `pytestmark` is accepted only as a direct canonical marker or a flat, explicitly bounded list/tuple of direct canonical markers (no starred elements, nested/open-ended values, calls, mutation, or computed values). Mutation statements targeting `pytestmark` are always prohibited or unsupported-error, never silently ignored.
- `.only`/`.focus` are recognized only in the direct syntactic forms the contract names; do not infer arbitrary attribute provenance. Suspicious use in a call/decorator target is rejected, while unrelated attribute reads remain outside the focused-test policy if the contract explicitly says so.
- Collection independence means: parsing and scanning use only bytes and filesystem metadata; no imports, pytest collection, plugin loading, configuration execution, or test execution. It guarantees independence from Python runtime semantics, not semantic completeness: unsupported constructs are rejected rather than classified as safe.

Filesystem contract should be honest and portable: scan only a requested directory; reject a symlink root, symlink entry, non-directory root, stat/enumeration/read/parse error; sort entries and stay root-confined by lexical path checks. This guarantees fail-closed behavior for symlinks observed during the scan, not immunity to a concurrent attacker replacing pathnames after checks. Descriptor-anchored `openat`/`O_NOFOLLOW` traversal could strengthen race resistance but is platform-specific and materially larger; it should not be claimed for this Python/macOS/Linux repository CI contract unless separately designed and tested. The contract should state a non-adversarial stable-tree assumption (or explicitly require exclusive workspace access during CI).

Diagnostics must include path, source line where available, stable reason/code, and remediation: rewrite to a direct canonical form, remove the focused marker/mutation, or propose a new SDD contract for required indirection. Avoid claiming exact semantic detection for rejected code.

Minimal acceptance scenarios:

1. Direct prohibited decorator, call, bare marker, and direct `pytestmark` fail.
2. Direct allowed marker (`ci_recipe`) and unrelated attribute/dynamic expression outside a marker-sensitive position pass.
3. Alias, any `getattr`, mutation, starred/container-computed marker, decorator/call wrapper, and unknown marker-sensitive expression fail with the stable unsupported diagnostic.
4. Syntax, read, stat, enumeration, root, and symlink errors fail non-zero without reading outside the root.
5. A hostile `conftest.py` or plugin is never imported; scanner output is unchanged by pytest collection/configuration.
6. Multiple files produce deterministic path/line/reason ordering and deduplicated findings.

Given the repeated bypasses and the current TOCTOU claim, discard the staged PR2B implementation as an implementation attempt and rebuild from `f505c81` after proposal/spec/design/tasks are revised. Preserve the staged diff untouched until that evidence is captured; do not patch it in place. **Superseded audit history:** this exploration recorded the former 800-line PR2B exception; Engram #3588 now grants the current PR2B-only size exception, while PR3/PR4 remain unexcepted.

## Risks

- Conservative rejection will produce false positives for alias-heavy but valid tests; this is an intentional safety tradeoff and requires actionable remediation.
- Pathname traversal cannot honestly guarantee race-free reads; overstating it would recreate the current security defect.
- A direct-spelling policy may miss prohibited behavior hidden behind arbitrary Python, but the contract remains safe because unknown/dynamic marker-sensitive syntax fails closed.
- Changing the contract requires synchronized proposal/spec/design/tasks/apply-progress updates before implementation; changing only tests would preserve contradictory documentation.

## Ready for Proposal

Yes. The next phase should revise the proposal and then spec/design/tasks around the closed grammar, explicit non-goals, stable diagnostics, and filesystem race assumption. After approval, rebuild PR2B from `f505c81`; do not amend the current staged implementation or treat its 692-line size as evidence that the semantic resolver is complete.
