from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

SCANNER_PATH = Path(__file__).parents[2] / "scripts/ci/check_dependency_boundaries.py"


def _scanner() -> ModuleType:
    spec = importlib.util.spec_from_file_location("dependency_boundaries", SCANNER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _scan(tmp_path: Path, source: str) -> list[tuple[str, int, str]]:
    (tmp_path / "governance").mkdir()
    (tmp_path / "pyproject.toml").write_text("[project]\ndependencies = []\n")
    (tmp_path / "governance/direct-dependencies.yaml").write_text("entries: []\n")
    (tmp_path / "sample.py").write_text(source)
    return _scanner().scan_tree(tmp_path)  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    ("source", "line", "distribution"),
    [
        ("import langchain as chain", 1, "langchain"),
        ("from llama_index.core import VectorStoreIndex", 1, "llamaindex"),
        ("import importlib as loader\nloader.import_module('redis')", 2, "redis"),
        ("from importlib import import_module as load\nload('kubernetes')", 2, "kubernetes"),
    ],
)
def test_excluded_direct_and_literal_dynamic_imports_fail(
    tmp_path: Path, source: str, line: int, distribution: str
) -> None:
    assert _scan(tmp_path, source) == [("sample.py", line, distribution)]


def test_import_module_alias_assignment_is_resolved(tmp_path: Path) -> None:
    findings = _scan(tmp_path, "import importlib\nload = importlib.import_module\nload('redis')")
    assert findings == [("sample.py", 3, "redis")]


def test_importlib_module_alias_chain_is_resolved(tmp_path: Path) -> None:
    findings = _scan(
        tmp_path,
        "import importlib\nalias = importlib\nsecond = alias\nsecond.import_module('redis')",
    )
    assert findings == [("sample.py", 4, "redis")]


def test_annotated_importlib_module_alias_is_resolved(tmp_path: Path) -> None:
    findings = _scan(
        tmp_path,
        'import importlib\nalias: object = importlib\nalias.import_module("redis")',
    )
    assert findings == [("sample.py", 3, "redis")]


def test_unrelated_import_and_non_literal_dynamic_import_pass(tmp_path: Path) -> None:
    assert _scan(tmp_path, "import pathlib\nname = 'redis'\n__import__(name)") == []


def test_policy_map_gaps_and_non_importable_entries_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _scanner()
    monkeypatch.delitem(module.EXCLUDED_DISTRIBUTIONS, "redis")
    monkeypatch.setattr(
        module, "NON_IMPORTABLE_EXCLUSIONS", module.NON_IMPORTABLE_EXCLUSIONS | {"langchain"}
    )
    assert module.validate_policy() == ["map-gap:redis", "non-importable-mapped:langchain"]


def test_invalid_root_fails_closed(tmp_path: Path) -> None:
    assert _scanner().scan_tree(tmp_path / "missing") == [(".", 0, "root-stat-error")]  # type: ignore[attr-defined]


def test_non_directory_root_fails_closed(tmp_path: Path) -> None:
    root = tmp_path / "file"
    root.write_text("x")
    assert _scanner().scan_tree(root) == [(".", 0, "root-not-directory")]  # type: ignore[attr-defined]


def test_observed_symlink_fails_before_external_import_is_hidden(tmp_path: Path) -> None:
    _scan(tmp_path, "import pathlib")
    external = tmp_path.parent / "external.py"
    external.write_text("import redis")
    (tmp_path / "hidden.py").symlink_to(external)
    assert _scanner().scan_tree(tmp_path) == [("hidden.py", 0, "symlink-not-allowed")]  # type: ignore[attr-defined]


def test_production_dependency_requires_approved_governance_entry(tmp_path: Path) -> None:
    _scan(tmp_path, "import pathlib")
    (tmp_path / "pyproject.toml").write_text('[project]\ndependencies = ["fastapi"]\n')
    assert _scanner().scan_tree(tmp_path) == [  # type: ignore[attr-defined]
        ("pyproject.toml", 0, "unapproved-production-dependency:fastapi")
    ]


