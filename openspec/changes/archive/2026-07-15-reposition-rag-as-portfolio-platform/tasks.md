# Tasks: Reposition RAG as OpsKnowledge

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 680–930 (AGENTS ~50, roadmap ~340–510, architecture ~260–360, OpenSpec/path move ~30, supersession index) |
| 400-line budget risk | High |
| 800-line active budget risk | High (final split/exception decisions use 800) |
| Chained PRs recommended | Yes (original forecast) |
| Delivery decision | size:exception — maintainer approved single atomic review unit |
| Chain strategy | not applicable — workspace is not a Git repository; single atomic delivery |

Delivery decision resolved: size:exception. The maintainer explicitly approved a single atomic review unit for the 680–930-line forecast against the 800-line budget. The workspace is NOT a Git repository; no branches, PRs, or chained-PR base branches apply. All work units (WU1 + WU2 + WU3 + verification) are delivered as one atomic review unit.

### Work Units (implemented as one atomic review unit)

| Unit | Goal | Scope | Notes |
|------|------|-------|-------|
| WU1 | Lock authority contract and supersession links | AGENTS.md + supersession-index.md | Establishes invariant hierarchy |
| WU2 | Realign RAG_ROADMAP.md to AGENTS | Roadmap phases/candidate renames | Depends on WU1 |
| WU3 | Realign architecture + move governance file | docs/architecture stays; architecture/direct-dependencies.yaml → governance/direct-dependencies.yaml | Depends on WU2 |

## Phase 1: Foundation — Authority Anchor (WU1)

- [x] 1.1 Edit `AGENTS.md` title and "RAG and business safety invariants" bullets; replace `Consultation App` with `human expert` (Req 1, 6)
- [x] 1.2 Update `AGENTS.md` "Dependency governance" and "Where to look" sections; point to `governance/direct-dependencies.yaml` (Req 1)
- [x] 1.3 Create `openspec/changes/reposition-rag-as-portfolio-platform/supersession-index.md` mapping #3226→#3122, #3227→#3125, #3228→#3133, new tasks→#3134 (Req 9)
- [x] 1.4 Call `engram_mem_compare` for each supersession pair with `relation: supersedes`; if unsupported, persist via immutable index
- [x] 1.5 Verify (no Git): `AGENTS.md` hierarchy section is consistent; no completed interval where lower source contradicts higher source

## Phase 2: Roadmap Realignment (WU2)

- [x] 2.1 Update `RAG_ROADMAP.md` title, Product boundary, Guiding principles, Phase 0 canonical-source/completion notes (Req 1, 2)
- [x] 2.2 Rename Phase 0–10 candidate slugs: P0 dental-guidance → OpsKnowledge contract; P1 `build-minimal-grounded-dental-rag` → `build-minimal-grounded-opsknowledge-core`; P2 RAG/clinical → OpsKnowledge/technical; P3 SharePoint-guide → approved-source; P6 expose-rag → expose-opsknowledge; P7 technician/clinical → reader/reviewer; P9 RAG/five-technician → OpsKnowledge/five-user
- [x] 2.3 Rename `build-consultation-evaluation-dataset` → `build-opsknowledge-evaluation-dataset` and `integrate-dental-design-software` → `integrate-approved-operations-tool`
- [x] 2.4 Update cross-phase abstention invariant, Next step, and dependency-evidence path to `governance/direct-dependencies.yaml` (Req 6)
- [x] 2.5 Verify (no Git): roadmap matches AGENTS contract; P4/P5/P8/P10 untouched unless containing replaced terms

## Phase 3: Architecture + Governance-Move Realignment (WU3)

