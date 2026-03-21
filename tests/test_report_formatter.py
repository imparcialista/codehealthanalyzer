"""Testes para ReportFormatter e ReportGenerator.generate_html_report."""

import csv
import json

import pytest

from codehealthanalyzer.reports.formatter import ReportFormatter
from codehealthanalyzer.reports.generator import ReportGenerator


@pytest.fixture
def formatter():
    return ReportFormatter()


@pytest.fixture
def generator():
    return ReportGenerator()


# ---------------------------------------------------------------------------
# to_json
# ---------------------------------------------------------------------------


def test_to_json_creates_valid_json_file(formatter, full_report, tmp_path):
    out = str(tmp_path / "report.json")
    formatter.to_json(full_report, out)
    with open(out, encoding="utf-8") as f:
        data = json.load(f)
    assert "summary" in data
    assert "violations" in data


def test_to_json_preserves_quality_score(formatter, full_report, tmp_path):
    out = str(tmp_path / "report.json")
    formatter.to_json(full_report, out)
    data = json.loads(open(out, encoding="utf-8").read())
    assert data["quality_score"] == full_report["quality_score"]


# ---------------------------------------------------------------------------
# to_markdown
# ---------------------------------------------------------------------------


def test_to_markdown_contains_headers(formatter, full_report, tmp_path):
    out = str(tmp_path / "report.md")
    md = formatter.to_markdown(full_report, out)
    assert "## Resumo" in md
    assert "## Erros" in md
    assert "## Templates" in md
    assert "## Arquivos com Violações" in md


def test_to_markdown_shows_quality_score(formatter, full_report, tmp_path):
    out = str(tmp_path / "report.md")
    md = formatter.to_markdown(full_report, out)
    assert "80" in md  # quality_score == 80


def test_to_markdown_creates_file(formatter, full_report, tmp_path):
    out = str(tmp_path / "report.md")
    formatter.to_markdown(full_report, out)
    assert (tmp_path / "report.md").exists()


def test_to_markdown_empty_report_no_crash(formatter, tmp_path):
    empty = {
        "metadata": {"generated_at": ""},
        "summary": {},
        "violations": {},
        "templates": {},
        "errors": {},
        "priorities": [],
        "quality_score": 0,
    }
    out = str(tmp_path / "empty.md")
    md = formatter.to_markdown(empty, out)
    assert isinstance(md, str)


def test_to_markdown_shows_violation_file(formatter, full_report, tmp_path):
    out = str(tmp_path / "report.md")
    md = formatter.to_markdown(full_report, out)
    assert "big_module.py" in md


def test_to_markdown_shows_error_file(formatter, full_report, tmp_path):
    out = str(tmp_path / "report.md")
    md = formatter.to_markdown(full_report, out)
    assert "foo.py" in md


# ---------------------------------------------------------------------------
# to_csv
# ---------------------------------------------------------------------------


def test_to_csv_creates_file_with_headers(formatter, full_report, tmp_path):
    out = str(tmp_path / "report.csv")
    formatter.to_csv(full_report, out)
    with open(out, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert set(reader.fieldnames) == {"type", "file", "priority", "lines"}


def test_to_csv_rows_from_violations(formatter, full_report, tmp_path):
    out = str(tmp_path / "report.csv")
    formatter.to_csv(full_report, out)
    with open(out, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    types = [r["type"] for r in rows]
    assert "violation" in types


def test_to_csv_rows_from_errors(formatter, full_report, tmp_path):
    out = str(tmp_path / "report.csv")
    formatter.to_csv(full_report, out)
    with open(out, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    types = [r["type"] for r in rows]
    assert "error" in types


def test_to_csv_rows_from_templates(formatter, full_report, tmp_path):
    out = str(tmp_path / "report.csv")
    formatter.to_csv(full_report, out)
    with open(out, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    types = [r["type"] for r in rows]
    assert "template" in types


# ---------------------------------------------------------------------------
# generate_summary_table
# ---------------------------------------------------------------------------


def test_generate_summary_table_format(formatter, full_report):
    table = formatter.generate_summary_table(full_report)
    assert "Score de Qualidade" in table
    assert "80" in table
    assert "+" in table  # border chars


# ---------------------------------------------------------------------------
# generate_html_report (via ReportGenerator)
# ---------------------------------------------------------------------------


def test_generate_html_report_is_valid_html(generator, full_report, tmp_path):
    out = str(tmp_path / "report.html")
    html = generator.generate_html_report(full_report, out)
    assert html.startswith("<!DOCTYPE html>")
    assert "<html" in html
    assert "</html>" in html


def test_generate_html_report_creates_file(generator, full_report, tmp_path):
    out = str(tmp_path / "report.html")
    generator.generate_html_report(full_report, out)
    assert (tmp_path / "report.html").exists()


def test_generate_html_report_contains_quality_score(generator, full_report, tmp_path):
    out = str(tmp_path / "report.html")
    html = generator.generate_html_report(full_report, out)
    assert "80" in html


def test_generate_html_report_contains_violation_file(generator, full_report, tmp_path):
    out = str(tmp_path / "report.html")
    html = generator.generate_html_report(full_report, out)
    assert "big_module.py" in html
