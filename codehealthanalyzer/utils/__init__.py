"""Módulo de utilitários.

Contém classes e funções auxiliares para categorização, validação,
e outras operações de suporte.
"""

from .categorizer import Categorizer
from .helpers import FileHelper
from .validators import PathValidator

__all__ = ["Categorizer", "PathValidator", "FileHelper"]
