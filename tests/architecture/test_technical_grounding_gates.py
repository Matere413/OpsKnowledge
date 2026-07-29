"""Architecture contracts for the technical grounding safety gates (Unit 3).

Static contracts over the Makefile, gate CLI entry point, and gate feature
source. No ``make`` invocation, no subprocess, no network, no database, no
provider. Mirrors the static-contract style of
``test_quality_evaluation_harness.py``.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parents[2]
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
GATE_FEATURE = PROJECT_ROOT / "backend" / "features" / "evaluation" / "gates"


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


# ---------------------------------------------------------------------------
# Makefile: eval-quality-gate target exists, is opt-in, uses frozen uv
# ---------------------------------------------------------------------------


def test_eval_quality_gate_target_exists_and_is_opt_in() -> None:
    text = _makefile_text()
    assert "eval-quality-gate:" in text, "make eval-quality-gate target missing"
    ci_block = _target_block(text, "ci")
    assert "eval-quality-gate" not in ci_block, "eval-quality-gate must NOT be in the ci recipe"
    pr2a_block = _target_block(text, "ci-pr2a")
    assert "eval-quality-gate" not in pr2a_block, "eval-quality-gate must NOT be in ci-pr2a"


def test_eval_quality_gate_uses_frozen_uv_run_and_gate_cli() -> None:
    block = _target_block(_makefile_text(), "eval-quality-gate")
    recipe = "\n".join(line for line in block.splitlines() if line.startswith("\t"))
    assert "$(UV_RUN) run --frozen" in recipe, "eval-quality-gate must use $(UV_RUN) run --frozen"
    assert "python -m backend.features.evaluation.gates.cli" in recipe, (
        "eval-quality-gate must invoke the gate CLI module"
    )


def test_eval_quality_gate_uses_validated_dataset_root() -> None:
    block = _target_block(_makefile_text(), "eval-quality-gate")
    recipe = "\n".join(line for line in block.splitlines() if line.startswith("\t"))
    assert "evaluation-dataset" in recipe, (
        "eval-quality-gate must point at the committed dataset root"
    )


def test_eval_quality_gate_is_phony() -> None:
    text = _makefile_text()
    phony_line = next((line for line in text.splitlines() if line.startswith(".PHONY:")), "")
    assert "eval-quality-gate" in phony_line, "eval-quality-gate must be declared .PHONY"


# ---------------------------------------------------------------------------
# CI membership and order unchanged (must include both ci and ci-pr2a)
# ---------------------------------------------------------------------------


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
    header = block.splitlines()[0] if block else ""
    header_deps = header.split(":", 1)[1].strip().split() if ":" in header else []
    body = [line.strip() for line in block.splitlines() if line.startswith("\t")]
    found = []
    for stage in expected:
        if stage in header_deps or any(stage in line for line in body):
            found.append(stage)
    assert found == expected, f"ci stages changed: expected {expected}, found {found}"


def test_ci_pr2a_membership_and_order_unchanged() -> None:
    """The ci-pr2a target MUST retain its stages unchanged."""
    block = _target_block(_makefile_text(), "ci-pr2a")
    expected = [
        "check-uv-version",
        "sync-env",
        "ruff-check",
        "ruff-format",
        "pyright-check",
        "pytest-check",
    ]
    header = block.splitlines()[0] if block else ""
    header_deps = header.split(":", 1)[1].strip().split() if ":" in header else []
    body = [line.strip() for line in block.splitlines() if line.startswith("\t")]
    found = []
    for stage in expected:
        if stage in header_deps or any(stage in line for line in body):
            found.append(stage)
    assert found == expected, f"ci-pr2a stages changed: expected {expected}, found {found}"


# ---------------------------------------------------------------------------
# Gate feature imports no excluded modules (hex boundary)
# ---------------------------------------------------------------------------


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
        "subprocess",
    ],
)
def test_gate_feature_imports_no_external_surfaces(module: str) -> None:
    """The gate feature MUST NOT import HTTP, persistence, auth, UI, corporate,
    LangChain, LlamaIndex, Redis, Kubernetes, subprocess, or new providers."""
    for py in GATE_FEATURE.rglob("*.py"):
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


# ---------------------------------------------------------------------------
# Gate application/CLI does not import kernel/dataset/query (no reimplementation)
# ---------------------------------------------------------------------------


def test_gate_cli_does_not_import_kernel_or_dataset() -> None:
    cli_path = GATE_FEATURE / "cli.py"
    tree = ast.parse(cli_path.read_text(encoding="utf-8"), filename=str(cli_path))
    forbidden = {
        "backend.features.evaluation.adapters.kernel",
        "backend.features.query",
        "backend.features.evaluation.adapters.dataset",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name not in forbidden, f"cli.py imports forbidden {alias.name}"
        elif isinstance(node, ast.ImportFrom) and node.module:
            assert node.module not in forbidden, f"cli.py imports forbidden {node.module}"


def test_gate_adapters_do_not_import_kernel_or_dataset() -> None:
    report_path = GATE_FEATURE / "adapters" / "report.py"
    assert report_path.exists(), "gate report adapter missing"
    tree = ast.parse(report_path.read_text(encoding="utf-8"), filename=str(report_path))
    forbidden = {
        "backend.features.evaluation.adapters.kernel",
        "backend.features.query",
        "backend.features.evaluation.adapters.dataset",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name not in forbidden, f"report.py imports forbidden {alias.name}"
        elif isinstance(node, ast.ImportFrom) and node.module:
            assert node.module not in forbidden, f"report.py imports forbidden {node.module}"


# ---------------------------------------------------------------------------
# Gate stays separate from the harness: harness modules unchanged
# ---------------------------------------------------------------------------


def test_harness_cli_unchanged() -> None:
    """The harness CLI module path must still exist and be unchanged."""
    harness_cli = PROJECT_ROOT / "backend" / "features" / "evaluation" / "cli.py"
    assert harness_cli.exists(), "harness cli.py must remain"


def test_gate_report_store_uses_gate_specific_adapter_not_harness_report() -> None:
    """The gate MUST use its own report adapter, not the harness ReportAdapter,
    so harness multi-file writes cannot move gate current before a later failure."""
    report_path = GATE_FEATURE / "adapters" / "report.py"
    assert report_path.exists(), "gate report adapter missing"
    text = report_path.read_text(encoding="utf-8")
    assert "GateReportAdapter" in text, "gate must define its own GateReportAdapter"
    assert "from backend.features.evaluation.adapters.report import ReportAdapter" not in text, (
        "gate must not reuse the harness ReportAdapter"
    )
