#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${1:-.}"

echo "== isort (apply) =="
isort --profile black "$TARGET_DIR"

echo "== Black (apply) =="
black "$TARGET_DIR"

echo "== Ruff (auto-fix) =="
ruff check "$TARGET_DIR" --fix --exit-non-zero-on-fix --unsafe-fixes

echo "Formatting and auto-fixes applied."
