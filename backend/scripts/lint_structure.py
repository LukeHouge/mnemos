#!/usr/bin/env python3
"""Structural architecture linter for Mnemos.

Enforces layered architecture rules with remediation instructions in error messages.
These remediation messages are designed to be actionable by both humans and AI agents.

Rules enforced:
  1. Models must not import from routes or services
  2. Routes must not import from other routes
  3. Middleware must not import from routes or services
  4. No inline imports (imports must be at module top level)
  5. Route files must not define Pydantic models (use app/models/)
  6. Files should not exceed a size limit (keeps agent context manageable)

Run: python scripts/lint_structure.py
"""

import ast
import sys
from pathlib import Path

APP_DIR = Path(__file__).parent.parent / "app"
MAX_FILE_LINES = 400

errors: list[str] = []


def add_error(file: Path, line: int, rule: str, message: str, remediation: str) -> None:
    """Record an error with a remediation instruction for agent consumption."""
    rel = file.relative_to(APP_DIR.parent)
    errors.append(f"{rel}:{line}: [{rule}] {message}\n  FIX: {remediation}")


def get_import_module(node: ast.Import | ast.ImportFrom) -> str | None:
    """Extract the top-level module path from an import statement."""
    if isinstance(node, ast.ImportFrom) and node.module:
        return node.module
    return None


def check_layer_violations(file: Path, tree: ast.AST) -> None:
    """Check that import dependencies respect layer boundaries."""
    rel = str(file.relative_to(APP_DIR))

    for node in ast.walk(tree):
        module = get_import_module(node) if isinstance(node, (ast.Import, ast.ImportFrom)) else None
        if not module or not module.startswith("app."):
            continue

        lineno = node.lineno

        # Models must not import routes or services
        if rel.startswith("models/"):
            if ".routes." in module or module.startswith("app.routes"):
                add_error(
                    file,
                    lineno,
                    "LAYER001",
                    f"Model file imports from routes: `{module}`",
                    "Models must be pure data schemas. Move any route-dependent logic to a service, "
                    "then have the route call the service. See docs/architecture.md.",
                )
            if ".services." in module or module.startswith("app.services"):
                add_error(
                    file,
                    lineno,
                    "LAYER002",
                    f"Model file imports from services: `{module}`",
                    "Models must not depend on services. If you need computed fields, add a "
                    "classmethod on the model or create a service function. See docs/architecture.md.",
                )

        # Routes must not import from other route files
        if rel.startswith("routes/"):
            if (".routes." in module or module.startswith("app.routes")) and module != f"app.{rel.replace('/', '.').removesuffix('.py')}":
                add_error(
                    file,
                    lineno,
                    "LAYER003",
                    f"Route file imports from another route: `{module}`",
                    "Routes must not cross-import. Extract shared logic into a service in "
                    "app/services/ and import from there. See docs/architecture.md.",
                )

        # Middleware must not import routes or services
        if rel.startswith("middleware/"):
            if ".routes." in module or module.startswith("app.routes"):
                add_error(
                    file,
                    lineno,
                    "LAYER004",
                    f"Middleware imports from routes: `{module}`",
                    "Middleware must not depend on routes. Middleware processes requests/responses "
                    "generically. See docs/architecture.md.",
                )
            if ".services." in module or module.startswith("app.services"):
                add_error(
                    file,
                    lineno,
                    "LAYER005",
                    f"Middleware imports from services: `{module}`",
                    "Middleware must not depend on services. If you need service logic in middleware, "
                    "reconsider the design - middleware should be generic. See docs/architecture.md.",
                )


def check_inline_imports(file: Path, tree: ast.AST) -> None:
    """Check for imports inside functions/methods (inline imports)."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for child in ast.walk(node):
                if isinstance(child, (ast.Import, ast.ImportFrom)):
                    module = ""
                    if isinstance(child, ast.ImportFrom) and child.module:
                        module = child.module
                    elif isinstance(child, ast.Import) and child.names:
                        module = child.names[0].name
                    # Allow TYPE_CHECKING inline imports
                    if module and "typing" not in module.lower():
                        add_error(
                            file,
                            child.lineno,
                            "IMPORT001",
                            f"Inline import found: `{module}`",
                            "Move this import to the top of the file. All imports must be at module "
                            "level. See docs/style-guide.md.",
                        )


def check_models_in_routes(file: Path, tree: ast.AST) -> None:
    """Check that route files don't define Pydantic models."""
    rel = str(file.relative_to(APP_DIR))
    if not rel.startswith("routes/"):
        return

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                base_name = ""
                if isinstance(base, ast.Name):
                    base_name = base.id
                elif isinstance(base, ast.Attribute):
                    base_name = base.attr
                if base_name in ("BaseModel", "BaseSettings"):
                    add_error(
                        file,
                        node.lineno,
                        "STRUCT001",
                        f"Pydantic model `{node.name}` defined in route file",
                        "Models must live in app/models/. Create or update the appropriate model "
                        "file and import it in the route. See docs/architecture.md.",
                    )


def check_file_size(file: Path) -> None:
    """Check that files don't exceed the size limit."""
    line_count = len(file.read_text().splitlines())
    if line_count > MAX_FILE_LINES:
        add_error(
            file,
            1,
            "SIZE001",
            f"File has {line_count} lines (max {MAX_FILE_LINES})",
            "Split this file into smaller, focused modules. Large files are harder for agents "
            "to reason about and increase context usage. See docs/architecture.md.",
        )


def lint_file(file: Path) -> None:
    """Run all structural checks on a single Python file."""
    try:
        source = file.read_text()
        tree = ast.parse(source, filename=str(file))
    except SyntaxError as e:
        add_error(file, e.lineno or 1, "PARSE001", f"Syntax error: {e.msg}", "Fix the syntax error before continuing.")
        return

    check_layer_violations(file, tree)
    check_inline_imports(file, tree)
    check_models_in_routes(file, tree)
    check_file_size(file)


def main() -> int:
    """Run the structural linter on all Python files in app/."""
    if not APP_DIR.exists():
        print(f"ERROR: App directory not found: {APP_DIR}")
        return 1

    py_files = sorted(APP_DIR.rglob("*.py"))
    if not py_files:
        print("No Python files found in app/")
        return 0

    for f in py_files:
        lint_file(f)

    if errors:
        print(f"Structural lint: {len(errors)} violation(s) found\n")
        for err in errors:
            print(f"  {err}\n")
        return 1

    print(f"Structural lint: OK ({len(py_files)} files checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
