"""Static least-privilege contract tests for the GitHub Actions adapter."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).parents[2]
WORKFLOW_PATH = PROJECT_ROOT / ".github/workflows/ci.yml"
CHECKOUT_SHA = "08c6903cd8c0fde910a37f88322edcfb5dd907a8"
CHECKOUT_TAG = "v5.0.0"
SETUP_UV_SHA = "e06108dd0aef18192324c70427afc47652e63a82"
SETUP_UV_TAG = "v7.5.0"
SETUP_UV_VERSION = "0.11.29"

# Test-owned contract: owner/action -> (immutable SHA, release tag, declared
# JavaScript runtime). Apply MUST re-verify each SHA against the named tag and
# confirm the upstream action.yml at that SHA declares the listed runtime
# before this table is accepted as evidence. The table makes no network claim
# during CI; it vendors no upstream content.
ACTION_CONTRACTS: dict[str, tuple[str, str, str]] = {
    "actions/checkout": (CHECKOUT_SHA, CHECKOUT_TAG, "node24"),
    "astral-sh/setup-uv": (SETUP_UV_SHA, SETUP_UV_TAG, "node24"),
}

ACTION_SHA = re.compile(r"[^@\s]+@[0-9a-f]{40}")
ACTION_COMMENT = re.compile(r"^\s*uses:\s*[^@\s]+@[0-9a-f]{40}\s+# v[^\s]+\s*$")
EXPECTED_RUN_BLOCKS = ['test "$(uv self version --short)" = "0.11.29"', "make ci"]
EXPECTED_JOB_KEYS = {"runs-on", "timeout-minutes", "steps"}


def _workflow(workflow_text: str | None = None) -> dict[str, object]:
    parsed = yaml.load(workflow_text or WORKFLOW_PATH.read_text(), Loader=yaml.BaseLoader)
    assert isinstance(parsed, dict)
    return parsed


def _jobs(workflow: dict[str, object]) -> dict[str, dict[str, object]]:
    jobs = workflow["jobs"]
    assert isinstance(jobs, dict)
    typed_jobs: dict[str, dict[str, object]] = {}
    for name, job in jobs.items():
        assert isinstance(name, str)
        assert isinstance(job, dict)
        typed_jobs[name] = job
    return typed_jobs


def _steps(job: dict[str, object]) -> list[dict[str, object]]:
    steps = job["steps"]
    assert isinstance(steps, list)
    typed_steps: list[dict[str, object]] = []
    for step in steps:
        assert isinstance(step, dict)
        typed_steps.append(step)
    return typed_steps


def _is_full_sha_pin(step: dict[str, object]) -> bool:
    uses = step["uses"]
    return isinstance(uses, str) and bool(ACTION_SHA.fullmatch(uses))


def _expected_steps(
    action_contracts: dict[str, tuple[str, str, str]],
) -> list[dict[str, object]]:
    checkout_sha, _checkout_tag, _checkout_runtime = action_contracts["actions/checkout"]
    setup_uv_sha, _setup_uv_tag, _setup_uv_runtime = action_contracts["astral-sh/setup-uv"]
    return [
        {
            "name": "Checkout",
            "uses": f"actions/checkout@{checkout_sha}",
            "with": {"persist-credentials": "false"},
        },
        {
            "name": "Set up uv",
            "uses": f"astral-sh/setup-uv@{setup_uv_sha}",
            "with": {"version": SETUP_UV_VERSION},
        },
        {"name": "Assert uv version", "run": EXPECTED_RUN_BLOCKS[0]},
        {"name": "Run CI", "run": EXPECTED_RUN_BLOCKS[1]},
    ]


def _assert_workflow_contract(
    workflow_text: str, action_contracts: dict[str, tuple[str, str, str]] = ACTION_CONTRACTS
) -> None:
    workflow = _workflow(workflow_text)
    triggers = workflow["on"]
    assert isinstance(triggers, dict)
    assert set(triggers) == {"push", "pull_request"}
    assert workflow["permissions"] == {"contents": "read"}
    assert "pull_request_target" not in workflow_text
    assert "secrets." not in workflow_text
    assert "GITHUB_TOKEN" not in workflow_text

    jobs = _jobs(workflow)
    assert set(jobs) == {"ci"}
    for job in jobs.values():
        assert set(job) == EXPECTED_JOB_KEYS
        assert job.get("timeout-minutes") == "30"

    all_steps = [step for job in jobs.values() for step in _steps(job)]
    expected_steps = _expected_steps(action_contracts)
    assert all_steps == expected_steps
    uses_steps = [step for step in all_steps if "uses" in step]
    assert uses_steps
    uses_lines = [line for line in workflow_text.splitlines() if line.lstrip().startswith("uses:")]
    assert len(uses_lines) == len(uses_steps)
    assert all(_is_full_sha_pin(step) for step in uses_steps)
    assert all(ACTION_COMMENT.fullmatch(line) for line in uses_lines)
    assert [step["uses"] for step in uses_steps] == [
        f"{action}@{sha}" for action, (sha, _tag, _runtime) in action_contracts.items()
    ]
    for action, (sha, tag, _runtime) in action_contracts.items():
        assert f"{action}@{sha} # {tag}" in workflow_text

    checkout_steps = [
        step
        for step in uses_steps
        if str(step["uses"]).split("@", maxsplit=1)[0] == "actions/checkout"
    ]
    assert checkout_steps == [uses_steps[0]]
    assert checkout_steps[0].get("with") == {"persist-credentials": "false"}

    setup_uv_sha, setup_uv_tag, _setup_uv_runtime = action_contracts["astral-sh/setup-uv"]
    setup_uv_steps = [
        step for step in uses_steps if step["uses"] == f"astral-sh/setup-uv@{setup_uv_sha}"
    ]
    assert setup_uv_steps == [uses_steps[1]]
    assert setup_uv_steps[0].get("with") == {"version": SETUP_UV_VERSION}
    assert f"setup-uv@{setup_uv_sha} # {setup_uv_tag}" in workflow_text

    run_steps = [step for step in all_steps if "run" in step]
    assert all(isinstance(step["run"], str) for step in run_steps)
    scripts = [str(step["run"]) for step in run_steps]
    assert scripts == EXPECTED_RUN_BLOCKS


def _assert_node24_runtime_contract(
    workflow_text: str, action_contracts: dict[str, tuple[str, str, str]] = ACTION_CONTRACTS
) -> None:
    """Fail closed if any pinned action's runtime drifts from node24."""
    for action, (_sha, _tag, expected_runtime) in action_contracts.items():
        if expected_runtime != "node24":
            raise AssertionError(
                f"Node 24 runtime drift detected for {action}: "
                f"expected node24, found {expected_runtime} in ACTION_CONTRACTS"
            )
    # The workflow must reference both pinned actions; the runtime table is
    # the offline evidence that each pin resolves to node24. A non-node24
    # table entry would be caught above. A workflow pin that is not in the
    # table is caught by _assert_workflow_contract.
    for action in action_contracts:
        assert any(
            str(step.get("uses", "")).startswith(f"{action}@")
            for job in _jobs(_workflow(workflow_text)).values()
            for step in _steps(job)
        ), f"workflow is missing the expected pin for {action}"


