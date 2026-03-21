"""Testes para ErrorsAnalyzer."""

from unittest.mock import MagicMock, patch

import pytest

from codehealthanalyzer.analyzers.errors import ErrorsAnalyzer
from codehealthanalyzer.exceptions import AnalyzerExecutionError

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_analyzer(tmp_path, config=None):
    return ErrorsAnalyzer(str(tmp_path), config=config)


def _run_with_stdout(analyzer, stdout, returncode=1):
    """Executa analyze() mockando subprocess para retornar stdout fornecido."""
    result = MagicMock()
    result.returncode = returncode
    result.stdout = stdout
    result.stderr = ""
    with patch("shutil.which", return_value="/usr/bin/ruff"), patch(
        "subprocess.run", return_value=result
    ):
        return analyzer.analyze()


# ---------------------------------------------------------------------------
# run_ruff_check
# ---------------------------------------------------------------------------


def test_run_ruff_check_raises_when_ruff_missing(minimal_project):
    analyzer = _make_analyzer(minimal_project)
    with patch("shutil.which", return_value=None):
        with pytest.raises(AnalyzerExecutionError, match="Ruff não encontrado"):
            analyzer.run_ruff_check()


def test_run_ruff_check_raises_on_bad_returncode(minimal_project):
    result = MagicMock(returncode=2, stdout="", stderr="internal error")
    with patch("shutil.which", return_value="/usr/bin/ruff"), patch(
        "subprocess.run", return_value=result
    ):
        with pytest.raises(AnalyzerExecutionError):
            _make_analyzer(minimal_project).run_ruff_check()


def test_run_ruff_check_raises_on_invalid_json(minimal_project):
    result = MagicMock(returncode=1, stdout="not json", stderr="")
    with patch("shutil.which", return_value="/usr/bin/ruff"), patch(
        "subprocess.run", return_value=result
    ):
        with pytest.raises(AnalyzerExecutionError, match="JSON"):
            _make_analyzer(minimal_project).run_ruff_check()


def test_run_ruff_check_returns_empty_on_no_stdout(minimal_project):
    result = MagicMock(returncode=0, stdout="", stderr="")
    with patch("shutil.which", return_value="/usr/bin/ruff"), patch(
        "subprocess.run", return_value=result
    ):
        assert _make_analyzer(minimal_project).run_ruff_check() == []


# ---------------------------------------------------------------------------
# categorize_error
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "code,expected_category",
    [
        ("F401", "Erros de Importação"),
        ("F811", "Erros de Importação"),
        ("F821", "Erros de Importação"),
        ("F841", "Erros de Sintaxe"),
        ("E302", "Erros de Estilo"),
        ("W291", "Avisos"),
        ("C901", "Complexidade"),
        ("N802", "Nomenclatura"),
        ("XYZ", "Outros"),
        ("", "Outros"),
    ],
)
def test_categorize_error(code, expected_category, minimal_project):
    analyzer = _make_analyzer(minimal_project)
    assert analyzer.categorize_error({"code": code}) == expected_category


# ---------------------------------------------------------------------------
# determine_priority
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "code,expected_priority",
    [
        ("F821", "high"),
        ("F822", "high"),
        ("E999", "high"),
        ("F401", "medium"),
        ("E302", "low"),
        ("W291", "low"),
        ("", "low"),
    ],
)
def test_determine_priority(code, expected_priority, minimal_project):
    analyzer = _make_analyzer(minimal_project)
    assert analyzer.determine_priority({"code": code}) == expected_priority


# ---------------------------------------------------------------------------
# analyze — com mock do subprocess
# ---------------------------------------------------------------------------


def test_analyze_returns_required_keys(minimal_project, ruff_json_output):
    report = _run_with_stdout(_make_analyzer(minimal_project), ruff_json_output)
    assert "metadata" in report
    assert "errors" in report
    assert "statistics" in report


def test_analyze_groups_errors_by_file(minimal_project, ruff_json_output):
    report = _run_with_stdout(_make_analyzer(minimal_project), ruff_json_output)
    files = {e["file"] for e in report["errors"]}
    assert "/proj/foo.py" in files
    assert "/proj/bar.py" in files


def test_analyze_counts_total_errors(minimal_project, ruff_json_output):
    report = _run_with_stdout(_make_analyzer(minimal_project), ruff_json_output)
    assert report["metadata"]["total_errors"] == 3


def test_analyze_high_priority_file_detected(minimal_project, ruff_json_output):
    report = _run_with_stdout(_make_analyzer(minimal_project), ruff_json_output)
    bar = next(e for e in report["errors"] if e["file"] == "/proj/bar.py")
    assert bar["priority"] == "high"


def test_analyze_medium_priority_file_detected(minimal_project, ruff_json_output):
    report = _run_with_stdout(_make_analyzer(minimal_project), ruff_json_output)
    foo = next(e for e in report["errors"] if e["file"] == "/proj/foo.py")
    assert foo["priority"] == "medium"


def test_analyze_empty_project_returns_empty(minimal_project):
    result = MagicMock(returncode=0, stdout="[]", stderr="")
    with patch("shutil.which", return_value="/usr/bin/ruff"), patch(
        "subprocess.run", return_value=result
    ):
        report = _make_analyzer(minimal_project).analyze()
    assert report["errors"] == []
    assert report["metadata"]["total_errors"] == 0


def test_analyze_ruff_missing_returns_empty_gracefully(minimal_project):
    """analyze() não deve lançar exceção quando ruff não está instalado."""
    with patch("shutil.which", return_value=None):
        report = _make_analyzer(minimal_project).analyze()
    assert report["errors"] == []


def test_analyze_statistics_reflect_priorities(minimal_project, ruff_json_output):
    report = _run_with_stdout(_make_analyzer(minimal_project), ruff_json_output)
    stats = report["statistics"]
    assert stats["high_priority"] >= 1
    assert stats["medium_priority"] >= 1
