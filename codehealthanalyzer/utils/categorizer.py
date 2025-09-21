"""Utilitário para categorização de arquivos e problemas.

Este módulo contém a classe Categorizer que fornece métodos para categorizar
arquivos, violações e outros elementos baseado em regras predefinidas.
"""

from pathlib import Path
from typing import Any, Dict, List


class Categorizer:
    """Categorizador de arquivos e problemas.

    Args:
        config (dict, optional): Configurações de categorização
    """

    def __init__(self, config: dict = None):
        self.config = config or {}
        self._load_rules()

    def _load_rules(self):
        """Carrega regras de categorização."""
        self.file_rules = self.config.get(
            "file_rules",
            {
                "critical_files": [
                    "stock_updater_mlb.py",
                    "mlb_clone_backend.py",
                    "manage_product_links.html",
                ],
                "admin_patterns": ["admin", "admin_views"],
                "blueprint_patterns": ["blueprint", "blueprints"],
                "template_patterns": ["template", "templates"],
                "integration_patterns": ["integration", "integrations"],
                "payment_patterns": ["payment", "payments"],
            },
        )

        self.priority_rules = self.config.get(
            "priority_rules",
            {
                "high_threshold": {
                    "function_lines": 50,
                    "class_lines": 500,
                    "module_lines": 1000,
                    "template_lines": 200,
                    "css_js_chars": 20000,
                },
                "medium_threshold": {
                    "function_lines": 30,
                    "class_lines": 300,
                    "module_lines": 500,
                    "template_lines": 150,
                    "css_js_chars": 10000,
                },
            },
        )

    def categorize_file(self, file_path: Path) -> str:
        """Categoriza um arquivo baseado no seu caminho e nome.

        Args:
            file_path (Path): Caminho do arquivo

        Returns:
            str: Categoria do arquivo
        """
        path_str = str(file_path).lower()
        file_name = file_path.name.lower()

        # Verifica arquivos críticos
        if file_name in [f.lower() for f in self.file_rules["critical_files"]]:
            return "Arquivo Crítico"

        # Verifica padrões específicos
        if any(pattern in path_str for pattern in self.file_rules["admin_patterns"]):
            return "Views Admin"

        if any(
            pattern in path_str for pattern in self.file_rules["blueprint_patterns"]
        ):
            if any(
                pattern in path_str
                for pattern in self.file_rules["integration_patterns"]
            ):
                return "Blueprint Crítico"
            elif any(
                pattern in path_str for pattern in self.file_rules["payment_patterns"]
            ):
                return "Blueprint Pagamentos"
            else:
                return "Blueprint"

        if any(pattern in path_str for pattern in self.file_rules["template_patterns"]):
            if "manage_product_links" in file_name:
                return "Template Crítico"
            elif "base.html" in file_name:
                return "Template Base"
            elif "admin" in path_str:
                return "Template Admin"
            else:
                return "Template"

        return "Arquivo Padrão"

    def categorize_template(self, file_path: Path) -> str:
        """Categoriza um template HTML.

        Args:
            file_path (Path): Caminho do template

        Returns:
            str: Categoria do template
        """
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

    def categorize_error(self, error_code: str, message: str = "") -> str:
        """Categoriza um erro baseado no código e mensagem.

        Args:
            error_code (str): Código do erro (ex: F401, E501)
            message (str): Mensagem do erro

        Returns:
            str: Categoria do erro
        """
        # Categorização baseada no código do erro
        if error_code.startswith("F"):
            if error_code in ["F401", "F811", "F821"]:
                return "Erros de Importação"
            else:
                return "Erros de Sintaxe"
        elif error_code.startswith("E"):
            return "Erros de Estilo"
        elif error_code.startswith("W"):
            return "Avisos"
        elif error_code.startswith("C"):
            return "Complexidade"
        elif error_code.startswith("N"):
            return "Nomenclatura"
        else:
            return "Outros"

    def determine_priority(self, item_type: str, metrics: Dict[str, Any]) -> str:
        """Determina a prioridade de um item baseado em métricas.

        Args:
            item_type (str): Tipo do item (file, template, error)
            metrics (dict): Métricas do item

        Returns:
            str: Prioridade (high, medium, low)
        """
        if item_type == "file":
            lines = metrics.get("lines", 0)
            file_type = metrics.get("type", "").lower()

            if file_type == "python":
                if lines > self.priority_rules["high_threshold"]["module_lines"]:
                    return "high"
                elif lines > self.priority_rules["medium_threshold"]["module_lines"]:
                    return "medium"
            elif file_type == "html template":
                if lines > self.priority_rules["high_threshold"]["template_lines"]:
                    return "high"
                elif lines > self.priority_rules["medium_threshold"]["template_lines"]:
                    return "medium"

        elif item_type == "template":
            total_chars = metrics.get("css", 0) + metrics.get("js", 0)
            if total_chars > self.priority_rules["high_threshold"]["css_js_chars"]:
                return "high"
            elif total_chars > self.priority_rules["medium_threshold"]["css_js_chars"]:
                return "medium"

        elif item_type == "error":
            error_code = metrics.get("code", "")
            # Erros críticos (alta prioridade)
            critical_codes = ["F821", "F822", "F823", "E999"]
            if error_code in critical_codes:
                return "high"
            # Erros de sintaxe (média prioridade)
            if error_code.startswith("F") or error_code.startswith("E9"):
                return "medium"

        return "low"

    def get_category_icon(self, category: str) -> str:
        """Retorna ícone para uma categoria.

        Args:
            category (str): Nome da categoria

        Returns:
            str: Emoji/ícone da categoria
        """
        icons = {
            "Arquivo Crítico": "🔥",
            "Views Admin": "👑",
            "Blueprint Crítico": "⚡",
            "Blueprint Pagamentos": "💳",
            "Blueprint": "🔧",
            "Template Crítico": "🎯",
            "Template Base": "🏗️",
            "Template Admin": "👑",
            "Template Interativo": "🎮",
            "Template de Produtos": "📦",
            "Template ML": "🛒",
            "Template de Integração": "🔗",
            "Template": "📄",
            "Erros de Sintaxe": "❌",
            "Erros de Estilo": "🎨",
            "Erros de Importação": "📥",
            "Avisos": "⚠️",
            "Complexidade": "🌀",
            "Nomenclatura": "🏷️",
            "Outros": "❓",
        }

        return icons.get(category, "📁")

    def get_priority_color(self, priority: str) -> str:
        """Retorna cor para uma prioridade.

        Args:
            priority (str): Nível de prioridade

        Returns:
            str: Código de cor hexadecimal
        """
        colors = {"high": "#e74c3c", "medium": "#f39c12", "low": "#27ae60"}

        return colors.get(priority, "#95a5a6")

    def sort_by_priority(self, items: List[Dict], key: str = "priority") -> List[Dict]:
        """Ordena itens por prioridade.

        Args:
            items (list): Lista de itens para ordenar
            key (str): Chave que contém a prioridade

        Returns:
            list: Lista ordenada por prioridade
        """
        priority_order = {"high": 3, "medium": 2, "low": 1}

        return sorted(
            items, key=lambda x: priority_order.get(x.get(key, "low"), 0), reverse=True
        )
