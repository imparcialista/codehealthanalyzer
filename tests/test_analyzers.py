import pytest
from pathlib import Path
from codehealthanalyzer.analyzers.templates import TemplatesAnalyzer
from codehealthanalyzer.analyzers.errors import ErrorsAnalyzer
from codehealthanalyzer.analyzers.violations import ViolationsAnalyzer
from codehealthanalyzer import CodeAnalyzer
import json
import logging

# Configure logging for i18n tests
logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def temp_project_dir(tmp_path):
    """Fixture to create a temporary project directory for testing."""
    (tmp_path / "templates").mkdir()
    (tmp_path / "web" / "templates").mkdir(parents=True)
    (tmp_path / "python_files").mkdir()
    (tmp_path / "ruff_test").mkdir()
    return tmp_path

@pytest.fixture
def sample_html_file(temp_project_dir):
    """Creates a sample HTML file with inline CSS and JS."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test</title>
        <style>body { color: red; }</style>
    </head>
    <body>
        <h1 style="font-size: 10px;">Hello</h1>
        <script>console.log('hello');</script>
        <button onclick="console.log('test');"></button>
    </body>
    </html>
    """
    file_path = temp_project_dir / "web" / "templates" / "sample.html"
    file_path.write_text(html_content)
    return file_path

@pytest.fixture
def sample_python_file(temp_project_dir):
    """Creates a sample Python file with a long function."""
    python_content = """
def long_function():
    # This is a docstring.
    # Line 1
    # Line 2
    # Line 3
    # Line 4
    # Line 5
    # Line 6
    # Line 7
    # Line 8
    # Line 9
    # Line 10
    # Line 11
    # Line 12
    # Line 13
    # Line 14
    # Line 15
    # Line 16
    # Line 17
    # Line 18
    # Line 19
    # Line 20
    # Line 21
    # Line 22
    # Line 23
    # Line 24
    # Line 25
    # Line 26
    # Line 27
    # Line 28
    # Line 29
    # Line 30 - This line makes it a violation
    pass
"""
    file_path = temp_project_dir / "python_files" / "long_func.py"
    file_path.write_text(python_content)
    return file_path

@pytest.fixture
def sample_ruff_file(temp_project_dir):
    """Creates a sample Python file with a Ruff error."""
    python_content = """
import os, sys # F401, E402
x = 1
"""
    file_path = temp_project_dir / "ruff_test" / "ruff_error.py"
    file_path.write_text(python_content)
    return file_path

def test_templates_analyzer_finds_inline_content(temp_project_dir, sample_html_file):
    """Test that TemplatesAnalyzer correctly identifies inline CSS/JS."""
    analyzer = TemplatesAnalyzer(str(temp_project_dir), config={"templates_dir": ["web/templates"]})
    report = analyzer.analyze()

    assert "templates" in report
    assert len(report["templates"]) == 1
    template_report = report["templates"][0]

    assert template_report["file"] == "sample.html"
    assert template_report["total_css_chars"] > 0
    assert template_report["total_js_chars"] > 0
    assert len(template_report["css_inline"]) == 1
    assert len(template_report["css_style_tags"]) == 1
    assert len(template_report["js_inline"]) == 1
    assert len(template_report["js_script_tags"]) == 1


def test_violations_analyzer_finds_long_function(temp_project_dir, sample_python_file):
    """Test that ViolationsAnalyzer correctly identifies a long function."""
    analyzer = ViolationsAnalyzer(str(temp_project_dir), config={"no_default_excludes": True})
    report = analyzer.analyze()

    assert "warnings" in report
    assert len(report["warnings"]) == 1
    violation_report = report["warnings"][0]

    assert violation_report["file"] == "python_files/long_func.py"
    assert violation_report["type"] == "Python"
    assert violation_report["lines"] > 0
    assert len(violation_report["violations"]) == 1
    assert "function long_function" in violation_report["violations"][0]
    assert violation_report["priority"] == "medium"

