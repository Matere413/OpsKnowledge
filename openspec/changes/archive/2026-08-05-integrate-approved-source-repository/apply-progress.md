# Apply Progress: Integrate Approved Source Repository

**Change**: integrate-approved-source-repository
**Mode**: Standard (strict_tdd: false per `openspec/config.yaml`)
**Artifact store**: hybrid (OpenSpec + Engram)
- **Delivery strategy**: ask-on-risk
- **Chain strategy**: stacked-to-main
**Work units covered**: unit-1-provider-neutral-contracts (PR 1, complete), unit-2-local-source-scanner (PR 2, complete), unit-3-boundary-diagnostic-tests (complete), unit-4-canonical-verification (complete)
**Native authority cap**: 800 changed lines per work unit (parent-owned runtime attempt `unit-3-boundary-diagnostic-tests`)
**Unit 3 delivery**: ask-on-risk, bounded to the parent-provided 800-line cap; executor did not acquire, settle, reset, or mutate the native attempt ledger.
**Unit 4 delivery**: ask-on-risk, bounded to the parent-provided native runtime attempt; executor did not acquire, settle, reset, or mutate the native attempt ledger.

## Cumulative Task Status

| Task | Status | Phase |
|------|--------|-------|
| 1.1 Provider-neutral contracts + application gate | [x] complete | 1 |
| 1.2 Contract/identity tests | [x] complete | 1 |
| 2.1 RED tests for manifest/path/coverage/rejection | [x] complete | 2 |
| 2.2 Synthetic fixture + manifest | [x] complete | 2 |
| 2.3 Local adapter + scanner | [x] complete | 2 |
| 3.1 Architecture boundary tests | [x] complete | 3 |
| 3.2 Diagnostic taxonomy coverage | [x] complete | 3 |
| 4.1 Focused unit + architecture commands | [x] complete | 4 |
| 4.2 Canonical `make ci` | [x] complete | 4 |

**Completed this batch**: 4.1, 4.2 (2 tasks). **Cumulative**: 9/9 tasks complete. Unit 1–3 evidence remains unchanged below.

## Work Unit Evidence (Unit 1)

| Evidence | Value |
|---|---|
| Focused test command and exact result | `uv run --frozen pytest tests/unit/test_approved_source_inventory.py -q` -> 27 passed, 0 failed, 0.03s. Work-unit filter `-k 'contract or identity'` -> 1 passed, 26 deselected (filter matches by test-name substring; the full file is the unit proof). |
| Runtime harness command/scenario and exact result | N/A — no integration/E2E harness configured (`openspec/config.yaml` layers: integration=false, e2e=false); the repository-port/application-gate tests are the runtime boundary for this unit. |
| Rollback boundary | Remove `backend/features/indexing/{__init__.py,domain.py,ports.py,application.py}` and `tests/unit/test_approved_source_inventory.py`. No other file, dependency, fixture, or CI target is touched. |

## Work Unit Evidence (Unit 2)

| Evidence | Value |
|---|---|
| Focused test command and exact result | `uv run --frozen pytest tests/unit/test_approved_source_local_scanner.py -q` -> 30 passed, 0 failed, 0.07s. Combined with Unit 1: `uv run --frozen pytest tests/unit/test_approved_source_inventory.py tests/unit/test_approved_source_local_scanner.py -q` -> 57 passed, 0 failed. |
| Runtime harness command/scenario and exact result | N/A — no integration/E2E/provider process boundary (`openspec/config.yaml` layers: integration=false, e2e=false); the local-adapter scanner tests against temporary fixtures (and the committed fixture golden) are the runtime boundary for this unit. |
| Rollback boundary | Remove `backend/features/indexing/adapters/{__init__.py,local_repository.py}`, `approved-source-fixture/` (manifest + two PDFs), and `tests/unit/test_approved_source_local_scanner.py`. No Unit 1 file, dependency, or CI target is touched. |

## Work Unit Evidence (Unit 3)

