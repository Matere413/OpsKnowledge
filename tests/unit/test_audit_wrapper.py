from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Protocol

import pytest

AUDIT_PATH = Path(__file__).parents[2] / "scripts/ci/run_vulnerability_audit.py"
UV_RUNNER_PATH = Path(__file__).parents[2] / "scripts/ci/run_uv_command.py"
OFFLINE_ERROR = OSError("offline")
TIMEOUT_ERROR = subprocess.TimeoutExpired("pip-audit", 1)


class _Captured(Protocol):
    err: str


class _CaptureFixture(Protocol):
    def readouterr(self) -> _Captured: ...


def _audit() -> ModuleType:
    spec = importlib.util.spec_from_file_location("audit_wrapper", AUDIT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("returncode", "expected"),
    [(0, "success"), (1, "vulnerability_finding"), (2, "vulnerability_tool_failure")],
)
def test_classifies_one_completed_call(
    monkeypatch: pytest.MonkeyPatch, returncode: int, expected: str
) -> None:
    module = _audit()
    monkeypatch.delenv("UV", raising=False)
    calls: list[list[str]] = []

    def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        return subprocess.CompletedProcess(command, returncode, "stdout", "stderr")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    result = module.run_audit()
    assert (result.classification, result.exit_code, result.output) == (
        expected,
        returncode,
        "stdoutstderr",
    )
    assert calls == [["uv", "run", "--frozen", "pip-audit"]]


@pytest.mark.parametrize("error", [OFFLINE_ERROR, TIMEOUT_ERROR])
def test_unavailable_service_fails_closed(
    monkeypatch: pytest.MonkeyPatch, error: Exception
) -> None:
    module = _audit()
    monkeypatch.setattr(
        module.subprocess, "run", lambda *_args, **_kwargs: (_ for _ in ()).throw(error)
    )
    assert module.run_audit().classification == "vulnerability_service_unavailable"


def test_unchanged_rerun_can_recover_without_internal_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _audit()
    outcomes = [
        subprocess.CompletedProcess(["uv"], 1, "finding", ""),
        subprocess.CompletedProcess(["uv"], 0, "", ""),
    ]
    monkeypatch.setattr(module.subprocess, "run", lambda *_args, **_kwargs: outcomes.pop(0))
    assert module.run_audit().classification == "vulnerability_finding"
    assert module.run_audit().classification == "success"


def test_honors_make_configured_uv_for_nested_invocation(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _audit()
    calls: list[list[str]] = []
    monkeypatch.setenv("UV_EXECUTABLE", "/tmp/pinned-uv")
    monkeypatch.setattr(
        module.subprocess,
        "run",
        lambda command, **_kwargs: (
            calls.append(command) or subprocess.CompletedProcess(command, 0, "ok", "")
        ),
    )
    assert module.run_audit() == module.AuditResult("success", "ok", 0)
    assert calls == [["/tmp/pinned-uv", "run", "--frozen", "pip-audit"]]


def test_cli_preserves_output_and_exit_code(
    monkeypatch: pytest.MonkeyPatch, capsys: _CaptureFixture
) -> None:
    module = _audit()
    monkeypatch.setattr(
        module, "run_audit", lambda: module.AuditResult("vulnerability_finding", "finding\n", 1)
    )
    assert module.main() == 1
    assert capsys.readouterr().err == "finding\naudit classification: vulnerability_finding\n"


def test_uv_runner_treats_malicious_value_as_one_executable_path(tmp_path: Path) -> None:
    sentinel = tmp_path / "injected"
    result = subprocess.run(
        [sys.executable, UV_RUNNER_PATH, "--version"],
        capture_output=True,
        text=True,
        check=False,
        env={"UV": f"not-a-command; touch {sentinel}"},
    )
    assert result.returncode == 127
    assert not sentinel.exists()


def test_uv_runner_accepts_absolute_executable_path(tmp_path: Path) -> None:
    executable = tmp_path / "uv"
    executable.write_text("#!/bin/sh\nexit 7\n")
    executable.chmod(0o755)
    result = subprocess.run(
        [sys.executable, UV_RUNNER_PATH, "--version"],
        capture_output=True,
        text=True,
        check=False,
        env={"UV": str(executable)},
    )
    assert result.returncode == 7
