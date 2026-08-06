"""Architecture tests for approved-source inventory ownership and isolation."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from backend.features.indexing.adapters.local_repository import LocalApprovedSourceRepository
from backend.features.indexing.application import InventoryApprovedSources
from backend.features.indexing.domain import RejectedSnapshot

PROJECT_ROOT = Path(__file__).parents[2]
INDEXING_ROOT = PROJECT_ROOT / "backend/features/indexing"
FIXTURE_ROOT = PROJECT_ROOT / "approved-source-fixture"
EVALUATION_ROOT = PROJECT_ROOT / "evaluation-dataset"

CORPUS_OR_EVALUATION_IMPORTS = (
    "backend.features.corpus",
    "backend.features.evaluation",
    "scripts.ci.validate_evaluation_dataset",
)
CORPORATE_OR_PROVIDER_IMPORT_TOKENS = (
    "sharepoint",
    "graph",
    "entra",
    "azure",
    "openai",
    "managed_identity",
    "private_endpoint",
    "provider",
)


def _indexing_imports() -> set[str]:
    modules: set[str] = set()
    for path in sorted(INDEXING_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.add(node.module)
    return modules


def test_indexing_owns_inventory_without_reusing_corpus_or_evaluation_loaders() -> None:
    """The inventory adapter belongs to indexing and has no loader dependency."""
    assert INDEXING_ROOT.is_dir()
    assert (INDEXING_ROOT / "domain.py").is_file()
    assert (INDEXING_ROOT / "application.py").is_file()
    assert (INDEXING_ROOT / "ports.py").is_file()
    assert (INDEXING_ROOT / "adapters/local_repository.py").is_file()

    imported = _indexing_imports()
    forbidden = [module for module in imported if module.startswith(CORPUS_OR_EVALUATION_IMPORTS)]
    assert forbidden == []

    source = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted(INDEXING_ROOT.rglob("*.py"))
    )
    assert "load_corpus" not in source
    assert "load_validated_corpus" not in source
    assert "base_scenario_payloads" not in source


def test_indexing_has_no_corporate_or_provider_imports() -> None:
    """The approved-source boundary cannot introduce corporate/provider egress."""
    imported = _indexing_imports()
    findings = {
        module
        for module in imported
        if any(
            token in module.lower().replace("-", "_")
            for token in CORPORATE_OR_PROVIDER_IMPORT_TOKENS
        )
    }
    assert findings == set()


def test_synthetic_fixture_is_separate_from_evaluation_dataset() -> None:
    """The development fixture is not the committed evaluation corpus."""
    fixture = FIXTURE_ROOT.resolve()
    evaluation = EVALUATION_ROOT.resolve()
    assert fixture.is_dir()
    assert evaluation.is_dir()
    assert not fixture.is_relative_to(evaluation)
    assert fixture != evaluation

    manifest = json.loads((fixture / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["profile"] == "development"
    assert manifest["classification"] == "synthetic"
    assert all((fixture / record["path"]).is_file() for record in manifest["artifacts"])


def test_denied_requests_read_no_source_bytes(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Evaluation, non-development, and corporate requests stop before reads."""
    reads: list[Path] = []

    def forbidden_read(path: Path) -> bytes:
        reads.append(path)
        raise AssertionError("denied inventory request attempted a source read")

    monkeypatch.setattr(Path, "read_bytes", forbidden_read)
    requests = (
        (
            project_root / "approved-source-fixture",
            "production",
            "local",
            "profile-not-development",
        ),
        (
            project_root / "approved-source-fixture",
            "development",
            "corporate",
            "corporate-source-denied",
        ),
        (
            project_root / "evaluation-dataset",
            "development",
            "local",
            "unsafe-path",
        ),
    )

    for root, profile, source_mode, expected_code in requests:
        repository = LocalApprovedSourceRepository(root, profile=profile)
        result = InventoryApprovedSources(
            repository=repository,
            profile=profile,
            source_mode=source_mode,
        ).inventory()
        assert isinstance(result, RejectedSnapshot)
        assert [diagnostic.code for diagnostic in result.diagnostics] == [expected_code]

    assert reads == []
