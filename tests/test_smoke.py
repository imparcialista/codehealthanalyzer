import subprocess
import sys


def test_import_package():
    import codehealthanalyzer  # noqa: F401


def test_cli_help_runs():
    # Run the CLI help and assert it exits successfully
    cmd = [sys.executable, "-m", "codehealthanalyzer.cli.main", "--help"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, f"CLI help failed: rc={proc.returncode}, stderr={proc.stderr} stdout={proc.stdout}"
