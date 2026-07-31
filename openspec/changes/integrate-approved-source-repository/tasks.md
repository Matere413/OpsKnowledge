# Tasks: Integrate Approved Source Repository

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 850–1,000 authored lines across contracts, adapter, fixtures, and tests |
| 800-line budget risk | High; adapter failure semantics and boundary tests are substantial |
| Chained PRs recommended | Yes |
| Suggested split | PR 1: provider-neutral contracts; PR 2: local adapter, fixture, and boundary tests |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending user selection |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High
800-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Immutable contracts and application gate | PR 1 | `uv run --frozen pytest tests/unit/test_approved_source_inventory.py -q -k 'contract or identity'` | N/A — no integration/E2E harness; port/use-case tests are the runtime boundary | Remove `backend/features/indexing/{__init__.py,domain.py,application.py,ports.py}` and contract tests |
| 2 | Development scanner, fixture, and isolation proof | PR 2 | `uv run --frozen pytest tests/unit/test_approved_source_inventory.py tests/architecture/test_approved_source_inventory_boundary.py -q` | N/A — no provider or process boundary; temporary-fixture scanner tests exercise the complete flow | Remove `backend/features/indexing/adapters/`, `approved-source-fixture/`, and the two new test files |

## Phase 1: Provider-Neutral Contracts

- [x] 1.1 Create `backend/features/indexing/{__init__.py,domain.py,ports.py,application.py}` with frozen slot-based metadata value objects, `SourceIdentity`, immutable complete/rejected results, safe `Diagnostic`, the repository protocol, and profile/corporate denial before port invocation (R1, R3, R8).
- [x] 1.2 Add contract tests in `tests/unit/test_approved_source_inventory.py` proving metadata-only immutable output and distinct Spanish/English identities without revision comparison (R1/S1, R3/S3).

## Phase 2: Local Fixture and Fail-Closed Scanner

- [ ] 2.1 Add RED tests for manifest authority, unsafe paths/order, completed-empty versus incomplete scans, and whole-snapshot rejection; preserve safe diagnostic fields and exercise R2/S2, R4/S4, R5/S5–S6, and R6/S7.
- [ ] 2.2 Create `approved-source-fixture/manifest.json` plus opaque synthetic files `runbooks/runbook-1_ESP_REV_2.pdf` and `runbooks/runbook-1_EN_REV_7.pdf`; keep the fixture outside `evaluation-dataset/` and treat files as unread semantic bytes.
- [ ] 2.3 Implement `backend/features/indexing/adapters/{__init__.py,local_repository.py}` with development-only wiring, safe normalized paths/links, canonical manifest validation, exact filename grammar, duplicate/hash/coverage checks, deterministic output, and explicit incomplete-scan rejection.

## Phase 3: Boundary and Integration Tests

- [ ] 3.1 Add `tests/architecture/test_approved_source_inventory_boundary.py` proving indexing ownership, no corpus/evaluation-loader reuse, no corporate/provider imports, fixture separation, and denial before scanning for `evaluation-dataset/`, non-development, and corporate requests (R7/S8, R8/S9).
- [ ] 3.2 Complete focused unit coverage for every diagnostic taxonomy case and assert no partial snapshot, document text, bytes, absolute path, secret, credential, or provider payload is returned.

## Phase 4: Canonical Verification Handoff

- [ ] 4.1 Run focused unit and architecture commands from the work units; confirm the existing corpus/evaluation files and CI wiring remain unchanged.
- [ ] 4.2 Run canonical `make ci`; record the result and confirm evaluation-dataset validation still precedes the existing quality and test stages.