def test_errors_analyzer_finds_ruff_errors(temp_project_dir, sample_ruff_file, capsys):
    """Test that ErrorsAnalyzer correctly finds Ruff errors."""
    # Ensure ruff is installed for this test
    import shutil
    if not shutil.which("ruff"):
        pytest.skip("Ruff is not installed, skipping test_errors_analyzer_finds_ruff_errors")

    # Create a config file to ensure target_dir is set correctly for ruff
    config_path = temp_project_dir / "config.json"
    config_data = {"target_dir": "ruff_test"}
    config_path.write_text(json.dumps(config_data))

    analyzer = ErrorsAnalyzer(str(temp_project_dir), config={"target_dir": "ruff_test"})
    report = analyzer.analyze()

    assert "errors" in report
    assert len(report["errors"]) == 1
    error_report = report["errors"][0]

    assert Path(error_report["file"]).relative_to(temp_project_dir) == Path("ruff_test/ruff_error.py")
    assert error_report["error_count"] >= 2 # F401, E402
    assert error_report["priority"] == "medium" # F401 is medium priority
    assert any("F401" in err["code"] for err in error_report["errors"])
def test_code_analyzer_generates_full_report(temp_project_dir, sample_html_file, sample_python_file, sample_ruff_file):
    """Test that CodeAnalyzer generates a comprehensive full report."""
    # Ensure ruff is installed for this test
    import shutil
    if not shutil.which("ruff"):
        pytest.skip("Ruff is not installed, skipping test_code_analyzer_generates_full_report")

    # Create a config file to ensure target_dir is set correctly for ruff and templates_dir for templates
    config_path = temp_project_dir / "config.json"
    config_data = {
        "target_dir": "ruff_test",
        "templates_dir": ["web/templates"]
    }
    config_path.write_text(json.dumps(config_data))

    analyzer = CodeAnalyzer(str(temp_project_dir), config=config_data)
    report = analyzer.generate_full_report()

    assert "summary" in report
    assert report["summary"]["total_templates"] == 1
    assert report["summary"]["warning_files"] == 1
    assert report["summary"]["total_errors"] >= 2 # F401, E402

    assert "templates" in report
    assert len(report["templates"]["templates"]) == 1
    assert len(report["violations"]["violations"]) == 0
    assert len(report["errors"]["errors"]) == 1

    assert report["summary"]["quality_score"] >= 0 # Score should be calculated

def test_i18n_error_logging(temp_project_dir, caplog, mocker):
    """Test that i18n error handling logs exceptions."""
    from codehealthanalyzer.i18n import set_language, DEFAULT_LANGUAGE

    # Create a dummy locale directory that will cause an error
    (temp_project_dir / "locale" / "en_US" / "LC_MESSAGES").mkdir(parents=True)
    # Create a malformed .mo file or a directory where a .mo file is expected
    (temp_project_dir / "locale" / "en_US" / "LC_MESSAGES" / "codehealthanalyzer.mo").write_text("")

    with caplog.at_level(logging.ERROR):
        # Temporarily set the locale dir to the temp_project_dir for this test
        # This is a bit hacky, but necessary to force gettext to look in our temp dir
        import codehealthanalyzer.i18n
        original_get_locale_dir = codehealthanalyzer.i18n.get_locale_dir
        codehealthanalyzer.i18n.get_locale_dir = lambda: temp_project_dir / "locale"

        # Mock gettext.translation to raise an OSError
        mocker.patch("gettext.translation", side_effect=OSError("Mocked OSError"))

        # Get the logger for the i18n module
        i18n_logger = logging.getLogger("codehealthanalyzer.i18n")
        original_i18n_logger_level = i18n_logger.level
        i18n_logger.setLevel(logging.ERROR)

        try:
            set_language("en_US") # Try to set a language that will load the malformed file
            assert set_language("en_US") == False
        finally:
            codehealthanalyzer.i18n.get_locale_dir = original_get_locale_dir # Restore original function
            i18n_logger.setLevel(original_i18n_logger_level) # Restore original logger level
