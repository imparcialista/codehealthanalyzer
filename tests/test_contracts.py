from codehealthanalyzer import __version__
from codehealthanalyzer.reports.generator import ReportGenerator


def test_full_report_contract_contains_stable_keys():
    violations = {
        "metadata": {
            "generated_at": "2024-01-01T00:00:00",
            "directory": ".",
            "total_files": 1,
            "violation_files": 0,
            "warning_files": 0,
        },
        "violations": [],
        "warnings": [],
        "statistics": {
            "total_files": 1,
            "violation_files": 0,
            "warning_files": 0,
            "high_priority": 0,
            "medium_priority": 0,
            "python_files": 1,
            "html_files": 0,
        },
    }
    templates = {
        "metadata": {
            "generated_at": "2024-01-01T00:00:00",
            "templates_paths": [],
            "total_templates": 0,
        },
        "templates": [],
        "statistics": {
            "total_templates": 0,
            "total_css_chars": 0,
            "total_js_chars": 0,
            "high_priority": 0,
            "medium_priority": 0,
            "templates_with_css": 0,
            "templates_with_js": 0,
        },
    }
    errors = {
        "metadata": {
            "generated_at": "2024-01-01T00:00:00",
            "total_errors": 0,
            "total_files": 0,
        },
        "errors": [],
        "statistics": {
            "high_priority": 0,
            "medium_priority": 0,
            "low_priority": 0,
            "syntax_errors": 0,
            "style_errors": 0,
            "critical_errors": 0,
        },
    }

    report = ReportGenerator().generate_full_report(violations, templates, errors)

    assert set(report) == {
        "metadata",
        "summary",
        "violations",
        "templates",
        "errors",
        "priorities",
        "quality_score",
    }
    assert report["metadata"]["version"] == __version__
    assert "quality_score" in report["summary"]
