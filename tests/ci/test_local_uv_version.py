"""CI recipe tests: uv version assertion and ordered fail-fast.

Controlled fake executables + invocation-log prove: exact success log;
trailing token; ``(build)`` suffix; multiline; mismatch; unavailable;
same-named ``ci-pr2a`` file still runs; exact prefix log on failure; ci
keeps PR2A independent while ci reaches the PR3 audit boundary.
"""

from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

import pytest

if TYPE_CHECKING:
    from collections.abc import Sequence

EXPECTED_UV_VERSION = "0.11.29"
MISMATCH_LINE1 = "ERROR: uv version mismatch; expected 0.11.29, found {actual}."
MISMATCH_LINE2 = "Remediation: install uv 0.11.29 and rerun make ci."
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

S_UV_OK = "=== uv version OK ==="
S_SYNC_OK = "=== frozen sync OK ==="
S_RUFF_CHECK_OK = "=== ruff check OK ==="
S_RUFF_FORMAT_OK = "=== ruff format OK ==="
S_PYRIGHT_OK = "=== pyright OK ==="
S_PYTEST_OK = "=== pytest OK ==="
S_FOCUSED_OK = "=== focused-test guard OK ==="
S_CI_PR2A_DONE = "=== ci-pr2a complete"
PR2A_SUCCESS_STAGES = [
    S_UV_OK,
    S_SYNC_OK,
    S_RUFF_CHECK_OK,
    S_RUFF_FORMAT_OK,
    S_PYRIGHT_OK,
    S_PYTEST_OK,
    S_CI_PR2A_DONE,
]
FAKE_TOOL_NAMES = ("ruff", "pyright", "pytest")

# Exact fake invocation log on a full PR2A success run (single source of truth).
# Trailing spaces from empty $* are significant.
EXPECTED_PR2A_LOG = [
    "uv self version --short",
    "uv sync --frozen --extra dev",
    "uv run --frozen ruff check .",
    "ruff check .",
    "uv run --frozen ruff format --check .",
    "ruff format --check .",
    "uv run --frozen pyright",
    "pyright ",
    "uv run --frozen pytest",
    "pytest ",
]

_FAKE_UV = """\
#!/bin/sh
LOG="$(dirname "$0")/../invocations.log"
echo "uv $*" >> "$LOG"
if [ "$1" = "self" ] && [ "$2" = "version" ] && [ "$3" = "--short" ]; then
    printf '%s\\n' '{version}'
    exit {exit_code}
fi
if [ "$1" = "run" ] && [ "$2" = "--frozen" ]; then
    tool="$3"; shift 3; exec "$tool" "$@"
fi
exit 0
"""


class _Maker(Protocol):
    def __call__(self, d: Path) -> Path: ...


def _write_fake(bin_dir: Path, name: str, body: str) -> Path:
    path = bin_dir / name
    path.write_text(body)
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return path


def _fake_uv(d: Path, version: str, *, exit_code: int = 0) -> Path:
    return _write_fake(d, "uv", _FAKE_UV.format(version=version, exit_code=exit_code))


def _fake_uv_raw(d: Path, version_body: str) -> Path:
    body = (
        '#!/bin/sh\nif [ "$1" = "self" ] && [ "$2" = "version" ] '
        '&& [ "$3" = "--short" ]; then\n'
        f"printf '%s\\n' '{version_body}'\nexit 0\nfi\nexit 0\n"
    )
    return _write_fake(d, "uv", body)


def _fake_tool(d: Path, name: str, *, fail: bool = False) -> Path:
    log_line = f'echo "{name} $*" >> "$LOG"'
    body = f'#!/bin/sh\nLOG="$(dirname "$0")/../invocations.log"\n{log_line}\n'
    body += f'echo "{name}: simulated failure" >&2\nexit 1\n' if fail else "exit 0\n"
    return _write_fake(d, name, body)


def _run_make(
    target: str,
    *,
    env: dict[str, str] | None = None,
    timeout: int = 60,
) -> subprocess.CompletedProcess[str]:
    run_env = dict(os.environ)
    if env:
        run_env.update(env)
    return subprocess.run(
        ["make", target],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
        env=run_env,
    )


