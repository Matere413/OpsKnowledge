# Design: Integrate Approved Source Repository

## Technical Approach

Add a provider-neutral `indexing` feature that returns only immutable metadata for one complete development snapshot. A local outbound adapter scans a separate synthetic fixture using the standard library; it never parses PDF bytes, interprets OCR, persists state, or calls a provider. The manifest is the policy authority; the filename supplies only entry, language, and revision identity. Existing `evaluation-dataset/` loaders remain untouched.

## Architecture Decisions

Traceability shorthand: `Spec R1`–`R8` follow the eight requirements in `spec.md` order; proposal references identify its scope and approach sections.

| Decision | Choice, rejected alternative, and rationale | Traceability |
|---|---|---|
| Feature boundary | Own domain, application, port, and local adapter under `backend/features/indexing/`; keep filesystem concerns out of domain/application. Reject a shared port because this contract is not cross-feature yet. | Proposal in-scope approach; Spec R1, R8 |
| Metadata model | Use frozen, slot-based value objects: `RepositoryRelativePath`, `Collection`, `EntryId`, `Language`, `Revision`, `Approval`, `Classification`, `Sha256`; `SourceIdentity` is `(collection, entry, language, revision)`. Reject raw dictionaries/bytes because consumers need immutable metadata only. | Spec R1, R3 |
| Authority and fixture | Use canonical UTF-8 JSON with `schema_version`, `source_id`, `profile`, and `artifacts[]`; each record owns normalized `path`, `collection`, `approval`, `classification`, and lowercase 64-hex `sha256`. Reject filename- or sidecar-only authority: filenames identify but never approve. The parser accepts exactly `<entry-id>_ESP_REV_<revision>.pdf` or `<entry-id>_EN_REV_<revision>.pdf`; tokens are non-empty, unnormalized, and contain no separators, controls, or whitespace. | Spec R2, R3, R7 |
| Completeness | `InventoryApprovedSources` returns `CompleteSnapshot(artifacts=tuple)` or `RejectedSnapshot(diagnostics=tuple)`. An empty tuple is valid only after completed exact coverage. Reject list-plus-error or partial results because failure must never masquerade as empty. | Spec R5, R6 |

## Data Flow

```text
use case profile/source gate
        ↓ (no filesystem access on denial)
local adapter → safe manifest read → sorted path/link enumeration
        → filename + manifest validation → byte reads → SHA-256 checks
        → exact coverage/completeness gate → immutable sorted snapshot
```

The explicit order is: profile/corporate denial; root and manifest path/link checks; manifest read/schema validation; sorted enumeration with path/link checks; manifest coverage set construction; filename and duplicate-identity checks; reads of only safe declared regular files; hash comparison; final exact coverage and completion gate. Absolute, traversal, non-normalized, symlink, external-link, and non-regular paths are rejected before reads. Any enumeration/read uncertainty yields `scan-incomplete`, never an empty result. Successful zero-artifact coverage yields an immutable empty snapshot.

## File Changes

| File | Action | Description / owner |
|---|---|---|
| `backend/features/indexing/{__init__.py,domain.py,application.py,ports.py}` | Create | Indexing domain value objects/identity, result types, use case, and `ApprovedSourceRepository` protocol. |
| `backend/features/indexing/adapters/{__init__.py,local_repository.py}` | Create | Development-only filesystem adapter, deterministic scanner, manifest authority, and safe diagnostics. |
| `approved-source-fixture/manifest.json` | Create | Logical authority for the synthetic source fixture. |
| `approved-source-fixture/runbooks/runbook-1_ESP_REV_2.pdf` | Create | Opaque synthetic artifact proving Spanish identity. |
| `approved-source-fixture/runbooks/runbook-1_EN_REV_7.pdf` | Create | Opaque synthetic artifact proving independent English revision. |
| `tests/unit/test_approved_source_inventory.py` | Create | Domain, scanner, result, validation, determinism, and failure tests. |
| `tests/architecture/test_approved_source_inventory_boundary.py` | Create | Proves feature ownership, no evaluation-loader reuse, no provider/corporate imports, and development-only wiring. |

No existing corpus/evaluation file, manifest, dependency, database, or CI target changes.

## Interfaces / Contracts

```python
class ApprovedSourceRepository(Protocol):
    def inventory(self) -> InventoryResult: ...

@dataclass(frozen=True, slots=True)
class SourceIdentity:
    collection: Collection
    entry: EntryId
    language: Language
    revision: Revision
```

`InventoryApprovedSources` rejects `profile != development` and any corporate source mode before invoking the port. `Diagnostic` exposes only a stable code and repository-relative reference; the taxonomy includes `profile-not-development`, `corporate-source-denied`, `unsafe-path`, `unsafe-link`, `manifest-invalid`, `filename-invalid`, `identity-duplicate`, `coverage-missing`, `coverage-unlisted`, `source-unreadable`, `source-non-regular`, `hash-mismatch`, and `scan-incomplete`. Diagnostics are sorted by relative reference then code and never include absolute paths, bytes, text, secrets, credentials, or OS/provider error text.

## Testing Strategy

| Layer | What to Test | Approach |
|---|---|---|
| Unit | VOs, filename grammar, ES/EN independence, manifest authority, hashes, duplicates, safe diagnostics, immutable complete/empty/rejected results | Temporary fixtures and deterministic enumeration/read failure injection; assert whole-snapshot rejection. |
| Architecture | Feature dependency direction, fixture separation, profile/corporate denial, no new production dependency | Import/path inspection tests. |
| Integration/E2E | N/A | Current `openspec/config.yaml` has no integration or E2E harness; no runtime boundary is introduced. |

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file classification, or process-integration boundary. Filesystem path/link safety is covered by the inventory unit tests above.

## Migration / Rollout

No migration required. Wire the local adapter only in development; rollback is deletion/reversion of the indexing feature, fixture, and tests as one bounded change. No database, index, or persistent state exists.

## Open Questions

None blocking. A corporate adapter requires a separate approved SDD after Phase 8 and TI gates.
