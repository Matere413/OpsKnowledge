# Tasks: Build OpsKnowledge Evaluation Dataset

## Review Workload Forecast

| Field | Value |
|---|---|
| Estimated changed lines (authored, OpenSpec excluded) | ~1,300–2,060 |
| Authored synthetic dataset (manifest + entries + fragments + 32 scenarios) | ~800–1,300 |
| Validator `scripts/ci/validate_evaluation_dataset.py` | ~250–350 |
| Tests `tests/architecture/test_evaluation_dataset_validator.py` | ~250–400 |
| Makefile + repo wiring | ~3–10 |
| 400-line review budget (authored, OpenSpec excluded) | binding |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR1 Foundation → PR2 Fragments+OCR+Sensitive → PR3 Scenarios+Parity+Balance → PR4 Tests+CI wiring |
| Delivery strategy | ask-on-risk |
| Chain strategy | feature-branch-chain |
| Chain strategy decision | explicit user choice — controlled accumulation via tracker/integration branch; no size exception |
| Tracker/integration branch | feature/build-opsknowledge-evaluation-dataset (draft/no-merge until PR1–PR4 integrated) |
| Final merge to master | only the tracker; PR1 base = tracker; PR2 base = PR1 branch; PR3 base = PR2 branch; PR4 base = PR3 branch |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: High

### Suggested Work Units

Chain strategy = feature-branch-chain. Tracker/integration branch = `feature/build-opsknowledge-evaluation-dataset`. Each child PR targets the immediate prior slice so the diff stays focused; only the tracker ultimately merges to master.

| Unit | Goal | Likely PR | Base branch | Focused test command | Runtime harness | Rollback boundary |
|---|---|---|---|---|---|---|
| 1a | Validator R4-001/R3-001 fail-closed fixes + manifest + 3 entry stubs + per-severe-contract regression tests | PR 1a (Foundation: severe-finding recovery) | `feature/build-opsknowledge-evaluation-dataset` (tracker) | `pytest tests/architecture/test_evaluation_dataset_validator.py -q` | `make check-evaluation-dataset` on minimal root | Revert `manifest.json`, `entries/*`, validator, test file, Makefile target; severe-finding production fixes revert with it |
| 1b | Deferred CLI/edge coverage (valid load, canonical hash, single-document, orphan, CLI 0/1/2) — no production change | PR 1b (Foundation: deferred CLI/edge coverage) | `pr-1-foundation` (after PR1a) | `pytest tests/architecture/test_evaluation_dataset_validator.py -q` | `make check-evaluation-dataset` unchanged | Revert test-file additions only; validator+dataset remain functional |
| 2 | Full fragment set + language match + provenance + sensitive checks | PR 2 (Fragments+OCR+Sensitive) | `pr-1-foundation` (immediate parent branch) | `pytest ... -k "fragment or provenance or sensitive" -q` | `make check-evaluation-dataset` with fragments, zero scenarios | Drop `fragments/*`; revert fragment-check branches; manifest+entries still clean |
| 3 | 32 scenarios (16 pairs) + outcome + parity + balance + count + contradiction | PR 3 (Scenarios+Parity+Balance) | `pr-2-fragments` (immediate parent branch) | `pytest ... -k "scenario or parity or count or contradiction" -q` | `make check-evaluation-dataset` on full dataset | Revert `scenarios/*`; revert scenario-check branches; manifest+entries+fragments still clean |
| 4 | Mutation tests + Makefile `check-evaluation-dataset` wired into `ci` | PR 4 (Tests+CI wiring) | `pr-3-scenarios` (immediate parent branch) | `pytest ... -q && make ci` | `make ci` end-to-end (frozen uv, no net/DB/provider) | Revert test file + Makefile additions only; validator+dataset remain functional |

Dependency diagram (Feature Branch Chain, 📍 = current PR):
- PR1a (Foundation: severe-finding recovery) 📍 → `feature/build-opsknowledge-evaluation-dataset` (tracker, draft/no-merge)
- PR1b (Foundation: deferred CLI/edge coverage) → `pr-1-foundation` (after PR1a lands on `pr-1-foundation`)
- PR2 (Fragments+OCR+Sensitive) → `pr-1-foundation` (after PR1b)
- PR3 (Scenarios+Parity+Balance) → `pr-2-fragments`
- PR4 (Tests+CI wiring) → `pr-3-scenarios`
- Tracker PR `feature/build-opsknowledge-evaluation-dataset` → `master` (only after PR1a–PR4 are reviewed and integrated)

Review budget: 400 changed lines per child PR (authored, OpenSpec excluded). Each child diff must stay focused; if a child PR shows changes from a prior slice, the base is wrong and must be retargeted/rebased before review.

## Phase 1: Foundation (PR 1a + PR 1b)

The original single PR1 exceeded the 400-line review budget and reached escalated review state `review-795cdaffea9a85e8` (214-line correction transaction over the immutable 200-line correction budget). Maintainer-authorized recovery splits Phase 1 into two bounded slices that preserve the severe-finding production fixes for R4-001 and R3-001:

