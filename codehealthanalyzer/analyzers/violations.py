"""Analisador de violações de tamanho de arquivos e funções.

Este módulo contém a classe ViolationsAnalyzer que verifica limites de tamanho
conforme definido nas práticas de código do projeto.
"""


from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import json

# Limites definidos no CODE_PRACTICES.md
DEFAULT_LIMITS = {
    "python_function": {"yellow": 30, "red": 50},
    "python_class": {"yellow": 300, "red": 500},
    "python_module": {"yellow": 500, "red": 1000},
    "html_template": {"yellow": 150, "red": 200},
    "test_file": {"yellow": 400, "red": 600},
}


class ViolationsAnalyzer:
    """Analisador de violações de tamanho de código.
    
    Args:
        project_path (str): Caminho para o diretório do projeto
        config (dict, optional): Configurações personalizadas
    """
    
    def __init__(self, project_path: str, config: dict = None):
        self.project_path = Path(project_path)
        self.config = config or {}
        self.limits = self.config.get('limits', DEFAULT_LIMITS)
        self.violations = []
        self.warnings = []
    
    def count_effective_lines(self, file_path: Path, file_type: str) -> int:
        """Conta linhas efetivas (sem docstrings e linhas em branco)."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if file_type == "python":
                # Remove docstrings e linhas em branco para Python
                effective_lines = []
                in_docstring = False

                for line in lines:
                    stripped = line.strip()

                    # Detecta início/fim de docstring
                    if stripped.startswith('"""') or stripped.startswith("'''"):
                        if not in_docstring and not (
                            stripped.endswith('"""') or stripped.endswith("'''")
                        ):
                            in_docstring = True
                        continue
                    elif in_docstring and (
                        stripped.endswith('"""') or stripped.endswith("'''")
                    ):
                        in_docstring = False
                        continue

                    # Pula linhas em branco e comentários
                    if not in_docstring and stripped and not stripped.startswith("#"):
                        effective_lines.append(line)

                return len(effective_lines)
            else:
                # Para outros tipos, conta todas as linhas não vazias
                return len([line for line in lines if line.strip()])

        except Exception as e:
            print(f"Erro ao ler arquivo {file_path}: {e}")
            return 0
    
    def count_class_lines(self, file_path: Path) -> List[Tuple[str, int]]:
        """Conta linhas de cada classe no arquivo Python."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            classes = []
            current_class = None
            class_start = 0
            indent_level = 0

            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith("class ") and ":" in stripped:
                    if current_class:
                        classes.append((current_class, i - class_start))
                    current_class = stripped.split(":")[0].replace("class ", "")
                    class_start = i
                    indent_level = len(line) - len(line.lstrip())
                elif current_class and line.strip() and not line.startswith(" " * (indent_level + 1)):
                    if not stripped.startswith("#"):
                        classes.append((current_class, i - class_start))
                        current_class = None

            if current_class:
                classes.append((current_class, len(lines) - class_start))

            return classes
        except Exception as e:
            print(f"Erro ao analisar classes em {file_path}: {e}")
            return []
    
    def count_function_lines(self, file_path: Path) -> List[Tuple[str, int]]:
        """Conta linhas de cada função no arquivo Python."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            functions = []
            current_function = None
            function_start = 0
            indent_level = 0

            for i, line in enumerate(lines):
                stripped = line.strip()
                if (stripped.startswith("def ") or stripped.startswith("async def ")) and ":" in stripped:
                    if current_function:
                        functions.append((current_function, i - function_start))
                    current_function = stripped.split("(")[0].replace("def ", "").replace("async def ", "")
                    function_start = i
                    indent_level = len(line) - len(line.lstrip())
                elif current_function and line.strip() and not line.startswith(" " * (indent_level + 1)):
                    if not stripped.startswith("#") and not stripped.startswith('"""') and not stripped.startswith("'''"):
                        functions.append((current_function, i - function_start))
                        current_function = None

            if current_function:
                functions.append((current_function, len(lines) - function_start))

            return functions
        except Exception as e:
            print(f"Erro ao analisar funções em {file_path}: {e}")
            return []
    
    def categorize_file(self, file_path: Path) -> str:
        """Categoriza o arquivo baseado no seu caminho e nome."""
        path_str = str(file_path).lower()
        
        # Categorização baseada no caminho
        if 'admin' in path_str:
            return 'Views Admin'
        elif 'blueprint' in path_str:
            if 'integrations' in path_str:
                return 'Blueprint Crítico'
            elif 'payments' in path_str:
                return 'Blueprint Pagamentos'
            else:
                return 'Blueprint'
        elif 'templates' in path_str:
            if 'manage_product_links' in path_str:
                return 'Template Crítico'
            elif 'base.html' in path_str:
                return 'Template Base'
            else:
                return 'Template'
        elif file_path.name in ['stock_updater_mlb.py', 'mlb_clone_backend.py']:
            return 'Arquivo Crítico'
        else:
            return 'Arquivo Padrão'
    
    def check_file(self, file_path: Path) -> Dict:
        """Verifica um arquivo específico."""
        result = {
            "file": str(file_path.relative_to(self.project_path)),
            "type": "Unknown",
            "lines": 0,
            "violations": [],
            "priority": "low",
            "category": self.categorize_file(file_path)
        }

        if file_path.suffix == ".py":
            result["type"] = "Python"
            result["lines"] = self.count_effective_lines(file_path, "python")

            # Verifica limites do módulo
            if result["lines"] > self.limits["python_module"]["red"]:
                result["violations"].append(f"módulo: {result['lines']} linhas (limite: {self.limits['python_module']['red']})")
                result["priority"] = "high"
            elif result["lines"] > self.limits["python_module"]["yellow"]:
                result["violations"].append(f"módulo: {result['lines']} linhas (limite: {self.limits['python_module']['yellow']})")
                result["priority"] = "medium"

            # Verifica classes
            classes = self.count_class_lines(file_path)
            for class_name, class_lines in classes:
                if class_lines > self.limits["python_class"]["red"]:
                    result["violations"].append(f"class {class_name}: {class_lines} linhas (limite: {self.limits['python_class']['red']})")
                    result["priority"] = "high"
                elif class_lines > self.limits["python_class"]["yellow"]:
                    result["violations"].append(f"class {class_name}: {class_lines} linhas (limite: {self.limits['python_class']['yellow']})")
                    if result["priority"] == "low":
                        result["priority"] = "medium"

            # Verifica funções
            functions = self.count_function_lines(file_path)
            for func_name, func_lines in functions:
                if func_lines > self.limits["python_function"]["red"]:
                    result["violations"].append(f"function {func_name}: {func_lines} linhas (limite: {self.limits['python_function']['red']})")
                    result["priority"] = "high"
                elif func_lines > self.limits["python_function"]["yellow"]:
                    result["violations"].append(f"function {func_name}: {func_lines} linhas (limite: {self.limits['python_function']['yellow']})")
                    if result["priority"] == "low":
                        result["priority"] = "medium"

        elif file_path.suffix == ".html":
            result["type"] = "HTML Template"
            result["lines"] = self.count_effective_lines(file_path, "html")

            if result["lines"] > self.limits["html_template"]["red"]:
                result["violations"].append(f"template: {result['lines']} linhas (limite: {self.limits['html_template']['red']})")
                result["priority"] = "high"
            elif result["lines"] > self.limits["html_template"]["yellow"]:
                result["violations"].append(f"template: {result['lines']} linhas (limite: {self.limits['html_template']['yellow']})")
                result["priority"] = "medium"

        return result
    
    def should_skip_file(self, file_path: Path) -> bool:
        """Verifica se o arquivo deve ser ignorado."""
        skip_patterns = [
            ".git", "__pycache__", ".pytest_cache", "node_modules",
            ".venv", "venv", ".env", "migrations", ".ruff_cache"
        ]
        
        path_str = str(file_path)
        return any(pattern in path_str for pattern in skip_patterns)
    
    def analyze(self) -> Dict:
        """Executa a análise completa de violações.
        
        Returns:
            dict: Relatório completo com violações encontradas
        """
        all_results = []
        violations = []
        warnings = []
        
        # Processa arquivos Python
        for py_file in self.project_path.rglob("*.py"):
            if self.should_skip_file(py_file):
                continue
                
            result = self.check_file(py_file)
            all_results.append(result)
            
            if result["violations"]:
                if result["priority"] == "high":
                    violations.append(result)
                else:
                    warnings.append(result)
        
        # Processa templates HTML
        for html_file in self.project_path.rglob("*.html"):
            if self.should_skip_file(html_file):
                continue
                
            result = self.check_file(html_file)
            all_results.append(result)
            
            if result["violations"]:
                if result["priority"] == "high":
                    violations.append(result)
                else:
                    warnings.append(result)
        
        # Gera estatísticas
        stats = {
            "total_files": len(all_results),
            "violation_files": len(violations),
            "warning_files": len(warnings),
            "high_priority": len([v for v in violations if v["priority"] == "high"]),
            "medium_priority": len([v for v in violations + warnings if v["priority"] == "medium"]),
            "python_files": len([r for r in all_results if r["type"] == "Python"]),
            "html_files": len([r for r in all_results if r["type"] == "HTML Template"])
        }
        
        return {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "directory": str(self.project_path),
                "total_files": stats["total_files"],
                "violation_files": stats["violation_files"],
                "warning_files": stats["warning_files"]
            },
            "violations": violations,
            "warnings": warnings,
            "statistics": stats
        }
    
    def save_report(self, report: Dict, output_file: str):
        """Salva o relatório em arquivo JSON.
        
        Args:
            report (dict): Relatório gerado pela análise
            output_file (str): Caminho do arquivo de saída
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)