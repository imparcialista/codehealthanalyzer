"""Testes unitários para ViolationsAnalyzer."""

import textwrap

from codehealthanalyzer.analyzers.violations import ViolationsAnalyzer


def _make(tmp_path, config=None):
    return ViolationsAnalyzer(str(tmp_path), config=config)


def _py_file(tmp_path, content, name="module.py"):
    f = tmp_path / name
    f.write_text(textwrap.dedent(content), encoding="utf-8")
    return f


def _html_file(tmp_path, lines, name="tpl.html"):
    content = "\n".join(f"<p>line {i}</p>" for i in range(lines))
    f = tmp_path / name
    f.write_text(content, encoding="utf-8")
    return f


# ---------------------------------------------------------------------------
# check_file — Python
# ---------------------------------------------------------------------------


def test_check_file_python_no_violations(tmp_path):
    f = _py_file(tmp_path, "x = 1\ny = 2\n")
    result = _make(tmp_path, {"no_default_excludes": True}).check_file(f)
    assert result["violations"] == []
    assert result["priority"] == "low"
    assert result["type"] == "Python"


def test_check_file_python_function_warning(tmp_path):
    # 31 lines inside function body → yellow threshold (30)
    body = "\n".join(f"    x{i} = {i}" for i in range(31))
    src = f"def foo():\n{body}\n"
    f = _py_file(tmp_path, src)
    result = _make(tmp_path, {"no_default_excludes": True}).check_file(f)
    assert any("foo" in v for v in result["violations"])
    assert result["priority"] == "medium"


def test_check_file_python_function_violation(tmp_path):
    # 51 lines → red threshold (50)
    body = "\n".join(f"    x{i} = {i}" for i in range(51))
    src = f"def big():\n{body}\n"
    f = _py_file(tmp_path, src)
    result = _make(tmp_path, {"no_default_excludes": True}).check_file(f)
    assert any("big" in v for v in result["violations"])
    assert result["priority"] == "high"


def test_check_file_python_class_warning(tmp_path):
    # 301 lines in class body → yellow (300)
    body = "\n".join(f"    x{i} = {i}" for i in range(301))
    src = f"class Foo:\n{body}\n"
    f = _py_file(tmp_path, src)
    result = _make(tmp_path, {"no_default_excludes": True}).check_file(f)
    assert any("Foo" in v for v in result["violations"])


def test_check_file_python_syntax_error(tmp_path):
    f = _py_file(tmp_path, "def broken(\n")
    result = _make(tmp_path, {"no_default_excludes": True}).check_file(f)
    assert result["priority"] == "medium"
    assert len(result["violations"]) > 0


# ---------------------------------------------------------------------------
# check_file — HTML
# ---------------------------------------------------------------------------


def test_check_file_html_no_violations(tmp_path):
    f = _html_file(tmp_path, 100)  # < 150 yellow
    result = _make(tmp_path, {"no_default_excludes": True}).check_file(f)
    assert result["violations"] == []
    assert result["type"] == "HTML Template"


def test_check_file_html_warning(tmp_path):
    f = _html_file(tmp_path, 160)  # 151-200 → yellow
    result = _make(tmp_path, {"no_default_excludes": True}).check_file(f)
    assert len(result["violations"]) > 0
    assert result["priority"] == "medium"


def test_check_file_html_violation(tmp_path):
    f = _html_file(tmp_path, 210)  # > 200 → red
    result = _make(tmp_path, {"no_default_excludes": True}).check_file(f)
    assert result["priority"] == "high"


# ---------------------------------------------------------------------------
# analyze
# ---------------------------------------------------------------------------


def test_analyze_returns_required_keys(tmp_path):
    _py_file(tmp_path, "x = 1\n")
    report = _make(tmp_path, {"no_default_excludes": True}).analyze()
    assert "metadata" in report
    assert "violations" in report
    assert "warnings" in report
    assert "statistics" in report


def test_analyze_separates_violations_from_warnings(tmp_path):
    # high violation: function > 50 lines
    body_high = "\n".join(f"    x{i} = {i}" for i in range(51))
    _py_file(tmp_path, f"def big():\n{body_high}\n", "high.py")

    # medium warning: function 31-50 lines
    body_med = "\n".join(f"    x{i} = {i}" for i in range(31))
    _py_file(tmp_path, f"def med():\n{body_med}\n", "medium.py")

    report = _make(tmp_path, {"no_default_excludes": True}).analyze()
    high_files = {v["file"] for v in report["violations"]}
    warn_files = {v["file"] for v in report["warnings"]}
    assert any("high" in f for f in high_files)
    assert any("medium" in f for f in warn_files)


def test_analyze_skip_excluded_dirs(tmp_path):
    excluded = tmp_path / "vendor"
    excluded.mkdir()
    body = "\n".join(f"    x{i} = {i}" for i in range(51))
    (excluded / "big.py").write_text(f"def foo():\n{body}\n")

    report = _make(
        tmp_path, {"exclude_dirs": ["vendor"], "no_default_excludes": True}
    ).analyze()
    all_files = [v["file"] for v in report["violations"] + report["warnings"]]
    assert not any("vendor" in f for f in all_files)


def test_analyze_statistics_counts_python_and_html(tmp_path):
    _py_file(tmp_path, "x = 1\n")
    _html_file(tmp_path, 10)
    report = _make(tmp_path, {"no_default_excludes": True}).analyze()
    assert report["statistics"]["python_files"] >= 1
    assert report["statistics"]["html_files"] >= 1


def test_analyze_clean_project_no_violations(minimal_project):
    # minimal_project tem apenas __init__.py com "x = 1"
    report = ViolationsAnalyzer(
        str(minimal_project), config={"no_default_excludes": True}
    ).analyze()
    assert report["violations"] == []
    assert report["warnings"] == []
