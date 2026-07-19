"""Smoke test: verify the project root contains expected baseline files."""

from __future__ import annotations

from pathlib import Path

import pytest

_BASELINE_FILES = ["AGENTS.md", "RAG_ROADMAP.md", "pyproject.toml", "uv.lock", "Makefile"]


@pytest.mark.parametrize("filename", _BASELINE_FILES)
def test_baseline_file_exists(project_root: Path, filename: str) -> None:
    assert (project_root / filename).is_file(), f"{filename} not found at project root"


def test_python_version_pins_312(project_root: Path) -> None:
    pv = project_root / ".python-version"
    assert pv.is_file(), ".python-version not found at project root"
    assert pv.read_text().strip() == "3.12"
