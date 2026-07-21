## Exploration: refresh-github-actions-node-runtime-pins

### Current State

The repository has a single thin, least-privilege GitHub Actions workflow at `.github/workflows/ci.yml` that runs only `make ci`. It pins two third-party Actions to full commit SHAs with release-version comments and asserts the exact `uv` version before invoking the canonical local gate.

| Step | Pinned reference | Source |
|---|---|---|
| `Checkout` | `actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2` (with `persist-credentials: false`) | `.github/workflows/ci.yml` line 16 |
| `Set up uv` | `astral-sh/setup-uv@d4b2f3b6ecc6e67c4457f6d3e41ec42d3d0fcb86 # v5.4.2` with `version: "0.11.29"` | `.github/workflows/ci.yml` line 20 |
| `Assert uv version` | `test "$(uv self version --short)" = "0.11.29"` | `.github/workflows/ci.yml` line 24 |
| `Run CI` | `make ci` | `.github/workflows/ci.yml` line 25 |

The exact SHAs are also reproduced and tested by `tests/architecture/test_github_actions_workflow.py` (module-level `CHECKOUT_SHA`, `SETUP_UV_SHA`, `ACTION_SHA` regex, `ACTION_COMMENT` regex, `EXPECTED_ACTIONS`, `EXPECTED_STEPS`, and an in-text assertion that `setup-uv@<SHA> # v5.4.2` is present). The same SHA and version are quoted verbatim by the canonical test-harness specification at `openspec/specs/test-harness/spec.md` line 37 (Requirement: "Deterministic CI Runner Bootstrap"), and the change is governed jointly by `docs/contributing/ci.md` lines 43–50, which states the workflow and its contract test "are governed by `tests/architecture/test_github_actions_workflow.py`. Update the workflow and that contract together when an approved pin-refresh change requires it." `RAG_ROADMAP.md` (Pre-Phase 1 CI hardening, line 117) lists `refresh-github-actions-node-runtime-pins` as the open candidate change and explicitly notes (line 555) that "Node runtime pins also belongs in this pre-Phase-1 CI-hardening boundary and remains independent for review and rollback."

The "runtime-pin warning" the roadmap and `ci.md` refer to is the GitHub-hosted runner JavaScript runtime: Node 20 reached end-of-life in April 2026 and is scheduled to be completely removed from hosted runners on **2026-09-16**. The currently pinned `actions/checkout@v4.2.2` and `astral-sh/setup-uv@v5.4.2` are both Node 20 era; GitHub surfaces an "Node.js 20 deprecated" warning in workflow logs and a future removal will hard-fail the runner. The fix is to advance both pins to versions that target the Node 24 runtime while preserving the workflow's least-privilege shape.

Today the same SHA pair is referenced from three coupled files (workflow, contract test, canonical test-harness spec) plus a fourth file that gives governance (`docs/contributing/ci.md`); a safe refresh must update all of them in lockstep and re-verify the new SHAs against upstream `git ls-remote`, exactly as the bootstrap change did in its `apply-progress.md` (line 10).

### Affected Areas

- `.github/workflows/ci.yml` — replaces the two SHA pins (and their release comments) and may need to update `setup-uv` `with:` keys if a new major changes accepted inputs.
- `tests/architecture/test_github_actions_workflow.py` — module constants `CHECKOUT_SHA` / `SETUP_UV_SHA`, `EXPECTED_ACTIONS` / `EXPECTED_STEPS`, the literal `setup-uv@<SHA> # v5.4.2` assertion, and the test that rejects `@v5` un-pinned shapes; the `_is_full_sha_pin` / `ACTION_COMMENT` regexes must still match any new pin.
- `openspec/specs/test-harness/spec.md` (Requirement "Deterministic CI Runner Bootstrap", line 37) — quotes the exact SHA and tag in the spec text; the delta for this change updates the same line in the spec snapshot.
- `docs/contributing/ci.md` (lines 43–50) — already pre-names the change and prescribes the workflow + contract update pattern; no rewrite required, only a re-anchor against the new pin (if a comment reference is added).
- `openspec/changes/refresh-github-actions-node-runtime-pins/{proposal,spec,design,tasks,exploration,verify-report}.md` and `openspec/changes/refresh-github-actions-node-runtime-pins/specs/test-harness/spec.md` — the new SDD artifact set, mirroring the layout used by the archived `harden-focused-test-scanner-import-aliases` change.
- `RAG_ROADMAP.md` Pre-Phase 1 list (line 117) and completion notes block — flipped to `[x]` and a brief completion note appended by the archive step, not by exploration.
- `Makefile`, `pyproject.toml`, `uv.lock`, `governance/direct-dependencies.yaml`, `scripts/ci/*` — explicitly unaffected. The refresh touches only the runner-side JavaScript runtime; the Python pin (`uv 0.11.29`) and every other contract are preserved.

