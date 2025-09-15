"""Módulo de utilitários.

Contém classes e funções auxiliares para categorização, validação,
e outras operações de suporte.
"""

from .categorizer import Categorizer
from .validators import PathValidator
from .helpers import FileHelper

__all__ = ['Categorizer', 'PathValidator', 'FileHelper']