| Evidence | Value |
|---|---|
| Focused test command and exact result | `uv run --frozen pytest tests/unit/test_approved_source_local_scanner.py tests/architecture/test_approved_source_inventory_boundary.py -q` -> 40 passed, 0 failed, 0.10s. Relevant approved-source suite: `uv run --frozen pytest tests/unit/test_approved_source_inventory.py tests/unit/test_approved_source_local_scanner.py tests/architecture/test_approved_source_inventory_boundary.py -q` -> 67 passed, 0 failed, 0.10s. |
| Runtime harness command/scenario and exact result | N/A — `openspec/config.yaml` has no integration/E2E harness and Unit 3 introduces no provider/process boundary; architecture tests execute real import/path isolation and deny-before-read scenarios. |
| Rollback boundary | Remove `tests/architecture/test_approved_source_inventory_boundary.py`, revert the Unit 3 additions in `tests/unit/test_approved_source_local_scanner.py`, and revert only the 3.1/3.2 task/progress evidence. Preserve all Unit 1–2 production, fixture, and test candidate files. |

**Parent-owned native runtime attempt**: `sha256:e54d40472d0b5381aa9997c4ca454bb2a37575dbe6d65a5addea5432ed33ffe6`; work unit `unit-3-boundary-diagnostic-tests`. This executor did not mutate the attempt ledger.

## Work Unit Evidence (Unit 4)

| Evidence | Value |
|---|---|
| Focused test command and exact result | `uv run --frozen pytest tests/unit/test_approved_source_inventory.py tests/unit/test_approved_source_local_scanner.py tests/architecture/test_approved_source_inventory_boundary.py tests/architecture/test_evaluation_dataset_ci_order.py -q` -> 79 passed, 0 failed, 0.13s. |
| Runtime harness command/scenario and exact result | N/A — no integration/E2E harness is configured; the focused unit/architecture suite is the runtime boundary for this metadata-only change. The canonical repository process harness below also passed. |
| Canonical process command and exact result | `make ci` (run exactly once) -> exit 0; evaluation-dataset validator OK before focused-test guard, Ruff, format, Pyright, pytest, dependency boundaries, audit, and license inventory; full suite 574 passed in 20.52s. |
| Protected-path and cleanup evidence | `git diff --quiet -- Makefile .github/workflows/ci.yml scripts/ci evaluation-dataset backend/features/corpus backend/features/evaluation` -> unchanged; matching `git status --short -- ...` -> clean. No generated or temporary files were left by verification. |
| Rollback boundary | Revert only the Unit 4 metadata additions in `openspec/changes/integrate-approved-source-repository/tasks.md` and `apply-progress.md`; preserve all production, fixture, and test candidate files. |

**Parent-owned native runtime attempt**: token `sha256:4ef54484249eae154bc89b5d632a553d743e11af1deec91cf5eb07ce0f1a5e3a5`; work unit `unit-4-canonical-verification`; goal `complete 4.1 and 4.2 with focused verification and canonical make ci`. This executor did not acquire, settle, reset, or mutate the native ledger. Settlement disposition: all assigned evidence passed; parent may settle the already-acquired attempt.

## Static Checks (Unit 2 touched files only)

| Check | Command | Result |
|---|---|---|
| Focused-test guard | `make check-focused-tests` | === focused-test guard OK === (whole-repo scan) |
| Lint | `uv run --frozen ruff check backend/features/indexing/adapters tests/unit/test_approved_source_local_scanner.py` | All checks passed |
| Format | `uv run --frozen ruff format --check backend/features/indexing/adapters tests/unit/test_approved_source_local_scanner.py` | 3 files already formatted |
| Type check | `uv run --frozen pyright backend/features/indexing/adapters tests/unit/test_approved_source_local_scanner.py` | 0 errors, 0 warnings, 0 informations |
| Existing suite | `uv run --frozen pytest tests/unit -q` | 284 passed (57 approved-source + 227 existing), 0 failed |

`make ci` was NOT run per instructions; it belongs to Phase 4 (task 4.2).

## Static Checks (Unit 3 touched files)

