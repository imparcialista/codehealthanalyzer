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
        # Calcula score uma única vez e constrói summary consistente
        score = self.calculate_quality_score(violations, templates, errors)
        summary = self._generate_summary(violations, templates, errors)
        summary["generated_at"] = datetime.now().isoformat()
        summary["quality_score"] = score

        # Prioridades de ação
        priorities: list[dict[str, Any]] = []
        high_v = violations.get("statistics", {}).get("high_priority", 0)
        if high_v:
            priorities.append(
                {
                    "title": "Violações de código de alta prioridade",
                    "priority": "high",
                    "count": high_v,
                }
            )

        report: Dict[str, Any] = {
            "metadata": {
                "generated_at": summary["generated_at"],
                "version": "1.1.1",
                "analyzer": "CodeHealthAnalyzer",
            },
            "summary": summary,
            "violations": violations,
            "templates": templates,
            "errors": errors,
            "priorities": priorities,
            "quality_score": score,
        }

        if output_dir:
            out = Path(output_dir)
            out.mkdir(parents=True, exist_ok=True)
            FileHelper.write_json(report, out / "full_report.json")

        return report

    def _generate_summary(self, violations: Dict[str, Any], templates: Dict[str, Any], errors: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "total_files": violations.get("metadata", {}).get("total_files", 0),
            "violation_files": violations.get("metadata", {}).get("violation_files", 0),
            "total_templates": templates.get("metadata", {}).get("total_templates", 0),
            "total_errors": errors.get("metadata", {}).get("total_errors", 0),
            "high_priority_issues": violations.get("statistics", {}).get("high_priority", 0),
        }

    def calculate_quality_score(
        self, violations: Dict[str, Any], templates: Dict[str, Any], errors: Dict[str, Any]
    ) -> int:
        score = 100
        score -= 10 * violations.get("statistics", {}).get("high_priority", 0)
        score -= 2 * errors.get("metadata", {}).get("total_errors", 0)
        score -= 5 * templates.get("statistics", {}).get("high_priority", 0)
        return max(0, min(100, score))

    def generate_html_report(self, report: Dict[str, Any], output_file: str) -> str:
        # Build priorities list
        priorities_items = "".join(
            f"<li>{p.get('title','N/A')} ({p.get('count',0)})</li>" for p in report.get("priorities", [])
        ) or "<li>Nenhuma ação urgente necessária</li>"

        # Violations rows (combine violations + warnings)
        vio = (report.get("violations", {}).get("violations", []) or []) + (
            report.get("violations", {}).get("warnings", []) or []
        )
        vio_rows = "".join(
            f"<tr><td>{it.get('file','')}</td><td>{it.get('priority','')}</td><td>{len(it.get('violations',[]))}</td><td>{it.get('lines',0)}</td></tr>"
            for it in vio
        ) or "<tr><td colspan='4'>Sem registros</td></tr>"

        # Errors rows
        err_rows = "".join(
            f"<tr><td>{f.get('file','')}</td><td>{f.get('category','')}</td><td>{f.get('priority','')}</td><td>{f.get('error_count',0)}</td></tr>"
            for f in report.get("errors", {}).get("errors", []) or []
        ) or "<tr><td colspan='4'>Sem registros</td></tr>"

        # Templates rows
        tmpls = report.get("templates", {}).get("templates", []) or []
        tmpl_rows = "".join(
            f"<tr><td>{t.get('file','')}</td><td>{t.get('category','')}</td><td>{t.get('priority','')}</td><td>{t.get('total_css_chars', t.get('css', 0))}</td><td>{t.get('total_js_chars', t.get('js', 0))}</td></tr>"
            for t in tmpls
        ) or "<tr><td colspan='5'>Sem registros</td></tr>"

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
    .section {{ margin-top: 2rem; }}
  </style>
</head>
<body>
  <h1>Relatório - CodeHealthAnalyzer</h1>
  <p>Gerado em: {report.get("metadata", {}).get("generated_at", "")}</p>
  <h2>Resumo</h2>
  <ul>
    <li>Score de Qualidade: <strong>{report.get("summary", {}).get("quality_score", 0)}</strong></li>
    <li>Total de arquivos: {report.get("summary", {}).get("total_files", 0)}</li>
    <li>Arquivos com violações: {report.get("summary", {}).get("violation_files", 0)}</li>
    <li>Templates: {report.get("summary", {}).get("total_templates", 0)}</li>
    <li>Erros Ruff: {report.get("summary", {}).get("total_errors", 0)}</li>
  </ul>

  <div class="section">
    <h2>Prioridades</h2>
    <ol>
      {priorities_items}
    </ol>
  </div>

  <div class="section">
    <h2>Arquivos com Violações</h2>
    <table>
      <thead><tr><th>Arquivo</th><th>Prioridade</th><th>Qtd. Violações</th><th>Linhas</th></tr></thead>
      <tbody>
        {vio_rows}
      </tbody>
    </table>
  </div>

  <div class="section">
    <h2>Erros (Ruff)</h2>
    <table>
      <thead><tr><th>Arquivo</th><th>Categoria</th><th>Prioridade</th><th>Qtd. Erros</th></tr></thead>
      <tbody>
        {err_rows}
      </tbody>
    </table>
  </div>

  <div class="section">
    <h2>Templates</h2>
    <table>
      <thead><tr><th>Arquivo</th><th>Categoria</th><th>Prioridade</th><th>CSS (chars)</th><th>JS (chars)</th></tr></thead>
      <tbody>
        {tmpl_rows}
      </tbody>
    </table>
  </div>
</body>
</html>
""".strip()

        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        Path(output_file).write_text(html, encoding="utf-8")
        return html