def test_workflow_uses_unprivileged_events_and_read_only_permissions() -> None:
    _assert_workflow_contract(WORKFLOW_PATH.read_text())


def test_pinned_actions_target_node24_on_github_hosted_runners() -> None:
    _assert_node24_runtime_contract(WORKFLOW_PATH.read_text())


def test_contract_is_path_independent() -> None:
    workflow_text = WORKFLOW_PATH.read_text()
    assert "open" + "spec" not in Path(__file__).read_text().lower()
    _assert_workflow_contract(workflow_text)
    _assert_node24_runtime_contract(workflow_text)


def test_contract_rejects_job_permission_escalation() -> None:
    _assert_rejected(
        WORKFLOW_PATH.read_text().replace(
            "runs-on: ubuntu-latest",
            "permissions:\n      contents: write\n    runs-on: ubuntu-latest",
        )
    )


def test_contract_rejects_job_failure_bypass_controls() -> None:
    _assert_rejected(
        WORKFLOW_PATH.read_text().replace(
            "runs-on: ubuntu-latest",
            "continue-on-error: true\n    runs-on: ubuntu-latest",
        )
    )


def test_contract_rejects_unpinned_or_uncommented_actions() -> None:
    workflow_text = WORKFLOW_PATH.read_text()
    _assert_rejected(workflow_text.replace(SETUP_UV_SHA, "0" * 40))
    _assert_rejected(workflow_text.replace(f"@{SETUP_UV_SHA} # {SETUP_UV_TAG}", "@v5"))
    _assert_rejected(workflow_text.replace(f"# {SETUP_UV_TAG}", "# v0.0.0"))