### Approaches

1. **Bounded SHA bump to the current Node 24–era pins** (recommended) — pick the lowest-risk `actions/checkout` and `astral-sh/setup-uv` tags that explicitly target the Node 24 runtime, resolve their SHAs with `git ls-remote`, replace the two `uses:` lines and their comments, update the `CHECKOUT_SHA` / `SETUP_UV_SHA` constants and the `setup-uv@<SHA> # v<tag>` text assertion in the contract test, and amend the canonical test-harness spec to quote the new SHA and tag.
   - Pros: smallest possible diff; preserves the existing least-privilege shape, `persist-credentials: false`, exact `uv` assertion, and `make ci` step; no changes to the Makefile, dependency manifests, lockfile, governance record, or contract test grammar (other than the constants). Independently reversible by re-pinning prior SHAs. The roadmap already calls this a single bounded pre-Phase-1 change.
   - Cons: must pick a target tag whose `setup-uv` "known checksums" still include `uv 0.11.29`, otherwise the exact-version assertion can break in CI even though the local gate still passes; requires a careful re-verification step (`git ls-remote` for both tags) and a real `make ci` run before merge.
   - Effort: Low

2. **Jump to the latest published major (`actions/checkout@v7.0.0`, `astral-sh/setup-uv@v8.x`)** — adopt the newest published Node 24 majors even if they include non-runtime breaking changes.
   - Pros: maximum forward window before the next runtime cliff; pulls in upstream hardening (for example `actions/checkout` v7 blocks checking out fork PRs in `pull_request_target`/`workflow_run`, which the contract test currently forbids anyway).
   - Cons: `setup-uv` v8.x's "immutable release" model and v8.3.x "known checksums for 0.11.28" notes suggest the embedded checksum table may not yet include `uv 0.11.29`; a major-version bump also broadens the review surface to upstream behavior changes that are out of scope for a CI-pin refresh. Higher risk of accidentally needing to bump the `uv` pin or adjust the Makefile. The roadmap's "Node runtime pins" framing favors the minimum viable bump.
   - Effort: Medium

3. **Force the runner Node 24 via `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24` and leave the pins** — keep `actions/checkout@v4.2.2` and `astral-sh/setup-uv@v5.4.2` and silence the warning through an environment variable.
   - Pros: zero SHA churn; the workflow diff shrinks to one environment line.
   - Cons: documented as a partial fix only; the warning can still surface from transitive metadata, and any future Node 24 removal of `actions/checkout@v4`/`setup-uv@v5` would still break CI. Also contradicts the change name and the contract test that asserts the exact SHA-tag form. The roadmap names this change as a pin refresh, not an env-only mitigation.
   - Effort: Low

### Recommendation

Use Approach 1: advance to the lowest published `actions/checkout` and `astral-sh/setup-uv` tags that explicitly target the Node 24 runtime and that the maintainers have had time to stabilize. Resolve both SHAs with `git ls-remote`, update `.github/workflows/ci.yml`, `tests/architecture/test_github_actions_workflow.py`, and the `Deterministic CI Runner Bootstrap` requirement in `openspec/specs/test-harness/spec.md` in the same bounded change. Do not modify the Makefile, the Python `uv 0.11.29` pin, `pyproject.toml`, `uv.lock`, `governance/direct-dependencies.yaml`, or any `scripts/ci/*` file. The change is independently reversible, fits the 400-line session review budget (forecast: workflow + contract test + spec line updates = a few dozen changed lines, well under budget), and stays narrowly aligned with the pre-Phase-1 CI-hardening framing already written into `RAG_ROADMAP.md` and `docs/contributing/ci.md`.