| Check | Command | Result |
|---|---|---|
| Focused-test guard | `make check-focused-tests` | === focused-test guard OK === (whole-repo scan) |
| Lint | `uv run --frozen ruff check backend/features/indexing tests/unit/test_approved_source_inventory.py tests/unit/test_approved_source_local_scanner.py tests/architecture/test_approved_source_inventory_boundary.py` | All checks passed |
| Format | `uv run --frozen ruff format --check backend/features/indexing tests/unit/test_approved_source_inventory.py tests/unit/test_approved_source_local_scanner.py tests/architecture/test_approved_source_inventory_boundary.py` | 9 files already formatted |
| Type check | `uv run --frozen pyright backend/features/indexing tests/unit/test_approved_source_inventory.py tests/unit/test_approved_source_local_scanner.py tests/architecture/test_approved_source_inventory_boundary.py` | 0 errors, 0 warnings, 0 informations |
| Existing unit suite | `uv run --frozen pytest tests/unit -q` | 290 passed, 0 failed |

## Files Changed (Unit 1 — preserved from prior batch)

| File | Action | Lines | What Was Done |
|------|--------|-------|---------------|
| `backend/features/indexing/__init__.py` | Created | 11 | Feature package docstring. |
| `backend/features/indexing/domain.py` | Created | 186 | Frozen slot-based value objects (`RepositoryRelativePath`, `Collection`, `EntryId`, `Language`, `Revision`, `Approval`, `Classification`, `Sha256`, `SourceIdentity`, `SourceArtifact`), immutable `CompleteSnapshot`/`RejectedSnapshot`, safe `Diagnostic`, controlled vocabularies, closed `DIAGNOSTIC_CODES` taxonomy. |
| `backend/features/indexing/ports.py` | Created | 50 | `ApprovedSourceRepository` runtime-checkable Protocol + `InventoryResult` alias. |
| `backend/features/indexing/application.py` | Created | 78 | `InventoryApprovedSources` use case: profile + corporate denial before port invocation, port result returned unchanged. |
| `tests/unit/test_approved_source_inventory.py` | Created | 265 | Contract/identity tests: immutability, metadata-only surface, ES/EN identity independence, denial-before-port-invocation, runtime-checkable protocol. |

## Files Changed (Unit 2 — this batch)

| File | Action | Lines | What Was Done |
|------|--------|-------|---------------|
| `backend/features/indexing/adapters/__init__.py` | Created | 15 | Adapter package docstring; exports `LocalApprovedSourceRepository`. |
| `backend/features/indexing/adapters/local_repository.py` | Created | 574 | Development-only local filesystem adapter: profile denial, evaluation-dataset separation guard (resolved-path marker), root/path/link/non-regular safety, manifest read + schema validation, record-shape coverage set, sorted payload enumeration, filename grammar parsing, manifest authority (collection/approval/classification), duplicate-identity detection, read+SHA-256 verification, exact coverage/completion gate, deterministic ascending snapshot. Standard library only. Fixed the broken prior-worker import of non-existent domain constants by defining local schema constants and refactored brittle union-return helpers into clean typed results (`_ParsedFilename`, `_RecordAuthority`, `_HashOutcome`). |
| `approved-source-fixture/manifest.json` | Created | 1 (552 bytes) | Canonical UTF-8 JSON authority: `schema_version=1`, `source_id=opsknowledge-approved-source-fixture`, `profile=development`, `approval=approved`, `classification=synthetic`, two artifact records (normalized path, collection, approval, classification, lowercase 64-hex sha256). Preserved from the aborted worker; hashes verified to match on-disk PDFs. |
| `approved-source-fixture/runbooks/runbook-1_ESP_REV_2.pdf` | Created | 335 bytes | Opaque synthetic ES PDF (never parsed); SHA-256 `79bbbd3919be8529155db6d5e32273cd60915daeda77721fbe7bc2b4eccf1139`. Preserved from aborted worker. |
| `approved-source-fixture/runbooks/runbook-1_EN_REV_7.pdf` | Created | 335 bytes | Opaque synthetic EN PDF (never parsed); SHA-256 `93452672f7dc75b8ee5c1bec6f046f47ab2008f497df719649532e81d3097a94`. Preserved from aborted worker. |
| `tests/unit/test_approved_source_local_scanner.py` | Created | 577 | 30 behavior-first tests: committed-fixture golden bilingual snapshot, manifest authority (unapproved/non-synthetic/hash-mismatch/profile), bilingual distinctness, unsafe paths (absolute/traversal), deterministic ordering, sorted diagnostics, safe-content diagnostics, completed-empty vs coverage-missing vs coverage-unlisted, incomplete-scan-never-empty, whole-snapshot rejection (one-bad/dup/invalid-name/symlink/non-regular/unreadable/malformed-manifest/missing-manifest), immutable artifacts, non-PDF ignored, real evaluation-dataset guard + same-named-elsewhere allowance, symlinked/non-directory root. Uses `_ExpectRaise` helper (NOT `pytest.raises`, which the focused-test guard forbids). |
| `openspec/changes/integrate-approved-source-repository/tasks.md` | Modified | +3 checkbox flips | Marked 2.1, 2.2, 2.3 complete. |

