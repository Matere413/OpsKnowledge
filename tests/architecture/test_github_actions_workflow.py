"""Static least-privilege contract tests for the GitHub Actions adapter."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).parents[2]
WORKFLOW_PATH = PROJECT_ROOT / ".github/workflows/ci.yml"
CHECKOUT_SHA = "11bd71901bbe5b1630ceea73d27597364c9af683"
SETUP_UV_SHA = "d4b2f3b6ecc6e67c4457f6d3e41ec42d3d0fcb86"
SETUP_UV_VERSION = "0.11.29"
ACTION_SHA = re.compile(r"[^@\s]+@[0-9a-f]{40}")
ACTION_COMMENT = re.compile(r"^\s*uses:\s*[^@\s]+@[0-9a-f]{40}\s+# v[^\s]+\s*$")
EXPECTED_ACTIONS = [
    f"actions/checkout@{CHECKOUT_SHA}",
    f"astral-sh/setup-uv@{SETUP_UV_SHA}",
]
EXPECTED_RUN_BLOCKS = ['test "$(uv self version --short)" = "0.11.29"', "make ci"]
EXPECTED_STEPS: list[dict[str, object]] = [
    {
        "name": "Checkout",
        "uses": f"actions/checkout@{CHECKOUT_SHA}",
        "with": {"persist-credentials": "false"},
    },
    {
        "name": "Set up uv",
        "uses": f"astral-sh/setup-uv@{SETUP_UV_SHA}",
        "with": {"version": SETUP_UV_VERSION},
    },
    {"name": "Assert uv version", "run": EXPECTED_RUN_BLOCKS[0]},
    {"name": "Run CI", "run": EXPECTED_RUN_BLOCKS[1]},
]
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


def _assert_workflow_contract(workflow_text: str) -> None:
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
    assert all_steps == EXPECTED_STEPS
    uses_steps = [step for step in all_steps if "uses" in step]
    assert uses_steps
    uses_lines = [line for line in workflow_text.splitlines() if line.lstrip().startswith("uses:")]
    assert len(uses_lines) == len(uses_steps)
    assert all(_is_full_sha_pin(step) for step in uses_steps)
    assert all(ACTION_COMMENT.fullmatch(line) for line in uses_lines)
    assert [step["uses"] for step in uses_steps] == EXPECTED_ACTIONS

    checkout_steps = [
        step
        for step in uses_steps
        if str(step["uses"]).split("@", maxsplit=1)[0] == "actions/checkout"
    ]
    assert checkout_steps == [uses_steps[0]]
    assert checkout_steps[0].get("with") == {"persist-credentials": "false"}

    setup_uv_steps = [
        step for step in uses_steps if step["uses"] == f"astral-sh/setup-uv@{SETUP_UV_SHA}"
    ]
    assert setup_uv_steps == [uses_steps[1]]
    assert setup_uv_steps[0].get("with") == {"version": SETUP_UV_VERSION}
    assert f"setup-uv@{SETUP_UV_SHA} # v5.4.2" in workflow_text

    run_steps = [step for step in all_steps if "run" in step]
    assert all(isinstance(step["run"], str) for step in run_steps)
    scripts = [str(step["run"]) for step in run_steps]
    assert scripts == EXPECTED_RUN_BLOCKS


def test_workflow_uses_unprivileged_events_and_read_only_permissions() -> None:
    _assert_workflow_contract(WORKFLOW_PATH.read_text())


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
    _assert_rejected(workflow_text.replace(f"@{SETUP_UV_SHA} # v5.4.2", "@v5"))
    _assert_rejected(workflow_text.replace(" # v5.4.2", ""))


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


def _assert_rejected(workflow_text: str) -> None:
    try:
        _assert_workflow_contract(workflow_text)
    except AssertionError:
        return
    raise AssertionError("mutated workflow unexpectedly satisfied the contract")
