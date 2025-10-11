"""Interface de linha de comando para CodeHealthAnalyzer.

Este módulo fornece uma CLI amigável para usar a biblioteca CodeHealthAnalyzer.
"""

import json
import shutil
import subprocess
from pathlib import Path
from typing import Optional

import click

from .. import CodeAnalyzer, __version__
from ..analyzers.errors import ErrorsAnalyzer
from ..analyzers.templates import TemplatesAnalyzer
from ..analyzers.violations import ViolationsAnalyzer
from ..reports.formatter import ReportFormatter
from ..reports.generator import ReportGenerator
from ..utils.helpers import ColorHelper
from ..utils.validators import PathValidator


@click.group()
@click.version_option(version=__version__)
def cli():
    """CodeHealthAnalyzer - Análise de qualidade e saúde de código.

    Uma ferramenta para analisar a qualidade do seu código Python,
    detectar violações de tamanho, analisar templates HTML e integrar com
    ferramentas de linting como Ruff.
    """
    pass


@cli.command()
@click.argument(
    "project_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=".",
    required=False,
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Diretório de saída para relatórios (padrão: ./reports)",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "html", "markdown", "all"]),
    default="json",
    help="Formato do relatório (além do JSON padrão)",
)
@click.option("--no-json", is_flag=True, help="Não gerar o relatório JSON padrão")
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Arquivo de configuração JSON"
)
@click.option(
    "--no-default-excludes",
    is_flag=True,
    help="Não aplicar exclusões padrão (tests, scripts, reports, venv, etc.)",
)
@click.option("--verbose", "-v", is_flag=True, help="Saída detalhada")
def analyze(
    project_path: str,
    output: Optional[str],
    format: str,
    no_json: bool,
    config: Optional[str],
    no_default_excludes: bool,
    verbose: bool,
):
    """Executa análise completa do projeto.

    Analisa violações de tamanho, templates HTML com CSS/JS inline,
    e erros de linting (Ruff) em um projeto Python.

    PROJECT_PATH: Caminho para o diretório do projeto
    """
    if verbose:
        click.echo(ColorHelper.info(f"Iniciando análise de {project_path}"))

    # Valida o projeto
    project_info = PathValidator.get_project_info(project_path)
    if not project_info["valid"]:
        click.echo(
            ColorHelper.error(
                f"Projeto inválido: {project_info.get('error', 'Erro desconhecido')}"
            )
        )
        return

    if verbose:
        click.echo(f"Projeto: {project_info['name']}")
        click.echo(f"Arquivos Python: {project_info['python_files']}")
        click.echo(f"Templates HTML: {project_info['html_files']}")

    # Carrega configuração se fornecida
    config_data = {}
    if config:
        try:
            with open(config, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            if verbose:
                click.echo(ColorHelper.info(f"Configuração carregada de {config}"))
        except Exception as e:
            click.echo(ColorHelper.warning(f"Erro ao carregar configuração: {e}"))
    # Aplica flag de exclusões
    if no_default_excludes:
        config_data["no_default_excludes"] = True

    # Adiciona diretórios de templates padrão se não configurados
    if "templates_dir" not in config_data:
        config_data["templates_dir"] = [
            "templates",
            "cha/templates",
            "codehealthanalyzer/web/templates",
        ]

    # Executa análise
    try:
        analyzer = CodeAnalyzer(project_path, config_data)

        if verbose:
            click.echo("Executando análise...")

        # Gera relatório em memória (salvamento tratado abaixo)
        report = analyzer.generate_full_report()

        # Exibe resumo
        summary = report.get("summary", {})
        quality_score = summary.get("quality_score", 0)

        click.echo("\n" + "=" * 50)
        click.echo("RESUMO DA ANÁLISE")
        click.echo("=" * 50)

        # Score de qualidade com cor
        if quality_score >= 80:
            score_text = ColorHelper.success(f"Score de Qualidade: {quality_score}/100")
        elif quality_score >= 60:
            score_text = ColorHelper.warning(f"Score de Qualidade: {quality_score}/100")
        else:
            score_text = ColorHelper.error(f"Score de Qualidade: {quality_score}/100")

        click.echo(score_text)
        click.echo(f"Arquivos analisados: {summary.get('total_files', 0)}")
        click.echo(f"Arquivos com violações: {summary.get('violation_files', 0)}")
        click.echo(f"Templates: {summary.get('total_templates', 0)}")
        click.echo(f"Erros Ruff: {summary.get('total_errors', 0)}")
        click.echo(
            f"Issues de alta prioridade: {summary.get('high_priority_issues', 0)}"
        )

        # Prioridades de ação
        priorities = report.get("priorities", [])
        if priorities:
            click.echo("\nPRIORIDADES DE AÇÃO:")
            for i, priority in enumerate(priorities[:5], 1):  # Top 5
                icon = {"high": "", "medium": "", "low": ""}.get(
                    priority.get("priority", "low"), ""
                )
                click.echo(
                    f"{i}. {icon} {priority.get('title', 'N/A')} ({priority.get('count', 0)})"
                )
        else:
            click.echo(ColorHelper.success("\nNenhuma ação urgente necessária!"))

        # Diretório de saída padrão
        output_path = Path(output or "reports")
        output_path.mkdir(parents=True, exist_ok=True)
        formatter = ReportFormatter()

        # Sempre gerar JSON por padrão, a menos que o usuário desabilite
        if not no_json:
            json_file = output_path / "full_report.json"
            formatter.to_json(report, str(json_file))
            if verbose:
                click.echo(ColorHelper.success(f"Relatório JSON salvo em {json_file}"))

        # Gerar formatos adicionais conforme solicitado
        if format in ["html", "all"]:
            html_file = output_path / "report.html"
            ReportGenerator().generate_html_report(report, str(html_file))
            if verbose:
                click.echo(ColorHelper.success(f"Relatório HTML salvo em {html_file}"))

        if format in ["markdown", "all"]:
            md_file = output_path / "report.md"
            formatter.to_markdown(report, str(md_file))
            if verbose:
                click.echo(
                    ColorHelper.success(f"Relatório Markdown salvo em {md_file}")
                )

        click.echo("\n" + ColorHelper.success("Análise concluída com sucesso!"))

    except Exception as e:
        click.echo(ColorHelper.error(f"Erro durante análise: {e}"))
        if verbose:
            import traceback

            click.echo(traceback.format_exc())


@cli.command()
@click.argument(
    "project_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=".",
    required=False,
)
@click.option(
    "--output", "-o", type=click.Path(), help="Diretório de saída (padrão: ./reports)"
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "html", "markdown", "all"]),
    default="json",
    help="Formato adicional do relatório",
)
@click.option("--no-json", is_flag=True, help="Não gerar o relatório JSON padrão")
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Arquivo de configuração JSON"
)
@click.option(
    "--no-default-excludes",
    is_flag=True,
    help="Não aplicar exclusões padrão (tests, scripts, reports, venv, etc.)",
)
def violations(
    project_path: str,
    output: Optional[str],
    format: str,
    no_json: bool,
    config: Optional[str],
    no_default_excludes: bool,
):
    """Analisa apenas violações de tamanho.

    PROJECT_PATH: Caminho para o diretório do projeto
    """
    config_data = {}
    if config:
        try:
            with open(config, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except Exception as e:
            click.echo(ColorHelper.warning(f"Erro ao carregar configuração: {e}"))
    if no_default_excludes:
        config_data["no_default_excludes"] = True

    try:
        analyzer = ViolationsAnalyzer(project_path, config_data)
        report = analyzer.analyze()

        # Diretório de saída padrão
        output_path = Path(output or "reports")
        output_path.mkdir(parents=True, exist_ok=True)

        # JSON por padrão
        if not no_json:
            json_file = output_path / "violations_report.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            click.echo(ColorHelper.success(f"Relatório JSON salvo em {json_file}"))

        # Formatos adicionais
        if format in ["html", "all"]:
            html_file = output_path / "violations_report.html"
            _render_violations_html(report, html_file)
            click.echo(ColorHelper.success(f"Relatório HTML salvo em {html_file}"))

        if format in ["markdown", "all"]:
            md_file = output_path / "violations_report.md"
            _render_violations_md(report, md_file)
            click.echo(ColorHelper.success(f"Relatório Markdown salvo em {md_file}"))

    except Exception as e:
        click.echo(ColorHelper.error(f"Erro: {e}"))


@cli.command()
@click.argument(
    "project_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=".",
    required=False,
)
@click.option(
    "--output", "-o", type=click.Path(), help="Diretório de saída (padrão: ./reports)"
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "html", "markdown", "all"]),
    default="json",
    help="Formato adicional do relatório",
)
@click.option("--no-json", is_flag=True, help="Não gerar o relatório JSON padrão")
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Arquivo de configuração JSON"
)
@click.option(
    "--no-default-excludes",
    is_flag=True,
    help="Não aplicar exclusões padrão (tests, scripts, reports, venv, etc.)",
)
def templates(
    project_path: str,
    output: Optional[str],
    format: str,
    no_json: bool,
    config: Optional[str],
    no_default_excludes: bool,
):
    """Analisa apenas templates HTML com CSS/JS inline.

    PROJECT_PATH: Caminho para o diretório do projeto
    """
    config_data = {}
    if config:
        try:
            with open(config, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except Exception as e:
            click.echo(ColorHelper.warning(f"Erro ao carregar configuração: {e}"))

    if no_default_excludes:
        config_data["no_default_excludes"] = True

    # Adiciona diretórios de templates padrão se não configurados
    if "templates_dir" not in config_data:
        config_data["templates_dir"] = [
            "templates",
            "cha/templates",
            "codehealthanalyzer/web/templates",
        ]

    try:
        analyzer = TemplatesAnalyzer(project_path, config_data)
        report = analyzer.analyze()

        # Diretório de saída padrão
        output_path = Path(output or "reports")
        output_path.mkdir(parents=True, exist_ok=True)

        if not no_json:
            json_file = output_path / "templates_report.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            click.echo(ColorHelper.success(f"Relatório JSON salvo em {json_file}"))

        if format in ["html", "all"]:
            html_file = output_path / "templates_report.html"
            _render_templates_html(report, html_file)
            click.echo(ColorHelper.success(f"Relatório HTML salvo em {html_file}"))

        if format in ["markdown", "all"]:
            md_file = output_path / "templates_report.md"
            _render_templates_md(report, md_file)
            click.echo(ColorHelper.success(f"Relatório Markdown salvo em {md_file}"))

    except Exception as e:
        click.echo(ColorHelper.error(f"Erro: {e}"))


@cli.command()
@click.argument(
    "project_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=".",
    required=False,
)
@click.option(
    "--output", "-o", type=click.Path(), help="Diretório de saída (padrão: ./reports)"
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "html", "markdown", "all"]),
    default="json",
    help="Formato adicional do relatório",
)
@click.option("--no-json", is_flag=True, help="Não gerar o relatório JSON padrão")
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Arquivo de configuração JSON"
)
@click.option(
    "--no-default-excludes",
    is_flag=True,
    help="Não aplicar exclusões padrão (tests, scripts, reports, venv, etc.)",
)
def errors(
    project_path: str,
    output: Optional[str],
    format: str,
    no_json: bool,
    config: Optional[str],
    no_default_excludes: bool,
):
    """Analisa apenas erros de linting (Ruff).

    PROJECT_PATH: Caminho para o diretório do projeto
    """
    config_data = {}
    if config:
        try:
            with open(config, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except Exception as e:
            click.echo(ColorHelper.warning(f"Erro ao carregar configuração: {e}"))

    try:
        analyzer = ErrorsAnalyzer(project_path, config_data)
        report = analyzer.analyze()

        output_path = Path(output or "reports")
        output_path.mkdir(parents=True, exist_ok=True)

        if not no_json:
            json_file = output_path / "errors_report.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            click.echo(ColorHelper.success(f"Relatório JSON salvo em {json_file}"))

        if format in ["html", "all"]:
            html_file = output_path / "errors_report.html"
            _render_errors_html(report, html_file)
            click.echo(ColorHelper.success(f"Relatório HTML salvo em {html_file}"))

        if format in ["markdown", "all"]:
            md_file = output_path / "errors_report.md"
            _render_errors_md(report, md_file)
            click.echo(ColorHelper.success(f"Relatório Markdown salvo em {md_file}"))

    except Exception as e:
        click.echo(ColorHelper.error(f"Erro: {e}"))


@cli.command()
@click.argument(
    "project_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=".",
    required=False,
)
def score(project_path: str):
    """Mostra apenas o score de qualidade do projeto.

    PROJECT_PATH: Caminho para o diretório do projeto
    """
    try:
        analyzer = CodeAnalyzer(project_path)
        quality_score = analyzer.get_quality_score()

        if quality_score >= 80:
            score_text = ColorHelper.success(
                f"Score de Qualidade: {quality_score}/100 - Excelente!"
            )
        elif quality_score >= 60:
            score_text = ColorHelper.warning(
                f"Score de Qualidade: {quality_score}/100 - Bom"
            )
        else:
            score_text = ColorHelper.error(
                f"Score de Qualidade: {quality_score}/100 - Precisa melhorar"
            )

        click.echo(score_text)

    except Exception as e:
        click.echo(ColorHelper.error(f"Erro: {e}"))


@cli.command()
@click.argument(
    "project_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=".",
    required=False,
)
def info(project_path: str):
    """Mostra informações sobre o projeto.

    PROJECT_PATH: Caminho para o diretório do projeto
    """
    project_info = PathValidator.get_project_info(project_path)

    if not project_info["valid"]:
        click.echo(
            ColorHelper.error(
                f"Projeto inválido: {project_info.get('error', 'Erro desconhecido')}"
            )
        )
        return

    click.echo("INFORMAÇÕES DO PROJETO")
    click.echo("=" * 30)
    click.echo(f"Nome: {project_info['name']}")
    click.echo(f"Caminho: {project_info['path']}")
    click.echo(
        f"Projeto Python: {'Sim' if project_info['is_python_project'] else 'Não'}"
    )
    click.echo(f"Tem templates: {'Sim' if project_info['has_templates'] else 'Não'}")
    click.echo(f"Arquivos Python: {project_info['python_files']}")
    click.echo(f"Arquivos HTML: {project_info['html_files']}")
    click.echo(f"Total de arquivos: {project_info['total_files']}")


@cli.command()
@click.argument(
    "project_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=".",
)
@click.option(
    "--host", "-h", default="127.0.0.1", help="Host do servidor (padrão: 127.0.0.1)"
)
@click.option(
    "--port", "-p", default=8000, type=int, help="Porta do servidor (padrão: 8000)"
)
@click.option("--reload", is_flag=True, help="Recarregar automaticamente em mudanças")
def dashboard(project_path: str, host: str, port: int, reload: bool):
    """Inicia o dashboard interativo.

    Abre uma interface web com métricas em tempo real,
    gráficos interativos e monitoramento contínuo da
    qualidade do código.

    PROJECT_PATH: Caminho para o diretório do projeto (padrão: diretório atual)
    """
    try:
        from ..web.server import DashboardServer

        click.echo(ColorHelper.success("Iniciando dashboard interativo..."))
        click.echo(f"Projeto: {project_path}")
        click.echo(f"URL: http://{host}:{port}")
        click.echo("\n" + ColorHelper.info("Pressione Ctrl+C para parar o servidor"))

        server = DashboardServer(project_path)
        server.run(host=host, port=port, reload=reload)

    except ImportError as e:
        click.echo(ColorHelper.error("❌ Dependências do dashboard não encontradas!"))
        click.echo(
            ColorHelper.warning(
                "💡 Instale as dependências com: pip install 'codehealthanalyzer[web]'"
            )
        )
        click.echo(f"Erro: {e}")
    except KeyboardInterrupt:
        click.echo("\n" + ColorHelper.info("🛑 Dashboard interrompido pelo usuário"))
    except Exception as e:
        click.echo(ColorHelper.error(f"❌ Erro ao iniciar dashboard: {e}"))


@cli.command()
@click.argument(
    "project_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=".",
    required=False,
)
@click.option(
    "--ruff",
    is_flag=True,
    default=True,
    help="Aplicar auto-fix com ruff (padrão: ligado)",
)
@click.option(
    "--isort",
    "use_isort",
    is_flag=True,
    default=True,
    help="Aplicar isort (padrão: ligado)",
)
@click.option(
    "--black",
    "use_black",
    is_flag=True,
    default=True,
    help="Aplicar black (padrão: ligado)",
)
def format(project_path: str, ruff: bool, use_isort: bool, use_black: bool):
    """Formata e aplica auto-fix no código do projeto."""

    def _run(cmd):
        click.echo(" ".join(cmd))
        return subprocess.run(cmd, cwd=project_path).returncode

    rc = 0
    if use_isort:
        if shutil.which("isort"):
            rc |= _run(["isort", "--profile", "black", project_path])
        else:
            click.echo(ColorHelper.warning("isort não encontrado (pip install isort)"))
    if use_black:
        if shutil.which("black"):
            black_rc = _run(["black", project_path])
            if black_rc != 0:
                # Tenta fallback: enumerar arquivos .py e passar explicitamente para evitar leitura de .gitignore
                click.echo(
                    ColorHelper.warning(
                        "Black falhou, tentando fallback por arquivo (possível problema de encoding no .gitignore)."
                    )
                )
                try:
                    from pathlib import Path as _P

                    skip_subs = [
                        ".git",
                        "__pycache__",
                        ".pytest_cache",
                        "node_modules",
                        ".ruff_cache",
                        "tests",
                        "scripts",
                        "reports",
                        "dist",
                        "build",
                        "site-packages",
                        ".tox",
                        ".nox",
                        ".venv",
                        "venv",
                    ]
                    all_files = []
                    for p in _P(project_path).rglob("*.py"):
                        ps = str(p)
                        if any(s in ps for s in skip_subs):
                            continue
                        all_files.append(ps)
                    if all_files:
                        # Chama black em lotes para evitar limite de linha de comando no Windows
                        batch = 200
                        for i in range(0, len(all_files), batch):
                            rc |= _run(["black", *all_files[i : i + batch]])
                    else:
                        click.echo(
                            ColorHelper.info(
                                "Nenhum arquivo .py encontrado para formatar no fallback."
                            )
                        )
                except Exception as ex:
                    click.echo(ColorHelper.warning(f"Falha no fallback do black: {ex}"))
        else:
            click.echo(ColorHelper.warning("black não encontrado (pip install black)"))
    if ruff:
        if shutil.which("ruff"):
            rc |= _run(
                [
                    "ruff",
                    "check",
                    project_path,
                    "--fix",
                    "--exit-non-zero-on-fix",
                    "--unsafe-fixes",
                ]
            )
        else:
            click.echo(ColorHelper.warning("ruff não encontrado (pip install ruff)"))

    if rc == 0:
        click.echo(
            ColorHelper.success("Formatação e auto-fixes aplicados com sucesso.")
        )
    else:
        click.echo(
            ColorHelper.warning(
                "Alguns comandos retornaram códigos de saída diferentes de zero."
            )
        )


@cli.command()
@click.argument(
    "project_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=".",
    required=False,
)
def lint(project_path: str):
    """Executa checagens de qualidade e segurança (ruff, isort, black, bandit)."""

    def _run(name, cmd):
        click.echo(ColorHelper.info(f"== {name} =="))
        if not shutil.which(cmd[0]):
            click.echo(
                ColorHelper.warning(
                    f"{cmd[0]} não encontrado. Instale para habilitar esta verificação."
                )
            )
            return 0
        return subprocess.run(cmd, cwd=project_path).returncode

    rc = 0
    rc |= _run("Ruff (lint)", ["ruff", "check", project_path])
    rc |= _run(
        "isort (check)", ["isort", "--profile", "black", "--check-only", project_path]
    )
    rc |= _run("Black (check)", ["black", "--check", project_path])
    rc |= _run("Bandit (security)", ["bandit", "-q", "-r", project_path])

    if rc == 0:
        click.echo(ColorHelper.success("Todas as checagens passaram."))
    else:
        click.echo(ColorHelper.error("Falhas detectadas nas checagens."))


def _render_violations_html(report: dict, output_file: Path) -> None:
    rows = []
    items = (report.get("violations", []) or []) + (report.get("warnings", []) or [])
    for it in items:
        rows.append(
            f"<tr><td>{it.get('file','')}</td><td>{it.get('priority','')}</td><td>{len(it.get('violations',[]))}</td><td>{it.get('lines',0)}</td></tr>"
        )
    html = f"""
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="utf-8" />
  <title>Relatório de Violações</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; }}
    th {{ background: #f5f5f5; text-align: left; }}
  </style>
  </head>
  <body>
  <h1>Relatório de Violações</h1>
  <ul>
    <li>Arquivos analisados: {report.get('metadata',{}).get('total_files',0)}</li>
    <li>Arquivos com violações: {report.get('metadata',{}).get('violation_files',0)}</li>
  </ul>
  <table>
    <thead><tr><th>Arquivo</th><th>Prioridade</th><th>Qtd. Violações</th><th>Linhas</th></tr></thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
  </body>
</html>
""".strip()
    output_file.write_text(html, encoding="utf-8")


def _render_violations_md(report: dict, output_file: Path) -> None:
    lines = [
        "# Relatório de Violações",
        "",
        f"- Arquivos analisados: {report.get('metadata',{}).get('total_files',0)}",
        f"- Arquivos com violações: {report.get('metadata',{}).get('violation_files',0)}",
        "",
        "| Arquivo | Prioridade | Qtd. Violações | Linhas |",
        "|---|---|---:|---:|",
    ]
    items = (report.get("violations", []) or []) + (report.get("warnings", []) or [])
    for it in items:
        lines.append(
            f"| {it.get('file','')} | {it.get('priority','')} | {len(it.get('violations',[]))} | {it.get('lines',0)} |"
        )
    output_file.write_text("\n".join(lines), encoding="utf-8")


def _render_templates_html(report: dict, output_file: Path) -> None:
    rows = []
    for t in report.get("templates", []) or []:
        css_chars = t.get("total_css_chars", t.get("css", 0))
        js_chars = t.get("total_js_chars", t.get("js", 0))
        rows.append(
            f"<tr><td>{t.get('file','')}</td><td>{t.get('category','')}</td><td>{t.get('priority','')}</td><td>{css_chars}</td><td>{js_chars}</td></tr>"
        )
    stats = report.get("statistics", {})
    html = f"""
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="utf-8" />
  <title>Relatório de Templates</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; }}
    th {{ background: #f5f5f5; text-align: left; }}
  </style>
  </head>
  <body>
  <h1>Relatório de Templates</h1>
  <ul>
    <li>Total templates: {stats.get('total_templates',0)}</li>
    <li>CSS total (chars): {stats.get('total_css_chars',0)}</li>
    <li>JS total (chars): {stats.get('total_js_chars',0)}</li>
  </ul>
  <table>
    <thead><tr><th>Arquivo</th><th>Categoria</th><th>Prioridade</th><th>CSS (chars)</th><th>JS (chars)</th></tr></thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
  </body>
</html>
""".strip()
    output_file.write_text(html, encoding="utf-8")


def _render_templates_md(report: dict, output_file: Path) -> None:
    stats = report.get("statistics", {})
    lines = [
        "# Relatório de Templates",
        "",
        f"- Total templates: {stats.get('total_templates',0)}",
        f"- CSS total (chars): {stats.get('total_css_chars',0)}",
        f"- JS total (chars): {stats.get('total_js_chars',0)}",
        "",
        "| Arquivo | Categoria | Prioridade | CSS (chars) | JS (chars) |",
        "|---|---|---|---:|---:|",
    ]
    for t in report.get("templates", []) or []:
        css_chars = t.get("total_css_chars", t.get("css", 0))
        js_chars = t.get("total_js_chars", t.get("js", 0))
        lines.append(
            f"| {t.get('file','')} | {t.get('category','')} | {t.get('priority','')} | {css_chars} | {js_chars} |"
        )
    output_file.write_text("\n".join(lines), encoding="utf-8")


def _render_errors_html(report: dict, output_file: Path) -> None:
    rows = []
    for f in report.get("errors", []) or []:
        rows.append(
            f"<tr><td>{f.get('file','')}</td><td>{f.get('category','')}</td><td>{f.get('priority','')}</td><td>{f.get('error_count',0)}</td></tr>"
        )
    stats = report.get("statistics", {})
    html = f"""
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="utf-8" />
  <title>Relatório de Erros (Ruff)</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; }}
    th {{ background: #f5f5f5; text-align: left; }}
  </style>
  </head>
  <body>
  <h1>Relatório de Erros (Ruff)</h1>
  <ul>
    <li>Alta prioridade: {stats.get('high_priority',0)}</li>
    <li>Média prioridade: {stats.get('medium_priority',0)}</li>
    <li>Baixa prioridade: {stats.get('low_priority',0)}</li>
  </ul>
  <table>
    <thead><tr><th>Arquivo</th><th>Categoria</th><th>Prioridade</th><th>Qtd. Erros</th></tr></thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
  </body>
</html>
""".strip()
    output_file.write_text(html, encoding="utf-8")


def _render_errors_md(report: dict, output_file: Path) -> None:
    stats = report.get("statistics", {})
    lines = [
        "# Relatório de Erros (Ruff)",
        "",
        f"- Alta prioridade: {stats.get('high_priority',0)}",
        f"- Média prioridade: {stats.get('medium_priority',0)}",
        f"- Baixa prioridade: {stats.get('low_priority',0)}",
        "",
        "| Arquivo | Categoria | Prioridade | Qtd. Erros |",
        "|---|---|---|---:|",
    ]
    for f in report.get("errors", []) or []:
        lines.append(
            f"| {f.get('file','')} | {f.get('category','')} | {f.get('priority','')} | {f.get('error_count',0)} |"
        )
    output_file.write_text("\n".join(lines), encoding="utf-8")


def main():
    """Ponto de entrada principal da CLI."""
    cli()


if __name__ == "__main__":
    main()
