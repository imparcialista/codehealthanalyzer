import json
import subprocess
import sys


def test_cli_help_lists_public_commands():
    proc = subprocess.run(
        [sys.executable, "-m", "codehealthanalyzer.cli.main", "--help"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "analyze" in proc.stdout
    assert "dashboard" in proc.stdout
    assert "violations" in proc.stdout


def test_cli_analyze_generates_json_report(tmp_path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("x = 1\n", encoding="utf-8")

    output_dir = tmp_path / "reports"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "codehealthanalyzer.cli.main",
            "analyze",
            str(tmp_path),
            "--output",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0
    report_file = output_dir / "summary_report.json"
    assert report_file.exists()
    report = json.loads(report_file.read_text(encoding="utf-8"))
    assert "summary" in report
    assert "quality_score" in report["summary"]
