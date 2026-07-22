"""Makefile-ordering contract test for the evaluation-dataset CI wiring.

Mirrors the static contract style of ``test_focused_test_scanner.py``: the
test parses the Makefile text directly and asserts that
``check-evaluation-dataset`` is wired into the canonical ``ci`` target before
``check-focused-tests`` and ``pytest-check``, and that ``ci-pr2a`` is unchanged.

The test never invokes ``make``; it reasons over the Makefile source so it is
deterministic and free of network, subprocess, database, or provider access.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parents[2]
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"


def _makefile_text() -> str:
    return MAKEFILE_PATH.read_text()


def _target_block(text: str, target: str) -> str:
    """Return the target header line plus its raw recipe body (tab-indented
    lines and intervening comments/blanks) up to the next target or end of
    file. Makefile targets may carry prerequisites on the same line
    (``ci: check-uv-version``); the recipe is the block of tab-prefixed lines
    that immediately follows."""
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(f"{target}:"):
            start = index
            break
    assert start is not None, f"Makefile target '{target}' not found"
    block_lines = [lines[start]]
    for line in lines[start + 1 :]:
        if line and not line.startswith("\t") and not line.startswith(" ") and line.strip():
            if re.match(r"^[A-Za-z0-9_.-]+:", line):
                break
            if not line.startswith("#"):
                break
        block_lines.append(line)
    return "\n".join(block_lines)


def _prerequisites(header: str) -> list[str]:
    """Return prerequisites from a target header line like ``ci: a b``."""
    if ":" not in header:
        return []
    deps = header.split(":", 1)[1].strip()
    return deps.split() if deps else []


def _recipe_lines(block: str) -> list[str]:
    return [line for line in block.splitlines() if line.startswith("\t")]


def _order_index(block: str, target_ref: str) -> int:
    """Return the first position at which ``target_ref`` appears in the target
    block — either as a prerequisite on the header line or as a recipe line.
    Prerequisites precede recipe lines in ordering."""
    lines = block.splitlines()
    header = lines[0] if lines else ""
    deps = _prerequisites(header)
    if target_ref in deps:
        return -len(deps) + deps.index(target_ref)
    recipe = _recipe_lines(block)
    for index, line in enumerate(recipe):
        if target_ref in line:
            return index
    raise AssertionError(f"'{target_ref}' not found in target block")


def test_ci_target_exists() -> None:
    block = _target_block(_makefile_text(), "ci")
    assert _recipe_lines(block), "ci target has no recipe lines"


def test_check_evaluation_dataset_runs_before_check_focused_tests() -> None:
    block = _target_block(_makefile_text(), "ci")
    assert _order_index(block, "check-evaluation-dataset") < _order_index(
        block, "check-focused-tests"
    ), "check-evaluation-dataset must run before check-focused-tests in ci"


def test_check_evaluation_dataset_runs_before_pytest_check() -> None:
    block = _target_block(_makefile_text(), "ci")
    assert _order_index(block, "check-evaluation-dataset") < _order_index(block, "pytest-check"), (
        "check-evaluation-dataset must run before pytest-check in ci"
    )


def test_ci_pr2a_unchanged_and_excludes_evaluation_dataset() -> None:
    """The ci-pr2a target is the frozen PR2A gate and MUST NOT gain the
    evaluation-dataset stage."""
    block = _target_block(_makefile_text(), "ci-pr2a")
    assert "check-evaluation-dataset" not in block, (
        "ci-pr2a must remain unchanged and exclude check-evaluation-dataset"
    )
    assert "check-uv-version" in block, "ci-pr2a must still start with check-uv-version"


def test_check_evaluation_dataset_target_uses_frozen_validator() -> None:
    """The standalone target invokes the validator with --frozen and the
    committed dataset root; no network, DB, or provider wiring."""
    block = _target_block(_makefile_text(), "check-evaluation-dataset")
    text = "\n".join(_recipe_lines(block))
    assert "$(UV_RUN) run --frozen" in text, (
        "check-evaluation-dataset must use $(UV_RUN) run --frozen"
    )
    assert "scripts/ci/validate_evaluation_dataset.py" in text, (
        "check-evaluation-dataset must invoke the validator script"
    )
    assert "evaluation-dataset" in text, (
        "check-evaluation-dataset must point at the committed dataset root"
    )


def test_ci_still_runs_all_canonical_stages() -> None:
    """The ci target must retain every canonical stage in order."""
    block = _target_block(_makefile_text(), "ci")
    expected = [
        "check-uv-version",
        "sync-env",
        "check-evaluation-dataset",
        "check-focused-tests",
        "ruff-check",
        "ruff-format",
        "pyright-check",
        "pytest-check",
        "check-dependency-boundaries",
        "check-audit",
        "license-inventory",
    ]
    indices = [_order_index(block, stage) for stage in expected]
    assert indices == sorted(indices), (
        "ci stages are out of order; expected canonical fail-fast sequence"
    )


@pytest.mark.parametrize(
    ("stage", "must_precede"),
    [
        ("check-evaluation-dataset", "ruff-check"),
        ("check-evaluation-dataset", "ruff-format"),
        ("check-evaluation-dataset", "pyright-check"),
        ("check-evaluation-dataset", "check-dependency-boundaries"),
        ("check-evaluation-dataset", "check-audit"),
        ("check-evaluation-dataset", "license-inventory"),
    ],
)
def test_evaluation_dataset_precedes_every_later_ci_stage(stage: str, must_precede: str) -> None:
    block = _target_block(_makefile_text(), "ci")
    assert _order_index(block, stage) < _order_index(block, must_precede), (
        f"{stage} must precede {must_precede} in the ci recipe"
    )
