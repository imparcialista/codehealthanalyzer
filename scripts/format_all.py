#!/usr/bin/env python3
"""Format all source files using isort and black.

Usage:
    python scripts/format_all.py [path]
Defaults to current directory.
"""

import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> int:
    print("$", " ".join(cmd))
    proc = subprocess.run(cmd)
    return proc.returncode


def main() -> int:
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    target_path = str(Path(target))

    rc = 0

    rc |= run([sys.executable, "-m", "isort", "--profile", "black", target_path])
    rc |= run([sys.executable, "-m", "black", target_path])

    return rc


if __name__ == "__main__":
    raise SystemExit(main())
