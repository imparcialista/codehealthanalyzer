"""Interface de linha de comando para CodeHealthAnalyzer.

Este módulo fornece uma CLI amigável para usar a biblioteca CodeHealthAnalyzer.
"""

import click
import json
from pathlib import Path
from typing import Optional

from ..analyzers.violations import ViolationsAnalyzer
from ..analyzers.templates import TemplatesAnalyzer
from ..analyzers.errors import ErrorsAnalyzer
from ..reports.generator import ReportGenerator
from ..reports.formatter import ReportFormatter
from ..utils.validators import PathValidator
from ..utils.helpers import ColorHelper, TimeHelper
from .. import CodeAnalyzer


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """🔍 CodeHealthAnalyzer - Análise de qualidade e saúde de código.
    
    Uma ferramenta completa para analisar a qualidade do seu código Python,
    detectar violações de tamanho, analisar templates HTML e integrar com
    ferramentas de linting como Ruff.
    """
    pass


@cli.command()
@click.argument('project_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--output', '-o', type=click.Path(), help='Diretório de saída para relatórios')
@click.option('--format', '-f', type=click.Choice(['json', 'html', 'markdown', 'all']), default='json', help='Formato do relatório')
@click.option('--config', '-c', type=click.Path(exists=True), help='Arquivo de configuração JSON')
@click.option('--verbose', '-v', is_flag=True, help='Saída detalhada')
def analyze(project_path: str, output: Optional[str], format: str, config: Optional[str], verbose: bool):
    """🔍 Executa análise completa do projeto.
    
    Analisa violações de tamanho, templates HTML com CSS/JS inline,
    e erros de linting (Ruff) em um projeto Python.
    
    PROJECT_PATH: Caminho para o diretório do projeto
    """
    if verbose:
        click.echo(ColorHelper.info(f"Iniciando análise de {project_path}"))
    
    # Valida o projeto
    project_info = PathValidator.get_project_info(project_path)
    if not project_info['valid']:
        click.echo(ColorHelper.error(f"Projeto inválido: {project_info.get('error', 'Erro desconhecido')}"))
        return
    
    if verbose:
        click.echo(f"📊 Projeto: {project_info['name']}")
        click.echo(f"📁 Arquivos Python: {project_info['python_files']}")
        click.echo(f"🎨 Templates HTML: {project_info['html_files']}")
    
    # Carrega configuração se fornecida
    config_data = {}
    if config:
        try:
            with open(config, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            if verbose:
                click.echo(ColorHelper.info(f"Configuração carregada de {config}"))
        except Exception as e:
            click.echo(ColorHelper.warning(f"Erro ao carregar configuração: {e}"))
    
    # Executa análise
    try:
        analyzer = CodeAnalyzer(project_path, config_data)
        
        if verbose:
            click.echo("🔍 Executando análise...")
        
        report = analyzer.generate_full_report(output_dir=output)
        
        # Exibe resumo
        summary = report.get('summary', {})
        quality_score = summary.get('quality_score', 0)
        
        click.echo("\n" + "="*50)
        click.echo("📊 RESUMO DA ANÁLISE")
        click.echo("="*50)
        
        # Score de qualidade com cor
        if quality_score >= 80:
            score_text = ColorHelper.success(f"Score de Qualidade: {quality_score}/100")
        elif quality_score >= 60:
            score_text = ColorHelper.warning(f"Score de Qualidade: {quality_score}/100")
        else:
            score_text = ColorHelper.error(f"Score de Qualidade: {quality_score}/100")
        
        click.echo(score_text)
        click.echo(f"📁 Arquivos analisados: {summary.get('total_files', 0)}")
        click.echo(f"⚠️  Arquivos com violações: {summary.get('violation_files', 0)}")
        click.echo(f"🎨 Templates: {summary.get('total_templates', 0)}")
        click.echo(f"🔍 Erros Ruff: {summary.get('total_errors', 0)}")
        click.echo(f"🔥 Issues de alta prioridade: {summary.get('high_priority_issues', 0)}")
        
        # Prioridades de ação
        priorities = report.get('priorities', [])
        if priorities:
            click.echo("\n🎯 PRIORIDADES DE AÇÃO:")
            for i, priority in enumerate(priorities[:5], 1):  # Top 5
                icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(priority.get('priority', 'low'), '⚪')
                click.echo(f"{i}. {icon} {priority.get('title', 'N/A')} ({priority.get('count', 0)})")
        else:
            click.echo(ColorHelper.success("\n✅ Nenhuma ação urgente necessária!"))
        
        # Salva relatórios nos formatos solicitados
        if output:
            output_path = Path(output)
            formatter = ReportFormatter()
            
            if format in ['json', 'all']:
                json_file = output_path / 'full_report.json'
                formatter.to_json(report, str(json_file))
                if verbose:
                    click.echo(ColorHelper.success(f"Relatório JSON salvo em {json_file}"))
            
            if format in ['html', 'all']:
                html_file = output_path / 'report.html'
                ReportGenerator().generate_html_report(report, str(html_file))
                if verbose:
                    click.echo(ColorHelper.success(f"Relatório HTML salvo em {html_file}"))
            
            if format in ['markdown', 'all']:
                md_file = output_path / 'report.md'
                formatter.to_markdown(report, str(md_file))
                if verbose:
                    click.echo(ColorHelper.success(f"Relatório Markdown salvo em {md_file}"))
        
        click.echo("\n" + ColorHelper.success("Análise concluída com sucesso!"))
        
    except Exception as e:
        click.echo(ColorHelper.error(f"Erro durante análise: {e}"))
        if verbose:
            import traceback
            click.echo(traceback.format_exc())


@cli.command()
@click.argument('project_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--output', '-o', type=click.Path(), help='Arquivo de saída JSON')
@click.option('--config', '-c', type=click.Path(exists=True), help='Arquivo de configuração JSON')
def violations(project_path: str, output: Optional[str], config: Optional[str]):
    """🚨 Analisa apenas violações de tamanho.
    
    PROJECT_PATH: Caminho para o diretório do projeto
    """
    config_data = {}
    if config:
        try:
            with open(config, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except Exception as e:
            click.echo(ColorHelper.warning(f"Erro ao carregar configuração: {e}"))
    
    try:
        analyzer = ViolationsAnalyzer(project_path, config_data)
        report = analyzer.analyze()
        
        if output:
            analyzer.save_report(report, output)
            click.echo(ColorHelper.success(f"Relatório salvo em {output}"))
        else:
            click.echo(json.dumps(report, indent=2, ensure_ascii=False))
        
    except Exception as e:
        click.echo(ColorHelper.error(f"Erro: {e}"))


@cli.command()
@click.argument('project_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--output', '-o', type=click.Path(), help='Arquivo de saída JSON')
@click.option('--config', '-c', type=click.Path(exists=True), help='Arquivo de configuração JSON')
def templates(project_path: str, output: Optional[str], config: Optional[str]):
    """🎨 Analisa apenas templates HTML com CSS/JS inline.
    
    PROJECT_PATH: Caminho para o diretório do projeto
    """
    config_data = {}
    if config:
        try:
            with open(config, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except Exception as e:
            click.echo(ColorHelper.warning(f"Erro ao carregar configuração: {e}"))
    
    try:
        analyzer = TemplatesAnalyzer(project_path, config_data)
        report = analyzer.analyze()
        
        if output:
            analyzer.save_report(report, output)
            click.echo(ColorHelper.success(f"Relatório salvo em {output}"))
        else:
            click.echo(json.dumps(report, indent=2, ensure_ascii=False))
        
    except Exception as e:
        click.echo(ColorHelper.error(f"Erro: {e}"))


@cli.command()
@click.argument('project_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--output', '-o', type=click.Path(), help='Arquivo de saída JSON')
@click.option('--markdown', '-m', type=click.Path(), help='Arquivo de saída Markdown')
@click.option('--config', '-c', type=click.Path(exists=True), help='Arquivo de configuração JSON')
def errors(project_path: str, output: Optional[str], markdown: Optional[str], config: Optional[str]):
    """⚠️ Analisa apenas erros de linting (Ruff).
    
    PROJECT_PATH: Caminho para o diretório do projeto
    """
    config_data = {}
    if config:
        try:
            with open(config, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except Exception as e:
            click.echo(ColorHelper.warning(f"Erro ao carregar configuração: {e}"))
    
    try:
        analyzer = ErrorsAnalyzer(project_path, config_data)
        report = analyzer.analyze()
        
        if output:
            analyzer.save_report(report, output)
            click.echo(ColorHelper.success(f"Relatório JSON salvo em {output}"))
        
        if markdown:
            analyzer.create_markdown_report(report, markdown)
            click.echo(ColorHelper.success(f"Relatório Markdown salvo em {markdown}"))
        
        if not output and not markdown:
            click.echo(json.dumps(report, indent=2, ensure_ascii=False))
        
    except Exception as e:
        click.echo(ColorHelper.error(f"Erro: {e}"))


@cli.command()
@click.argument('project_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
def score(project_path: str):
    """📊 Mostra apenas o score de qualidade do projeto.
    
    PROJECT_PATH: Caminho para o diretório do projeto
    """
    try:
        analyzer = CodeAnalyzer(project_path)
        quality_score = analyzer.get_quality_score()
        
        if quality_score >= 80:
            score_text = ColorHelper.success(f"Score de Qualidade: {quality_score}/100 - Excelente!")
        elif quality_score >= 60:
            score_text = ColorHelper.warning(f"Score de Qualidade: {quality_score}/100 - Bom")
        else:
            score_text = ColorHelper.error(f"Score de Qualidade: {quality_score}/100 - Precisa melhorar")
        
        click.echo(score_text)
        
    except Exception as e:
        click.echo(ColorHelper.error(f"Erro: {e}"))


@cli.command()
@click.argument('project_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
def info(project_path: str):
    """ℹ️ Mostra informações sobre o projeto.
    
    PROJECT_PATH: Caminho para o diretório do projeto
    """
    project_info = PathValidator.get_project_info(project_path)
    
    if not project_info['valid']:
        click.echo(ColorHelper.error(f"Projeto inválido: {project_info.get('error', 'Erro desconhecido')}"))
        return
    
    click.echo("📊 INFORMAÇÕES DO PROJETO")
    click.echo("="*30)
    click.echo(f"📁 Nome: {project_info['name']}")
    click.echo(f"📂 Caminho: {project_info['path']}")
    click.echo(f"🐍 Projeto Python: {'Sim' if project_info['is_python_project'] else 'Não'}")
    click.echo(f"🎨 Tem templates: {'Sim' if project_info['has_templates'] else 'Não'}")
    click.echo(f"📄 Arquivos Python: {project_info['python_files']}")
    click.echo(f"🌐 Arquivos HTML: {project_info['html_files']}")
    click.echo(f"📊 Total de arquivos: {project_info['total_files']}")


def main():
    """Ponto de entrada principal da CLI."""
    cli()


if __name__ == '__main__':
    main()