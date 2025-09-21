from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from ..utils.helpers import FileHelper


class ReportGenerator:
    """Gera relatórios consolidados e HTML básico."""

    def __init__(self, config: Optional[dict] = None) -> None:
        self.config = config or {}

    def generate_full_report(
        self,
        violations: Dict[str, Any],
        templates: Dict[str, Any],
        errors: Dict[str, Any],
        output_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        summary = {
            "generated_at": datetime.now().isoformat(),
            "quality_score": self.calculate_quality_score(violations, templates, errors),
            "total_files": violations.get("metadata", {}).get("total_files", 0),
            "violation_files": violations.get("metadata", {}).get("violation_files", 0),
            "total_templates": templates.get("metadata", {}).get("total_templates", 0),
            "total_errors": errors.get("metadata", {}).get("total_errors", 0),
            "high_priority_issues": violations.get("statistics", {}).get("high_priority", 0),
        }

        priorities = []
        high_v = violations.get("statistics", {}).get("high_priority", 0)
        if high_v:
            priorities.append({
                "title": "Violações de código de alta prioridade",
                "priority": "high",
                "count": high_v,
            })

        report = {
            "summary": summary,
            "priorities": priorities,
            "violations": violations,
            "templates": templates,
            "errors": errors,
        }

        if output_dir:
            out = Path(output_dir)
            out.mkdir(parents=True, exist_ok=True)
            FileHelper.write_json(report, out / "full_report.json")

        return report

    def calculate_quality_score(
        self, violations: Dict[str, Any], templates: Dict[str, Any], errors: Dict[str, Any]
    ) -> int:
        score = 100
        score -= 10 * violations.get("statistics", {}).get("high_priority", 0)
        score -= 2 * errors.get("metadata", {}).get("total_errors", 0)
        score -= 5 * templates.get("statistics", {}).get("high_priority", 0)
        return max(0, min(100, score))

    def generate_html_report(self, report: Dict[str, Any], output_file: str) -> str:
        html = f"""
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="utf-8" />
  <title>CodeHealthAnalyzer - Relatório</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; }}
    h1, h2 {{ color: #333; }}
    .ok {{ color: #2ecc71; }}
    .warn {{ color: #f1c40f; }}
    .err {{ color: #e74c3c; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; }}
    th {{ background: #f5f5f5; text-align: left; }}
  </style>
</head>
<body>
  <h1>Relatório - CodeHealthAnalyzer</h1>
  <p>Gerado em: {report.get("summary", {}).get("generated_at", "")}</p>
  <h2>Resumo</h2>
  <ul>
    <li>Score de Qualidade: <strong>{report.get("summary", {}).get("quality_score", 0)}</strong></li>
    <li>Total de arquivos: {report.get("summary", {}).get("total_files", 0)}</li>
    <li>Arquivos com violações: {report.get("summary", {}).get("violation_files", 0)}</li>
    <li>Templates: {report.get("summary", {}).get("total_templates", 0)}</li>
    <li>Erros Ruff: {report.get("summary", {}).get("total_errors", 0)}</li>
  </ul>
</body>
</html>
""".strip()

        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        Path(output_file).write_text(html, encoding="utf-8")
        return html