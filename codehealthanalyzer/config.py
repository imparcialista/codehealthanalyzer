"""Configuracoes padrao compartilhadas."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .exceptions import ConfigurationError

DEFAULT_EXCLUDE_DIRS = [
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".tox",
    ".nox",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "site-packages",
    "reports",
    "scripts",
    "tests",
]

DEFAULT_TEMPLATE_DIRS = [
    "templates",
    "cha/templates",
    "codehealthanalyzer/web/templates",
]


def normalize_config(config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Normaliza configuracoes publicas do pacote."""
    normalized = dict(config or {})

    template_dirs = normalized.get("templates_dir", DEFAULT_TEMPLATE_DIRS)
    if isinstance(template_dirs, (str, Path)):
        template_dirs = [str(template_dirs)]
    elif not isinstance(template_dirs, (list, tuple)):
        raise ConfigurationError("'templates_dir' deve ser string ou lista de strings")
    normalized["templates_dir"] = [str(item) for item in template_dirs]

    exclude_dirs = normalized.get("exclude_dirs", [])
    if isinstance(exclude_dirs, (str, Path)):
        exclude_dirs = [str(exclude_dirs)]
    elif not isinstance(exclude_dirs, (list, tuple)):
        raise ConfigurationError("'exclude_dirs' deve ser string ou lista de strings")
    normalized["exclude_dirs"] = [str(item) for item in exclude_dirs]

    target_dir = normalized.get("target_dir", ".")
    if not isinstance(target_dir, str):
        raise ConfigurationError("'target_dir' deve ser uma string")
    normalized["target_dir"] = target_dir

    normalized["no_default_excludes"] = bool(
        normalized.get("no_default_excludes", False)
    )
    normalized["ruff_fix"] = bool(normalized.get("ruff_fix", False))
    return normalized
