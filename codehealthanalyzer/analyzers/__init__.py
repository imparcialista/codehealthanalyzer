"""Módulo de analisadores de código.

Contém os analisadores especializados para diferentes aspectos da qualidade do código:
- ViolationsAnalyzer: Analisa violações de tamanho
- TemplatesAnalyzer: Analisa templates HTML com CSS/JS inline
- ErrorsAnalyzer: Analisa erros de linting (Ruff, etc.)
"""

from .errors import ErrorsAnalyzer
from .templates import TemplatesAnalyzer
from .violations import ViolationsAnalyzer

__all__ = ["ViolationsAnalyzer", "TemplatesAnalyzer", "ErrorsAnalyzer"]
