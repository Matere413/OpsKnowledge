# Proposal: Bootstrap OpsKnowledge Test Harness

## Intent

Establish a Python quality harness. PR2B replaces bypass-prone detection with a finite structural test-API whitelist. PR1/PR2A safety invariants remain intact.

## Scope

### In Scope
- Locked Python/governance checks behind `make ci` and thin GitHub Actions.
- The whitelist applies globally to every executable structural pytest/unittest API use in included first-party Python; ordinary strings/docs are outside validation.
- Every other test-API AST use/reference fails closed with path, line, rejected form, and safe direct-syntax remediation.
- Collection-independent scanning uses exclusions and a global 100,000-entry bound; observable filesystem/parse errors and symlinks fail closed.

### Out of Scope
- Runtime implementation and production dependency/approval changes.
- Blacklist-style detection, semantic resolution, runtime inspection, Python emulation, and TOCTOU/race-resistance claims. CI assumes a stable tree.
- PR1/PR2A runtime implementation or accepted behavior; PR2B governance artifacts may be revised.

## Capabilities

### New Capabilities
- `test-harness`: Structural test-API whitelist through `make ci`.

### Modified Capabilities
- None; `test-harness` has no corresponding current specification.

## Approach

Retain locked `uv`/`make ci`. Supersede blacklist detection: prohibited-form enumeration cannot converge. Only named direct pytest/unittest forms are allowed; aliases, `getattr`, dunder/subscript access, computed receivers, and indirection are outside the whitelist. Dynamic-import policy owns finite direct forms with exact literal `pytest`/`unittest` targets and rejects syntactic `importlib` aliases/import-from access without resolving values; standard-library/project imports remain unrestricted. Other API uses/references fail closed. Intentional false positives require direct syntax or a future change. Scanner reads bytes/metadata only, with a global 100,000-entry bound and stable-tree/no-TOCTOU claim. Rebuild from `f505c81`; staged PR2B remains evidence. Engram #3588 grants a size exception only to PR2B; PR2A, PR3, and PR4 have no size exception. Planning artifacts are separate.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| Tooling, Makefile, workflow | New | Locked single CI contract. |
| Scanner, architecture tests | Modified | Whitelist policy. |
| First-party `**/*.py` | Validated | Coverage, exclusions, global bound. |
| Governance | Validated | No approval changes. |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Whitelist false positives | Medium | Direct-syntax remediation or future change. |
| Filesystem changes | Low | Fail closed; stable-tree, not race resistance. |

## Rollback Plan

Revert the PR2B guard slice to `f505c81`, retaining PR1/PR2A.

## Dependencies

- Python and GitHub Actions.

## Success Criteria

- [ ] `make ci` is locked and fails on errors.
- [ ] GitHub Actions invokes it without duplicated checks.
- [ ] No production dependency or approval changes.
- [ ] CI scans all first-party Python without imports/execution; non-whitelisted test-API AST uses and scan uncertainty fail closed with actionable diagnostics.
