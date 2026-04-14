"""Analisador de violações de tamanho de arquivos e funções."""

from __future__ import annotations

import ast
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple, cast

from ..schemas import ViolationFileReport, ViolationsReport, ViolationStatistics
from .base import BaseAnalyzer

logger = logging.getLogger(__name__)

# Limites definidos no CODE_PRACTICES.md
DEFAULT_LIMITS = {
    "python_function": {"yellow": 30, "red": 50},
    "python_class": {"yellow": 300, "red": 500},
    "python_module": {"yellow": 500, "red": 1000},
    "html_template": {"yellow": 150, "red": 200},
    "test_file": {"yellow": 400, "red": 600},
}


@dataclass
class _FunctionInfo:
    name: str
    length: int


@dataclass
class _ClassInfo:
    name: str
    length: int


class _FunctionVisitor(ast.NodeVisitor):
    """Coleta informações de funções e métodos via AST."""

    def __init__(self) -> None:
        self.functions: List[_FunctionInfo] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        length = ViolationsAnalyzer._end_lineno(node) - node.lineno + 1
        self.functions.append(_FunctionInfo(node.name or "<lambda>", length))
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef  # type: ignore[assignment]


class _ClassVisitor(ast.NodeVisitor):
    """Coleta informações de classes via AST."""

    def __init__(self) -> None:
        self.classes: List[_ClassInfo] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        length = ViolationsAnalyzer._end_lineno(node) - node.lineno + 1
        self.classes.append(_ClassInfo(node.name, length))
        self.generic_visit(node)


