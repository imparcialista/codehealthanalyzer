"""Interface de linha de comando para CodeHealthAnalyzer.

Este módulo fornece uma CLI amigável para usar a biblioteca CodeHealthAnalyzer.
"""

from __future__ import annotations

import json
import logging
import shutil
import subprocess  # nosec B404
from pathlib import Path
from typing import Any, Optional, cast

import click

from .. import CodeAnalyzer, __version__
from ..analyzers.errors import ErrorsAnalyzer
from ..analyzers.templates import TemplatesAnalyzer
from ..analyzers.violations import ViolationsAnalyzer
from ..config import normalize_config
from ..exceptions import ConfigurationError
from ..reports.formatter import ReportFormatter
from ..reports.generator import ReportGenerator
from ..schemas import ErrorsReport, FullReport, TemplatesReport, ViolationsReport
from ..utils.helpers import ColorHelper
from ..utils.validators import PathValidator

_LOG_FORMAT = "%(levelname)s:%(name)s:%(message)s"


def _configure_logging(verbose: bool = False) -> None:
    """Configura logging para os analisadores."""
    level = logging.INFO if verbose else logging.WARNING
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(level=level, format=_LOG_FORMAT)
    else:
        root.setLevel(level)


def _load_config(
    config_path: Optional[str], no_default_excludes: bool, verbose: bool = False
) -> dict[str, Any]:
    config_data: dict[str, Any] = {}
    if config_path:
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
        if verbose:
            click.echo(ColorHelper.info(f"Configuração carregada de {config_path}"))
    if no_default_excludes:
        config_data["no_default_excludes"] = True
    return normalize_config(config_data)


def _empty_violations_report() -> ViolationsReport:
    return {
        "metadata": {
            "generated_at": "",
            "directory": "",
            "total_files": 0,
            "violation_files": 0,
            "warning_files": 0,
        },
        "violations": [],
        "warnings": [],
        "statistics": {
            "total_files": 0,
            "violation_files": 0,
            "warning_files": 0,
            "high_priority": 0,
            "medium_priority": 0,
            "python_files": 0,
            "html_files": 0,
        },
    }


def _empty_templates_report() -> TemplatesReport:
    return {
        "metadata": {"generated_at": "", "templates_paths": [], "total_templates": 0},
        "templates": [],
        "statistics": {
            "total_templates": 0,
            "total_css_chars": 0,
            "total_js_chars": 0,
            "high_priority": 0,
            "medium_priority": 0,
            "templates_with_css": 0,
            "templates_with_js": 0,
        },
    }


def _empty_errors_report() -> ErrorsReport:
    return {
        "metadata": {"generated_at": "", "total_errors": 0, "total_files": 0},
        "errors": [],
        "statistics": {
            "high_priority": 0,
            "medium_priority": 0,
            "low_priority": 0,
            "syntax_errors": 0,
            "style_errors": 0,
            "critical_errors": 0,
        },
    }


def _wrap_single_report(kind: str, report: Any) -> FullReport:
    generator = ReportGenerator()
    violations = (
        cast(ViolationsReport, report)
        if kind == "violations"
        else _empty_violations_report()
    )
    templates = (
        cast(TemplatesReport, report)
        if kind == "templates"
        else _empty_templates_report()
    )
    errors = cast(ErrorsReport, report) if kind == "errors" else _empty_errors_report()
    return generator.generate_full_report(violations, templates, errors)


def _write_report_files(
    report: FullReport,
    output_path: Path,
    base_name: str,
    format_name: str,
    no_json: bool,
    detail: str = "full",
) -> None:
    formatter = ReportFormatter()
    output_path.mkdir(parents=True, exist_ok=True)

    if not no_json:
        summary_report = _build_summary_report(report)
        if detail == "summary":
            formatter.to_json(summary_report, str(output_path / f"{base_name}.json"))
            formatter.to_json(
                summary_report, str(output_path / f"{base_name}.summary.json")
            )
        elif detail == "standard":
            formatter.to_json(
                _build_standard_report(report), str(output_path / f"{base_name}.json")
            )
            formatter.to_json(
                summary_report, str(output_path / f"{base_name}.summary.json")
            )
        else:
            formatter.to_json(report, str(output_path / f"{base_name}.json"))
            formatter.to_json(report, str(output_path / f"{base_name}.full.json"))
            formatter.to_json(
                summary_report, str(output_path / f"{base_name}.summary.json")
            )
    if format_name in ["html", "all"]:
        ReportGenerator().generate_html_report(
            report, str(output_path / f"{base_name}.html")
        )
    if format_name in ["markdown", "all"]:
        formatter.to_markdown(report, str(output_path / f"{base_name}.md"))
    if format_name in ["csv", "all"]:
        formatter.to_csv(report, str(output_path / f"{base_name}.csv"))


