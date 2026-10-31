"""Enforce maintainable source-file and Python function-size guardrails.

The checker deliberately uses graduated thresholds: warnings prompt review; only
large outliers fail CI. It has no third-party dependencies.
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOTS = ("crm_signals", "tests", "e2e", "scripts")
CODE_SUFFIXES = {".py", ".js", ".jsx", ".ts", ".tsx", ".vue"}
IGNORED_PARTS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    "sites",
    "generated",
}
FILE_THRESHOLDS = {
    "production": (500, 800),
    "test": (800, 1200),
}
FUNCTION_THRESHOLDS = {
    "production": (50, 100),
    "test": (80, 150),
}
EXCEPTIONS_PATH = ROOT / "scripts" / "code_standards_exceptions.json"


def is_test_file(path: Path) -> bool:
    """Return whether a source file belongs to a test suite."""
    parts = {part.lower() for part in path.parts}
    name = path.name.lower()
    return bool(
        parts.intersection({"tests", "test", "e2e"})
        or name.startswith("test_")
        or name.endswith((".test.js", ".test.jsx", ".test.ts", ".test.tsx"))
        or name.endswith((".spec.js", ".spec.jsx", ".spec.ts", ".spec.tsx"))
    )


def nonblank_line_count(source: str) -> int:
    """Count non-empty physical lines, including comments for a stable LOC rule."""
    return sum(1 for line in source.splitlines() if line.strip())


def load_exceptions() -> dict[str, str]:
    """Load exact-path exceptions; every exception must include a reason."""
    if not EXCEPTIONS_PATH.exists():
        return {}
    payload = json.loads(EXCEPTIONS_PATH.read_text(encoding="utf-8"))
    exceptions: dict[str, str] = {}
    for item in payload.get("file_exceptions", []):
        path = str(item.get("path", "")).strip()
        reason = str(item.get("reason", "")).strip()
        if not path or not reason:
            raise ValueError("Each file exception must include a path and a reason.")
        exceptions[path] = reason
    return exceptions


def discover_files(arguments: list[str]) -> list[Path]:
    """Resolve passed filenames or scan the standard project source roots."""
    candidates: list[Path] = []
    if arguments:
        for argument in arguments:
            path = Path(argument)
            if not path.is_absolute():
                path = ROOT / path
            if path.is_dir():
                candidates.extend(path.rglob("*"))
            elif path.is_file():
                candidates.append(path)
    else:
        for root_name in DEFAULT_ROOTS:
            root = ROOT / root_name
            if root.exists():
                candidates.extend(root.rglob("*"))

    result = []
    seen = set()
    for path in candidates:
        try:
            resolved = path.resolve()
            relative = resolved.relative_to(ROOT)
        except (OSError, ValueError):
            continue
        if (
            not resolved.is_file()
            or resolved.suffix.lower() not in CODE_SUFFIXES
            or any(part in IGNORED_PARTS for part in relative.parts)
            or resolved.name.endswith(".min.js")
            or ".generated." in resolved.name
            or resolved.name.endswith("_generated.py")
            or resolved in seen
        ):
            continue
        seen.add(resolved)
        result.append(resolved)
    return sorted(result)


def inspect_file(path: Path, exceptions: dict[str, str]) -> tuple[list[str], list[str]]:
    """Return (warnings, errors) for one supported source file."""
    try:
        relative = path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        # Temporary paths are used by unit tests; source discovery still enforces ROOT.
        relative = path.name
    if relative in exceptions:
        return [], []

    source = path.read_text(encoding="utf-8")
    is_test = is_test_file(Path(relative))
    category = "test" if is_test else "production"
    file_warning, file_error = FILE_THRESHOLDS[category]
    count = nonblank_line_count(source)
    warnings: list[str] = []
    errors: list[str] = []

    if count > file_error:
        errors.append(
            f"{relative}: {count} non-blank lines; hard limit is {file_error}."
        )
    elif count > file_warning:
        warnings.append(
            f"{relative}: {count} non-blank lines; review/refactor threshold is {file_warning}."
        )

    if path.suffix.lower() == ".py":
        try:
            tree = ast.parse(source, filename=relative)
        except SyntaxError as error:
            errors.append(f"{relative}: Python syntax error at line {error.lineno}: {error.msg}.")
            return warnings, errors

        function_warning, function_error = FUNCTION_THRESHOLDS[category]
        lines = source.splitlines()
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            end_line = getattr(node, "end_lineno", node.lineno)
            function_lines = nonblank_line_count(
                "\n".join(lines[node.lineno - 1 : end_line])
            )
            label = f"{relative}:{node.lineno} ({node.name})"
            if function_lines > function_error:
                errors.append(
                    f"{label}: {function_lines} non-blank lines; hard function limit is {function_error}."
                )
            elif function_lines > function_warning:
                warnings.append(
                    f"{label}: {function_lines} non-blank lines; review/refactor threshold is {function_warning}."
                )
    return warnings, errors


def main(arguments: list[str] | None = None) -> int:
    """Run the repository standards check."""
    try:
        exceptions = load_exceptions()
        files = discover_files(arguments or [])
        warnings: list[str] = []
        errors: list[str] = []
        for path in files:
            file_warnings, file_errors = inspect_file(path, exceptions)
            warnings.extend(file_warnings)
            errors.extend(file_errors)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
        print(f"Code standards checker failed: {error}", file=sys.stderr)
        return 2

    for message in warnings:
        print(f"WARNING: {message}")
    for message in errors:
        print(f"ERROR: {message}", file=sys.stderr)

    if errors:
        print(f"Code standards failed: {len(errors)} error(s), {len(warnings)} warning(s).")
        return 1
    print(f"Code standards passed: {len(files)} source file(s), {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
