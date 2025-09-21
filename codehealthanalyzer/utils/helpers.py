"""Utilitários auxiliares.

Este módulo contém funções auxiliares para operações comuns como
manipulação de arquivos, formatação de dados, etc.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class FileHelper:
    """Auxiliar para operações com arquivos."""

    @staticmethod
    def read_json(file_path: Union[str, Path]) -> Optional[Dict]:
        """Lê arquivo JSON de forma segura.

        Args:
            file_path: Caminho do arquivo JSON

        Returns:
            dict ou None: Dados do JSON ou None se erro
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"Erro ao ler {file_path}: {e}")
            return None

    @staticmethod
    def write_json(data: Dict, file_path: Union[str, Path], indent: int = 2) -> bool:
        """Escreve dados em arquivo JSON.

        Args:
            data: Dados para escrever
            file_path: Caminho do arquivo
            indent: Indentação do JSON

        Returns:
            bool: True se sucesso
        """
        try:
            # Cria diretório se não existir
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao escrever {file_path}: {e}")
            return False

    @staticmethod
    def read_text(file_path: Union[str, Path]) -> Optional[str]:
        """Lê arquivo de texto de forma segura.

        Args:
            file_path: Caminho do arquivo

        Returns:
            str ou None: Conteúdo do arquivo ou None se erro
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except (FileNotFoundError, UnicodeDecodeError) as e:
            print(f"Erro ao ler {file_path}: {e}")
            return None

    @staticmethod
    def write_text(content: str, file_path: Union[str, Path]) -> bool:
        """Escreve texto em arquivo.

        Args:
            content: Conteúdo para escrever
            file_path: Caminho do arquivo

        Returns:
            bool: True se sucesso
        """
        try:
            # Cria diretório se não existir
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Erro ao escrever {file_path}: {e}")
            return False

    @staticmethod
    def get_file_size(file_path: Union[str, Path]) -> int:
        """Obtém tamanho do arquivo em bytes.

        Args:
            file_path: Caminho do arquivo

        Returns:
            int: Tamanho em bytes ou 0 se erro
        """
        try:
            return Path(file_path).stat().st_size
        except (FileNotFoundError, OSError):
            return 0

    @staticmethod
    def get_file_lines(file_path: Union[str, Path]) -> int:
        """Conta número de linhas no arquivo.

        Args:
            file_path: Caminho do arquivo

        Returns:
            int: Número de linhas ou 0 se erro
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return sum(1 for _ in f)
        except (FileNotFoundError, UnicodeDecodeError):
            return 0

    @staticmethod
    def find_files(directory: Union[str, Path], pattern: str = "*") -> List[Path]:
        """Encontra arquivos em diretório.

        Args:
            directory: Diretório para buscar
            pattern: Padrão de busca (ex: '*.py')

        Returns:
            list: Lista de caminhos encontrados
        """
        try:
            return list(Path(directory).rglob(pattern))
        except Exception:
            return []


class DataHelper:
    """Auxiliar para manipulação de dados."""

    @staticmethod
    def format_bytes(bytes_count: int) -> str:
        """Formata bytes em formato legível.

        Args:
            bytes_count: Número de bytes

        Returns:
            str: Formato legível (ex: '1.5 KB')
        """
        for unit in ["B", "KB", "MB", "GB"]:
            if bytes_count < 1024.0:
                return f"{bytes_count:.1f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.1f} TB"

    @staticmethod
    def format_number(number: int) -> str:
        """Formata número com separadores de milhares.

        Args:
            number: Número para formatar

        Returns:
            str: Número formatado (ex: '1,234')
        """
        return f"{number:,}"

    @staticmethod
    def calculate_percentage(part: int, total: int) -> float:
        """Calcula percentual.

        Args:
            part: Parte
            total: Total

        Returns:
            float: Percentual (0-100)
        """
        if total == 0:
            return 0.0
        return (part / total) * 100

    @staticmethod
    def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
        """Mescla dois dicionários recursivamente.

        Args:
            dict1: Primeiro dicionário
            dict2: Segundo dicionário

        Returns:
            dict: Dicionário mesclado
        """
        result = dict1.copy()

        for key, value in dict2.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = DataHelper.merge_dicts(result[key], value)
            else:
                result[key] = value

        return result

    @staticmethod
    def flatten_list(nested_list: List[Any]) -> List[Any]:
        """Achata lista aninhada.

        Args:
            nested_list: Lista aninhada

        Returns:
            list: Lista achatada
        """
        result = []
        for item in nested_list:
            if isinstance(item, list):
                result.extend(DataHelper.flatten_list(item))
            else:
                result.append(item)
        return result

    @staticmethod
    def group_by(items: List[Dict], key: str) -> Dict[str, List[Dict]]:
        """Agrupa itens por chave.

        Args:
            items: Lista de dicionários
            key: Chave para agrupar

        Returns:
            dict: Itens agrupados
        """
        groups = {}
        for item in items:
            group_key = item.get(key, "unknown")
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(item)
        return groups

    @staticmethod
    def sort_by_key(items: List[Dict], key: str, reverse: bool = False) -> List[Dict]:
        """Ordena lista de dicionários por chave.

        Args:
            items: Lista de dicionários
            key: Chave para ordenar
            reverse: Ordem decrescente se True

        Returns:
            list: Lista ordenada
        """
        return sorted(items, key=lambda x: x.get(key, 0), reverse=reverse)


class TimeHelper:
    """Auxiliar para operações com tempo."""

    @staticmethod
    def now_iso() -> str:
        """Retorna timestamp atual em formato ISO.

        Returns:
            str: Timestamp ISO
        """
        return datetime.now().isoformat()

    @staticmethod
    def format_duration(seconds: float) -> str:
        """Formata duração em formato legível.

        Args:
            seconds: Duração em segundos

        Returns:
            str: Duração formatada
        """
        if seconds < 1:
            return f"{seconds*1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}min"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"

    @staticmethod
    def parse_iso_date(iso_string: str) -> Optional[datetime]:
        """Converte string ISO para datetime.

        Args:
            iso_string: String no formato ISO

        Returns:
            datetime ou None: Objeto datetime ou None se erro
        """
        try:
            return datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        except ValueError:
            return None


class ColorHelper:
    """Auxiliar para cores e formatação de terminal."""

    # Códigos ANSI para cores
    COLORS = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "reset": "\033[0m",
        "bold": "\033[1m",
    }

    @staticmethod
    def colorize(text: str, color: str) -> str:
        """Adiciona cor ao texto para terminal.

        Args:
            text: Texto para colorir
            color: Nome da cor

        Returns:
            str: Texto colorido
        """
        if color not in ColorHelper.COLORS:
            return text

        return f"{ColorHelper.COLORS[color]}{text}{ColorHelper.COLORS['reset']}"

    @staticmethod
    def success(text: str) -> str:
        """Formata texto como sucesso (verde)."""
        return ColorHelper.colorize(f"[OK] {text}", "green")

    @staticmethod
    def warning(text: str) -> str:
        """Formata texto como aviso (amarelo)."""
        return ColorHelper.colorize(f"[WARN] {text}", "yellow")

    @staticmethod
    def error(text: str) -> str:
        """Formata texto como erro (vermelho)."""
        return ColorHelper.colorize(f"[ERROR] {text}", "red")

    @staticmethod
    def info(text: str) -> str:
        """Formata texto como informação (azul)."""
        return ColorHelper.colorize(f"[INFO] {text}", "blue")