def _write_analyze_json_files(
    report: FullReport,
    output_path: Path,
    detail: str,
) -> None:
    formatter = ReportFormatter()
    summary_report = _build_summary_report(report)

    # Arquivos base amigaveis para consumo humano e integracoes simples.
    formatter.to_json(summary_report, str(output_path / "summary_report.json"))
    formatter.to_json(
        report.get("violations", {}), str(output_path / "violations_report.json")
    )
    formatter.to_json(
        report.get("templates", {}), str(output_path / "templates_report.json")
    )
    formatter.to_json(report.get("errors", {}), str(output_path / "errors_report.json"))

    if detail in ["standard", "full"]:
        formatter.to_json(
            _build_standard_report(report), str(output_path / "analysis_report.json")
        )

    # Relatorio completo agora e opcional e so e gerado explicitamente.
    if detail == "full":
        formatter.to_json(report, str(output_path / "full_report.json"))


def _build_summary_report(report: FullReport, top_n: int = 10) -> dict[str, Any]:
    violations = report.get("violations", {})
    templates = report.get("templates", {})
    errors = report.get("errors", {})
    return {
        "metadata": report.get("metadata", {}),
        "summary": report.get("summary", {}),
        "priorities": report.get("priorities", []),
        "top_violations": (violations.get("violations", []) or [])[:top_n],
        "top_warnings": (violations.get("warnings", []) or [])[:top_n],
        "top_templates": (templates.get("templates", []) or [])[:top_n],
        "top_errors": (errors.get("errors", []) or [])[:top_n],
    }


def _standardize_violation_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in items:
        messages = item.get("violations", []) or []
        out.append(
            {
                "file": item.get("file", ""),
                "type": item.get("type", ""),
                "lines": item.get("lines", 0),
                "priority": item.get("priority", "low"),
                "violation_count": len(messages),
                "sample_violations": messages[:5],
            }
        )
    return out


