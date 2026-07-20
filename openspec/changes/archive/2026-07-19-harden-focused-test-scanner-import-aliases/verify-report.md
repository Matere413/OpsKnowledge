```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:23c34cb905ccc4cbc77080e60fdc73b898fa1997debfbe8f7243f7fecf9ea56f
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 3/3
scenarios: 7/7
test_command: uv run --frozen pytest
test_exit_code: 0
test_output_hash: sha256:23c34cb905ccc4cbc77080e60fdc73b898fa1997debfbe8f7243f7fecf9ea56f
build_command: make ci
build_exit_code: 0
build_output_hash: sha256:744bfd31eb4a583a2ca7509be48b7746e95c00f3a25ccb204505e86b79af60f6
```

# Verification Report: Harden Focused-Test Scanner Import Aliases

**Change:** `harden-focused-test-scanner-import-aliases`  
**Mode:** Hybrid (OpenSpec + Engram), independent requirements/runtime verification; Strict TDD inactive.  
**Approved review binding:** `review-2a046689b3615fb3` / `sha256:3bd9c7ec4d826f06481b228edde3da4181cee20895bb4be20d40a19a921e26c2`  
**Verdict:** **PASS WITH WARNINGS**

## Completeness

| Dimension | Result | Evidence |
|---|---:|---|
| Proposal, spec, design, tasks | Present | All four artifacts reviewed. |
| Tasks | 9/9 | Every task checkbox is complete. |
| Requirements | 3/3 | Each requirement has implementation and passing runtime evidence. |
| Scenarios | 7/7 | Exact count from the delta spec; each heading is covered by the passing focused suite. |

## Runtime Evidence

| Command | Exit | Result | Output hash |
|---|---:|---|---|
| `uv run --frozen pytest tests/architecture/test_focused_test_scanner.py` | 0 | 65 passed in 3.68s | `sha256:3f6f0dc46f093aa14d3aadece38f8f6440517af590513cba75d314af89e5dda6` |
| `uv run --frozen pytest` | 0 | 132 passed in 19.72s | `sha256:23c34cb905ccc4cbc77080e60fdc73b898fa1997debfbe8f7243f7fecf9ea56f` |
| `make ci` | 0 | Frozen sync, scanner guard, Ruff check/format, Pyright (0 errors), pytest (132 passed), dependency boundary, audit, and license gates passed | `sha256:744bfd31eb4a583a2ca7509be48b7746e95c00f3a25ccb204505e86b79af60f6` |
| `git diff --check` | 0 | No whitespace errors | `sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

## Specification Compliance Matrix

| Requirement / scenario | Exact runtime coverage | Status |
|---|---|---|
| Bounded Dynamic-Import Alias Grammar | `ALIAS_DYNAMIC_CASES` in `test_focused_test_scanner.py`; focused suite 65/65 and full suite 132/132 | PASS |
| Direct callable and module aliases are rejected | `ALIAS_DYNAMIC_CASES` exercises direct callable/module aliases and literal positional/`name=` targets | PASS |
| Supported alias forms are equivalent | `ALIAS_DYNAMIC_CASES` exercises direct, annotated, and name-chain forms | PASS |
| Closed grammar does not resolve arbitrary expressions | `test_closed_alias_grammar_does_not_resolve_arbitrary_expressions` explicitly covers the closed-grammar non-resolution cases | PASS |
| Definite Rebinding and Conditional Ambiguity | Focused rebinding and conditional-ambiguity cases in `test_focused_test_scanner.py` | PASS |
| Definite reassignment removes tracking | Focused unconditional reassignment case | PASS |
| Conditional reassignment fails closed | Focused recognized-`if` ambiguity case asserting the stable ambiguity diagnostic | PASS |
| Isolated Alias Environments and Stable Findings | Focused scope, ownership, ordering, and determinism cases; full suite and CI | PASS |
| Lexical environments do not inherit aliases | `test_aliases_do_not_cross_lexical_boundaries` covers function, async-function, class, and lambda environments | PASS |
| Repeated findings are deterministic | `test_repeated_alias_scans_are_ordered_deduplicated_and_equivalent` runs the same tree twice and asserts sorted, deduplicated, byte-equivalent results | PASS |

## Correctness and Design Coherence

| Dimension | Result | Evidence |
|---|---|---|
| Closed AST-local grammar | PASS | `_classify()` accepts only tracked names and direct recognized attributes; arbitrary expressions are not resolved. |
| Definite invalidation / recognized ambiguity | PASS | `_assign()` removes unknown reassignment classifications; `visit_If()` merges divergent bindings to `ambiguous`. |
| Lexical isolation / stable diagnostics | PASS | Fresh environments at lexical boundaries, `claim()` ownership, set collection, and sorted output remain in place. |
| Design and non-goals | PASS | Changed scanner/tests implement the bounded design without containers, dynamic attributes, closures, interprocedural analysis, dependencies, or workflow changes. |

## Findings

### CRITICAL

None.

### WARNING — approved non-blocking follow-ups

- **R1-001:** Dynamic skip via imported `__import__` remains a follow-up.
- **R2-001:** Resolved by the single bounded correction in review lineage `review-eb4ec3eaa0df3568` — conditional canonical `importlib` rebinding now fails closed with the stable `ambiguous-dynamic-import-alias` diagnostic; no longer a follow-up.
- **R3-001:** Tuple-unpacking direct callable alias has a runtime mismatch; remains a follow-up.

These review follow-ups are informational and non-blocking. R1-001 and R3-001 were not remediated in this bounded change; R2-001 was remediated by the bounded correction.

### SUGGESTION

None.

## Final Decision

**PASS WITH WARNINGS.** All 3 requirements and all 7 specification scenarios have implementation evidence and passed runtime coverage. The focused frozen suite (65), full frozen suite (132), canonical `make ci`, and `git diff --check` all exited zero. The verification is bound to the renewed approved review lineage and receipt above; the three preserved informational follow-ups do not block this result.
