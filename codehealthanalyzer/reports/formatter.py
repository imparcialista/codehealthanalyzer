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
        md.write(f"**Gerado em:** {report.get('metadata', {}).get('generated_at', '')}\n\n")


        # Resumo
        md.write("## Resumo\n\n")
        md.write("| Métrica | Valor |\n")
        md.write("|---|---:|\n")
        md.write(f"| Score de Qualidade | {s.get('quality_score', 0)} |\n")
        md.write(f"| Total de arquivos | {s.get('total_files', 0)} |\n")
        md.write(f"| Arquivos com violações | {s.get('violation_files', 0)} |\n")
        md.write(f"| Templates | {s.get('total_templates', 0)} |\n")
        md.write(f"| Erros Ruff | {s.get('total_errors', 0)} |\n\n")


        # Prioridades
        md.write("## Prioridades de Ação\n\n")
        priorities = report.get("priorities", [])
        if priorities:
            for p in priorities:
                md.write(f"- {p.get('title','N/A')} ({p.get('count', 0)})\n")
        else:
            md.write("- Nenhuma ação urgente necessária\n")
        md.write("\n")


        # Violações (consolidado)
        md.write("## Arquivos com Violações\n\n")
        md.write("| Arquivo | Prioridade | Qtd. Violações | Linhas |\n")
        md.write("|---|---|---:|---:|\n")
        vio = (report.get("violations", {}).get("violations", []) or []) + (
            report.get("violations", {}).get("warnings", []) or []
        )
        if vio:
            for it in vio:
                md.write(
                    f"| {it.get('file','')} | {it.get('priority','')} | {len(it.get('violations',[]))} | {it.get('lines',0)} |\n"
                )
        else:
            md.write("| _Sem registros_ |  |  |  |\n")
        md.write("\n")


        # Erros (Ruff)
        md.write("## Erros (Ruff)\n\n")
        md.write("| Arquivo | Categoria | Prioridade | Qtd. Erros |\n")
        md.write("|---|---|---|---:|\n")
        errs = report.get("errors", {}).get("errors", []) or []
        if errs:
            for f in errs:
                md.write(
                    f"| {f.get('file','')} | {f.get('category','')} | {f.get('priority','')} | {f.get('error_count',0)} |\n"
                )
        else:
            md.write("| _Sem registros_ |  |  |  |\n")
        md.write("\n")


        # Templates
        md.write("## Templates\n\n")
        md.write("| Arquivo | Categoria | Prioridade | CSS (chars) | JS (chars) |\n")
        md.write("|---|---|---|---:|---:|\n")
        tmpls = report.get("templates", {}).get("templates", []) or []
        if tmpls:
            for t in tmpls:
                css_chars = t.get('total_css_chars', t.get('css', 0))
                js_chars = t.get('total_js_chars', t.get('js', 0))
                md.write(
                    f"| {t.get('file','')} | {t.get('category','')} | {t.get('priority','')} | {css_chars} | {js_chars} |\n"
                )
        else:
            md.write("| _Sem registros_ |  |  |  |  |\n")
        md.write("\n")


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