## Files Changed (Unit 3 — this batch)

| File | Action | Lines | What Was Done |
|------|--------|-------|---------------|
| `tests/architecture/test_approved_source_inventory_boundary.py` | Created | 140 | Proves indexing ownership, no corpus/evaluation-loader reuse, no corporate/provider imports, fixture separation, and no-read denial for evaluation-dataset, non-development, and corporate requests. |
| `tests/unit/test_approved_source_local_scanner.py` | Modified | +57 authored | Adds cross-path duplicate-identity coverage and proves rejected results expose neither partial artifacts nor document text, bytes, absolute paths, secrets, credentials, or provider payloads. Existing Unit 2 tests remain preserved. |
| `openspec/changes/integrate-approved-source-repository/tasks.md` | Modified | 2 additions, 2 deletions | Marks only tasks 3.1 and 3.2 complete; tasks 4.1 and 4.2 remain pending. |
| `openspec/changes/integrate-approved-source-repository/apply-progress.md` | Modified | Unit 3 evidence merged | Preserves Unit 1–2 evidence and records Unit 3 checks, rollback, accounting, and hash. |

## Files Changed (Unit 4 — this batch)

| File | Action | What Was Done |
|------|--------|---------------|
| `openspec/changes/integrate-approved-source-repository/tasks.md` | Modified | Reconciled the established `stacked-to-main` chain strategy and marked only tasks 4.1 and 4.2 complete. |
| `openspec/changes/integrate-approved-source-repository/apply-progress.md` | Modified | Merged Unit 4 focused/CI evidence, protected-path checks, native settlement disposition, and the historical Unit 2 correction reconciliation. |

## Unit 4-local documentation accounting

- Executor-reported Unit 4-local documentation accounting: 42 additions and 12 deletions.
- This local accounting is distinct from the cumulative HEAD-relative documentation diff; it does not replace or restate that cumulative comparison.

## Changed-Line Count (Unit 2 native)

- Production: 589 lines (15 + 574)
- Tests: 577 lines
- Fixture: 1 line (manifest) + 22 + 22 lines (binary PDFs counted by git)
- Total native changed lines (git numstat): 1211 additions, 0 deletions = 1211 changed
- Cumulative across both units: ~1801 native changed lines (590 Unit 1 + 1211 Unit 2)

### Post-attempt Unit 2 correction reconciliation

- The 1211-line Unit 2 implementation/fixture total and the ~1801-line Unit 1–2 cumulative figure above are historical pre-correction evidence and remain unchanged.
- A later bounded scanner correction changed 135 lines: 28 in `backend/features/indexing/adapters/local_repository.py` (20 additions, 8 deletions) and 107 in `tests/unit/test_approved_source_local_scanner.py` (105 additions, 2 deletions), as documented by the later correction record.
- Reconciled current Unit 2 candidate accounting is 1346 implementation/fixture changed lines (1211 + 135); retaining the previously documented full Unit 2 native count of 1305 including SDD evidence yields 1440 full candidate changed lines after the correction. These reconciled figures supplement, and do not rewrite, the historical attempt evidence or its accepted size exception.
- Reconciled Unit 1–2 implementation/fixture baseline is 1936 changed lines (590 + 1346), before Unit 3/4 documentation and test-evidence changes.