def test_versioned_requirement_uses_canonical_distribution_name(tmp_path: Path) -> None:
    _scan(tmp_path, "import pathlib")
    (tmp_path / "pyproject.toml").write_text('[project]\ndependencies = ["fastapi>=0.1"]\n')
    (tmp_path / "governance/direct-dependencies.yaml").write_text(
        "entries:\n"
        "  - name: fastapi\n"
        "    scope: backend\n"
        "    purpose: API\n"
        "    owning_feature: query\n"
        "    license: MIT\n"
        "    risk: {level: low, reason: stable}\n"
        "    approval: {decision: approved, approver: reviewer, "
        "date: 2026-07-17, reference: SDD-1}\n"
    )
    assert _scanner().scan_tree(tmp_path) == []  # type: ignore[attr-defined]


def _governance_entry(decision: str, field: str, value: str) -> str:
    return (
        "entries:\n"
        "  - name: fastapi\n"
        "    scope: backend\n"
        "    purpose: API\n"
        "    owning_feature: query\n"
        "    license: MIT\n"
        "    risk: {level: low, reason: stable}\n"
        "    approval:\n"
        f"      decision: {decision}\n"
        f"      approver: {value if field == 'approver' else 'reviewer'}\n"
        f"      date: {value if field == 'date' else '2026-07-17'}\n"
        f"      reference: {value if field == 'reference' else 'SDD-1'}\n"
    )


@pytest.mark.parametrize("field", ("approver", "date", "reference"))
def test_approved_governance_rejects_normalized_pending_placeholders(
    tmp_path: Path, field: str
) -> None:
    _scan(tmp_path, "import pathlib")
    (tmp_path / "governance/direct-dependencies.yaml").write_text(
        _governance_entry("approved", field, "  TbD  ")
    )
    assert _scanner().scan_tree(tmp_path) == [  # type: ignore[attr-defined]
        ("governance/direct-dependencies.yaml", 0, "incomplete-governance-entry:fastapi")
    ]


@pytest.mark.parametrize("field", ("date",))
def test_pending_governance_allows_documented_pending_placeholders(
    tmp_path: Path, field: str
) -> None:
    _scan(tmp_path, "import pathlib")
    (tmp_path / "governance/direct-dependencies.yaml").write_text(
        _governance_entry("pending", field, "  TbD  ")
    )
    assert _scanner().scan_tree(tmp_path) == []  # type: ignore[attr-defined]


@pytest.mark.parametrize("level", ("", "   "))
def test_approved_governance_rejects_empty_risk_level(tmp_path: Path, level: str) -> None:
    _scan(tmp_path, "import pathlib")
    entry = _governance_entry("approved", "", "").replace(
        "risk: {level: low, reason: stable}", f"risk: {{level: {level!r}, reason: stable}}"
    )
    (tmp_path / "governance/direct-dependencies.yaml").write_text(entry)
    assert _scanner().scan_tree(tmp_path) == [  # type: ignore[attr-defined]
        ("governance/direct-dependencies.yaml", 0, "incomplete-governance-entry:fastapi")
    ]


@pytest.mark.parametrize(
    "omitted_line",
    [
        "      reason: stable\n",
        "      decision: approved\n",
        "      approver: reviewer\n",
        "      date: 2026-07-17\n",
        "      reference: SDD-1\n",
    ],
)
def test_missing_required_governance_fields_fail_closed(tmp_path: Path, omitted_line: str) -> None:
    _scan(tmp_path, "import pathlib")
    entry = (
        "entries:\n"
        "  - name: fastapi\n"
        "    scope: backend\n"
        "    purpose: API\n"
        "    owning_feature: query\n"
        "    license: MIT\n"
        "    risk:\n"
        "      level: low\n"
        "      reason: stable\n"
        "    approval:\n"
        "      decision: approved\n"
        "      approver: reviewer\n"
        "      date: 2026-07-17\n"
        "      reference: SDD-1\n"
    )
    (tmp_path / "governance/direct-dependencies.yaml").write_text(entry.replace(omitted_line, ""))
    assert _scanner().scan_tree(tmp_path) == [  # type: ignore[attr-defined]
        ("governance/direct-dependencies.yaml", 0, "incomplete-governance-entry:fastapi")
    ]
