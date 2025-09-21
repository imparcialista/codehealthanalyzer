"""Analisador de templates HTML com CSS/JS inline.

Este módulo contém a classe TemplatesAnalyzer que identifica CSS inline e JavaScript
que podem ser extraídos para arquivos externos.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class TemplatesAnalyzer:
    """Analisador de templates HTML.

    Args:
        project_path (str): Caminho para o diretório do projeto
        config (dict, optional): Configurações personalizadas
    """

    def __init__(self, project_path: str, config: dict = None):
        self.project_path = Path(project_path)
        self.config = config or {}
        # Permite configurar diretórios de templates via config['templates_dir']
        configured = self.config.get("templates_dir")
        paths: List[Path] = []
        if configured:
            if isinstance(configured, (list, tuple)):
                paths = [self.project_path / Path(p) for p in configured]
            else:
                paths = [self.project_path / Path(str(configured))]
        # Fallbacks comuns
        if not paths:
            paths = [
                self.project_path / "templates",
                self.project_path / "cha" / "templates",
            ]
        self.templates_paths = [p for p in paths]
        # Exclusions
        self.no_default_excludes = bool(self.config.get("no_default_excludes", False))
        self.user_exclude_dirs = list(self.config.get("exclude_dirs", []))

        self.results = []

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analisa um arquivo HTML em busca de CSS inline e JavaScript."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Remove comentários para análise mais limpa
            content_clean = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)

            analysis = {
                "file": str(file_path.relative_to(self.templates_paths[0])),
                "css_inline": self._extract_css_inline(content_clean),
                "css_style_tags": self._extract_style_tags(content_clean),
                "js_inline": self._extract_js_inline(content_clean),
                "js_script_tags": self._extract_script_tags(content_clean),
                "total_css_chars": 0,
                "total_js_chars": 0,
                "recommendations": [],
                "priority": "low",
                "category": self._categorize_template(file_path),
            }

            # Calcula totais
            analysis["total_css_chars"] = sum(
                len(css["content"]) for css in analysis["css_inline"]
            )
            analysis["total_css_chars"] += sum(
                len(css["content"]) for css in analysis["css_style_tags"]
            )

            analysis["total_js_chars"] = sum(
                len(js["content"]) for js in analysis["js_inline"]
            )
            analysis["total_js_chars"] += sum(
                len(js["content"]) for js in analysis["js_script_tags"]
            )

            # Gera recomendações
            analysis["recommendations"] = self._generate_recommendations(analysis)

            # Define prioridade
            total_chars = analysis["total_css_chars"] + analysis["total_js_chars"]
            if total_chars > 20000:
                analysis["priority"] = "high"
            elif total_chars > 10000:
                analysis["priority"] = "medium"

            # Adiciona campos para compatibilidade com o viewer
            analysis["css"] = analysis["total_css_chars"]
            analysis["js"] = analysis["total_js_chars"]

            return analysis

        except Exception as e:
            print(f"Erro ao analisar {file_path}: {e}")
            return {
                "file": str(file_path.relative_to(self.templates_paths[0])),
                "css_inline": [],
                "css_style_tags": [],
                "js_inline": [],
                "js_script_tags": [],
                "total_css_chars": 0,
                "total_js_chars": 0,
                "css": 0,
                "js": 0,
                "recommendations": [],
                "priority": "low",
                "category": "Template",
            }

    def _categorize_template(self, file_path: Path) -> str:
        """Categoriza o template baseado no seu nome e caminho."""
        path_str = str(file_path).lower()
        file_name = file_path.name.lower()

        if "manage_product_links" in file_name:
            return "Template Crítico"
        elif "base.html" in file_name:
            return "Template Base"
        elif "admin" in path_str:
            return "Template Admin"
        elif "clone_anuncios_progress" in file_name:
            return "Template Interativo"
        elif "product" in file_name or "bling_products" in file_name:
            return "Template de Produtos"
        elif "mercado_livre" in path_str:
            return "Template ML"
        elif "integrations" in path_str:
            return "Template de Integração"
        else:
            return "Template"

    def _extract_css_inline(self, content: str) -> List[Dict[str, Any]]:
        """Extrai CSS inline dos atributos style."""
        css_inline = []
        style_pattern = r'style\s*=\s*["\']([^"\'>]+)["\']'

        for match in re.finditer(style_pattern, content, re.IGNORECASE):
            css_content = match.group(1)
            if len(css_content.strip()) > 20:  # Só considera estilos significativos
                line_num = content[: match.start()].count("\n") + 1
                css_inline.append(
                    {
                        "line": line_num,
                        "content": css_content,
                        "length": len(css_content),
                    }
                )

        return css_inline

    def _extract_style_tags(self, content: str) -> List[Dict[str, Any]]:
        """Extrai conteúdo de tags <style>."""
        style_tags = []
        style_pattern = r"<style[^>]*>([\s\S]*?)</style>"

        for match in re.finditer(style_pattern, content, re.IGNORECASE):
            css_content = match.group(1).strip()
            if css_content:
                line_num = content[: match.start()].count("\n") + 1
                style_tags.append(
                    {
                        "line": line_num,
                        "content": css_content,
                        "length": len(css_content),
                    }
                )

        return style_tags

    def _extract_js_inline(self, content: str) -> List[Dict[str, Any]]:
        """Extrai JavaScript inline dos atributos de eventos."""
        js_inline = []

        # Padrões para eventos JavaScript inline
        event_patterns = [
            r'onclick\s*=\s*["\']([^"\'>]+)["\']',
            r'onchange\s*=\s*["\']([^"\'>]+)["\']',
            r'onsubmit\s*=\s*["\']([^"\'>]+)["\']',
            r'onload\s*=\s*["\']([^"\'>]+)["\']',
            r'onmouseover\s*=\s*["\']([^"\'>]+)["\']',
            r'onmouseout\s*=\s*["\']([^"\'>]+)["\']',
        ]

        for pattern in event_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                js_content = match.group(1)
                if len(js_content.strip()) > 10:  # Só considera JS significativo
                    line_num = content[: match.start()].count("\n") + 1
                    js_inline.append(
                        {
                            "line": line_num,
                            "content": js_content,
                            "length": len(js_content),
                            "event": pattern.split("\\")[0],
                        }
                    )

        return js_inline

    def _extract_script_tags(self, content: str) -> List[Dict[str, Any]]:
        """Extrai conteúdo de tags <script>."""
        script_tags = []
        script_pattern = r"<script(?![^>]*src\s*=)[^>]*>([\s\S]*?)</script>"

        for match in re.finditer(script_pattern, content, re.IGNORECASE):
            js_content = match.group(1).strip()
            if (
                js_content and len(js_content) > 50
            ):  # Só considera scripts significativos
                line_num = content[: match.start()].count("\n") + 1
                script_tags.append(
                    {
                        "line": line_num,
                        "content": js_content,
                        "length": len(js_content),
                    }
                )

        return script_tags

    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas na análise."""
        recommendations = []

        # Recomendações para CSS
        total_css = analysis["total_css_chars"]
        if total_css > 5000:
            recommendations.append(
                f"🎨 CSS: {total_css} caracteres - Considere extrair para arquivo CSS externo"
            )

        if analysis["css_style_tags"]:
            for style in analysis["css_style_tags"]:
                if style["length"] > 1000:
                    recommendations.append(
                        f"🎨 <style> grande na linha {style['line']} - Extrair para arquivo CSS"
                    )

        # Recomendações para JavaScript
        total_js = analysis["total_js_chars"]
        if total_js > 10000:
            recommendations.append(
                f"⚡ JavaScript: {total_js} caracteres - Considere extrair para arquivo JS externo"
            )

        if analysis["js_script_tags"]:
            for script in analysis["js_script_tags"]:
                if script["length"] > 2000:
                    recommendations.append(
                        f"⚡ <script> grande na linha {script['line']} - Extrair para arquivo JS"
                    )

        # Recomendações para JS inline
        if len(analysis["js_inline"]) > 5:
            recommendations.append(
                "⚡ Muitos eventos JavaScript inline - Considere usar event listeners"
            )

        return recommendations

    def _should_skip_file(self, file_path: Path) -> bool:
        """Verifica se o arquivo deve ser ignorado."""
        default_patterns = [
            "__pycache__",
            ".git",
            "node_modules",
            ".ruff_cache",
            "tests",
            "scripts",
            "reports",
            "dist",
            "build",
            "site-packages",
            ".tox",
            ".nox",
            ".venv",
            "venv",
        ]
        skip_patterns = [] if self.no_default_excludes else default_patterns
        skip_patterns.extend(self.user_exclude_dirs)
        path_str = str(file_path)
        return any(pattern in path_str for pattern in skip_patterns)

    def analyze(self) -> Dict:
        """Executa a análise completa de templates.

        Returns:
            dict: Relatório completo com análise de templates
        """
        results = []

        existing_paths = [p for p in self.templates_paths if p.exists()]
        if not existing_paths:
            # Nenhum diretório encontrado – retorna relatório vazio silenciosamente
            return self._empty_report()

        # Processa todos os arquivos HTML em todos os diretórios existentes
        for base in existing_paths:
            for html_file in base.rglob("*.html"):
                if self._should_skip_file(html_file):
                    continue
                analysis = self.analyze_file(html_file)
                if analysis["total_css_chars"] > 0 or analysis["total_js_chars"] > 0:
                    results.append(analysis)

        # Ordena por total de caracteres (CSS + JS)
        results.sort(
            key=lambda x: x["total_css_chars"] + x["total_js_chars"], reverse=True
        )

        # Gera estatísticas
        stats = {
            "total_templates": len(results),
            "total_css_chars": sum(r["total_css_chars"] for r in results),
            "total_js_chars": sum(r["total_js_chars"] for r in results),
            "high_priority": len([r for r in results if r["priority"] == "high"]),
            "medium_priority": len([r for r in results if r["priority"] == "medium"]),
            "templates_with_css": len([r for r in results if r["total_css_chars"] > 0]),
            "templates_with_js": len([r for r in results if r["total_js_chars"] > 0]),
        }

        return {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "templates_paths": [str(p) for p in existing_paths],
                "total_templates": stats["total_templates"],
            },
            "templates": results,
            "statistics": stats,
        }

    def _empty_report(self) -> Dict:
        """Retorna um relatório vazio."""
        return {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "templates_paths": [],
                "total_templates": 0,
            },
            "templates": [],
            "statistics": {
                "total_templates": 0,
                "total_css_chars": 0,
                "total_js_chars": 0,
                "high_priority": 0,
                "medium_priority": 0,
                "templates_with_css": 0,
                "templates_with_js": 0,
            },
        }

    def save_report(self, report: Dict, output_file: str):
        """Salva o relatório em arquivo JSON.

        Args:
            report (dict): Relatório gerado pela análise
            output_file (str): Caminho do arquivo de saída
        """
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