## Evidence Revision / Hash (Unit 2 — historical pre-correction)

- All combined and per-file SHA-256 entries in this section are historical pre-correction hashes from the original Unit 2 candidate. They are preserved unchanged for audit and do not represent hashes of the later corrected files.

- Combined evidence revision (SHA-256 of concatenated Unit 2 touched files): `08d7aa9ed1e8269fe93217f931bc2186054649fae68c6e2b4ae5e670588864d1`
- Per-file SHA-256:
  - `backend/features/indexing/adapters/__init__.py`: `d6e6e43f0fdbe991416ab5f81707381615c1c89b9dabac6870937b4705205d2c`
  - `backend/features/indexing/adapters/local_repository.py`: `592a8f63420de7cef10e35d411a72c321dc908c85e1e56be886dd7f83b2530fc`
  - `tests/unit/test_approved_source_local_scanner.py`: `7a42c078b400e0df0b344b97d4357560c033c16f8fc49eb4860fd68e3d7f2e14`
  - `approved-source-fixture/manifest.json`: `8016e693ab10aa72cb54235743b08db2f2a4a30fc1716ef261b24a09782aa601`
  - `approved-source-fixture/runbooks/runbook-1_ESP_REV_2.pdf`: `79bbbd3919be8529155db6d5e32273cd60915daeda77721fbe7bc2b4eccf1139`
  - `approved-source-fixture/runbooks/runbook-1_EN_REV_7.pdf`: `93452672f7dc75b8ee5c1bec6f046f47ab2008f497df719649532e81d3097a94`
- Current corrected state/evidence is represented only by the post-attempt reconciliation above, including the 135-line bounded correction and current candidate accounting; no post-correction combined or per-file hash is asserted here.

## Changed-Line Count (Unit 3 native)

- Production: 0 lines; no production file changed.
- Tests: 197 additions (140 architecture + 57 focused unit), 0 deletions.
- OpenSpec tasks: 2 additions, 2 deletions (only 3.1 and 3.2 checkboxes).
- Apply-progress artifact: 55 additions, 8 deletions for this batch's evidence.
- **Total Unit 3 authored changes: 254 additions + 10 deletions = 264 changed lines**, within the 800-line cap.
- Pre-existing Unit 1–2 uncommitted candidate lines are excluded from this Unit 3 accounting and remain preserved.

## Evidence Revision / Hash (Unit 3)

- Combined evidence revision: `sha256:ff0cdceb672e81b3809e1928af04e163fc68d2d409de61c7c571e25c25e75f38` (SHA-256 of concatenated sorted bytes of the two Unit 3 touched test files).
- Per-file SHA-256:
  - `tests/architecture/test_approved_source_inventory_boundary.py`: `9db525ea98101145017858d2c5abb13c71d757b16cc123b7a6f0d253ca7d1ec8`
  - `tests/unit/test_approved_source_local_scanner.py`: `e4088c0cd489e2b36a28c9525b5adbb84441ec0f00f0f400c809cd046406bad5`

## Evidence Revision / Hash (Unit 4)

- Combined evidence revision: `sha256:efc161786b27055ebf4310a73a1817023abcdc966054075e5eab4189ed65a549` (SHA-256 of concatenated sorted bytes of `Makefile` and the four focused unit/architecture test files used for Unit 4 verification).

## Evidence Revision / Hash (Unit 1 — preserved)

- Combined evidence revision (SHA-256 of concatenated touched files): `0f66108d7887779d09eda547aedb891f3784eec476fd99cf9388631a4817738d`
- Per-file SHA-256:
  - `backend/features/indexing/__init__.py`: `2ac8db2dad95ff43a16e466ee92caadc260e569e23e6135ab465ab9f0e7bbfb0`
  - `backend/features/indexing/domain.py`: `88935a1ba7fed1d1f918a0a364019fa00cb5dbfd0da572f8d968c032a328e618`
  - `backend/features/indexing/ports.py`: `c43020d48a5ad88937f26e462234366208b28d2b13ba6fe8e149ab518a4dfd90`
  - `backend/features/indexing/application.py`: `20aa23e33828682bdb8703e741d93157e97a8b8646d8a71110b5673b33dac4b6`
  - `tests/unit/test_approved_source_inventory.py`: `6834a97a8fecbac9ed047b72ed47b581a85e7be53ab03313bf854a859dc5b272`

