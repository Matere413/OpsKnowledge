# Design: Build OpsKnowledge Evaluation Dataset

## Technical Approach

Create a self-contained, static JSON dataset and a Python 3.12 stdlib validator. It realizes the proposal's reviewed synthetic corpus and the `evaluation-dataset` delta without runtime, providers, database, or profile wiring. `make ci` invokes the validator with the fixed dataset root before the existing quality/test stages.

## Architecture Decisions

| Decision | Options / trade-off | Choice and rationale |
|---|---|---|
| Format and location | YAML reuses a dev dependency; JSON is stdlib-only | `evaluation-dataset/manifest.json`, `entries/*.json`, `fragments/*.json`, and `scenarios/*.json`. JSON keeps the data readable while `json` needs no dependency. |
| Integrity identity | File digests alone cannot be self-declared | Manifest lists every repository-relative artifact, record ID, revision, and SHA-256 of canonical artifact bytes. Records declare `content_sha256` over their `content` value, separating payload integrity from file integrity. |
| Validation boundary | Runtime adapter or static CI utility | `scripts/ci/validate_evaluation_dataset.py` exports `validate(root) -> list[Diagnostic]` and provides a fixed-argument CLI. This is a repository guard, not a corpus loader or runtime feature. |
| Parity assurance | Infer pairs from text or explicit identity | Explicit `pair_id` prevents text inference. The validator compares declared structural fields; bilingual semantic equivalence remains reviewer-governed. |

## Data Flow

```text
manifest.json -> deterministic regular-file walk -> parse/shape checks
      |                    |                         v
      +-> SHA-256 checks <-+                 cross-reference/parity/count checks
                                                   -> safe diagnostics / exit 0|1
make ci ---------------------------------------------------------------> validator
```

Canonical artifact bytes are UTF-8 without BOM, JSON serialized with sorted keys, `,`/`:` separators, `ensure_ascii: false`, and exactly one trailing LF. SHA-256 uses those bytes. The validator rejects non-canonical bytes, symlinks, hidden/orphan files, duplicate IDs, and paths outside its resolved dataset root; traversal is lexically sorted.

## File Changes

| File | Action | Description |
|---|---|---|
| `evaluation-dataset/manifest.json` | Create | Single exhaustive inventory and artifact digests. |
| `evaluation-dataset/entries/*.json` | Create | Approved synthetic logical-entry revisions across all three collections. |
| `evaluation-dataset/fragments/*.json` | Create | Language-matched, parent-referenced evidence fragments. |
| `evaluation-dataset/scenarios/*.json` | Create | 32 language-paired evaluation scenarios. |
| `scripts/ci/validate_evaluation_dataset.py` | Create | Dependency-free structural validator and CLI. |
| `tests/architecture/test_evaluation_dataset_validator.py` | Create | Valid dataset and mutation coverage. |
| `Makefile` | Modify | Add `check-evaluation-dataset` to canonical CI. |

## Interfaces / Contracts

`manifest.json` has `schema_version`, `dataset_id`, `profile: "development"`, `approval`, `classification`, and sorted `artifacts[]` entries `{path, kind, id, revision?, sha256}`. IDs use lowercase ASCII namespaces: `entry.<logical-id>.rev.<revision>`, `fragment.<id>`, `scenario.<pair-id>.<language>`; IDs are globally unique and never reused.

Entry records include `logical_entry_id`, `revision`, `collection`, `language`, approval/classification/profile, and `content`. Fragment records include `entry_id`, `language`, `provenance`, `source_reference`, `quality`, and `content`. Scenario records include `pair_id`, `language`, `case_type`, `expected_outcome`, `safety_classification`, `claim_expectation` (a controlled claim ID, never answer prose), `abstention_reason` (controlled reason code), and `evidence[]` fragment IDs.

The validator allowlists fields and values: collections, `es|en`, the six outcomes, and safe reason codes. It requires 32 scenarios, 16 per language, 16 pair IDs, one record per language/pair, identical pair structural fields and evidence shape, and exactly 16 `supported` / 16 non-supported outcomes. It resolves every evidence ID to an approved, synthetic, development fragment and language-matched parent. Contradictions require exactly two approved revisions of one logical entry. OCR cases require `provenance: "ocr"`, a synthetic extracted-text source reference, and quality; no image field exists. Sensitive identifiers are structured allowlist values (`fictitious: true` plus `example.test`, `TEST-`, or `INVALID` patterns).

Diagnostics are sorted `path-or-id: reason-code: remediation`, sent to stderr; zero means valid, one means findings, and two means invalid CLI usage. They never print content, query text, evidence text, or answer-like text. `Makefile` uses `$(UV_RUN) run --frozen python scripts/ci/validate_evaluation_dataset.py evaluation-dataset`; it performs no network, subprocess, database, provider, or out-of-root access.

## Testing Strategy

| Layer | What to Test | Approach |
|---|---|---|
| Unit | Valid catalog, canonical hashing, references, counts, language isolation | Import validator as existing CI-guard tests do. |
| Mutation | Every documented failure class and exact reason code | Copy the valid dataset to `tmp_path`, mutate one file/field, then validate; do not duplicate the full corpus. |
| CLI/CI | Fixed root, safe stderr, nonzero failure, Make target order | Subprocess CLI test and Makefile contract assertion; no network/runtime fixtures. |

Mechanically enforced: schema, allowlists/prohibited field names (`answer`, `gold_answer`, `response`, `completion`, image terms), hashes, provenance, links, parity shape, and counts. Reviewer evidence governs semantic bilingual equivalence, whether a claim token could be expanded into a gold answer, and whether content/identifiers plausibly resemble real data; automated checks are deliberately conservative, not claims of perfect detection.

## Threat Matrix

| Boundary | Applicability | Design response / RED tests |
|---|---|---|
| Documentation-like paths | N/A — JSON is data, never classified or executed. | No executable classification test. |
| Git repository selection | N/A — no Git invocation. | No test. |
| Commit state | N/A — no index operations. | No test. |
| Push state | N/A — no remote operations. | No test. |
| PR commands | N/A — no PR automation. | No test. |

## Migration / Rollout

No migration required. The change is additive and CI-only. Roll back by reverting the dataset, validator, tests, and Make target; no durable state exists.

## Risks and Traceability

Proposal risks are mitigated by controlled claim IDs, declared pair identity, and OCR/identifier schemas. Spec requirements map to manifest/hash/reference checks; collection/classification/language checks; scenario/count/outcome checks; contradiction/OCR/safety checks; and validator/CI mutation tests. This preserves `AGENTS.md` safety and synthetic-boundary rules and roadmap Phase 0/Phase 2 ordering. Rejected alternatives: runtime evaluator, YAML dependency, inferred semantic parity, and generated answers.

## Open Questions

- [ ] None; content-level reviewer approval is an implementation review gate, not a design blocker.
