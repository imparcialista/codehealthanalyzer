from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from ..utils.helpers import FileHelper
from .report import Report


class ReportGenerator:
    """Gera relatórios consolidados."""

    def __init__(self, config: Optional[dict] = None) -> None:
        self.config = config or {}

    def generate_full_report(
        self,
        violations: Dict[str, Any],
        templates: Dict[str, Any],
        errors: Dict[str, Any],
        output_dir: Optional[str] = None,
    ) -> Report:
        """Gera um relatório completo a partir dos resultados da análise."""
        report = Report(
            config=self.config,
            violations=violations,
            templates=templates,
            errors=errors,
        )
        report.calculate_quality_score()
        report.generate_summary()
        report.generate_priorities()

        if output_dir:
            out = Path(output_dir)
            out.mkdir(parents=True, exist_ok=True)
            FileHelper.write_json(report.to_dict(), out / "full_report.json")

        return report