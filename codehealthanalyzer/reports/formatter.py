from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path
from typing import Dict, Any

from ..utils.helpers import FileHelper


class ReportFormatter:
    """Formatadores para JSON, Markdown e CSV."""

    def to_json(self, report: Dict[str, Any], output_file: str) -> bool:
        return FileHelper.write_json(report, output_file)

    def to_markdown(self, report: Dict[str, Any], output_file: str) -> str:
        md = StringIO()
        s = report.get("summary", {})

        md.write("# Relatório - CodeHealthAnalyzer\n\n")
        md.write("## Resumo\n\n")
        md.write(f"- Score de Qualidade: {s.get('quality_score', 0)}\n")
        md.write(f"- Total de arquivos: {s.get('total_files', 0)}\n")
        md.write(f"- Arquivos com violações: {s.get('violation_files', 0)}\n")
        md.write(f"- Templates: {s.get('total_templates', 0)}\n")
        md.write(f"- Erros Ruff: {s.get('total_errors', 0)}\n")

        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        Path(output_file).write_text(md.getvalue(), encoding="utf-8")
        return md.getvalue()

    def to_csv(self, report: Dict[str, Any], output_file: str) -> None:
        rows = []
        for item in report.get("violations", {}).get("violations", []):
            rows.append(
                {
                    "type": "violation",
                    "file": item.get("file"),
                    "priority": item.get("priority"),
                    "lines": item.get("lines"),
                }
            )

        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["type", "file", "priority", "lines"])
            writer.writeheader()
            for r in rows:
                writer.writerow(r)

    def generate_summary_table(self, report: Dict[str, Any]) -> str:
        s = report.get("summary", {})
        lines = [
            "+-------------------------+---------+",
            f"| Score de Qualidade      | {s.get('quality_score', 0):>7} |",
            f"| Total de arquivos       | {s.get('total_files', 0):>7} |",
            f"| Arquivos com violações  | {s.get('violation_files', 0):>7} |",
            f"| Templates               | {s.get('total_templates', 0):>7} |",
            f"| Erros Ruff              | {s.get('total_errors', 0):>7} |",
            "+-------------------------+---------+",
        ]
        return "\n".join(lines)