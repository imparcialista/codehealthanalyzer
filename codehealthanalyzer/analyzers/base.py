"""Infraestrutura comum para analisadores do CodeHealthAnalyzer."""

from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Iterable, List, Sequence


class BaseAnalyzer:
    """Classe base com utilidades compartilhadas entre analisadores.

    Args:
        project_path: Caminho raiz do projeto a ser analisado.
        config: Dicionário de configurações específicas.
    """

    DEFAULT_SKIP_DIRS: Sequence[str] = (
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
    )

    def __init__(self, project_path: str, config: dict | None = None) -> None:
        self.project_path = Path(project_path)
        self.config = config or {}
        self.no_default_excludes = bool(self.config.get("no_default_excludes", False))
        user_excludes = self.config.get("exclude_dirs", [])
        if isinstance(user_excludes, (str, Path)):
            user_excludes = [str(user_excludes)]
        self.user_exclude_dirs: List[str] = [str(p) for p in user_excludes]

    def iter_files(self, patterns: Iterable[str]) -> Iterable[Path]:
        """Itera pelos arquivos que combinam com os padrões fornecidos."""
        for pattern in patterns:
            yield from self.project_path.rglob(pattern)

    def should_skip(self, path: Path) -> bool:
        """Indica se um caminho deve ser ignorado com base nas configurações."""
        path_str = str(path)
        patterns: Sequence[str] = ()
        if not self.no_default_excludes:
            patterns = self.DEFAULT_SKIP_DIRS

        for candidate in (*patterns, *self.user_exclude_dirs):
            if self._matches(candidate, path_str):
                return True
        return False

    @staticmethod
    def _matches(pattern: str, value: str) -> bool:
        if not pattern:
            return False
        if any(ch in pattern for ch in ("*", "?", "[")):
            return fnmatch.fnmatch(value, pattern)
        return pattern in value

    def relpath(self, path: Path) -> str:
        """Retorna caminho relativo ao projeto, com fallback seguro."""
        try:
            return path.resolve().relative_to(self.project_path.resolve()).as_posix()
        except (ValueError, OSError):
            return path.as_posix()


__all__ = ["BaseAnalyzer"]