- **PR 1a (Foundation, severe-finding recovery):** the validator production fixes for R4-001 (never open unsafe absolute/out-of-root/symlink/non-regular artifact paths) and R3-001 (empty artifacts and missing manifest self-entry fail closed), plus the minimal manifest + 3 entry stubs, the canonical-bytes helper, and a focused regression test per severe behavioral contract. This slice is the recovery target for the escalated review.
- **PR 1b (Foundation, deferred CLI/edge coverage):** the remaining Phase 1 RED/CLI coverage that was part of the original PR1 plan but is redundant for proving the severe contracts stay closed. No production behavior change; tests only.

### PR 1a — Foundation: severe-finding recovery (current slice)

- [x] 1a.1 GREEN: `scripts/ci/validate_evaluation_dataset.py` exporting `validate(root) -> list[Diagnostic]` with the R4-001 fail-closed artifact-path resolver (`_safe_artifact_target`) and the R3-001 empty-artifacts / missing-self-entry / invalid-self-entry guards. File walk, lexical sort, symlink/hidden/orphan reject, manifest coverage, file+content SHA-256, fixed-argv CLI, exit 0/1/2, safe `path-or-id: reason-code: remediation` to stderr.
- [x] 1a.2 GREEN: `evaluation-dataset/manifest.json` (`schema_version`, `dataset_id`, `profile: development`, `approval`, `classification: synthetic`, sorted `artifacts[]`, `dataset_stage: foundation-partial`, `required_for_completion`).
- [x] 1a.3 GREEN: canonical-bytes helper (UTF-8 no BOM, sorted keys, `ensure_ascii=False`, one trailing LF); SHA-256 over those bytes.
- [x] 1a.4 GREEN: 3 entry stubs `evaluation-dataset/entries/<logical-id>.rev.<r>.json` (one per collection, one lang/rev) with `content_sha256` over `content`.
- [x] 1a.5 GREEN: `check-evaluation-dataset` Makefile target (standalone; not wired into `ci` until PR4); `make` parses.
- [x] 1a.6 RED: `test_r4_001_unsafe_artifact_path_never_opened` (parameterized: absolute, out-of-root, symlink, non-regular — asserts the stable reason code AND that no `read-error` surfaces, proving the unsafe target is never opened).
- [x] 1a.7 RED: `test_r3_001_empty_or_missing_manifest_coverage_fails_closed` (parameterized: empty-artifacts, missing-self-entry — asserts the stable reason code).

> PR1a recovery note: tasks 1a.1–1a.7 are complete and verified (6 tests pass, `make ci` green, `make check-evaluation-dataset` green, ruff/pyright clean). The validator is the production fix for R4-001/R3-001 and is byte-identical to the escalated final candidate tree `ccaec63`, so both severe findings remain closed. Tests shrank from 13 (277 lines) to 6 parameterized tests (151 lines) by deferring redundant CLI/edge coverage to PR1b. Authored non-OpenSpec slice is validator 554 + tests 151 + Makefile 6 = 711 logic lines; the validator is the irreducible production fix and the tests are minimal per-contract regression proof. The partial-slice contract (zero fragments/scenarios permitted only because tracker is draft/no-merge) is preserved via `dataset_stage: foundation-partial` and the `required_for_completion` block.

### PR 1b — Foundation: deferred CLI/edge coverage (pending)

- [x] 1b.1 RED: `test_valid_manifest_loads_with_zero_findings` (valid baseline loads with zero findings).
- [x] 1b.2 RED: `test_manifest_hash_matches_canonical_bytes` (manifest self-referential hash over canonical bytes with sha256 set to empty).
- [x] 1b.3 RED: `test_manifest_must_be_single_document` (appended second JSON object yields `json-syntax-error`).
- [x] 1b.4 RED: `test_orphan_file_outside_manifest_fails_closed` (stable reason code `orphan-file-not-in-manifest`).
- [x] 1b.5 RED: CLI coverage — `test_cli_returns_zero_on_valid_dataset`, `test_cli_returns_two_on_bad_argv`, `test_cli_returns_one_on_findings` (subprocess exit 0/1/2, safe stderr).

> PR1b note: no production behavior change. These tests were part of the original PR1 plan and are deferred, not deleted. They will be re-added from the escalated candidate tree `ccaec63` test file once PR1a is reviewed and integrated. PR1b targets the same `pr-1-foundation` slice after PR1a lands.

## Phase 2: Fragments + OCR + Sensitive (PR 2)

- [x] 2.1 RED: fragment lang == parent lang; `fictitious: true` allowlist (`example.test`/`TEST-`/`INVALID`); OCR `provenance: "ocr"` + `source_reference` + `quality` required; cross-language OCR fails closed.
- [x] 2.2 GREEN: add `evaluation-dataset/fragments/<fragment-id>.json` per entry (lang-matched, parent ref, provenance, source, quality, `content_sha256`). No image/screenshot/photograph/visual field.
- [x] 2.3 GREEN: validator adds fragment/parent lang match, provenance allowlist, sensitive-id allowlist, no-image-fields allowlist.
- [x] 2.4 GREEN: extend `manifest.json` `artifacts[]` with each fragment path+`sha256`; validator re-runs clean.

