"""Unit tests for the repository code-standards checker."""
from pathlib import Path

from scripts.check_code_standards import (
    ROOT,
    discover_files,
    inspect_file,
    is_test_file,
    nonblank_line_count,
)


def test_nonblank_line_count_counts_comments_but_not_blank_lines():
    assert nonblank_line_count("one\n\n# comment\n  \n two\n") == 3


def test_test_file_detection_uses_path_and_filename():
    assert is_test_file(Path("tests/test_rules.py"))
    assert is_test_file(Path("e2e/dashboard.spec.ts"))
    assert not is_test_file(Path("crm_signals/api.py"))


def test_production_file_warning_is_not_a_failure(tmp_path):
    path = tmp_path / "large_module.py"
    path.write_text("\n".join(f"value_{index} = {index}" for index in range(501)))
    warnings, errors = inspect_file(path, {})
    assert any("review/refactor threshold is 500" in item for item in warnings)
    assert errors == []


def test_production_file_hard_limit_fails(tmp_path):
    path = tmp_path / "oversized_module.py"
    path.write_text("\n".join(f"value_{index} = {index}" for index in range(801)))
    warnings, errors = inspect_file(path, {})
    assert warnings == []
    assert any("hard limit is 800" in item for item in errors)


def test_python_function_limit_is_enforced(tmp_path):
    path = tmp_path / "module.py"
    body = "\n".join(f"    value_{index} = {index}" for index in range(101))
    path.write_text(f"def oversized():\n{body}\n")
    warnings, errors = inspect_file(path, {})
    assert any("hard function limit is 100" in item for item in errors)


def test_test_file_uses_more_permissive_thresholds(tmp_path):
    path = tmp_path / "test_large.py"
    path.write_text("\n".join(f"value_{index} = {index}" for index in range(900)))
    warnings, errors = inspect_file(path, {})
    assert any("review/refactor threshold is 800" in item for item in warnings)
    assert errors == []


def test_discover_files_ignores_non_code_and_generated_assets(tmp_path, monkeypatch):
    source = tmp_path / "sample.py"
    source.write_text("value = 1\n")
    markdown = tmp_path / "notes.md"
    markdown.write_text("# Notes\n")
    generated = tmp_path / "bundle.min.js"
    generated.write_text("minified()\n")
    monkeypatch.setattr("scripts.check_code_standards.ROOT", tmp_path)
    found = discover_files([str(source), str(markdown), str(generated)])
    assert found == [source.resolve()]
