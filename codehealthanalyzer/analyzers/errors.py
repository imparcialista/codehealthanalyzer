"""Analisador de erros de linting (Ruff).

Este módulo contém a classe ErrorsAnalyzer que executa ferramentas de linting
como Ruff e analisa os erros encontrados.
"""

import json
import shutil
import subprocess  # nosec B404
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class ErrorsAnalyzer:
    """Analisador de erros de linting.

    Args:
        project_path (str): Caminho para o diretório do projeto
        config (dict, optional): Configurações personalizadas
    """

    def __init__(self, project_path: str, config: dict = None):
        self.project_path = Path(project_path)
        self.config = config or {}
        # Diretório alvo para varredura do Ruff; padrão para raiz do projeto
        self.target_dir = self.config.get("target_dir", ".")
        # Exclusions
        self.no_default_excludes = bool(self.config.get("no_default_excludes", False))
        self.user_exclude_dirs = list(self.config.get("exclude_dirs", []))

    def run_ruff_check(self) -> List[Dict]:
        """Executa ruff check e retorna os erros."""
        try:
            ruff_executable = shutil.which("ruff")
            if not ruff_executable:
                print("Ruff não encontrado. Instale com: pip install ruff")
                return []

            # Se habilitado na config, tenta aplicar correções automáticas
            if self.config.get("ruff_fix", False):
                subprocess.run(  # nosec B607, B603
                    [ruff_executable, "check", self.target_dir, "--fix"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_path,
                )

            # Depois, verifica erros restantes
            result = subprocess.run(  # nosec B607, B603
                [ruff_executable, "check", self.target_dir, "--output-format", "json"],
                capture_output=True,
                text=True,
                cwd=self.project_path,
            )

            if result.stdout:
                return json.loads(result.stdout)
            return []
        except subprocess.CalledProcessError as e:
            print(f"Erro ao executar ruff: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON: {e}")
            return []
        except FileNotFoundError:
            print("Ruff não encontrado. Instale com: pip install ruff")
            return []

    def categorize_error(self, error: Dict) -> str:
        """Categoriza o erro baseado no código."""
        code = error.get("code", "")

        # Categorização baseada no código do erro
        if code.startswith("F"):
            if code in ["F401", "F811", "F821"]:
                return "Erros de Importação"
            else:
                return "Erros de Sintaxe"
        elif code.startswith("E"):
            return "Erros de Estilo"
        elif code.startswith("W"):
            return "Avisos"
        elif code.startswith("C"):
            return "Complexidade"
        elif code.startswith("N"):
            return "Nomenclatura"
        else:
            return "Outros"

    def determine_priority(self, error: Dict) -> str:
        """Determina a prioridade do erro."""
        code = error.get("code", "")

        # Erros críticos (alta prioridade)
        critical_codes = ["F821", "F822", "F823", "E999"]
        if code in critical_codes:
            return "high"

        # Erros de sintaxe (média prioridade)
        if code.startswith("F") or code.startswith("E9"):
            return "medium"

        # Outros erros (baixa prioridade)
        return "low"

    def process_errors(self, raw_errors: List[Dict]) -> List[Dict]:
        """Processa e agrupa erros por arquivo."""
        files_data = {}
        default_patterns = [
            ".git",
            "__pycache__",
            ".pytest_cache",
            "node_modules",
            ".venv",
            "venv",
            ".env",
            "migrations",
            ".ruff_cache",
            "tests",
            "scripts",
            "reports",
            "dist",
            "build",
            "site-packages",
            ".tox",
            ".nox",
        ]
        skip_patterns = [] if self.no_default_excludes else default_patterns
        skip_patterns.extend(self.user_exclude_dirs)

        for error in raw_errors:
            filename = error.get("filename", "unknown")
            # Ignora arquivos/pastas não relevantes
            if any(pat in filename for pat in skip_patterns):
                continue

            if filename not in files_data:
                files_data[filename] = {
                    "file": filename,
                    "error_count": 0,
                    "errors": [],
                    "priority": "low",
                    "category": "Outros",
                }

            # Processa erro individual
            processed_error = {
                "line": error.get("location", {}).get("row", 0),
                "column": error.get("location", {}).get("column", 0),
                "code": error.get("code", ""),
                "message": error.get("message", ""),
                "rule": error.get("rule", ""),
            }

            files_data[filename]["errors"].append(processed_error)
            files_data[filename]["error_count"] += 1

            # Atualiza prioridade e categoria do arquivo
            error_priority = self.determine_priority(error)
            if error_priority == "high":
                files_data[filename]["priority"] = "high"
            elif (
                error_priority == "medium" and files_data[filename]["priority"] == "low"
            ):
                files_data[filename]["priority"] = "medium"

            # Atualiza categoria (usa a mais específica)
            error_category = self.categorize_error(error)
            if files_data[filename]["category"] == "Outros":
                files_data[filename]["category"] = error_category

        return list(files_data.values())

    def analyze(self) -> Dict:
        """Executa a análise completa de erros.

        Returns:
            dict: Relatório completo com erros encontrados
        """
        raw_errors = self.run_ruff_check()
        processed_errors = self.process_errors(raw_errors)

        # Calcula estatísticas
        total_errors = sum(file_data["error_count"] for file_data in processed_errors)

        stats = {
            "high_priority": len(
                [f for f in processed_errors if f["priority"] == "high"]
            ),
            "medium_priority": len(
                [f for f in processed_errors if f["priority"] == "medium"]
            ),
            "low_priority": len(
                [f for f in processed_errors if f["priority"] == "low"]
            ),
            "syntax_errors": len(
                [f for f in processed_errors if f["category"] == "Erros de Sintaxe"]
            ),
            "style_errors": len(
                [f for f in processed_errors if f["category"] == "Erros de Estilo"]
            ),
            "critical_errors": len(
                [f for f in processed_errors if f["priority"] == "high"]
            ),
        }

        return {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_errors": total_errors,
                "total_files": len(processed_errors),
            },
            "errors": processed_errors,
            "statistics": stats,
        }

    def save_report(self, report: Dict, output_file: str):
        """Salva o relatório em arquivo JSON.

        Args:
            report (dict): Relatório gerado pela análise
            output_file (str): Caminho do arquivo de saída
        """
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    def create_markdown_report(self, report: Dict, output_file: str):
        """Cria relatório em formato Markdown.

        Args:
            report (dict): Relatório gerado pela análise
            output_file (str): Caminho do arquivo de saída
        """
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# 🔍 Relatório de Erros Ruff\n\n")
            f.write(f"**Gerado em:** {report['metadata']['generated_at']}\n\n")
            f.write(f"**Total de erros:** {report['metadata']['total_errors']}\n")
            f.write(f"**Arquivos com erros:** {report['metadata']['total_files']}\n\n")

            if not report["errors"]:
                f.write("✅ **Nenhum erro encontrado!** Seu código está limpo.\n")
                return

            f.write("## 📊 Estatísticas\n\n")
            stats = report["statistics"]
            f.write(f"- **Alta prioridade:** {stats['high_priority']} arquivos\n")
            f.write(f"- **Média prioridade:** {stats['medium_priority']} arquivos\n")
            f.write(f"- **Baixa prioridade:** {stats['low_priority']} arquivos\n")
            f.write(f"- **Erros de sintaxe:** {stats['syntax_errors']} arquivos\n")
            f.write(f"- **Erros de estilo:** {stats['style_errors']} arquivos\n\n")

            f.write("## 📋 Detalhes dos Erros\n\n")

            for file_data in report["errors"]:
                priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                    file_data["priority"], "⚪"
                )

                f.write(f"### {priority_icon} {file_data['file']}\n\n")
                f.write(f"**Categoria:** {file_data['category']}\n")
                f.write(f"**Prioridade:** {file_data['priority']}\n")
                f.write(f"**Total de erros:** {file_data['error_count']}\n\n")

                for error in file_data["errors"]:
                    f.write(
                        f"- **Linha {error['line']}:** `{error['code']}` - {error['message']}\n"
                    )

                f.write("\n")