def _standardize_templates(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in items:
        out.append(
            {
                "file": item.get("file", ""),
                "priority": item.get("priority", "low"),
                "category": item.get("category", ""),
                "total_css_chars": item.get("total_css_chars", item.get("css", 0)),
                "total_js_chars": item.get("total_js_chars", item.get("js", 0)),
                "css_inline_count": len(item.get("css_inline", []) or []),
                "css_style_tags_count": len(item.get("css_style_tags", []) or []),
                "js_inline_count": len(item.get("js_inline", []) or []),
                "js_script_tags_count": len(item.get("js_script_tags", []) or []),
            }
        )
    return out


def _standardize_errors(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in items:
        details = item.get("errors", []) or []
        out.append(
            {
                "file": item.get("file", ""),
                "priority": item.get("priority", "low"),
                "category": item.get("category", ""),
                "error_count": item.get("error_count", len(details)),
                "sample_errors": details[:5],
            }
        )
    return out


def _build_standard_report(report: FullReport) -> dict[str, Any]:
    violations = report.get("violations", {})
    templates = report.get("templates", {})
    errors = report.get("errors", {})

    violation_items = cast(list[dict[str, Any]], violations.get("violations", []) or [])
    warning_items = cast(list[dict[str, Any]], violations.get("warnings", []) or [])
    template_items = cast(list[dict[str, Any]], templates.get("templates", []) or [])
    error_items = cast(list[dict[str, Any]], errors.get("errors", []) or [])

    return {
        "metadata": report.get("metadata", {}),
        "summary": report.get("summary", {}),
        "quality_score": report.get("quality_score", 0),
        "priorities": report.get("priorities", []),
        "violations": {
            "metadata": violations.get("metadata", {}),
            "statistics": violations.get("statistics", {}),
            "violations": _standardize_violation_items(violation_items),
            "warnings": _standardize_violation_items(warning_items),
        },
        "templates": {
            "metadata": templates.get("metadata", {}),
            "statistics": templates.get("statistics", {}),
            "templates": _standardize_templates(template_items),
        },
        "errors": {
            "metadata": errors.get("metadata", {}),
            "statistics": errors.get("statistics", {}),
            "errors": _standardize_errors(error_items),
        },
    }


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
    type=click.Choice(["json", "html", "markdown", "csv", "all"]),
    default="json",
    help="Formato do relatório (além do JSON padrão)",
)
@click.option("--no-json", is_flag=True, help="Não gerar o relatório JSON padrão")
@click.option(
    "--detail",
    type=click.Choice(["summary", "standard", "full"]),
    default="standard",
    show_default=True,
    help="Nível de detalhe (full_report.json é gerado apenas em 'full')",
)
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
    detail: str,
    config: Optional[str],
    no_default_excludes: bool,
    verbose: bool,
):
    """Executa análise completa do projeto.

    Analisa violações de tamanho, templates HTML com CSS/JS inline,
    e erros de linting (Ruff) em um projeto Python.

    PROJECT_PATH: Caminho para o diretório do projeto
    """
    _configure_logging(verbose)

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

    # Executa análise
    try:
        config_data = _load_config(config, no_default_excludes, verbose)
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
        if not no_json:
            _write_analyze_json_files(report, output_path, detail)
        _write_report_files(
            report, output_path, "analysis_report", format, no_json=True, detail=detail
        )

        click.echo("\n" + ColorHelper.success("Análise concluída com sucesso!"))

    except ConfigurationError as e:
        click.echo(ColorHelper.error(f"Configuração inválida: {e}"))
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
    type=click.Choice(["json", "html", "markdown", "csv", "all"]),
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
@click.option("--verbose", "-v", is_flag=True, help="Saída detalhada")
def violations(
    project_path: str,
    output: Optional[str],
    format: str,
    no_json: bool,
    config: Optional[str],
    no_default_excludes: bool,
    verbose: bool,
):
    """Analisa apenas violações de tamanho.

    PROJECT_PATH: Caminho para o diretório do projeto
    """
    _configure_logging(verbose)

    try:
        config_data = _load_config(config, no_default_excludes, verbose)
        analyzer = ViolationsAnalyzer(project_path, config_data)
        report = analyzer.analyze()
        output_path = Path(output or "reports")
        _write_report_files(
            _wrap_single_report("violations", report),
            output_path,
            "violations_report",
            format,
            no_json,
        )
    except ConfigurationError as e:
        click.echo(ColorHelper.error(f"Configuração inválida: {e}"))
    except Exception as e:
        logging.exception("Falha ao gerar relatório de violações.")
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
    type=click.Choice(["json", "html", "markdown", "csv", "all"]),
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
@click.option("--verbose", "-v", is_flag=True, help="Saída detalhada")
def templates(
    project_path: str,
    output: Optional[str],
    format: str,
    no_json: bool,
    config: Optional[str],
    no_default_excludes: bool,
    verbose: bool,
):
    """Analisa apenas templates HTML com CSS/JS inline.

    PROJECT_PATH: Caminho para o diretório do projeto
    """
    _configure_logging(verbose)

    try:
        config_data = _load_config(config, no_default_excludes, verbose)
        analyzer = TemplatesAnalyzer(project_path, config_data)
        report = analyzer.analyze()
        output_path = Path(output or "reports")
        _write_report_files(
            _wrap_single_report("templates", report),
            output_path,
            "templates_report",
            format,
            no_json,
        )
    except ConfigurationError as e:
        click.echo(ColorHelper.error(f"Configuração inválida: {e}"))
    except Exception as e:
        logging.exception("Falha ao gerar relatório de templates.")
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
    type=click.Choice(["json", "html", "markdown", "csv", "all"]),
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
@click.option("--verbose", "-v", is_flag=True, help="Saída detalhada")
def errors(
    project_path: str,
    output: Optional[str],
    format: str,
    no_json: bool,
    config: Optional[str],
    no_default_excludes: bool,
    verbose: bool,
):
    """Analisa apenas erros de linting (Ruff).

    PROJECT_PATH: Caminho para o diretório do projeto
    """
    _configure_logging(verbose)

    try:
        config_data = _load_config(config, no_default_excludes, verbose)
        analyzer = ErrorsAnalyzer(project_path, config_data)
        report = analyzer.analyze()
        output_path = Path(output or "reports")
        _write_report_files(
            _wrap_single_report("errors", report),
            output_path,
            "errors_report",
            format,
            no_json,
        )
    except ConfigurationError as e:
        click.echo(ColorHelper.error(f"Configuração inválida: {e}"))
    except Exception as e:
        logging.exception("Falha ao gerar relatório de erros.")
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
        click.echo(ColorHelper.error("Dependências do dashboard não encontradas!"))
        click.echo(
            ColorHelper.warning(
                "Instale as dependências com: pip install 'codehealthanalyzer[web]'"
            )
        )
        click.echo(f"Erro: {e}")
    except KeyboardInterrupt:
        click.echo("\n" + ColorHelper.info("Dashboard interrompido pelo usuário"))
    except Exception as e:
        click.echo(ColorHelper.error(f"Erro ao iniciar dashboard: {e}"))


@cli.command()
@click.argument(
    "project_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=".",
    required=False,
)
@click.option(
    "--ruff/--no-ruff",
    default=True,
    help="Aplicar auto-fix com ruff (padrão: ligado)",
)
@click.option(
    "--isort/--no-isort",
    "use_isort",
    default=True,
    help="Aplicar isort (padrão: ligado)",
)
@click.option(
    "--black/--no-black",
    "use_black",
    default=True,
    help="Aplicar black (padrão: ligado)",
)
def format(project_path: str, ruff: bool, use_isort: bool, use_black: bool):
    """Formata e aplica auto-fix no código do projeto."""

    def _run(cmd):
        click.echo(" ".join(cmd))
        return subprocess.run(cmd, cwd=project_path).returncode  # nosec B603

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
        return subprocess.run(cmd, cwd=project_path).returncode  # nosec B603

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


def main():
    """Ponto de entrada principal da CLI."""
    cli()


if __name__ == "__main__":
    main()