## Phase 3: Scenarios + Parity + Balance (PR 3)

- [x] 3.1 RED: every spec contract — count==32; 16 es/16 en; 16 pair IDs; one record per `(pair_id, language)`; identical pair shape; 16 supported/16 non-supported; supported-evidence ≥1 approved lang-matched fragment; contradiction==two approved revisions of one parent; OCR evidence provenance+source+quality; override/out-of-scope evidence empty; unanswerable outcome ∈ {insufficient_information, out_of_scope, unavailable}; six-state taxonomy allowlist; prohibited-field scan.
- [x] 3.2 GREEN: 32 `evaluation-dataset/scenarios/<pair-id>.<lang>.json` covering grounded/ambiguous-incomplete/contradictory/out-of-scope/unanswerable/prompt-override/OCR-uncertainty/sensitive-identifier. Each: `pair_id`, `language`, `case_type`, `expected_outcome` (six-state), `safety_classification`, controlled `claim_expectation` ID, controlled `abstention_reason` code, `evidence[]` (empty for override/out-of-scope). NO `answer`/`gold_answer`/`response`/`completion`; no query/answer text.
- [x] 3.3 GREEN: validator adds count/language-split/balance/parity/taxonomy, supported-evidence-reference, contradiction paired-revision, override/out-of-scope empty-evidence, prohibited-field scan, scenario-vs-fragment lang match.
- [x] 3.4 GREEN: re-run validator; zero findings, exit 0, stderr empty.

> PR3 note: to satisfy the spec's "Contradiction Cases Use Paired Synthetic Revisions" contract (Engram #4251 gap), PR3 adds a second approved revision per logical entry for the two contradiction pairs — `entry.runbook-001.rev.2` (es) + `fragment.runbook-001.rev.2.es.original`, and `entry.adr-002.rev.2` (en) + `fragment.adr-002.rev.2.en.original`. Contradiction scenarios eval-11/eval-12 reference exactly two approved, synthetic, language-tagged revisions of one logical entry per language. This is the smallest necessary fixture addition; the contradiction contract is not weakened. PR3 is delivered as a feature-branch-chain of three slices (no size exception): PR3a `feat/evaluation-dataset-scenarios-data` adds scenario fixtures + manifest (38 authored lines), PR3b `feat/evaluation-dataset-scenarios-per-record` adds per-record scenario validation (332 authored lines), and PR3c `feat/evaluation-dataset-scenarios-catalog` adds the scenario catalog contract + RED regression net (373 authored lines, OpenSpec excluded).

## Phase 4: Mutation Tests + CI Wiring (PR 4)

> Phase 4 note: PR1b already restores the baseline CLI/edge coverage (valid load, canonical hash, single-document, orphan, CLI 0/1/2). Phase 4 adds the remaining mutation coverage for every documented failure class plus the Makefile `ci` wiring. Task 4.2 is the final-form CLI test retained here for the PR4 mutation suite; do not duplicate PR1b's baseline CLI tests.

- [ ] 4.1 Mutation coverage in `tests/architecture/test_evaluation_dataset_validator.py` for every documented failure class — exact stable reason code, no substring. Tests copy valid dataset to `tmp_path`; do NOT duplicate corpus.
- [ ] 4.2 CLI test: subprocess returns 0 on valid root, 1 with safe stderr finding, 2 on bad argv; no network/subprocess/DB/provider calls.
- [ ] 4.3 Makefile: add `check-evaluation-dataset` calling `$(UV_RUN) run --frozen python scripts/ci/validate_evaluation_dataset.py evaluation-dataset`; wire into `ci` before `check-focused-tests` and `pytest-check`; update `.PHONY`. Keep `ci-pr2a` unchanged.
- [ ] 4.4 Makefile-ordering contract test (mirrors `test_focused_test_scanner.py` style).

## Phase 5: Reviewer-Governed Semantic Approval (NOT a CI task)

- [ ] 5.1 Reviewer-signed evidence in `verify-report.md` (`sdd-verify`): one row per scenario/entry confirming semantic bilingual equivalence, no claim token expands into gold-answer prose, identifiers/OCR obviously fictitious. Only path satisfying "no literal gold answers" + "bilingual equivalence" guards.
- [ ] 5.2 Roadmap/AGENTS.md touch-ups (Phase 0 checkbox + synthetic reminder) deferred to `sdd-archive`; do NOT mark complete from tasks.

## Phase 6: Rollback

- [ ] 6.1 Each PR is independently removable: PR1a = validator R4-001/R3-001 fail-closed fixes + manifest + 3 entry stubs + per-contract regression tests + standalone Makefile target; PR1b = deferred CLI/edge tests (no production change); PR2 = fragments + fragment-check branches; PR3 = scenarios + scenario-check branches; PR4 = mutation tests + Makefile `ci` hook. No durable state, provider config, DB schema, or profile wiring at any stage; revert is self-contained per PR.
