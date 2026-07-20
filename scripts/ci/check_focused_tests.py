"""Fail-closed, collection-independent structural pytest policy scanner."""

from __future__ import annotations

import ast
import os
import stat
import sys
from pathlib import Path
from typing import Literal

Diagnostic = tuple[str, int, str, str]
AliasKind = Literal["importlib-module", "dynamic-import-callable", "ambiguous"]
Environment = dict[str, AliasKind]
MAX_FILE_BYTES = 1024 * 1024
MAX_TOTAL_BYTES = 64 * 1024 * 1024
MAX_FILES = 10_000
MAX_ENTRIES = 100_000
EXCLUDED = frozenset(
    {
        ".git",
        ".venv",
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        ".pyright",
        ".cache",
    }
)
REWRITE = (
    "rewrite to an allowed direct spelling, remove the focused construct, "
    "or propose a separately reviewed SDD grammar"
)
REMOVE_RUNTIME = "remove the runtime pytest control"
REMOVE_MUTATION = "remove pytestmark mutation or use a direct assignment"


def _mentions_api(node: ast.AST) -> bool:
    return any(
        isinstance(part, ast.Name) and part.id in {"pytest", "unittest"} for part in ast.walk(node)
    )


def _dotted(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _dotted(node.value)
        return f"{base}.{node.attr}" if base else None
    return None


def _is_pytestmark_target(node: ast.expr) -> bool:
    return (
        isinstance(node, ast.Name)
        and node.id == "pytestmark"
        or (
            isinstance(node, ast.Subscript)
            and isinstance(node.value, ast.Name)
            and node.value.id == "pytestmark"
        )
    )


class _Policy(ast.NodeVisitor):
    def __init__(self, path: str) -> None:
        self.path = path
        self.findings: set[Diagnostic] = set()
        self.handled: set[int] = set()
        self.environments: list[Environment] = [self._fresh_environment()]
        self.reported_import_aliases: set[str] = set()

    def add(self, node: ast.AST, reason: str, remediation: str = REWRITE) -> None:
        self.findings.add((self.path, getattr(node, "lineno", 0), reason, remediation))

    def claim(self, node: ast.AST, reason: str | None = None, remediation: str = REWRITE) -> None:
        self.handled.update(id(part) for part in ast.walk(node))
        if reason:
            self.add(node, reason, remediation)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name == "importlib":
                self._environment()[alias.asname or alias.name] = "importlib-module"
                if alias.asname is not None:
                    self.reported_import_aliases.add(alias.asname)
            if alias.name == "pytest" and alias.asname is None:
                continue
            if alias.name in {"pytest", "unittest"} or alias.name.startswith(
                ("pytest.", "unittest.")
            ):
                self.claim(node, "unsupported-test-api")
                return
            if alias.name == "importlib" and alias.asname is not None:
                self.claim(
                    node,
                    "unsupported-dynamic-import",
                    "remove the dynamic import or use canonical import pytest",
                )
                return
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module == "importlib":
            for alias in node.names:
                if alias.name in {"import_module", "__import__"}:
                    self._environment()[alias.asname or alias.name] = "dynamic-import-callable"
                    self.reported_import_aliases.add(alias.asname or alias.name)
        if (node.module or "").split(".")[0] in {"pytest", "unittest"}:
            self.claim(node, "unsupported-test-api")
            return
        if node.module == "importlib" and any(
            alias.name == "import_module" for alias in node.names
        ):
            self.claim(
                node,
                "unsupported-dynamic-import",
                "remove the dynamic import or use canonical import pytest",
            )
            return
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        targets_pytestmark = any(_is_pytestmark_target(target) for target in node.targets)
        if targets_pytestmark:
            if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
                self.claim(node, "pytestmark-mutation", REMOVE_MUTATION)
            elif self._valid_pytestmark(node.value):
                self.claim(node)
            else:
                self.claim(node, "pytestmark-mutation", REMOVE_MUTATION)
            return
        if _mentions_api(node.value):
            self.claim(node, "unsupported-test-api")
            return
        self.visit(node.value)
        self._assign(
            node.value, [target.id for target in node.targets if isinstance(target, ast.Name)]
        )
        for target in node.targets:
            if not isinstance(target, ast.Name):
                self.visit(target)
        return

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if _is_pytestmark_target(node.target):
            self.claim(node, "pytestmark-mutation", REMOVE_MUTATION)
            return
        if (node.value and _mentions_api(node.value)) or _mentions_api(node.annotation):
            self.claim(node, "unsupported-test-api")
            return
        self.visit(node.annotation)
        if node.value is not None:
            self.visit(node.value)
            if isinstance(node.target, ast.Name):
                self._assign(node.value, [node.target.id])
        self.visit(node.target)

    def visit_If(self, node: ast.If) -> None:
        self.visit(node.test)
        before = self._environment().copy()
        self.environments[-1] = before.copy()
        for statement in node.body:
            self.visit(statement)
        body = self._environment().copy()
        self.environments[-1] = before.copy()
        for statement in node.orelse:
            self.visit(statement)
        otherwise = self._environment().copy()
        self.environments[-1] = self._merge_environments(body, otherwise)

    def visit_While(self, node: ast.While) -> None:
        self._visit_control_flow(node)

    def visit_For(self, node: ast.For) -> None:
        self._visit_control_flow(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self._visit_control_flow(node)

    def visit_Try(self, node: ast.Try) -> None:
        self._visit_control_flow(node)

    def visit_TryStar(self, node: ast.TryStar) -> None:
        self._visit_control_flow(node)

    def visit_Match(self, node: ast.Match) -> None:
        self._visit_control_flow(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        if _is_pytestmark_target(node.target):
            self.claim(node, "pytestmark-mutation", REMOVE_MUTATION)
            return
        self.generic_visit(node)

    def visit_Delete(self, node: ast.Delete) -> None:
        if any(_is_pytestmark_target(target) for target in node.targets):
            self.claim(node, "pytestmark-mutation", REMOVE_MUTATION)
            return
        self.generic_visit(node)

    def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
        if _is_pytestmark_target(node.target):
            self.claim(node, "pytestmark-mutation", REMOVE_MUTATION)
            return
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._decorators(node.decorator_list)
        self._annotations(node)
        self._definition_defaults(node.args)
        self._scope(node.body)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._decorators(node.decorator_list)
        self._annotations(node)
        self._definition_defaults(node.args)
        self._scope(node.body)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._decorators(node.decorator_list)
        for expression in (*node.bases, *(keyword.value for keyword in node.keywords)):
            self.visit(expression)
        self._scope(node.body)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        self._definition_defaults(node.args)
        self.environments.append(self._fresh_environment())
        self.visit(node.body)
        self.environments.pop()

    def visit_Call(self, node: ast.Call) -> None:
        if id(node) in self.handled:
            return
        if isinstance(node.func, ast.Attribute) and _is_pytestmark_target(node.func.value):
            self.claim(node, "pytestmark-mutation", REMOVE_MUTATION)
            return
        if self._dynamic_import(node):
            return
        spelling = _dotted(node.func)
        if spelling in {"pytest.skip", "pytest.xfail", "pytest.skipif"}:
            self.claim(node, "prohibited-runtime-control", REMOVE_RUNTIME)
        elif _mentions_api(node):
            self.claim(node, "unsupported-test-api")
        else:
            self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if id(node) not in self.handled and _mentions_api(node):
            self.claim(node, "unsupported-test-api")
        elif id(node) not in self.handled:
            self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if id(node) not in self.handled and node.id in {"pytest", "unittest"}:
            self.claim(node, "unsupported-test-api")

    def _decorators(self, decorators: list[ast.expr]) -> None:
        for decorator in decorators:
            if self._fixture(decorator) or self._parametrize(decorator):
                self.claim(decorator)
            elif _mentions_api(decorator):
                self.claim(decorator, "unsupported-test-api")

    def _annotations(self, function: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        annotations = [
            argument.annotation for argument in (*function.args.args, *function.args.kwonlyargs)
        ]
        annotations.extend(
            [
                function.args.vararg.annotation if function.args.vararg else None,
                function.args.kwarg.annotation if function.args.kwarg else None,
                function.returns,
            ]
        )
        for annotation in annotations:
            if annotation is None:
                continue
            if _dotted(annotation) == "pytest.MonkeyPatch":
                self.claim(annotation)
            elif _mentions_api(annotation):
                self.claim(annotation, "unsupported-test-api")

    @staticmethod
    def _fixture(node: ast.expr) -> bool:
        return (
            isinstance(node, ast.Call)
            and _dotted(node.func) == "pytest.fixture"
            and not node.args
            and len(node.keywords) == 1
            and node.keywords[0].arg == "scope"
            and isinstance(node.keywords[0].value, ast.Constant)
            and node.keywords[0].value.value == "session"
        )

    def _parametrize(self, node: ast.expr) -> bool:
        if not isinstance(node, ast.Call) or _dotted(node.func) != "pytest.mark.parametrize":
            return False
        if len(node.args) != 2 or any(keyword.arg != "ids" for keyword in node.keywords):
            self.claim(
                node, "unsupported-parametrize-argument", "use literal containers or a direct Name"
            )
            return True
        if not self._parameter_names(node.args[0]):
            self.claim(
                node.args[0],
                "unsupported-parametrize-argument",
                "use literal containers or a direct Name",
            )
            return True
        for value in [node.args[1], *(keyword.value for keyword in node.keywords)]:
            invalid = self._invalid_value(value)
            if invalid:
                self.claim(
                    invalid,
                    "unsupported-parametrize-argument",
                    "use literal containers or a direct Name",
                )
                return True
        return True

    @staticmethod
    def _parameter_names(node: ast.expr) -> bool:
        return (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            or (
                isinstance(node, ast.Tuple)
                and all(
                    isinstance(item, ast.Constant) and isinstance(item.value, str)
                    for item in node.elts
                )
            )
        )

    def _invalid_value(self, node: ast.expr) -> ast.expr | None:
        if isinstance(node, ast.Name):
            return None
        if isinstance(node, ast.Constant) and (
            node.value is None or isinstance(node.value, (str, int, float, complex, bool))
        ):
            return None
        if isinstance(node, (ast.List, ast.Tuple)):
            return next(
                (invalid for item in node.elts if (invalid := self._invalid_value(item))), None
            )
        return node

    @staticmethod
    def _valid_pytestmark(node: ast.expr) -> bool:
        if _dotted(node) == "pytest.mark.ci_recipe":
            return True
        return (
            isinstance(node, ast.Tuple)
            and len(node.elts) == 1
            and _dotted(node.elts[0]) == "pytest.mark.ci_recipe"
        )

    def _dynamic_import(self, node: ast.Call) -> bool:
        kind = self._dynamic_import_kind(node.func)
        if kind is None:
            return False
        target = (
            node.args[0]
            if node.args
            else next((keyword.value for keyword in node.keywords if keyword.arg == "name"), None)
        )
        if isinstance(target, ast.Constant) and target.value in {"pytest", "unittest"}:
            if kind == "ambiguous":
                self.claim(
                    node,
                    "ambiguous-dynamic-import-alias",
                    "rewrite to a direct unambiguous dynamic import or remove the dynamic import",
                )
                return True
            self.claim(
                node,
                "unsupported-dynamic-import",
                "remove the dynamic import or use canonical import pytest",
            )
            return True
        return False

    def _environment(self) -> Environment:
        return self.environments[-1]

    @staticmethod
    def _fresh_environment() -> Environment:
        return {"importlib": "importlib-module", "__import__": "dynamic-import-callable"}

    def _visit_control_flow(self, node: ast.AST) -> None:
        before = self._environment().copy()
        self.generic_visit(node)
        self.environments[-1] = before

    def _assign(self, value: ast.expr, targets: list[str]) -> None:
        kind = self._classify(value)
        for target in targets:
            if kind is None:
                self._environment().pop(target, None)
            else:
                self._environment()[target] = kind
        if (
            isinstance(value, ast.Attribute)
            and isinstance(value.value, ast.Name)
            and value.value.id in self.reported_import_aliases
        ):
            self.reported_import_aliases.update(targets)

    def _classify(self, value: ast.expr) -> AliasKind | None:
        if isinstance(value, ast.Name):
            return self._environment().get(value.id)
        if (
            isinstance(value, ast.Attribute)
            and value.attr in {"import_module", "__import__"}
            and isinstance(value.value, ast.Name)
            and self._environment().get(value.value.id) == "importlib-module"
        ):
            return "dynamic-import-callable"
        return None

    def _dynamic_import_kind(self, function: ast.expr) -> AliasKind | None:
        if isinstance(function, ast.Name):
            if function.id in self.reported_import_aliases:
                return None
            return self._environment().get(function.id)
        if (
            isinstance(function, ast.Attribute)
            and function.attr in {"import_module", "__import__"}
            and isinstance(function.value, ast.Name)
            and function.value.id not in self.reported_import_aliases
        ):
            receiver_kind = self._environment().get(function.value.id)
            if receiver_kind == "importlib-module":
                return "dynamic-import-callable"
            if receiver_kind == "ambiguous":
                return "ambiguous"
        return None

    @staticmethod
    def _merge_environments(body: Environment, otherwise: Environment) -> Environment:
        return {
            name: body[name] if body.get(name) == otherwise.get(name) else "ambiguous"
            for name in body.keys() | otherwise.keys()
            if body.get(name) is not None or otherwise.get(name) is not None
        }

    def _scope(self, body: list[ast.stmt]) -> None:
        self.environments.append(self._fresh_environment())
        for statement in body:
            self.visit(statement)
        self.environments.pop()

    def _definition_defaults(self, arguments: ast.arguments) -> None:
        defaults = (*arguments.defaults, *(default for default in arguments.kw_defaults if default))
        for expression in defaults:
            self.visit(expression)


def scan_file(path: Path, root: Path, raw: bytes) -> list[Diagnostic]:
    relative = _relative(path, root)
    try:
        tree = ast.parse(raw.decode("utf-8"), filename=str(path))
    except UnicodeDecodeError:
        return [(relative, 0, "decode-error", "restore UTF-8 source")]
    except SyntaxError as error:
        return [(relative, error.lineno or 0, "syntax-error", "fix Python syntax")]
    policy = _Policy(relative)
    policy.visit(tree)
    return sorted(policy.findings)


def _relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return "."


def scan_tree(requested_root: Path) -> list[Diagnostic]:
    root = requested_root.absolute()
    try:
        root_stat = os.lstat(root)
    except OSError:
        return [(".", 0, "stat-error", "restore the scan root")]
    if stat.S_ISLNK(root_stat.st_mode):
        return [(".", 0, "symlink-not-allowed", "scan a real directory")]
    if not stat.S_ISDIR(root_stat.st_mode):
        return [(".", 0, "root-not-directory", "scan a directory")]

    findings: set[Diagnostic] = set()
    worklist, files, total_bytes, entries_seen = [root], 0, 0, 0
    while worklist:
        directory = worklist.pop()
        batch: list[os.DirEntry[str]] = []
        try:
            with os.scandir(directory) as entries:
                for entry in entries:
                    entries_seen += 1
                    path = Path(entry.path)
                    relative = _relative(path, root)
                    if entries_seen > MAX_ENTRIES:
                        limit = (
                            relative,
                            0,
                            "resource-limit-entries",
                            "reduce encountered entries to at most 100,000",
                        )
                        return sorted(findings | {limit})
                    batch.append(entry)
        except OSError:
            findings.add(
                (
                    _relative(directory, root),
                    0,
                    "traversal-error",
                    "restore readable directory traversal",
                )
            )
            continue
        children: list[Path] = []
        for entry in sorted(batch, key=lambda candidate: candidate.name):
            path = Path(entry.path)
            relative = _relative(path, root)
            try:
                metadata = os.lstat(path)
            except OSError:
                findings.add((relative, 0, "stat-error", "restore readable filesystem metadata"))
                continue
            if stat.S_ISLNK(metadata.st_mode):
                findings.add(
                    (
                        relative,
                        0,
                        "symlink-not-allowed",
                        "replace the symlink with a regular file or directory",
                    )
                )
            elif entry.name in EXCLUDED and stat.S_ISDIR(metadata.st_mode):
                continue
            elif stat.S_ISDIR(metadata.st_mode):
                children.append(path)
            elif stat.S_ISREG(metadata.st_mode) and path.suffix == ".py":
                files += 1
                if files > MAX_FILES:
                    limit = (
                        relative,
                        0,
                        "resource-limit-files",
                        "reduce in-scope Python files to at most 10,000",
                    )
                    return sorted(findings | {limit})
                if metadata.st_size > MAX_FILE_BYTES:
                    limit = (
                        relative,
                        0,
                        "resource-limit-file",
                        "reduce the Python file to at most 1 MiB",
                    )
                    return sorted(findings | {limit})
                if total_bytes + metadata.st_size > MAX_TOTAL_BYTES:
                    limit = (
                        relative,
                        0,
                        "resource-limit-total",
                        "reduce total scanned Python bytes to at most 64 MiB",
                    )
                    return sorted(findings | {limit})
                try:
                    raw = path.read_bytes()
                except OSError:
                    findings.add((relative, 0, "read-error", "restore readable UTF-8 source"))
                    continue
                if len(raw) != metadata.st_size:
                    findings.add(
                        (relative, 0, "read-error", "restore a stable readable Python file")
                    )
                    continue
                total_bytes += len(raw)
                findings.update(scan_file(path, root, raw))
        worklist.extend(reversed(children))
    return sorted(findings)


def main(argv: list[str]) -> int:
    findings = scan_tree(Path(argv[1]) if len(argv) == 2 else Path.cwd())
    for path, line, reason, remediation in findings:
        print(f"{path}:{line}: {reason}: {remediation}", file=sys.stderr)
    return int(bool(findings))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
