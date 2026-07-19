"""Fail closed for excluded imports and ungovened production dependencies."""

from __future__ import annotations

import ast
import os
import stat
import sys
import tomllib
from datetime import date
from pathlib import Path

import yaml
from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name

Diagnostic = tuple[str, int, str]
EXCLUDED_DISTRIBUTIONS = {
    "langchain": "langchain",
    "llamaindex": "llama_index",
    "redis": "redis",
    "kubernetes": "kubernetes",
}
NON_IMPORTABLE_EXCLUSIONS = {
    "streaming",
    "visualinterpretation",
    "email",
    "notifier",
    "reranking",
    "queues",
    "microservices",
}
EXCLUDED_DIRECTORIES = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".pyright",
    ".cache",
}


def _normalise(name: str) -> str:
    return canonicalize_name(name)


def _is_pending_placeholder(value: object) -> bool:
    return isinstance(value, str) and value.strip().casefold() == "tbd"


def validate_policy() -> list[str]:
    required = {"langchain", "llamaindex", "redis", "kubernetes"}
    missing = required - set(EXCLUDED_DISTRIBUTIONS)
    overlap = set(EXCLUDED_DISTRIBUTIONS) & NON_IMPORTABLE_EXCLUSIONS
    return [
        *(f"map-gap:{name}" for name in sorted(missing)),
        *(f"non-importable-mapped:{name}" for name in sorted(overlap)),
    ]


def _distribution(module: str) -> str | None:
    root = module.split(".", 1)[0]
    return next(
        (name for name, import_name in EXCLUDED_DISTRIBUTIONS.items() if root == import_name), None
    )


def _governance_diagnostics(root: Path) -> list[Diagnostic]:
    manifest, governance = root / "pyproject.toml", root / "governance/direct-dependencies.yaml"
    try:
        dependencies = tomllib.loads(manifest.read_text(encoding="utf-8"))["project"][
            "dependencies"
        ]
        document = yaml.safe_load(governance.read_text(encoding="utf-8"))
    except (KeyError, OSError, tomllib.TOMLDecodeError, yaml.YAMLError, TypeError):
        return [(".", 0, "governance-reconciliation-error")]
    if not isinstance(dependencies, list) or not isinstance(document, dict):
        return [(".", 0, "governance-reconciliation-error")]
    approved: set[str] = set()
    findings: list[Diagnostic] = []
    for entry in document.get("entries", []):
        if not isinstance(entry, dict):
            findings.append(
                ("governance/direct-dependencies.yaml", 0, "incomplete-governance-entry:unknown")
            )
            continue
        name = entry.get("name")
        approval, risk = entry.get("approval"), entry.get("risk")
        complete = (
            isinstance(name, str)
            and all(
                isinstance(entry.get(field), str) and entry[field]
                for field in ("scope", "purpose", "owning_feature", "license")
            )
            and isinstance(risk, dict)
            and isinstance(risk.get("level"), str)
            and risk["level"].strip()
            and isinstance(risk.get("reason"), str)
            and risk["reason"]
            and isinstance(approval, dict)
            and approval.get("decision") in {"approved", "pending", "rejected", "superseded"}
            and isinstance(approval.get("approver"), str)
            and approval["approver"]
            and isinstance(approval.get("date"), (str, date))
            and approval["date"]
            and isinstance(approval.get("reference"), str)
            and approval["reference"]
            and not (
                approval["decision"] == "approved"
                and any(
                    _is_pending_placeholder(approval[field])
                    for field in ("approver", "date", "reference")
                )
            )
        )
        if not complete:
            findings.append(
                (
                    "governance/direct-dependencies.yaml",
                    0,
                    f"incomplete-governance-entry:{name or 'unknown'}",
                )
            )
        elif approval["decision"] == "approved":
            approved.add(_normalise(name))
    for dependency in dependencies:
        if not isinstance(dependency, str) or not dependency.strip():
            findings.append(("pyproject.toml", 0, "invalid-production-dependency"))
            continue
        try:
            name = _normalise(Requirement(dependency).name)
        except InvalidRequirement:
            findings.append(("pyproject.toml", 0, "invalid-production-dependency"))
            continue
        if name not in approved:
            findings.append(
                ("pyproject.toml", 0, f"unapproved-production-dependency:{name or 'unknown'}")
            )
    return findings