## Deviations from Design

None — implementation matches design. Unit 1's 13 design-mandated value objects, the `SourceIdentity` contract, immutable result types, safe `Diagnostic`, the `ApprovedSourceRepository` Protocol, and the profile/corporate denial-before-port-invocation gate are present exactly as specified. Unit 2's adapter follows the documented data-flow order (profile denial -> evaluation-dataset guard -> root/manifest safety -> manifest read/schema -> record coverage set -> sorted enumeration -> filename grammar -> manifest authority -> duplicate identity -> read+hash -> exact coverage gate -> deterministic ascending snapshot). The evaluation-dataset separation guard resolves the marker relative to the working directory so it always protects the real committed corpus (verified: the real `evaluation-dataset/` is rejected; a same-named directory elsewhere is allowed — this is the intended, non-over-strict semantics).

Unit 3 matches the design: boundary tests inspect imports and fixture paths without changing production wiring, and focused tests close the `identity-duplicate` taxonomy gap while asserting safe whole-snapshot rejection. No production, fixture, corpus, evaluation, dependency, or CI file was changed.

## Budget Overrun (flagged for parent)

The parent-owned runtime attempt `unit-2-local-source-scanner` cap is 800 changed lines. Unit 2 produced 1211 native changed lines (589 production + 577 tests + 45 fixture). The overrun is ~411 lines over the 800-line cap, driven by the design-mandated adapter data-flow surface (9 ordered steps with distinct safety/validation gates), the closed diagnostic taxonomy the spec requires the adapter to emit, and the behavior-first test coverage the prompt requires (manifest authority, unsafe paths/order, valid-empty vs incomplete, whole-snapshot rejection). No design surface was stripped to fake compliance; docstrings were kept to the minimum preserving the data-flow intent. **Reported transparently rather than silently absorbed.** The parent/native authority must decide: accept a `size:exception` for this unit, or split Unit 2 further (e.g., move symlink/non-regular/unreadable rejection tests into a sub-unit). (Unit 1's prior overrun note is retained for audit: its 200-line cap was exceeded by ~125 production lines for the same design-mandated reason.)

## Issues Found

- The aborted prior Unit 2 worker left a broken adapter that imported `APPROVED_APPROVAL`, `SYNTHETIC_CLASSIFICATION`, and `DEVELOPMENT_PROFILE` from `backend.features.indexing.domain`, where none of those names exist (`domain` exports only `ALLOWED_*` frozensets; `DEVELOPMENT_PROFILE` lives in `application.py`). The import raised `ImportError` on any use. Fixed by defining local schema constants in the adapter that mirror the controlled vocabularies and are pinned to the exact values the manifest authority gate checks against.
- The prior worker's `_check_filename_grammar` and `_check_record_authority` returned a `Diagnostic | tuple` union and the caller unpacked the tuple via index after a confusing `is not None` branch. Refactored into clean typed results (`_ParsedFilename`, `_RecordAuthority`, `_HashOutcome`) so the control flow is type-safe and readable.
- The prior worker's fixture (`manifest.json` + two PDFs) was correct and fully preserved; its hashes match the manifest exactly. No duplication.
- The focused-test guard forbids `pytest.raises` (repo convention, see `test_technical_grounding_gates_report.py`); used the established `_ExpectRaise` plain context-manager helper instead. No `pytest.skip`/`xfail`, no `pytestmark` mutation, no dynamic imports.
- Unit 3 found no additional implementation issue; all focused tests, the approved-source suite, static checks, and the full unit suite passed.

## Remaining Tasks

- None — tasks 4.1 and 4.2 are complete.

## Status

9/9 tasks complete. Ready for `sdd-verify` handoff; extraction/OCR, persistence, sync/diff, and corporate/provider behavior remain excluded from this change.
