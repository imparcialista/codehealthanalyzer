"""Testes de CLI usando click.testing.CliRunner."""

import json
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from codehealthanalyzer.cli.main import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def project(tmp_path):
    """Projeto Python mínimo."""
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("x = 1\n", encoding="utf-8")
    return tmp_path


# ---------------------------------------------------------------------------
# help
# ---------------------------------------------------------------------------


def test_cli_help(runner):
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "analyze" in result.output
    assert "violations" in result.output
    assert "templates" in result.output


def test_cli_version(runner):
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# analyze
# ---------------------------------------------------------------------------


def test_analyze_help(runner):
    result = runner.invoke(cli, ["analyze", "--help"])
    assert result.exit_code == 0
    assert "PROJECT_PATH" in result.output


def test_analyze_runs_on_valid_project(runner, project, tmp_path):
    out = tmp_path / "out"
    with patch("shutil.which", return_value=None):  # sem ruff
        result = runner.invoke(
            cli,
            ["analyze", str(project), "--output", str(out), "--no-default-excludes"],
        )
    assert result.exit_code == 0
    assert (out / "full_report.json").exists()


def test_analyze_json_report_has_summary(runner, project, tmp_path):
    out = tmp_path / "out"
    with patch("shutil.which", return_value=None):
        runner.invoke(
            cli,
            ["analyze", str(project), "--output", str(out), "--no-default-excludes"],
        )
    report = json.loads((out / "full_report.json").read_text(encoding="utf-8"))
    assert "summary" in report
    assert "quality_score" in report["summary"]


def test_analyze_verbose_flag(runner, project, tmp_path):
    out = tmp_path / "out"
    with patch("shutil.which", return_value=None):
        result = runner.invoke(
            cli,
            ["analyze", str(project), "--output", str(out), "--verbose"],
        )
    assert result.exit_code == 0


def test_analyze_markdown_format(runner, project, tmp_path):
    out = tmp_path / "out"
    with patch("shutil.which", return_value=None):
        runner.invoke(
            cli,
            [
                "analyze",
                str(project),
                "--output",
                str(out),
                "--format",
                "markdown",
                "--no-default-excludes",
            ],
        )
    assert (out / "full_report.md").exists()


def test_analyze_no_json_flag(runner, project, tmp_path):
    out = tmp_path / "out"
    with patch("shutil.which", return_value=None):
        runner.invoke(
            cli,
            [
                "analyze",
                str(project),
                "--output",
                str(out),
                "--no-json",
                "--no-default-excludes",
            ],
        )
    assert not (out / "full_report.json").exists()


def test_analyze_detail_summary_generates_summary_files(runner, project, tmp_path):
    out = tmp_path / "out"
    with patch("shutil.which", return_value=None):
        runner.invoke(
            cli,
            [
                "analyze",
                str(project),
                "--output",
                str(out),
                "--detail",
                "summary",
                "--no-default-excludes",
            ],
        )

    assert (out / "full_report.json").exists()
    assert (out / "full_report.summary.json").exists()
    data = json.loads((out / "full_report.json").read_text(encoding="utf-8"))
    assert "summary" in data
    assert "top_violations" in data


def test_analyze_detail_full_generates_full_alias_file(runner, project, tmp_path):
    out = tmp_path / "out"
    with patch("shutil.which", return_value=None):
        runner.invoke(
            cli,
            [
                "analyze",
                str(project),
                "--output",
                str(out),
                "--detail",
                "full",
                "--no-default-excludes",
            ],
        )

    assert (out / "full_report.json").exists()
    assert (out / "full_report.full.json").exists()
    assert (out / "full_report.summary.json").exists()


# ---------------------------------------------------------------------------
# violations
# ---------------------------------------------------------------------------


def test_violations_help(runner):
    result = runner.invoke(cli, ["violations", "--help"])
    assert result.exit_code == 0


def test_violations_runs(runner, project, tmp_path):
    out = tmp_path / "out"
    result = runner.invoke(
        cli,
        ["violations", str(project), "--output", str(out), "--no-default-excludes"],
    )
    assert result.exit_code == 0
    assert (out / "violations_report.json").exists()


def test_violations_report_has_violations_key(runner, project, tmp_path):
    out = tmp_path / "out"
    runner.invoke(
        cli,
        ["violations", str(project), "--output", str(out), "--no-default-excludes"],
    )
    report = json.loads((out / "violations_report.json").read_text(encoding="utf-8"))
    assert "violations" in report


# ---------------------------------------------------------------------------
# templates
# ---------------------------------------------------------------------------


def test_templates_help(runner):
    result = runner.invoke(cli, ["templates", "--help"])
    assert result.exit_code == 0


def test_templates_runs(runner, project, tmp_path):
    out = tmp_path / "out"
    result = runner.invoke(
        cli,
        ["templates", str(project), "--output", str(out)],
    )
    assert result.exit_code == 0
    assert (out / "templates_report.json").exists()


# ---------------------------------------------------------------------------
# errors
# ---------------------------------------------------------------------------


def test_errors_help(runner):
    result = runner.invoke(cli, ["errors", "--help"])
    assert result.exit_code == 0


def test_errors_runs_without_ruff(runner, project, tmp_path):
    out = tmp_path / "out"
    with patch("shutil.which", return_value=None):
        result = runner.invoke(
            cli,
            ["errors", str(project), "--output", str(out)],
        )
    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# score
# ---------------------------------------------------------------------------


def test_score_help(runner):
    result = runner.invoke(cli, ["score", "--help"])
    assert result.exit_code == 0


def test_score_outputs_number(runner, project):
    with patch("shutil.which", return_value=None):
        result = runner.invoke(cli, ["score", str(project)])
    assert result.exit_code == 0
    # Output deve conter um número de score
    assert any(c.isdigit() for c in result.output)


# ---------------------------------------------------------------------------
# info
# ---------------------------------------------------------------------------


def test_info_help(runner):
    result = runner.invoke(cli, ["info", "--help"])
    assert result.exit_code == 0


def test_info_shows_project_name(runner, project):
    result = runner.invoke(cli, ["info", str(project)])
    assert result.exit_code == 0
    assert project.name in result.output


def test_info_shows_python_files_count(runner, project):
    result = runner.invoke(cli, ["info", str(project)])
    assert "Python" in result.output


# ---------------------------------------------------------------------------
# lint
# ---------------------------------------------------------------------------


def test_lint_help(runner):
    result = runner.invoke(cli, ["lint", "--help"])
    assert result.exit_code == 0


def test_lint_runs_without_tools(runner, project):
    with patch("shutil.which", return_value=None):
        result = runner.invoke(cli, ["lint", str(project)])
    # Sem ferramentas instaladas não deve travar
    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# format
# ---------------------------------------------------------------------------


def test_format_help(runner):
    result = runner.invoke(cli, ["format", "--help"])
    assert result.exit_code == 0


def test_format_runs_without_tools(runner, project):
    with patch("shutil.which", return_value=None):
        result = runner.invoke(cli, ["format", str(project)])
    assert result.exit_code == 0
