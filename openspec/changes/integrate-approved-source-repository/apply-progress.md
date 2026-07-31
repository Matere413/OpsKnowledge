# Apply Progress: Integrate Approved Source Repository

**Change**: integrate-approved-source-repository
**Mode**: Standard (strict_tdd: false per `openspec/config.yaml`)
**Artifact store**: hybrid (OpenSpec + Engram)
**Delivery**: auto-chain, stacked-to-main, PR 1 (provider-neutral contracts only)
**Work unit**: unit-1-provider-neutral-contracts
**Native authority cap**: 200 changed lines per work unit

## Cumulative Task Status

| Task | Status | Phase |
|------|--------|-------|
| 1.1 Provider-neutral contracts + application gate | [x] complete | 1 |
| 1.2 Contract/identity tests | [x] complete | 1 |
| 2.1 RED tests for manifest/path/coverage/rejection | [ ] pending | 2 |
| 2.2 Synthetic fixture + manifest | [ ] pending | 2 |
| 2.3 Local adapter + scanner | [ ] pending | 2 |
| 3.1 Architecture boundary tests | [ ] pending | 3 |
| 3.2 Diagnostic taxonomy coverage | [ ] pending | 3 |
| 4.1 Focused unit + architecture commands | [ ] pending | 4 |
| 4.2 Canonical `make ci` | [ ] pending | 4 |

**Completed this batch**: 1.1, 1.2 (2/9 tasks).

## Work Unit Evidence (Unit 1)

| Evidence | Value |
|---|---|
| Focused test command and exact result | `uv run --frozen pytest tests/unit/test_approved_source_inventory.py -q` -> 27 passed, 0 failed, 0.03s. Work-unit filter `-k 'contract or identity'` -> 1 passed, 26 deselected (filter matches by test-name substring; the full file is the unit proof). |
| Runtime harness command/scenario and exact result | N/A — no integration/E2E harness configured (`openspec/config.yaml` layers: integration=false, e2e=false); the repository-port/application-gate tests are the runtime boundary for this unit. |
| Rollback boundary | Remove `backend/features/indexing/{__init__.py,domain.py,ports.py,application.py}` and `tests/unit/test_approved_source_inventory.py`. No other file, dependency, fixture, or CI target is touched. |

## Static Checks (touched files only)

| Check | Command | Result |
|---|---|---|
| Lint | `uv run --frozen ruff check backend/features/indexing tests/unit/test_approved_source_inventory.py` | All checks passed |
| Format | `uv run --frozen ruff format --check backend/features/indexing tests/unit/test_approved_source_inventory.py` | 5 files already formatted |
| Type check | `uv run --frozen pyright backend/features/indexing tests/unit/test_approved_source_inventory.py` | 0 errors, 0 warnings, 0 informations |
| Existing suite | `uv run --frozen pytest tests/unit -q` | 254 passed (27 new + 227 existing), 0 failed |

`make ci` was NOT run per instructions; it belongs to Phase 4.

## Files Changed

| File | Action | Lines | What Was Done |
|------|--------|-------|---------------|
| `backend/features/indexing/__init__.py` | Created | 11 | Feature package docstring. |
| `backend/features/indexing/domain.py` | Created | 186 | Frozen slot-based value objects (`RepositoryRelativePath`, `Collection`, `EntryId`, `Language`, `Revision`, `Approval`, `Classification`, `Sha256`, `SourceIdentity`, `SourceArtifact`), immutable `CompleteSnapshot`/`RejectedSnapshot`, safe `Diagnostic`, controlled vocabularies, closed `DIAGNOSTIC_CODES` taxonomy. |
| `backend/features/indexing/ports.py` | Created | 50 | `ApprovedSourceRepository` runtime-checkable Protocol + `InventoryResult` alias. |
| `backend/features/indexing/application.py` | Created | 78 | `InventoryApprovedSources` use case: profile + corporate denial before port invocation, port result returned unchanged. |
| `tests/unit/test_approved_source_inventory.py` | Created | 265 | Contract/identity tests: immutability, metadata-only surface, ES/EN identity independence, denial-before-port-invocation, runtime-checkable protocol. |
| `openspec/changes/integrate-approved-source-repository/tasks.md` | Modified | +2 checkbox flips | Marked 1.1 and 1.2 complete. |