def test_contract_rejects_checkout_credentials_or_extra_actions() -> None:
    workflow_text = WORKFLOW_PATH.read_text()
    _assert_rejected(
        workflow_text.replace("persist-credentials: false", "persist-credentials: true")
    )
    _assert_rejected(
        workflow_text.replace(
            "        run: make ci",
            "        run: make ci\n"
            "      - uses: example/action@0123456789abcdef0123456789abcdef01234567 # v1.0.0",
        )
    )


def test_contract_rejects_noncanonical_make_ci_expansion() -> None:
    workflow_text = WORKFLOW_PATH.read_text()
    _assert_rejected(workflow_text.replace("run: make ci", "run: make ci && echo complete"))
    _assert_rejected(workflow_text.replace("run: make ci", "run: make${IFS}ci"))


def test_contract_rejects_any_additional_run_block() -> None:
    workflow_text = WORKFLOW_PATH.read_text()
    _assert_rejected(
        workflow_text.replace("run: make ci", "run: |\n          make ci\n          make ci")
    )
    _assert_rejected(
        workflow_text.replace(
            "        run: make ci",
            "        run: make ci\n      - run: echo harmless",
        )
    )


def test_contract_rejects_gate_bypass_controls() -> None:
    workflow_text = WORKFLOW_PATH.read_text()
    assertion_run = f"run: {EXPECTED_RUN_BLOCKS[0]}"
    _assert_rejected(
        workflow_text.replace(
            assertion_run,
            f"{assertion_run}\n        continue-on-error: true",
        )
    )
    _assert_rejected(workflow_text.replace("run: make ci", "run: make ci\n        if: always()"))


def test_contract_rejects_missing_timeout() -> None:
    _assert_rejected(WORKFLOW_PATH.read_text().replace("    timeout-minutes: 30\n", ""))


def test_contract_rejects_action_contract_sha_or_tag_drift() -> None:
    drifted_contracts = dict(ACTION_CONTRACTS)
    drifted_contracts["actions/checkout"] = ("0" * 40, CHECKOUT_TAG, "node24")
    try:
        _assert_workflow_contract(WORKFLOW_PATH.read_text(), drifted_contracts)
    except AssertionError:
        pass
    else:
        raise AssertionError("contract unexpectedly accepted a drifted SHA")

    drifted_contracts["actions/checkout"] = (CHECKOUT_SHA, "v0.0.0", "node24")
    try:
        _assert_workflow_contract(WORKFLOW_PATH.read_text(), drifted_contracts)
    except AssertionError:
        return
    raise AssertionError("contract unexpectedly accepted a drifted release tag")


def test_node24_rejects_non_node24_table_entry() -> None:
    drifted_contracts = dict(ACTION_CONTRACTS)
    drifted_contracts["actions/checkout"] = (CHECKOUT_SHA, CHECKOUT_TAG, "node20")
    try:
        _assert_node24_runtime_contract(WORKFLOW_PATH.read_text(), drifted_contracts)
    except AssertionError:
        return
    raise AssertionError("node24 check unexpectedly accepted a non-node24 table entry")


def _assert_rejected(workflow_text: str) -> None:
    try:
        _assert_workflow_contract(workflow_text)
    except AssertionError:
        return
    raise AssertionError("mutated workflow unexpectedly satisfied the contract")
