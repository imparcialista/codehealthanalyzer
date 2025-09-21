Param(
    [string]$Path = "."
)

Write-Host "== isort (apply) =="
isort --profile black $Path

Write-Host "== Black (apply) =="
black $Path

Write-Host "== Ruff (auto-fix) =="
ruff check $Path --fix --exit-non-zero-on-fix --unsafe-fixes

Write-Host "Formatting and auto-fixes applied."
