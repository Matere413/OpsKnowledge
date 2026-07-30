"""Architecture contracts for the quality evaluation harness (Unit 4).

Static contracts over the Makefile, CLI entry point, and feature source. No
``make`` invocation, no subprocess, no network, no database, no provider.

Mirrors the static-contract style of ``test_evaluation_dataset_ci_order.py``:
reasons over the Makefile text and the feature source directly.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parents[2]
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
EVAL_FEATURE = PROJECT_ROOT / "backend" / "features" / "evaluation"


def _makefile_text() -> str:
    return MAKEFILE_PATH.read_text()


def _target_block(text: str, target: str) -> str:
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


def test_eval_quality_target_exists_and_is_opt_in() -> None:
    text = _makefile_text()
    assert "eval-quality:" in text, "make eval-quality target missing"
    ci_block = _target_block(text, "ci")
    assert "eval-quality" not in ci_block, "eval-quality must NOT be in the ci recipe"


def test_eval_quality_uses_frozen_uv_run_and_fixed_argv() -> None:
    block = _target_block(_makefile_text(), "eval-quality")
    recipe = "\n".join(line for line in block.splitlines() if line.startswith("\t"))
    assert "$(UV_RUN) run --frozen" in recipe, "eval-quality must use $(UV_RUN) run --frozen"
    assert "python -m backend.features.evaluation.cli" in recipe, (
        "eval-quality must invoke the evaluation CLI module"
    )


def test_eval_quality_uses_validated_dataset_root() -> None:
    block = _target_block(_makefile_text(), "eval-quality")
    recipe = "\n".join(line for line in block.splitlines() if line.startswith("\t"))
    assert "evaluation-dataset" in recipe, "eval-quality must point at the committed dataset root"


def test_eval_quality_cli_promotes_all_three_files_through_report_adapter() -> None:
    cli_path = EVAL_FEATURE / "cli.py"
    tree = ast.parse(cli_path.read_text(encoding="utf-8"), filename=str(cli_path))
    main = next(
        node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "main"
    )
    promotions = [
        node
        for node in ast.walk(main)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "promote"
    ]
    assert len(promotions) == 1
    keywords = {keyword.arg for keyword in promotions[0].keywords}
    assert {"run_id", "payload", "records", "report"} <= keywords
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in {"write_text", "write_bytes"}
        for node in ast.walk(main)
    ), "CLI must not bypass ReportAdapter with direct current-file writes"


def test_eval_quality_and_gate_remain_outside_ci_and_ci_pr2a() -> None:
    text = _makefile_text()
    for target in ("ci", "ci-pr2a"):
        block = _target_block(text, target)
        assert "eval-quality" not in block
        assert "eval-quality-gate" not in block


@pytest.mark.parametrize(
    "module",
    [
        "http",
        "requests",
        "aiohttp",
        "httpx",
        "socket",
        "asyncio",
        "langchain",
        "llama_index",
        "redis",
        "kubernetes",
    ],
)
def test_evaluation_feature_imports_no_external_surfaces(module: str) -> None:
    """The evaluation feature MUST NOT import HTTP, persistence, auth, UI,
    corporate, LangChain, LlamaIndex, Redis, Kubernetes, or new providers."""
    for py in EVAL_FEATURE.rglob("*.py"):
        tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith(module), (
                        f"{py.name} imports forbidden module {alias.name}"
                    )
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert not node.module.startswith(module), (
                    f"{py.name} imports from forbidden module {node.module}"
                )


def test_ci_membership_and_order_unchanged() -> None:
    """The ci target MUST retain every canonical stage in the same order."""
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
    # Prerequisites on the header line (e.g. ``ci: check-uv-version``) come
    # before recipe lines; include them in the search.
    header = block.splitlines()[0] if block else ""
    header_deps = header.split(":", 1)[1].strip().split() if ":" in header else []
    body = [line.strip() for line in block.splitlines() if line.startswith("\t")]
    found = []
    for stage in expected:
        if stage in header_deps or any(stage in line for line in body):
            found.append(stage)
    assert found == expected, f"ci stages changed: expected {expected}, found {found}"
