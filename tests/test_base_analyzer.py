"""Testes para BaseAnalyzer."""

import pytest

from codehealthanalyzer.analyzers.base import BaseAnalyzer


def _make(tmp_path, config=None):
    return BaseAnalyzer(str(tmp_path), config=config)


# ---------------------------------------------------------------------------
# iter_files
# ---------------------------------------------------------------------------


def test_iter_files_finds_py_files(tmp_path):
    (tmp_path / "a.py").write_text("x = 1")
    (tmp_path / "b.py").write_text("y = 2")
    (tmp_path / "c.txt").write_text("ignored")

    analyzer = _make(tmp_path)
    found = list(analyzer.iter_files(["*.py"]))
    names = {f.name for f in found}
    assert "a.py" in names
    assert "b.py" in names
    assert "c.txt" not in names


def test_iter_files_finds_nested_files(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "nested.py").write_text("z = 3")

    analyzer = _make(tmp_path)
    found = list(analyzer.iter_files(["*.py"]))
    assert any(f.name == "nested.py" for f in found)


def test_iter_files_multiple_patterns(tmp_path):
    (tmp_path / "a.py").write_text("")
    (tmp_path / "b.html").write_text("")

    analyzer = _make(tmp_path)
    found = list(analyzer.iter_files(["*.py", "*.html"]))
    names = {f.name for f in found}
    assert "a.py" in names
    assert "b.html" in names


# ---------------------------------------------------------------------------
# should_skip — defaults
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "dirname", [".venv", "venv", "node_modules", "__pycache__", ".git"]
)
def test_should_skip_default_dirs(tmp_path, dirname):
    target = tmp_path / dirname / "file.py"
    analyzer = _make(tmp_path)
    assert analyzer.should_skip(target) is True


def test_should_skip_normal_dir_not_skipped(tmp_path):
    target = tmp_path / "src" / "file.py"
    analyzer = _make(tmp_path)
    assert analyzer.should_skip(target) is False


# ---------------------------------------------------------------------------
# should_skip — user exclude_dirs
# ---------------------------------------------------------------------------


def test_should_skip_user_exclude(tmp_path):
    target = tmp_path / "myvendor" / "file.py"
    analyzer = _make(
        tmp_path, config={"exclude_dirs": ["myvendor"], "no_default_excludes": True}
    )
    assert analyzer.should_skip(target) is True


def test_should_skip_user_exclude_string(tmp_path):
    target = tmp_path / "legacy" / "file.py"
    analyzer = _make(
        tmp_path, config={"exclude_dirs": "legacy", "no_default_excludes": True}
    )
    assert analyzer.should_skip(target) is True


# ---------------------------------------------------------------------------
# no_default_excludes
# ---------------------------------------------------------------------------


def test_no_default_excludes_bypasses_venv(tmp_path):
    target = tmp_path / ".venv" / "file.py"
    analyzer = _make(tmp_path, config={"no_default_excludes": True})
    assert analyzer.should_skip(target) is False


def test_no_default_excludes_still_applies_user_excludes(tmp_path):
    target = tmp_path / "custom" / "file.py"
    analyzer = _make(
        tmp_path, config={"no_default_excludes": True, "exclude_dirs": ["custom"]}
    )
    assert analyzer.should_skip(target) is True


# ---------------------------------------------------------------------------
# relpath
# ---------------------------------------------------------------------------


def test_relpath_returns_posix_string(tmp_path):
    file_path = tmp_path / "pkg" / "module.py"
    analyzer = _make(tmp_path)
    result = analyzer.relpath(file_path)
    assert result == "pkg/module.py"


def test_relpath_fallback_for_outside_path(tmp_path, tmp_path_factory):
    other = tmp_path_factory.mktemp("other") / "file.py"
    analyzer = _make(tmp_path)
    result = analyzer.relpath(other)
    assert "file.py" in result