## Changed-Line Count

- Production: 325 lines (11 + 186 + 50 + 78)
- Tests: 265 lines
- Total authored changed lines: 590
- No deletions (all new files).

## Evidence Revision / Hash

- Combined evidence revision (SHA-256 of concatenated touched files): `0f66108d7887779d09eda547aedb891f3784eec476fd99cf9388631a4817738d`
- Per-file SHA-256:
  - `backend/features/indexing/__init__.py`: `2ac8db2dad95ff43a16e466ee92caadc260e569e23e6135ab465ab9f0e7bbfb0`
  - `backend/features/indexing/domain.py`: `88935a1ba7fed1d1f918a0a364019fa00cb5dbfd0da572f8d968c032a328e618`
  - `backend/features/indexing/ports.py`: `c43020d48a5ad88937f26e462234366208b28d2b13ba6fe8e149ab518a4dfd90`
  - `backend/features/indexing/application.py`: `20aa23e33828682bdb8703e741d93157e97a8b8646d8a71110b5673b33dac4b6`
  - `tests/unit/test_approved_source_inventory.py`: `6834a97a8fecbac9ed047b72ed47b581a85e7be53ab03313bf854a859dc5b272`

## Deviations from Design

None — implementation matches design. All 13 design-mandated value objects, the `SourceIdentity` (collection, entry, language, revision) contract, immutable `CompleteSnapshot`/`RejectedSnapshot`, safe `Diagnostic`, the `ApprovedSourceRepository` Protocol, and the profile/corporate denial-before-port-invocation gate are present exactly as specified. Domain performs no runtime validation (corpus feature convention); validation belongs to the adapter in a later work unit.

## Budget Overrun (flagged for parent)

The native authority cap for this work unit is 200 changed lines. Production code alone is 325 lines because the design's metadata-model decision mandates 13 frozen slot-based value objects plus result types, the diagnostic taxonomy, and the application gate. Compressed docstrings to the minimum that preserves the design's semantic intent; no required design surface was stripped to fake compliance. **The 200-line cap is exceeded by ~125 production lines (590 total including tests).** This is reported transparently rather than silently absorbed. The parent/native authority must decide: accept a `size:exception` for this unit, or split Unit 1 further (e.g., move the application gate + diagnostic taxonomy into a sub-unit). No further compression is possible without removing design-mandated types.

## Issues Found

None blocking. The `-k 'contract or identity'` work-unit filter from the tasks artifact matches only 1 test by name substring; the full file (27 tests) is the actual unit proof and passes cleanly.

## Remaining Tasks

- [ ] 2.1 RED tests for manifest authority, unsafe paths/order, completed-empty vs incomplete scans, whole-snapshot rejection (R2/S2, R4/S4, R5/S5-S6, R6/S7)
- [ ] 2.2 `approved-source-fixture/manifest.json` + opaque synthetic `runbook-1_ESP_REV_2.pdf` and `runbook-1_EN_REV_7.pdf`
- [ ] 2.3 `backend/features/indexing/adapters/{__init__.py,local_repository.py}` local adapter + scanner
- [ ] 3.1 `tests/architecture/test_approved_source_inventory_boundary.py` boundary tests (R7/S8, R8/S9)
- [ ] 3.2 Diagnostic taxonomy full coverage + no-partial-snapshot/no-content proof
- [ ] 4.1 Focused unit + architecture commands; confirm corpus/evaluation + CI unchanged
- [ ] 4.2 Canonical `make ci`; record result

## Status

2/9 tasks complete. Ready for next batch (Phase 2). Not ready for verify — Phases 2-4 remain.