class ViolationsAnalyzer(BaseAnalyzer):
    """Analisador de violações de tamanho de código."""

    PYTHON_PATTERNS: Tuple[str, ...] = ("*.py",)
    TEMPLATE_PATTERNS: Tuple[str, ...] = ("*.html",)

    def __init__(self, project_path: str, config: dict | None = None) -> None:
        super().__init__(project_path, config)
        self.limits = self.config.get("limits", DEFAULT_LIMITS)
        self.violations: List[Dict] = []
        self.warnings: List[Dict] = []

    # -------------------------------------------------------------------------
    # Utilidades de AST
    # -------------------------------------------------------------------------

    @staticmethod
    def _end_lineno(node: ast.AST) -> int:
        end = getattr(node, "end_lineno", None)
        if end is not None:
            return end
        if hasattr(node, "body") and node.body:
            return ViolationsAnalyzer._end_lineno(node.body[-1])
        return getattr(node, "lineno", 0)

    @staticmethod
    def _collect_docstring_ranges(tree: ast.AST) -> Iterable[Tuple[int, int]]:
        targets = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)
        for node in ast.walk(tree):
            if isinstance(node, targets):
                body = getattr(node, "body", [])
                if not body:
                    continue
                first = body[0]
                if isinstance(first, ast.Expr) and isinstance(
                    first.value, (ast.Str, ast.Constant)
                ):
                    value = (
                        first.value.s
                        if isinstance(first.value, ast.Str)
                        else first.value.value
                    )
                    if isinstance(value, str):
                        start = getattr(first, "lineno", None)
                        end = getattr(first, "end_lineno", None) or start
                        if start is not None:
                            yield (start, end or start)

    def _python_docstring_lines(self, tree: ast.AST) -> set[int]:
        lines: set[int] = set()
        for start, end in self._collect_docstring_ranges(tree):
            lines.update(range(start, end + 1))
        return lines

    def _effective_python_lines(self, file_path: Path, tree: ast.AST) -> int:
        doc_lines = self._python_docstring_lines(tree)
        count = 0
        try:
            with open(file_path, "r", encoding="utf-8-sig") as fh:
                for idx, raw in enumerate(fh, 1):
                    stripped = raw.strip()
                    if not stripped or stripped.startswith("#"):
                        continue
                    if idx in doc_lines:
                        continue
                    count += 1
        except OSError as exc:
            logger.warning("Falha ao ler %s: %s", file_path, exc)
            return 0
        return count

    def _gather_functions(self, tree: ast.AST) -> List[_FunctionInfo]:
        visitor = _FunctionVisitor()
        visitor.visit(tree)
        return visitor.functions

    def _gather_classes(self, tree: ast.AST) -> List[_ClassInfo]:
        visitor = _ClassVisitor()
        visitor.visit(tree)
        return visitor.classes

    # -------------------------------------------------------------------------
    # Análise de arquivos
    # -------------------------------------------------------------------------

    def _count_html_lines(self, file_path: Path) -> int:
        try:
            with open(file_path, "r", encoding="utf-8-sig") as fh:
                return sum(1 for line in fh if line.strip())
        except OSError as exc:
            logger.warning("Falha ao ler template %s: %s", file_path, exc)
            return 0

    def _apply_threshold(
        self,
        result: Dict[str, Any],
        kind: str,
        name: str,
        value: int,
    ) -> None:
        limits = self.limits.get(kind)
        if not limits:
            return
        label = kind.split("_")[-1]
        if value > limits["red"]:
            result["violations"].append(
                f"{label} {name}: {value} linhas (limite: {limits['red']})"
            )
            result["priority"] = "high"
        elif value > limits["yellow"]:
            result["violations"].append(
                f"{label} {name}: {value} linhas (limite: {limits['yellow']})"
            )
            if result["priority"] == "low":
                result["priority"] = "medium"

    def check_file(self, file_path: Path) -> ViolationFileReport:
        """Analisa um arquivo individual e retorna o resultado."""
        result: Dict[str, Any] = {
            "file": self.relpath(file_path),
            "violations": [],
            "priority": "low",
            "type": "Unknown",
            "lines": 0,
        }

        if file_path.suffix == ".py":
            result["type"] = "Python"
            try:
                with open(file_path, "r", encoding="utf-8-sig") as fh:
                    source = fh.read()
                tree = ast.parse(source, filename=str(file_path))
            except (OSError, SyntaxError) as exc:
                logger.warning("Falha ao analisar %s: %s", file_path, exc)
                result["violations"].append(f"Falha ao analisar AST: {exc}")
                result["priority"] = "medium"
                return cast(ViolationFileReport, result)

            module_lines = self._effective_python_lines(file_path, tree)
            result["lines"] = module_lines

            for info in self._gather_functions(tree):
                self._apply_threshold(result, "python_function", info.name, info.length)

            for cls in self._gather_classes(tree):
                self._apply_threshold(result, "python_class", cls.name, cls.length)

            self._apply_threshold(result, "python_module", "module", module_lines)

        elif file_path.suffix == ".html":
            result["type"] = "HTML Template"
            template_lines = self._count_html_lines(file_path)
            result["lines"] = template_lines
            self._apply_threshold(result, "html_template", "template", template_lines)

        else:
            result["type"] = file_path.suffix or "Unknown"

        return cast(ViolationFileReport, result)

    # -------------------------------------------------------------------------
    # Execução geral
    # -------------------------------------------------------------------------

    def analyze(self) -> ViolationsReport:
        """Executa a análise completa de violações."""
        all_results: List[ViolationFileReport] = []
        violations: List[ViolationFileReport] = []
        warnings: List[ViolationFileReport] = []

        for py_file in self.iter_files(self.PYTHON_PATTERNS):
            if self.should_skip(py_file):
                continue
            result = self.check_file(py_file)
            all_results.append(result)

            if result["violations"]:
                if result["priority"] == "high":
                    violations.append(result)
                else:
                    warnings.append(result)

        for html_file in self.iter_files(self.TEMPLATE_PATTERNS):
            if self.should_skip(html_file):
                continue
            result = self.check_file(html_file)
            all_results.append(result)

            if result["violations"]:
                if result["priority"] == "high":
                    violations.append(result)
                else:
                    warnings.append(result)

        stats = {
            "total_files": len(all_results),
            "violation_files": len(violations),
            "warning_files": len(warnings),
            "high_priority": len([v for v in violations if v["priority"] == "high"]),
            "medium_priority": len(
                [v for v in violations + warnings if v["priority"] == "medium"]
            ),
            "python_files": len([r for r in all_results if r.get("type") == "Python"]),
            "html_files": len(
                [r for r in all_results if r.get("type") == "HTML Template"]
            ),
        }

        return cast(
            ViolationsReport,
            {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "directory": str(self.project_path),
                    "total_files": stats["total_files"],
                    "violation_files": stats["violation_files"],
                    "warning_files": stats["warning_files"],
                },
                "violations": violations,
                "warnings": warnings,
                "statistics": cast(ViolationStatistics, stats),
            },
        )

    def save_report(self, report: Dict, output_file: str) -> None:
        """Salva o relatório em arquivo JSON."""
        with open(output_file, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, ensure_ascii=False)


__all__ = ["ViolationsAnalyzer"]
