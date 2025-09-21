Param(
    [string]$Path = "."
)

Write-Host "== Ruff (lint) =="
ruff check $Path

Write-Host "== isort (check) =="
isort --profile black --check-only $Path

Write-Host "== Black (check) =="
black --check $Path

Write-Host "== Bandit (security) =="
bandit -q -r $Path

Write-Host "All checks passed."
