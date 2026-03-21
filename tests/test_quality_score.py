"""Testes para ReportGenerator.calculate_quality_score."""


from codehealthanalyzer.reports.generator import ReportGenerator


def _make_reports(high_violations=0, total_errors=0, high_templates=0):
    violations = {
        "metadata": {"total_files": 1, "violation_files": 0, "warning_files": 0},
        "violations": [],
        "warnings": [],
        "statistics": {
            "total_files": 1,
            "violation_files": high_violations,
            "warning_files": 0,
            "high_priority": high_violations,
            "medium_priority": 0,
            "python_files": 1,
            "html_files": 0,
        },
    }
    templates = {
        "metadata": {"generated_at": "", "templates_paths": [], "total_templates": 0},
        "templates": [],
        "statistics": {
            "total_templates": 0,
            "total_css_chars": 0,
            "total_js_chars": 0,
            "high_priority": high_templates,
            "medium_priority": 0,
            "templates_with_css": 0,
            "templates_with_js": 0,
        },
    }
    errors = {
        "metadata": {
            "generated_at": "",
            "total_errors": total_errors,
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
    return violations, templates, errors


gen = ReportGenerator()


def test_score_starts_at_100_with_clean_report():
    v, t, e = _make_reports()
    assert gen.calculate_quality_score(v, t, e) == 100


def test_score_decrements_10_per_high_violation():
    v, t, e = _make_reports(high_violations=3)
    assert gen.calculate_quality_score(v, t, e) == 70


def test_score_decrements_2_per_ruff_error():
    v, t, e = _make_reports(total_errors=5)
    assert gen.calculate_quality_score(v, t, e) == 90


def test_score_decrements_5_per_high_priority_template():
    v, t, e = _make_reports(high_templates=4)
    assert gen.calculate_quality_score(v, t, e) == 80


def test_score_never_goes_below_zero():
    v, t, e = _make_reports(high_violations=100, total_errors=100)
    assert gen.calculate_quality_score(v, t, e) == 0


def test_score_never_exceeds_100():
    v, t, e = _make_reports()
    score = gen.calculate_quality_score(v, t, e)
    assert score <= 100


def test_score_combined_penalties():
    v, t, e = _make_reports(high_violations=2, total_errors=10, high_templates=1)
    # 100 - 20 (violations) - 20 (errors) - 5 (templates) = 55
    assert gen.calculate_quality_score(v, t, e) == 55
