"""Testes unitários para TemplatesAnalyzer."""


from codehealthanalyzer.analyzers.templates import TemplatesAnalyzer


def _make(tmp_path, templates_subdir="templates", extra_config=None):
    config = {"templates_dir": [templates_subdir], "no_default_excludes": True}
    if extra_config:
        config.update(extra_config)
    return TemplatesAnalyzer(str(tmp_path), config=config)


def _write_html(tmp_path, content, subdir="templates", name="tpl.html"):
    d = tmp_path / subdir
    d.mkdir(parents=True, exist_ok=True)
    f = d / name
    f.write_text(content, encoding="utf-8")
    return f


# ---------------------------------------------------------------------------
# analyze — diretório inexistente
# ---------------------------------------------------------------------------


def test_analyze_empty_report_when_no_templates_dir(tmp_path):
    analyzer = TemplatesAnalyzer(
        str(tmp_path), config={"templates_dir": ["nonexistent"]}
    )
    report = analyzer.analyze()
    assert report["templates"] == []
    assert report["statistics"]["total_templates"] == 0
    assert report["metadata"]["total_templates"] == 0


# ---------------------------------------------------------------------------
# analyze — detecção de conteúdo inline
# ---------------------------------------------------------------------------


def test_analyze_file_with_style_tag(tmp_path):
    _write_html(tmp_path, "<html><style>body{color:red;}</style></html>")
    report = _make(tmp_path).analyze()
    assert len(report["templates"]) == 1
    tpl = report["templates"][0]
    assert len(tpl["css_style_tags"]) == 1
    assert tpl["total_css_chars"] > 0


def test_analyze_file_with_inline_style(tmp_path):
    _write_html(tmp_path, '<html><p style="color:red;">hi</p></html>')
    report = _make(tmp_path).analyze()
    assert len(report["templates"]) == 1
    tpl = report["templates"][0]
    assert len(tpl["css_inline"]) == 1


def test_analyze_file_with_script_tag(tmp_path):
    _write_html(tmp_path, "<html><script>console.log(1);</script></html>")
    report = _make(tmp_path).analyze()
    assert len(report["templates"]) == 1
    tpl = report["templates"][0]
    assert len(tpl["js_script_tags"]) == 1
    assert tpl["total_js_chars"] > 0


def test_analyze_file_with_event_handler(tmp_path):
    _write_html(tmp_path, '<html><button onclick="doSomething()">btn</button></html>')
    report = _make(tmp_path).analyze()
    assert len(report["templates"]) == 1
    tpl = report["templates"][0]
    assert len(tpl["js_inline"]) == 1


def test_analyze_file_external_script_ignored(tmp_path):
    _write_html(tmp_path, '<html><script src="/app.js"></script></html>')
    report = _make(tmp_path).analyze()
    # template sem inline não aparece no relatório
    assert len(report["templates"]) == 0


def test_analyze_file_html_comment_ignored(tmp_path):
    _write_html(tmp_path, "<!-- <style>body{color:red;}</style> --><html></html>")
    report = _make(tmp_path).analyze()
    assert len(report["templates"]) == 0


def test_analyze_clean_template_not_included(tmp_path):
    _write_html(tmp_path, "<html><body><p>clean</p></body></html>")
    report = _make(tmp_path).analyze()
    assert len(report["templates"]) == 0


# ---------------------------------------------------------------------------
# priority
# ---------------------------------------------------------------------------


def test_analyze_priority_high(tmp_path):
    # > 20000 chars de CSS → high
    big_css = "a { color: red; } " * 1200  # ~21600 chars
    _write_html(tmp_path, f"<html><style>{big_css}</style></html>")
    report = _make(tmp_path).analyze()
    assert report["templates"][0]["priority"] == "high"


def test_analyze_priority_medium(tmp_path):
    # > 10000 chars mas < 20000
    medium_css = "a { color: red; } " * 600  # ~10800 chars
    _write_html(tmp_path, f"<html><style>{medium_css}</style></html>")
    report = _make(tmp_path).analyze()
    assert report["templates"][0]["priority"] == "medium"


def test_analyze_priority_low(tmp_path):
    _write_html(tmp_path, "<html><style>body{color:red;}</style></html>")
    report = _make(tmp_path).analyze()
    assert report["templates"][0]["priority"] == "low"


# ---------------------------------------------------------------------------
# analyze — estrutura do relatório
# ---------------------------------------------------------------------------


def test_analyze_returns_required_keys(tmp_path):
    _write_html(tmp_path, "<html><style>x{}</style></html>")
    report = _make(tmp_path).analyze()
    assert "metadata" in report
    assert "templates" in report
    assert "statistics" in report


def test_analyze_statistics_correct(tmp_path):
    _write_html(tmp_path, "<html><style>body{color:red;}</style></html>", name="a.html")
    _write_html(tmp_path, '<html><p style="color:blue;">hi</p></html>', name="b.html")
    report = _make(tmp_path).analyze()
    assert report["statistics"]["total_templates"] == 2
    assert report["statistics"]["templates_with_css"] == 2
    assert report["statistics"]["total_css_chars"] > 0


def test_analyze_multiple_templates_dirs(tmp_path):
    _write_html(
        tmp_path, "<html><style>a{}</style></html>", subdir="tpl1", name="a.html"
    )
    _write_html(
        tmp_path, "<html><style>b{}</style></html>", subdir="tpl2", name="b.html"
    )
    analyzer = TemplatesAnalyzer(
        str(tmp_path),
        config={"templates_dir": ["tpl1", "tpl2"], "no_default_excludes": True},
    )
    report = analyzer.analyze()
    assert report["statistics"]["total_templates"] == 2