- [x] 3.1 Compute SHA-256 of `architecture/direct-dependencies.yaml` and record as pre-move checksum
- [x] 3.2 Create `governance/` directory; copy `architecture/direct-dependencies.yaml` to `governance/direct-dependencies.yaml` byte-for-byte (initial path-move verification: checksum matched pre-move `b8a8f9bd...bcc519`)
- [x] 3.3 Verify checksum (initial move): `shasum -a 256 governance/direct-dependencies.yaml` equals pre-move checksum `b8a8f9bd5c4eb04145bc01cd388e3b3b2b22f3c4743d5fc4b5152af7d9bcc519`; assert governance/ contains only this YAML. Subsequent remediation applied an intentional comment-only naming change (header "RAG platform" → "OpsKnowledge platform"); final checksum is `b176b51aef99b5999ac057ff0bcf033eb0ffdc87ad75456a904d92ba04cb4dc5` and is NOT byte-identical with the pre-move file.
- [x] 3.4 Remove `architecture/direct-dependencies.yaml` only after every reference targets the new path
- [x] 3.5 Update `docs/architecture/platform-architecture.md` title, introduction, overview for OpsKnowledge identity (Req 1); confirm `docs/architecture/` remains architecture-doc location
- [x] 3.6 Rewrite Guide/Fragment data model with `runbooks`/`adrs`/`operational-policies`, version+approval+classification+language fields (Req 2, 4)
- [x] 3.7 Update query/ingestion/failure flows: fragment-level language filter, six-state outcome taxonomy verbatim, provider-failure → `unavailable` (Req 4, 7)
- [x] 3.8 Update module ownership, risk/demo sections, traceability, checklist with reader/contributor/reviewer/admin roles, `human expert`, and `governance/` path (Req 5, 6)
- [x] 3.9 Update sensitive-screening gate ordering with technical-domain examples (Req 8)
- [x] 3.10 Update OpenSpec change artifacts (`proposal.md`, `specs/**`, this design) to reference `governance/direct-dependencies.yaml`
- [x] 3.11 Verify: `docs/architecture/` contains architecture docs only; `governance/` contains review/governance evidence; topology preserved

## Phase 4: Cross-Cutting Verification (Filesystem/Content)

- [x] 4.1 Content search LIVE authority docs (`AGENTS.md`, `RAG_ROADMAP.md`, `docs/architecture/platform-architecture.md`) for `Consultation App`/dental/technician — must appear only in supersession/historical links (Req 9)
- [x] 4.2 Content search LIVE authority/governance files (`AGENTS.md`, `RAG_ROADMAP.md`, `docs/architecture/platform-architecture.md`, `governance/direct-dependencies.yaml`) for `architecture/direct-dependencies.yaml` as a live reference path — must return zero matches; `governance/direct-dependencies.yaml` present with documented checksum. Historical/provenance artifacts in `openspec/changes/` may intentionally mention the old path as migration context and are excluded from this check.
- [x] 4.3 Confirm no runtime/manifest/lockfile files present anywhere in the changeset (path enumeration)
- [x] 4.4 Confirm all 9 spec requirements satisfied; exact six outcomes present; bilingual isolation present
- [x] 4.5 Rollback (safe order, non-Git workspace): (1) create `architecture/` directory; (2) copy current `governance/direct-dependencies.yaml` to `architecture/direct-dependencies.yaml`; (3) deterministically restore the former header comment ("RAG platform" → revert the OpsKnowledge naming change) if reverting the full product migration; (4) verify expected pre-move checksum `b8a8f9bd5c4eb04145bc01cd388e3b3b2b22f3c4743d5fc4b5152af7d9bcc519` (only if the comment-only naming change is also reverted); (5) retarget all references back to `architecture/direct-dependencies.yaml`; (6) only after verified restoration, remove `governance/`. Never delete sole evidence before verified restoration.

## Task Accounting Summary

Canonical totals (independently verified by filesystem count):

| Category | Count | Source |
|----------|------:|--------|
| Original planned tasks (Phase 1–4) | 26 | `tasks.md` `[x]` items: P1=5, P2=5, P3=11, P4=5 |
| Remediation tasks (R1–R12) | 12 | Engram apply-progress #3232: R1–R8 (8) + R9–R12 (4) |
| **Total completed work items** | **38** | 26 + 12 |

All 26 original planned tasks are checked `[x]` in tasks.md. All 12 remediation tasks are recorded complete in apply-progress #3232. Total = 38.