class _Imports(ast.NodeVisitor):
    def __init__(self, path: str) -> None:
        self.path, self.findings = path, set[Diagnostic]()
        # Governance names distributions; this finite map remains the reviewed
        # distribution-to-import-module boundary (`llamaindex` → `llama_index`).
        self.importlib_aliases, self.dynamic_imports = {"importlib"}, {"__import__"}

    def _add(self, node: ast.AST, module: str) -> None:
        if distribution := _distribution(module):
            self.findings.add((self.path, getattr(node, "lineno", 0), distribution))

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self._add(node, alias.name)
            if alias.name == "importlib":
                self.importlib_aliases.add(alias.asname or alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            self._add(node, node.module)
            if node.module == "importlib":
                self.dynamic_imports.update(
                    alias.asname or alias.name
                    for alias in node.names
                    if alias.name == "import_module"
                )
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        names = [target.id for target in node.targets if isinstance(target, ast.Name)]
        self._propagate_aliases(node.value, names)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value is not None and isinstance(node.target, ast.Name):
            self._propagate_aliases(node.value, [node.target.id])
        self.generic_visit(node)

    def _propagate_aliases(self, value: ast.expr, names: list[str]) -> None:
        if isinstance(value, ast.Name) and value.id in self.importlib_aliases:
            self.importlib_aliases.update(names)
        if (
            isinstance(value, ast.Name) and value.id in self.dynamic_imports
        ) or self._is_import_module(value):
            self.dynamic_imports.update(names)

    def visit_Call(self, node: ast.Call) -> None:
        target = (
            node.args[0]
            if node.args
            else next((item.value for item in node.keywords if item.arg == "name"), None)
        )
        if (
            isinstance(target, ast.Constant)
            and isinstance(target.value, str)
            and self._is_dynamic_import(node.func)
        ):
            self._add(node, target.value)
        self.generic_visit(node)

    def _is_import_module(self, value: ast.expr) -> bool:
        return (
            isinstance(value, ast.Attribute)
            and value.attr == "import_module"
            and isinstance(value.value, ast.Name)
            and value.value.id in self.importlib_aliases
        )

    def _is_dynamic_import(self, function: ast.expr) -> bool:
        return (
            isinstance(function, ast.Name)
            and function.id in self.dynamic_imports
            or self._is_import_module(function)
        )


def scan_tree(requested_root: Path) -> list[Diagnostic]:
    root = requested_root.absolute()
    try:
        root_stat = os.lstat(root)
    except OSError:
        return [(".", 0, "root-stat-error")]
    if stat.S_ISLNK(root_stat.st_mode):
        return [(".", 0, "symlink-not-allowed")]
    if not stat.S_ISDIR(root_stat.st_mode):
        return [(".", 0, "root-not-directory")]

    findings: set[Diagnostic] = {(".", 0, issue) for issue in validate_policy()}
    findings.update(_governance_diagnostics(root))
    worklist = [root]
    while worklist:
        directory = worklist.pop()
        try:
            entries = sorted(os.scandir(directory), key=lambda entry: entry.name)
        except OSError:
            findings.add((str(directory.relative_to(root)), 0, "traversal-error"))
            continue
        for entry in entries:
            path, relative = Path(entry.path), str(Path(entry.path).relative_to(root))
            try:
                metadata = os.lstat(path)
            except OSError:
                findings.add((relative, 0, "stat-error"))
                continue
            if stat.S_ISLNK(metadata.st_mode):
                findings.add((relative, 0, "symlink-not-allowed"))
            elif entry.name in EXCLUDED_DIRECTORIES and stat.S_ISDIR(metadata.st_mode):
                continue
            elif stat.S_ISDIR(metadata.st_mode):
                worklist.append(path)
            elif stat.S_ISREG(metadata.st_mode) and path.suffix == ".py":
                try:
                    tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
                except (OSError, SyntaxError, UnicodeDecodeError) as error:
                    findings.add((relative, getattr(error, "lineno", 0) or 0, "scan-error"))
                    continue
                visitor = _Imports(relative)
                visitor.visit(tree)
                findings.update(visitor.findings)
    return sorted(findings)


def main(argv: list[str]) -> int:
    findings = scan_tree(Path(argv[1]) if len(argv) == 2 else Path.cwd())
    for path, line, reason in findings:
        print(f"{path}:{line}:{reason}", file=sys.stderr)
    return int(bool(findings))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