def _run_with_fakes(
    target: str,
    tmp_path: Path,
    *,
    fake_uv_body: str | None = None,
    failing_tools: Sequence[str] = (),
    timeout: int = 60,
) -> tuple[subprocess.CompletedProcess[str], Path]:
    """Run ``make <target>`` with controlled fake stage tools + invocation log."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(parents=True)
    log = tmp_path / "invocations.log"
    log.touch()
    if fake_uv_body is not None:
        _write_fake(bin_dir, "uv", fake_uv_body)
    else:
        _fake_uv(bin_dir, EXPECTED_UV_VERSION)
    for name in FAKE_TOOL_NAMES:
        _fake_tool(bin_dir, name, fail=name in failing_tools)
    env = {"UV": str(bin_dir / "uv"), "PATH": f"{bin_dir}:{os.environ.get('PATH', '')}"}
    return _run_make(target, env=env, timeout=timeout), log


def _invocations(log: Path) -> list[str]:
    if not log.exists():
        return []
    return [line for line in log.read_text().splitlines() if line]


def _check_uv(maker: _Maker, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(parents=True)
    maker(bin_dir)
    return _run_make("check-uv-version", env={"UV": str(bin_dir / "uv")})


def _fake_trailing_version(bin_dir: Path) -> None:
    _fake_uv(bin_dir, "0.11.29 extra")


def _fake_build_version(bin_dir: Path) -> None:
    _fake_uv(bin_dir, "0.11.29 (build)")


def _fake_mismatched_version(bin_dir: Path) -> None:
    _fake_uv(bin_dir, "0.11.30")


@pytest.mark.parametrize(
    ("actual", "maker"),
    [
        ("0.11.29 extra", _fake_trailing_version),
        ("0.11.29 (build)", _fake_build_version),
        ("0.11.30", _fake_mismatched_version),
    ],
    ids=["trailing-token", "build-suffix", "mismatch"],
)
def test_rejected_outputs(tmp_path: Path, actual: str, maker: _Maker) -> None:
    result = _check_uv(maker, tmp_path)
    assert result.returncode != 0
    assert MISMATCH_LINE1.format(actual=actual) in result.stdout
    assert MISMATCH_LINE2 in result.stdout


def test_exact_version_output_passes(tmp_path: Path) -> None:
    result = _check_uv(lambda d: _fake_uv(d, EXPECTED_UV_VERSION), tmp_path)
    assert result.returncode == 0, f"Exact version check failed\nstdout: {result.stdout}"
    assert "ERROR" not in result.stdout


def test_multiline_extra_output_rejected(tmp_path: Path) -> None:
    result = _check_uv(lambda d: _fake_uv_raw(d, "0.11.29\nextra line"), tmp_path)
    assert result.returncode != 0
    assert MISMATCH_LINE2 in result.stdout
    assert "0.11.29" in result.stdout


def test_unavailable_substitutes_template(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(parents=True)
    _write_fake(bin_dir, "uv", "#!/bin/sh\nexit 127\n")
    result = _run_make("check-uv-version", env={"UV": str(bin_dir / "uv")})
    assert result.returncode != 0
    assert MISMATCH_LINE1.format(actual="unavailable") in result.stdout
    assert MISMATCH_LINE2 in result.stdout


def test_ci_pr2a_file_does_not_bypass_target(tmp_path: Path) -> None:
    sentinel_file = PROJECT_ROOT / "ci-pr2a"
    created = False
    if not sentinel_file.exists():
        sentinel_file.write_text("stale")
        created = True
    try:
        result, _log = _run_with_fakes("ci-pr2a", tmp_path)
        assert S_UV_OK in result.stdout, (
            "ci-pr2a target did not run; same-named file bypassed execution.\n"
            f"stdout: {result.stdout}"
        )
    finally:
        if created:
            sentinel_file.unlink(missing_ok=True)


def test_ci_pr2a_exact_invocation_log_on_success(tmp_path: Path) -> None:
    result, log = _run_with_fakes("ci-pr2a", tmp_path)
    assert result.returncode == 0, f"ci-pr2a failed\nstdout: {result.stdout}"
    assert _invocations(log) == EXPECTED_PR2A_LOG, (
        f"Invocation log mismatch:\nexpected: {EXPECTED_PR2A_LOG}\ngot: {_invocations(log)}"
    )


def test_no_duplicate_success_sentinels(tmp_path: Path) -> None:
    result, _log = _run_with_fakes("ci-pr2a", tmp_path)
    assert result.returncode == 0
    for sentinel in [S_SYNC_OK, S_RUFF_CHECK_OK, S_PYTEST_OK]:
        assert result.stdout.count(sentinel) == 1, (
            f"Sentinel '{sentinel}' appeared {result.stdout.count(sentinel)} times"
        )


def test_uv_mismatch_stops_before_sync(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(parents=True)
    log = tmp_path / "invocations.log"
    log.touch()
    _fake_uv(bin_dir, "0.11.30")
    for name in FAKE_TOOL_NAMES:
        _fake_tool(bin_dir, name)
    env = {"UV": str(bin_dir / "uv"), "PATH": f"{bin_dir}:{os.environ.get('PATH', '')}"}
    result = _run_make("ci-pr2a", env=env, timeout=10)
    assert result.returncode != 0
    assert S_UV_OK not in result.stdout
    assert S_SYNC_OK not in result.stdout
    assert MISMATCH_LINE1.format(actual="0.11.30") in result.stdout
    assert _invocations(log) == ["uv self version --short"], (
        f"Expected only version check; got: {_invocations(log)}"
    )


# Exact log prefix through each failing command (inclusive).
_FAILURE_PREFIXES = {
    "ruff": EXPECTED_PR2A_LOG[:4],
    "pyright": EXPECTED_PR2A_LOG[:8],
    "pytest": EXPECTED_PR2A_LOG[:10],
}
RUFF_FAILURE_PREFIX = _FAILURE_PREFIXES["ruff"]
PYRIGHT_FAILURE_PREFIX = _FAILURE_PREFIXES["pyright"]
PYTEST_FAILURE_PREFIX = _FAILURE_PREFIXES["pytest"]


@pytest.mark.parametrize(
    ("failing_tool", "expected_prefix"),
    [
        ("ruff", RUFF_FAILURE_PREFIX),
        ("pyright", PYRIGHT_FAILURE_PREFIX),
        ("pytest", PYTEST_FAILURE_PREFIX),
    ],
    ids=["ruff", "pyright", "pytest"],
)
def test_failure_exact_prefix_log(
    tmp_path: Path,
    failing_tool: str,
    expected_prefix: list[str],
) -> None:
    result, log = _run_with_fakes("ci-pr2a", tmp_path, failing_tools=(failing_tool,))
    assert result.returncode != 0
    assert S_CI_PR2A_DONE not in result.stdout
    invocations = _invocations(log)
    assert invocations == expected_prefix, (
        f"Log prefix mismatch for {failing_tool}:\nexpected: {expected_prefix}\ngot: {invocations}"
    )


def test_ci_reaches_pr3_audit_boundary(tmp_path: Path) -> None:
    ci_result, ci_log = _run_with_fakes("ci", tmp_path)
    assert ci_result.returncode != 0, (
        f"make ci should fail closed at the PR3 audit boundary\nstdout: {ci_result.stdout}"
    )
    assert S_PYTEST_OK in ci_result.stdout
    assert _invocations(ci_log) == [
        *EXPECTED_PR2A_LOG[:2],
        "uv run --frozen python scripts/ci/check_focused_tests.py .",
        *EXPECTED_PR2A_LOG[2:],
    ]
    assert S_FOCUSED_OK in ci_result.stdout
    assert "audit is not yet implemented until PR3" in (ci_result.stdout + ci_result.stderr)
    assert "=== make ci complete ===" not in ci_result.stdout
