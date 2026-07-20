"""Equivalence-class tests for the structural focused-test policy."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from types import ModuleType

import pytest

SCANNER_PATH = Path(__file__).parents[2] / "scripts/ci/check_focused_tests.py"
DYNAMIC_IMPORT_REMEDIATION = "remove the dynamic import or use canonical import pytest"


def _scanner() -> ModuleType:
    spec = importlib.util.spec_from_file_location("focused_scanner", SCANNER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _scan(
    tmp_path: Path, source: str, name: str = "test_case.py"
) -> list[tuple[str, int, str, str]]:
    root = tmp_path / "root"
    root.mkdir()
    (root / name).write_text(source)
    return _scanner().scan_tree(root)  # type: ignore[attr-defined]


ALLOWED_SOURCES = [
    "import pytest\n@pytest.fixture(scope='session')\ndef fixture(): pass\n",
    "import pytest\n@pytest.mark.parametrize('value', [1, None, ['x']])\n"
    "def test_case(value): pass\n",
    "import pytest\nVALUES = object()\n"
    "@pytest.mark.parametrize(('a', 'b'), VALUES, ids=VALUES)\n"
    "def test_case(a, b): pass\n",
    "import pytest\npytestmark = pytest.mark.ci_recipe\n",
    "import pytest\npytestmark = (pytest.mark.ci_recipe,)\n",
    "import pytest\ndef test_case(patch: pytest.MonkeyPatch): pass\n",
    "import importlib\nimportlib.import_module('project_module')\n",
    "import unittesting\n",
]


@pytest.mark.parametrize("source", ALLOWED_SOURCES)
def test_allowed_direct_shapes_pass(tmp_path: Path, source: str) -> None:
    assert _scan(tmp_path, source) == []


REJECTED_CASES = [
    ("import pytest as pt\n", "unsupported-test-api"),
    ("from pytest import fixture\n", "unsupported-test-api"),
    ("import unittest\n", "unsupported-test-api"),
    ("import pytest\n@pytest.mark.skip\ndef test_case(): pass\n", "unsupported-test-api"),
    ("import pytest\ndef test_case(): pytest.raises(ValueError)\n", "unsupported-test-api"),
    ("import pytest\npytestmark.append(pytest.mark.ci_recipe)\n", "pytestmark-mutation"),
    (
        "import pytest\n@pytest.mark.parametrize('x', lambda: 1)\ndef test_case(x): pass\n",
        "unsupported-parametrize-argument",
    ),
    (
        "import pytest\n@pytest.mark.parametrize('x', values[0])\ndef test_case(x): pass\n",
        "unsupported-parametrize-argument",
    ),
]


@pytest.mark.parametrize(("source", "reason"), REJECTED_CASES)
def test_unsupported_api_shapes_fail_closed(tmp_path: Path, source: str, reason: str) -> None:
    findings = _scan(tmp_path, source)
    assert findings
    assert findings[0][2] == reason


DYNAMIC_SOURCES = [
    "__import__('pytest')\n",
    "import importlib\nimportlib.import_module('unittest')\n",
    "import importlib\nimportlib.__import__('pytest')\n",
    "import importlib as module\nmodule.import_module('pytest').skip()\n",
    "from importlib import import_module\nimport_module('pytest')\n",
    "from importlib import import_module as alias\nalias('pytest')\n",
    "import importlib\nimportlib.import_module(name='pytest')\n",
]

ALIAS_DYNAMIC_CASES = [
    (
        "import importlib\nloader = importlib.import_module\nloader('pytest')\n",
        [("test_case.py", 3, "unsupported-dynamic-import", DYNAMIC_IMPORT_REMEDIATION)],
    ),
    (
        "import importlib as imports\n"
        "loader: object = imports.import_module\n"
        "loader(name='unittest')\n",
        [
            ("test_case.py", 1, "unsupported-dynamic-import", DYNAMIC_IMPORT_REMEDIATION),
        ],
    ),
    (
        "import importlib\nmodule = importlib\nloader = module.import_module\n"
        "alias = loader\nalias('pytest')\n",
        [("test_case.py", 5, "unsupported-dynamic-import", DYNAMIC_IMPORT_REMEDIATION)],
    ),
    (
        "loader = __import__\nloader(name='unittest')\n",
        [("test_case.py", 2, "unsupported-dynamic-import", DYNAMIC_IMPORT_REMEDIATION)],
    ),
]


@pytest.mark.parametrize(("source", "expected"), ALIAS_DYNAMIC_CASES)
def test_direct_dynamic_import_aliases_have_canonical_diagnostics(
    tmp_path: Path, source: str, expected: list[tuple[str, int, str, str]]
) -> None:
    assert _scan(tmp_path, source) == expected


def test_alias_assignment_uses_rhs_before_rebinding(tmp_path: Path) -> None:
    source = (
        "import importlib\nloader = importlib.import_module\nloader = loader\nloader('pytest')\n"
    )
    assert _scan(tmp_path, source) == [
        ("test_case.py", 4, "unsupported-dynamic-import", DYNAMIC_IMPORT_REMEDIATION)
    ]


def test_unconditional_alias_rebinding_invalidates_tracking(tmp_path: Path) -> None:
    source = (
        "import importlib\nloader = importlib.import_module\n"
        "loader = safe_loader\nloader('pytest')\n"
    )
    assert _scan(tmp_path, source) == []


def test_conditional_alias_rebinding_is_ambiguous(tmp_path: Path) -> None:
    source = (
        "import importlib\nloader = importlib.import_module\nif condition:\n"
        "    loader = safe_loader\nloader('pytest')\n"
    )
    assert _scan(tmp_path, source) == [
        (
            "test_case.py",
            5,
            "ambiguous-dynamic-import-alias",
            "rewrite to a direct unambiguous dynamic import or remove the dynamic import",
        )
    ]


def test_conditional_canonical_importlib_rebinding_is_ambiguous(tmp_path: Path) -> None:
    source = (
        "import importlib\nif condition:\n    importlib = safe_module\n"
        "importlib.import_module('pytest')\n"
    )
    assert _scan(tmp_path, source) == [
        (
            "test_case.py",
            4,
            "ambiguous-dynamic-import-alias",
            "rewrite to a direct unambiguous dynamic import or remove the dynamic import",
        )
    ]


@pytest.mark.parametrize(
    "source",
    [
        "import importlib\nloader = importlib.import_module\ndef inner():\n    loader('pytest')\n",
        "import importlib\nloader = importlib.import_module\nasync def inner():\n"
        "    loader('pytest')\n",
        "import importlib\nloader = importlib.import_module\nclass Inner:\n    loader('pytest')\n",
        "import importlib\nloader = importlib.import_module\ninner = lambda: loader('pytest')\n",
    ],
)
def test_aliases_do_not_cross_lexical_boundaries(tmp_path: Path, source: str) -> None:
    assert _scan(tmp_path, source) == []


@pytest.mark.parametrize(
    ("source", "line"),
    [
        ("import importlib\ndef inner():\n    importlib.import_module('pytest')\n", 3),
        ("import importlib\nasync def inner():\n    importlib.import_module('pytest')\n", 3),
        ("import importlib\nclass Inner:\n    importlib.import_module('pytest')\n", 3),
        ("import importlib\ninner = lambda: importlib.import_module('pytest')\n", 2),
    ],
)
def test_lexical_body_canonical_dynamic_import_is_diagnosed(
    tmp_path: Path, source: str, line: int
) -> None:
    assert _scan(tmp_path, source) == [
        ("test_case.py", line, "unsupported-dynamic-import", DYNAMIC_IMPORT_REMEDIATION)
    ]


def test_loop_rebinding_does_not_invalidate_dynamic_import_alias(tmp_path: Path) -> None:
    source = (
        "import importlib\nloader = importlib.import_module\nwhile condition:\n"
        "    loader = safe_loader\nloader('pytest')\n"
    )
    assert _scan(tmp_path, source) == [
        ("test_case.py", 5, "unsupported-dynamic-import", DYNAMIC_IMPORT_REMEDIATION)
    ]


@pytest.mark.parametrize(
    "source",
    [
        "import importlib\nloaders = [importlib.import_module]\nloaders[0]('pytest')\n",
        "import importlib\nloader = getattr(importlib, 'import_module')\nloader('pytest')\n",
        "import importlib\nholder.loader = importlib.import_module\nholder.loader('pytest')\n",
        "import importlib\ndef wrapper():\n    return importlib.import_module\n"
        "loader = wrapper()\nloader('pytest')\n",
    ],
)
def test_closed_alias_grammar_does_not_resolve_arbitrary_expressions(
    tmp_path: Path, source: str
) -> None:
    assert _scan(tmp_path, source) == []


def test_repeated_alias_scans_are_ordered_deduplicated_and_equivalent(tmp_path: Path) -> None:
    root = tmp_path / "root"
    nested = root / "nested"
    nested.mkdir(parents=True)
    (root / "z.py").write_text("import unittest\n")
    (root / "a.py").write_text(
        "import importlib\nloader = importlib.import_module\nloader('pytest')\n"
    )
    (nested / "b.py").write_text(
        "import importlib\nloader = importlib.import_module\nloader('unittest')\n"
    )

    scanner = _scanner()
    first = scanner.scan_tree(root)  # type: ignore[attr-defined]
    second = scanner.scan_tree(root)  # type: ignore[attr-defined]

    assert first == sorted(set(first))
    assert repr(first).encode() == repr(second).encode()


RESOURCE_CASES = [
    ("MAX_ENTRIES", 0, "resource-limit-entries", {"one.txt": "x"}),
    ("MAX_FILES", 0, "resource-limit-files", {"one.py": "pass\n"}),
    ("MAX_FILE_BYTES", 1, "resource-limit-file", {"one.py": "pass\n"}),
    ("MAX_TOTAL_BYTES", 1, "resource-limit-total", {"one.py": "pass\n"}),
]


@pytest.mark.parametrize("source", DYNAMIC_SOURCES)
def test_dynamic_test_imports_have_owned_diagnostic(tmp_path: Path, source: str) -> None:
    assert _scan(tmp_path, source) == [
        (
            "test_case.py",
            1 if source.startswith(("__", "import importlib as", "from importlib")) else 2,
            "unsupported-dynamic-import",
            "remove the dynamic import or use canonical import pytest",
        )
    ]


def test_strings_and_unrelated_calls_are_not_api_references(tmp_path: Path) -> None:
    assert _scan(tmp_path, "TEXT = 'pytest.mark.skip'\nobj.only()\n") == []


def test_fixed_exclusions_are_not_enumerated(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    excluded = root / ".venv"
    excluded.mkdir()
    (excluded / "bad.py").write_text("import unittest\n")
    assert _scanner().scan_tree(root) == []  # type: ignore[attr-defined]


def test_syntax_and_symlink_uncertainty_fail_closed(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    (root / "bad.py").write_text("def broken(:\n")
    assert _scanner().scan_tree(root)[0][2] == "syntax-error"  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    ("attribute", "limit", "reason", "files"),
    RESOURCE_CASES,
)
def test_resource_limits_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    attribute: str,
    limit: int,
    reason: str,
    files: dict[str, str],
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    for name, content in files.items():
        (root / name).write_text(content)
    scanner = _scanner()
    monkeypatch.setattr(scanner, attribute, limit)
    assert scanner.scan_tree(root)[0][2] == reason  # type: ignore[attr-defined]


def test_excluded_entries_count_before_classification(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    (root / ".venv").mkdir()
    scanner = _scanner()
    monkeypatch.setattr(scanner, "MAX_ENTRIES", 0)
    assert scanner.scan_tree(root)[0][2] == "resource-limit-entries"  # type: ignore[attr-defined]


def test_diagnostics_are_lexical_and_deduplicated(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    (root / "z.py").write_text("import unittest\n")
    (root / "a.py").write_text("import unittest\n")
    findings = _scanner().scan_tree(root)  # type: ignore[attr-defined]
    assert [finding[0] for finding in findings] == ["a.py", "z.py"]


def test_decode_and_read_errors_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    source = root / "bad.py"
    source.write_bytes(b"\xff")
    scanner = _scanner()
    assert scanner.scan_tree(root)[0][2] == "decode-error"  # type: ignore[attr-defined]
    monkeypatch.setattr(Path, "read_bytes", lambda _: (_ for _ in ()).throw(OSError("blocked")))
    assert scanner.scan_tree(root)[0][2] == "read-error"  # type: ignore[attr-defined]


def test_symlink_entry_fails_closed(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    target = root / "target.py"
    target.write_text("pass\n")
    (root / "linked.py").symlink_to(target)
    assert _scanner().scan_tree(root)[0][2] == "symlink-not-allowed"  # type: ignore[attr-defined]


def test_entry_limit_allows_boundary_then_rejects_next(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    (root / "a.txt").write_text("a")
    (root / "b.txt").write_text("b")
    scanner = _scanner()
    monkeypatch.setattr(scanner, "MAX_ENTRIES", 1)
    finding = scanner.scan_tree(root)[0]  # type: ignore[attr-defined]
    assert finding[1:] == (
        0,
        "resource-limit-entries",
        "reduce encountered entries to at most 100,000",
    )


def test_observed_stat_and_traversal_errors_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    source = root / "source.py"
    source.write_text("pass\n")
    scanner = _scanner()
    original_lstat = scanner.os.lstat

    def failing_lstat(path: Path) -> object:
        if Path(path).name == "source.py":
            raise OSError("blocked")
        return original_lstat(path)

    monkeypatch.setattr(scanner.os, "lstat", failing_lstat)
    assert scanner.scan_tree(root)[0][2] == "stat-error"  # type: ignore[attr-defined]
    monkeypatch.setattr(scanner.os, "scandir", lambda _: (_ for _ in ()).throw(OSError("blocked")))
    assert scanner.scan_tree(root)[0][2] == "traversal-error"  # type: ignore[attr-defined]


def test_root_errors_fail_closed(tmp_path: Path) -> None:
    scanner = _scanner()
    assert scanner.scan_tree(tmp_path / "missing")[0][2] == "stat-error"  # type: ignore[attr-defined]
    file_root = tmp_path / "file"
    file_root.write_text("x")
    assert scanner.scan_tree(file_root)[0][2] == "root-not-directory"  # type: ignore[attr-defined]


def test_entry_limit_stops_before_metadata(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "root"
    root.mkdir()
    (root / "entry.py").write_text("pass\n")
    scanner = _scanner()
    monkeypatch.setattr(scanner, "MAX_ENTRIES", 0)
    original_lstat = scanner.os.lstat

    def lstat_root_only(path: Path) -> object:
        if Path(path) != root:
            raise AssertionError("lstat must not run")
        return original_lstat(path)

    monkeypatch.setattr(
        scanner.os,
        "lstat",
        lstat_root_only,
    )
    assert scanner.scan_tree(root)[0][2] == "resource-limit-entries"  # type: ignore[attr-defined]


def test_scan_does_not_execute_conftest(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    (root / "conftest.py").write_text("raise RuntimeError('must not execute')\n")
    assert _scanner().scan_tree(root) == []  # type: ignore[attr-defined]


def test_exact_file_and_total_byte_boundaries_pass(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    scanner = _scanner()
    source = b"#" + b"x" * (scanner.MAX_FILE_BYTES - 1)  # type: ignore[attr-defined]
    for index in range(64):
        (root / f"source_{index}.py").write_bytes(source)
    assert scanner.scan_tree(root) == []  # type: ignore[attr-defined]


def test_exact_file_count_boundary_passes(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    scanner = _scanner()
    for index in range(scanner.MAX_FILES):  # type: ignore[attr-defined]
        (root / f"source_{index}.py").write_text("pass\n")
    assert scanner.scan_tree(root) == []  # type: ignore[attr-defined]


def test_excluded_entry_metadata_error_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    excluded = root / ".venv"
    excluded.mkdir()
    scanner = _scanner()
    original_lstat = scanner.os.lstat

    def failing_lstat(path: Path) -> object:
        if Path(path) == excluded:
            raise OSError("blocked")
        return original_lstat(path)

    monkeypatch.setattr(scanner.os, "lstat", failing_lstat)
    assert scanner.scan_tree(root)[0][2] == "stat-error"  # type: ignore[attr-defined]


def test_root_symlink_fails_closed(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    root_link = tmp_path / "root-link"
    root_link.symlink_to(target, target_is_directory=True)
    assert _scanner().scan_tree(root_link)[0][2] == "symlink-not-allowed"  # type: ignore[attr-defined]


def test_scandir_stops_incrementally_at_entry_boundary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    for name in ("a.txt", "b.txt", "c.txt"):
        (root / name).write_text(name)
    entries = list(os.scandir(root))
    scanner = _scanner()
    seen = 0

    class EntryStream:
        def __enter__(self) -> EntryStream:
            return self

        def __exit__(self, *_: object) -> None:
            return None

        def __iter__(self) -> EntryStream:
            return self

        def __next__(self) -> os.DirEntry[str]:
            nonlocal seen
            if seen == 2:
                raise AssertionError("scanner eagerly consumed entries")
            entry = entries[seen]
            seen += 1
            return entry

    monkeypatch.setattr(scanner, "MAX_ENTRIES", 1)
    monkeypatch.setattr(scanner.os, "scandir", lambda _: EntryStream())
    assert scanner.scan_tree(root)[0][2] == "resource-limit-entries"  # type: ignore[attr-defined]
    assert seen == 2