Verification must reproduce the bootstrap evidence pattern from `apply-progress.md` (line 10): `git ls-remote https://github.com/actions/checkout.git refs/tags/<tag>` and the equivalent for `astral-sh/setup-uv`, the focused architecture test module (`uv run --frozen pytest tests/architecture/test_github_actions_workflow.py`), and the canonical `make ci` from a clean `uv` 0.11.29 environment. The `refresh-github-actions-node-runtime-pins` artifact set should follow the `harden-focused-test-scanner-import-aliases` shape (proposal, spec delta, design, tasks, verify-report) with exploration already captured here, and the spec delta should add an explicit Node-runtime requirement while leaving the rest of the test-harness spec intact.

### Risks

- **Mismatched `setup-uv` checksum coverage.** If the chosen `setup-uv` tag bundles a known-checksums table that does not include `uv 0.11.29`, the workflow's exact `uv self version --short` assertion or the local `make ci` `check-uv-version` stage can still pass (the local gate only requires the binary to be installed) but the runner's behavior diverges from the documented contract. The selected `setup-uv` tag must be confirmed to support `uv 0.11.29` before being pinned.
- **Major-version behavioral drift.** `actions/checkout` v7 changed fork-PR semantics for `pull_request_target`/`workflow_run`; even though the current contract test forbids both triggers, jumping too far in one step widens the implicit review surface. The proposed Approach 1 keeps the bump small and explicitly Node-runtime driven; Approach 2 should be rejected unless re-validation proves the major bump is also required.
- **Coupled-file drift.** Three sources of truth quote the SHA: the workflow, the contract test, and `openspec/specs/test-harness/spec.md` line 37. A change that updates only one or two of them will fail the contract test or break the spec-vs-implementation contract. Apply must update all three in one bounded transaction.
- **Supersession hazard for the test-harness spec.** The "Deterministic CI Runner Bootstrap" requirement is the canonical test-harness contract; an errant rewrite of surrounding language would silently change unrelated guarantees. The spec delta MUST be a minimal in-place edit to the SHA/tag plus a new ADDED requirement for the Node runtime, not a rewrite of the requirement body.
- **Roadmap and CI doc drift.** `RAG_ROADMAP.md` (line 117, line 555) and `docs/contributing/ci.md` (lines 43–50) name this change. The exploration does not touch them, but the eventual archive step must flip the roadmap checkbox and add a completion note; the `AGENTS.md` rule added in the current working tree ("Roadmap completion tracking") requires the archived SDD report and successful verification evidence before the checkbox is flipped. Failing to do so in the archive step is the most likely follow-on defect, not an exploration defect.
- **Pre-Phase-1 sequencing.** The roadmap states the scanner hardening is required before the next implementation PR, while the Actions pin refresh is "independently reviewable and reversible" and remains separate. This change MUST NOT touch `scripts/ci/check_focused_tests.py` or the focused-test scanner tests; any temptation to fold them in must be rejected.
- **Working-tree preservation.** The current working tree contains intentional edits in `AGENTS.md` (Roadmap completion tracking rule) and `RAG_ROADMAP.md` (marking the scanner change complete, completion note, and pre-Phase-1 framing). This change MUST NOT modify those edits, and the eventual PR must keep them as separate, reviewable commits.

### Ready for Proposal

Yes. The change name, scope, affected files, recommended approach, and verification path are sufficiently clear for `sdd-propose`. The proposal must:

- Limit scope to the two Actions pins and their three coupled references.
- Decide the exact target tag for `actions/checkout` and `astral-sh/setup-uv` (Approach 1) and document the upstream `git ls-remote` evidence.
- Keep `uv 0.11.29` exact, the Makefile, the contract-test grammar, the dependency manifests, the lockfile, and the governance record unchanged.
- Reserve chained PRs behind the `ask-always` strategy (the user preflight mandates it); the forecast is well under the 400-line session budget, so a single PR is likely, but the proposal should still answer the chained-PR question explicitly.
- Honor the pre-Phase-1 boundary: no scanner, governance, manifest, lockfile, or application code changes.

The orchestrator should pass this exploration, the recommended approach, the `uv 0.11.29` checksum-coverage risk, and the three-coupled-files warning to `sdd-propose`; the user is the final authority on the exact target tags before the spec delta is written.
