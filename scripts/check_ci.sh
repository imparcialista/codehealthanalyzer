#!/usr/bin/env bash
# check_ci.sh — espelha exatamente os steps do .github/workflows/ci.yml
# Uso: bash scripts/check_ci.sh
# Bloqueia git push se qualquer step falhar.

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RESET='\033[0m'

PASS=0
FAIL=0

run_step() {
    local name="$1"
    shift
    echo -e "\n${CYAN}== $name ==${RESET}"
    if "$@"; then
        echo -e "${GREEN}[OK] $name${RESET}"
        ((PASS++)) || true
    else
        echo -e "${RED}[FAIL] $name${RESET}"
        ((FAIL++)) || true
    fi
}

run_step_optional() {
    local name="$1"
    shift
    echo -e "\n${CYAN}== $name (continue-on-error) ==${RESET}"
    if "$@"; then
        echo -e "${GREEN}[OK] $name${RESET}"
    else
        echo -e "${YELLOW}[WARN] $name falhou, mas não bloqueia (continue-on-error)${RESET}"
    fi
}

echo -e "${CYAN}======================================${RESET}"
echo -e "${CYAN}  Verificação local do CI             ${RESET}"
echo -e "${CYAN}======================================${RESET}"

# --- Install dependencies ---
run_step "Install dependencies" pip install -e ".[dev,web]" -q

# --- Lint (ruff) ---
run_step "Lint (ruff)" ruff check codehealthanalyzer

# --- Format check (black) ---
# Passa o diretório explicitamente para evitar leitura do .gitignore com encoding inválido (Windows)
run_step "Format check (black)" black --check codehealthanalyzer --exclude '/(\.git|__pycache__|\.venv|venv|node_modules)/'

# --- Import order (isort) ---
run_step "Import order (isort)" isort --profile black --check-only codehealthanalyzer

# --- Security scan (bandit) ---
run_step "Security scan (bandit)" bandit -q -r codehealthanalyzer

# --- Type check (mypy) — continue-on-error no CI ---
run_step_optional "Type check (mypy)" mypy codehealthanalyzer --ignore-missing-imports

# --- Tests with coverage ---
run_step "Tests with coverage" pytest \
    --cov=codehealthanalyzer \
    --cov-report=term-missing \
    --cov-fail-under=50 \
    -q

# --- Resultado final ---
echo -e "\n${CYAN}======================================${RESET}"
if [ "$FAIL" -eq 0 ]; then
    echo -e "${GREEN}  Todos os checks passaram ($PASS/$PASS)${RESET}"
    echo -e "${CYAN}======================================${RESET}"
    exit 0
else
    echo -e "${RED}  $FAIL check(s) falharam — push bloqueado${RESET}"
    echo -e "${CYAN}======================================${RESET}"
    exit 1
fi
