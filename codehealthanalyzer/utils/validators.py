"""Utilitários de validação.

Este módulo contém validadores para caminhos, configurações e outros dados.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional


class PathValidator:
    """Validador de caminhos e arquivos."""
    
    @staticmethod
    def is_valid_directory(path: str) -> bool:
        """Verifica se o caminho é um diretório válido.
        
        Args:
            path (str): Caminho para verificar
            
        Returns:
            bool: True se for um diretório válido
        """
        try:
            return Path(path).is_dir()
        except (OSError, ValueError):
            return False
    
    @staticmethod
    def is_valid_file(path: str) -> bool:
        """Verifica se o caminho é um arquivo válido.
        
        Args:
            path (str): Caminho para verificar
            
        Returns:
            bool: True se for um arquivo válido
        """
        try:
            return Path(path).is_file()
        except (OSError, ValueError):
            return False
    
    @staticmethod
    def is_python_project(path: str) -> bool:
        """Verifica se o diretório contém um projeto Python.
        
        Args:
            path (str): Caminho do diretório
            
        Returns:
            bool: True se for um projeto Python
        """
        if not PathValidator.is_valid_directory(path):
            return False
        
        project_path = Path(path)
        
        # Verifica indicadores de projeto Python
        indicators = [
            'setup.py',
            'pyproject.toml',
            'requirements.txt',
            'Pipfile',
            'poetry.lock'
        ]
        
        for indicator in indicators:
            if (project_path / indicator).exists():
                return True
        
        # Verifica se há arquivos .py
        return any(project_path.rglob('*.py'))
    
    @staticmethod
    def has_templates(path: str) -> bool:
        """Verifica se o projeto tem templates HTML.
        
        Args:
            path (str): Caminho do diretório
            
        Returns:
            bool: True se houver templates
        """
        if not PathValidator.is_valid_directory(path):
            return False
        
        project_path = Path(path)
        return any(project_path.rglob('*.html'))
    
    @staticmethod
    def get_project_info(path: str) -> Dict[str, Any]:
        """Obtém informações sobre o projeto.
        
        Args:
            path (str): Caminho do projeto
            
        Returns:
            dict: Informações do projeto
        """
        if not PathValidator.is_valid_directory(path):
            return {'valid': False, 'error': 'Diretório inválido'}
        
        project_path = Path(path)
        
        info = {
            'valid': True,
            'path': str(project_path.absolute()),
            'name': project_path.name,
            'is_python_project': PathValidator.is_python_project(path),
            'has_templates': PathValidator.has_templates(path),
            'python_files': len(list(project_path.rglob('*.py'))),
            'html_files': len(list(project_path.rglob('*.html'))),
            'total_files': len([f for f in project_path.rglob('*') if f.is_file()])
        }
        
        return info
    
    @staticmethod
    def should_skip_path(path: Path) -> bool:
        """Verifica se um caminho deve ser ignorado.
        
        Args:
            path (Path): Caminho para verificar
            
        Returns:
            bool: True se deve ser ignorado
        """
        skip_patterns = [
            '.git', '__pycache__', '.pytest_cache', 'node_modules',
            '.venv', 'venv', '.env', 'migrations', '.ruff_cache',
            '.mypy_cache', '.tox', 'dist', 'build', '*.egg-info'
        ]
        
        path_str = str(path).lower()
        return any(pattern.lower() in path_str for pattern in skip_patterns)


class ConfigValidator:
    """Validador de configurações."""
    
    @staticmethod
    def validate_limits(limits: Dict) -> Dict[str, Any]:
        """Valida configurações de limites.
        
        Args:
            limits (dict): Configurações de limites
            
        Returns:
            dict: Resultado da validação
        """
        required_keys = [
            'python_function', 'python_class', 'python_module',
            'html_template', 'test_file'
        ]
        
        errors = []
        warnings = []
        
        for key in required_keys:
            if key not in limits:
                errors.append(f"Limite '{key}' não definido")
                continue
            
            limit_config = limits[key]
            if not isinstance(limit_config, dict):
                errors.append(f"Limite '{key}' deve ser um dicionário")
                continue
            
            if 'yellow' not in limit_config or 'red' not in limit_config:
                errors.append(f"Limite '{key}' deve ter 'yellow' e 'red'")
                continue
            
            yellow = limit_config['yellow']
            red = limit_config['red']
            
            if not isinstance(yellow, int) or not isinstance(red, int):
                errors.append(f"Limites de '{key}' devem ser inteiros")
                continue
            
            if yellow >= red:
                warnings.append(f"Limite yellow de '{key}' deve ser menor que red")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def validate_config(config: Dict) -> Dict[str, Any]:
        """Valida configuração completa.
        
        Args:
            config (dict): Configuração para validar
            
        Returns:
            dict: Resultado da validação
        """
        errors = []
        warnings = []
        
        # Valida limites se presentes
        if 'limits' in config:
            limits_validation = ConfigValidator.validate_limits(config['limits'])
            errors.extend(limits_validation['errors'])
            warnings.extend(limits_validation['warnings'])
        
        # Valida outras configurações
        if 'target_dir' in config:
            target_dir = config['target_dir']
            if not isinstance(target_dir, str):
                errors.append("'target_dir' deve ser uma string")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }


class DataValidator:
    """Validador de dados de relatórios."""
    
    @staticmethod
    def validate_report_data(data: Dict, report_type: str) -> Dict[str, Any]:
        """Valida dados de relatório.
        
        Args:
            data (dict): Dados para validar
            report_type (str): Tipo do relatório (violations, templates, errors)
            
        Returns:
            dict: Resultado da validação
        """
        errors = []
        warnings = []
        
        # Validações comuns
        if 'metadata' not in data:
            errors.append("Campo 'metadata' obrigatório")
        else:
            metadata = data['metadata']
            if 'generated_at' not in metadata:
                warnings.append("Campo 'generated_at' recomendado em metadata")
        
        if 'statistics' not in data:
            warnings.append("Campo 'statistics' recomendado")
        
        # Validações específicas por tipo
        if report_type == 'violations':
            if 'violations' not in data:
                errors.append("Campo 'violations' obrigatório para relatório de violações")
        
        elif report_type == 'templates':
            if 'templates' not in data:
                errors.append("Campo 'templates' obrigatório para relatório de templates")
        
        elif report_type == 'errors':
            if 'errors' not in data:
                errors.append("Campo 'errors' obrigatório para relatório de erros")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def sanitize_file_path(file_path: str) -> str:
        """Sanitiza caminho de arquivo para relatórios.
        
        Args:
            file_path (str): Caminho original
            
        Returns:
            str: Caminho sanitizado
        """
        # Remove caracteres problemáticos
        sanitized = file_path.replace('\\', '/')
        
        # Remove caminhos absolutos para relatórios
        if sanitized.startswith('/'):
            sanitized = sanitized[1:]
        
        return sanitized