#!/usr/bin/env python3
"""
Exemplo de uso da biblioteca CodeHealthAnalyzer.

Este script demonstra como usar a biblioteca para analisar a qualidade de código.
"""

from codehealthanalyzer import CodeAnalyzer
from codehealthanalyzer.reports.formatter import ReportFormatter
from codehealthanalyzer.utils.helpers import ColorHelper


def exemplo_basico():
    """Exemplo básico de uso da biblioteca."""
    print(ColorHelper.info("🔍 Exemplo básico - Análise de qualidade de código"))

    # Inicializa o analisador para o diretório atual
    analyzer = CodeAnalyzer(".")

    # Obtém o score de qualidade
    score = analyzer.get_quality_score()

    if score >= 80:
        print(ColorHelper.success(f"Score de Qualidade: {score}/100 - Excelente!"))
    elif score >= 60:
        print(ColorHelper.warning(f"Score de Qualidade: {score}/100 - Bom"))
    else:
        print(ColorHelper.error(f"Score de Qualidade: {score}/100 - Precisa melhorar"))


def exemplo_analise_completa():
    """Exemplo de análise completa com relatórios."""
    print(ColorHelper.info("📊 Exemplo avançado - Análise completa com relatórios"))

    # Configuração personalizada
    config = {
        "limits": {
            "python_function": {"yellow": 25, "red": 40},
            "python_class": {"yellow": 250, "red": 400},
            "python_module": {"yellow": 400, "red": 800},
        }
    }

    # Inicializa com configuração personalizada
    analyzer = CodeAnalyzer(".", config)

    # Gera relatório completo
    print("Gerando relatório completo...")
    report = analyzer.generate_full_report(output_dir="reports")

    # Exibe resumo
    summary = report.get("summary", {})
    print("\n📈 Resumo:")
    print(f"  📁 Arquivos analisados: {summary.get('total_files', 0)}")
    print(f"  ⚠️  Arquivos com violações: {summary.get('violation_files', 0)}")
    print(f"  🎨 Templates: {summary.get('total_templates', 0)}")
    print(f"  🔍 Erros: {summary.get('total_errors', 0)}")

    # Mostra prioridades
    priorities = report.get("priorities", [])
    if priorities:
        print("\n🎯 Top 3 Prioridades:")
        for i, priority in enumerate(priorities[:3], 1):
            icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                priority.get("priority", "low"), "⚪"
            )
            print(
                f"  {i}. {icon} {priority.get('title', 'N/A')} ({priority.get('count', 0)})"
            )

    print(ColorHelper.success("\n✅ Relatórios salvos em 'reports/'!"))


def exemplo_analises_individuais():
    """Exemplo de análises individuais."""
    print(ColorHelper.info("🔧 Exemplo de análises individuais"))

    analyzer = CodeAnalyzer(".")

    # Análise de violações
    print("\n🚨 Analisando violações...")
    violations = analyzer.analyze_violations()
    v_stats = violations.get("statistics", {})
    print(f"  - Arquivos com violações: {v_stats.get('violation_files', 0)}")
    print(f"  - Alta prioridade: {v_stats.get('high_priority', 0)}")

    # Análise de templates
    print("\n🎨 Analisando templates...")
    templates = analyzer.analyze_templates()
    t_stats = templates.get("statistics", {})
    print(f"  - Templates analisados: {t_stats.get('total_templates', 0)}")
    print(f"  - CSS inline: {t_stats.get('total_css_chars', 0)} caracteres")
    print(f"  - JS inline: {t_stats.get('total_js_chars', 0)} caracteres")

    # Análise de erros
    print("\n⚠️ Analisando erros...")
    errors = analyzer.analyze_errors()
    e_stats = errors.get("statistics", {})
    print(f"  - Erros encontrados: {errors.get('metadata', {}).get('total_errors', 0)}")
    print(f"  - Alta prioridade: {e_stats.get('high_priority', 0)}")


def exemplo_formatacao_relatorios():
    """Exemplo de formatação de relatórios."""
    print(ColorHelper.info("📄 Exemplo de formatação de relatórios"))

    analyzer = CodeAnalyzer(".")
    report = analyzer.generate_full_report()

    # Formatador de relatórios
    formatter = ReportFormatter()

    # Gera tabela resumo
    print("\n📊 Tabela Resumo:")
    table = formatter.generate_summary_table(report)
    print(table)

    # Salva em diferentes formatos
    print("\nSalvando relatórios em diferentes formatos...")
    formatter.to_json(report, "example_report.json")
    formatter.to_markdown(report, "example_report.md")
    formatter.to_csv(report, "example_report.csv")

    print(ColorHelper.success("✅ Relatórios salvos em múltiplos formatos!"))


def main():
    """Executa todos os exemplos."""
    print("🚀 CodeHealthAnalyzer - Exemplos de Uso\n")
    print("=" * 50)

    try:
        exemplo_basico()
        print("\n" + "=" * 50)

        exemplo_analise_completa()
        print("\n" + "=" * 50)

        exemplo_analises_individuais()
        print("\n" + "=" * 50)

        exemplo_formatacao_relatorios()
        print("\n" + "=" * 50)

        print(ColorHelper.success("\n🎉 Todos os exemplos executados com sucesso!"))
        print("\n💡 Dicas:")
        print("  - Use 'codehealthanalyzer --help' para ver todos os comandos")
        print("  - Personalize limites com arquivo config.json")
        print("  - Integre em seus scripts Python com a API")

    except Exception as e:
        print(ColorHelper.error(f"❌ Erro durante execução: {e}"))
        print("💡 Certifique-se de que a biblioteca está instalada: pip install -e .")


if __name__ == "__main__":
    main()
