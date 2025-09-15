"""CodeHealthAnalyzer - Uma biblioteca Python para análise de qualidade de código.

Esta biblioteca fornece ferramentas para analisar a saúde do código Python,
incluindo detecção de violações de tamanho, análise de templates HTML com CSS/JS inline,
e integração com ferramentas de linting como Ruff.

Exemplo de uso:
    from codehealthanalyzer import CodeAnalyzer
    
    analyzer = CodeAnalyzer('/path/to/project')
    report = analyzer.generate_full_report()
    print(report.summary())
"""

__version__ = "1.0.0"
__author__ = "Imparcialista Team"
__email__ = "dev@imparcialista.com"
__description__ = "Biblioteca Python para análise de qualidade e saúde de código"

from .analyzers.violations import ViolationsAnalyzer
from .analyzers.templates import TemplatesAnalyzer
from .analyzers.errors import ErrorsAnalyzer
from .reports.generator import ReportGenerator
from .utils.categorizer import Categorizer

# Classe principal da biblioteca
class CodeAnalyzer:
    """Classe principal para análise de código.
    
    Args:
        project_path (str): Caminho para o diretório do projeto
        config (dict, optional): Configurações personalizadas
    """
    
    def __init__(self, project_path: str, config: dict = None):
        self.project_path = project_path
        self.config = config or {}
        
        # Inicializa os analisadores
        self.violations_analyzer = ViolationsAnalyzer(project_path, self.config)
        self.templates_analyzer = TemplatesAnalyzer(project_path, self.config)
        self.errors_analyzer = ErrorsAnalyzer(project_path, self.config)
        
        # Inicializa o gerador de relatórios
        self.report_generator = ReportGenerator(self.config)
    
    def analyze_violations(self):
        """Analisa violações de tamanho de arquivo e função."""
        return self.violations_analyzer.analyze()
    
    def analyze_templates(self):
        """Analisa templates HTML com CSS/JS inline."""
        return self.templates_analyzer.analyze()
    
    def analyze_errors(self):
        """Analisa erros do Ruff e outras ferramentas de linting."""
        return self.errors_analyzer.analyze()
    
    def generate_full_report(self, output_dir: str = None):
        """Gera relatório completo com todas as análises.
        
        Args:
            output_dir (str, optional): Diretório para salvar os relatórios
            
        Returns:
            dict: Relatório completo com todas as análises
        """
        violations = self.analyze_violations()
        templates = self.analyze_templates()
        errors = self.analyze_errors()
        
        return self.report_generator.generate_full_report(
            violations=violations,
            templates=templates,
            errors=errors,
            output_dir=output_dir
        )
    
    def get_quality_score(self):
        """Calcula o score de qualidade do código (0-100).
        
        Returns:
            int: Score de qualidade entre 0 e 100
        """
        violations = self.analyze_violations()
        templates = self.analyze_templates()
        errors = self.analyze_errors()
        
        return self.report_generator.calculate_quality_score(
            violations, templates, errors
        )

# Exporta as classes principais
__all__ = [
    'CodeAnalyzer',
    'ViolationsAnalyzer',
    'TemplatesAnalyzer', 
    'ErrorsAnalyzer',
    'ReportGenerator',
    'Categorizer'
]