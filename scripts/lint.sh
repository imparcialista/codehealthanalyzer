#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${1:-.}"

echo "== Ruff (lint) =="
ruff check "$TARGET_DIR"

echo "== isort (check) =="
isort --profile black --check-only "$TARGET_DIR"

echo "== Black (check) =="
black --check "$TARGET_DIR"

echo "== Bandit (security) =="
bandit -q -r "$TARGET_DIR"

echo "All checks passed."
