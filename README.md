# 🔍 CodeHealthAnalyzer

> Uma biblioteca Python completa para análise de qualidade e saúde de código

🇧🇷 Português | [🇺🇸 English](README_EN.md)

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🚀 Visão Geral

CodeHealthAnalyzer é uma biblioteca Python moderna e abrangente para análise de qualidade de código. Ela combina múltiplas ferramentas de análise em uma interface unificada, fornecendo insights detalhados sobre a saúde do seu código.

### ✨ Principais Funcionalidades

- **🚨 Análise de Violações**: Detecta funções, classes e módulos que excedem limites de tamanho
- **🎨 Análise de Templates**: Identifica CSS/JS inline em templates HTML que podem ser extraídos
- **⚠️ Integração com Ruff**: Analisa erros de linting e os categoriza por prioridade
- **📊 Score de Qualidade**: Calcula um score de 0-100 baseado na saúde geral do código
- **🎯 Priorização Inteligente**: Sugere ações baseadas na criticidade dos problemas
- **📈 Relatórios Múltiplos**: Gera relatórios em JSON, HTML, Markdown e CSV
- **🖥️ CLI Amigável**: Interface de linha de comando completa e intuitiva
- **🔧 Altamente Configurável**: Personalize limites, regras e categorias

## 📦 Instalação

### Instalação via pip (recomendado)

```bash
# Instalação básica
pip install codehealthanalyzer

# Instalação com dashboard web interativo
pip install codehealthanalyzer[web]

# Instalação completa (web + desenvolvimento)
pip install codehealthanalyzer[web,dev]
```

### Instalação para desenvolvimento

```bash
git clone https://github.com/imparcialista/codehealthanalyzer.git
cd codehealthanalyzer
pip install -e .[web,dev]
```

### Dependências

- Python 3.8+
- ruff >= 0.1.0
- click >= 8.0.0
- rich >= 12.0.0 (opcional, para saída colorida)

## 🎯 Uso Rápido

### 🌐 Dashboard Interativo

```bash
# Iniciar dashboard web com métricas em tempo real
codehealthanalyzer dashboard .

# Dashboard em host e porta específicos
codehealthanalyzer dashboard . --host 0.0.0.0 --port 8080

# Dashboard com reload automático para desenvolvimento
codehealthanalyzer dashboard . --reload
```

**Funcionalidades do Dashboard:**
- 📊 Métricas em tempo real com atualizações automáticas
- 📈 Gráficos interativos de tendência de qualidade
- 🎯 Visualização de violações por tipo
- 📋 Tabela de arquivos com problemas
- 🔄 WebSockets para atualizações instantâneas
- 📱 Interface responsiva e moderna

### CLI (Interface de Linha de Comando)

```bash
# Análise completa do projeto atual
codehealthanalyzer analyze .

# Análise com saída em HTML
codehealthanalyzer analyze . --format html --output reports/

# Apenas score de qualidade
codehealthanalyzer score .

# Informações do projeto
codehealthanalyzer info .

# Análise específica de violações
codehealthanalyzer violations . --output violations.json
```

### API Python

```python
from codehealthanalyzer import CodeAnalyzer

# Inicializa o analisador
analyzer = CodeAnalyzer('/path/to/project')

# Gera relatório completo
report = analyzer.generate_full_report(output_dir='reports/')

# Obtém score de qualidade
score = analyzer.get_quality_score()
print(f"Score de Qualidade: {score}/100")

# Análises individuais
violations = analyzer.analyze_violations()
templates = analyzer.analyze_templates()
errors = analyzer.analyze_errors()
```

## 📊 Exemplo de Saída

```
📊 RESUMO DA ANÁLISE
==================================================
✅ Score de Qualidade: 85/100 - Excelente!
📁 Arquivos analisados: 124
⚠️  Arquivos com violações: 8
🎨 Templates: 15
🔍 Erros Ruff: 0
🔥 Issues de alta prioridade: 2

🎯 PRIORIDADES DE AÇÃO:
1. 🔴 Violações de Alta Prioridade (2)
2. 🟡 Templates com Muito CSS/JS Inline (3)
```

## 🔧 Configuração

### Arquivo de Configuração JSON

```json
{
  "limits": {
    "python_function": {"yellow": 30, "red": 50},
    "python_class": {"yellow": 300, "red": 500},
    "python_module": {"yellow": 500, "red": 1000},
    "html_template": {"yellow": 150, "red": 200},
    "test_file": {"yellow": 400, "red": 600}
  },
  "target_dir": "src/",
  "file_rules": {
    "critical_files": ["main.py", "core.py"],
    "skip_patterns": [".git", "__pycache__", "node_modules"]
  }
}
```

### Uso com Configuração

```bash
codehealthanalyzer analyze . --config config.json
```

```python
import json
from codehealthanalyzer import CodeAnalyzer

with open('config.json') as f:
    config = json.load(f)

analyzer = CodeAnalyzer('/path/to/project', config)
```

## 📈 Tipos de Análise

### 🚨 Análise de Violações

Detecta:
- Funções muito longas (> 50 linhas)
- Classes muito grandes (> 500 linhas)
- Módulos muito extensos (> 1000 linhas)
- Templates HTML muito longos (> 200 linhas)

### 🎨 Análise de Templates

Identifica:
- CSS inline em atributos `style`
- JavaScript inline em eventos (`onclick`, etc.)
- Tags `<style>` com muito conteúdo
- Tags `<script>` com muito código

### ⚠️ Análise de Erros

Integra com Ruff para detectar:
- Erros de sintaxe
- Problemas de estilo
- Imports não utilizados
- Variáveis não definidas
- Complexidade excessiva

## 📊 Score de Qualidade

O score é calculado baseado em:
- **Violações de alta prioridade**: -10 pontos cada
- **Erros de linting**: -2 pontos cada
- **Templates problemáticos**: -5 pontos cada
- **Base**: 100 pontos

### Interpretação
- **80-100**: 🟢 Excelente
- **60-79**: 🟡 Bom
- **0-59**: 🔴 Precisa melhorar

## 🎯 Categorização Inteligente

### Arquivos
- **Arquivo Crítico**: Arquivos essenciais do sistema
- **Views Admin**: Interfaces administrativas
- **Blueprint Crítico**: Rotas críticas da aplicação
- **Template Base**: Templates fundamentais

### Prioridades
- **Alta**: Problemas que afetam funcionalidade
- **Média**: Problemas de manutenibilidade
- **Baixa**: Melhorias recomendadas

## 📋 Formatos de Relatório

### JSON
```json
{
  "metadata": {
    "generated_at": "2024-01-15T10:30:00",
    "generator": "CodeHealthAnalyzer v1.0.0"
  },
  "summary": {
    "quality_score": 85,
    "total_files": 124,
    "violation_files": 8
  },
  "priorities": [...],
  "violations": [...],
  "templates": [...],
  "errors": [...]
}
```

### HTML
Relatório interativo com gráficos e métricas visuais.

### Markdown
Relatório em formato Markdown para documentação.

### CSV
Dados tabulares para análise em planilhas.

## 🛠️ API Avançada

### Analisadores Individuais

```python
from codehealthanalyzer.analyzers import (
    ViolationsAnalyzer,
    TemplatesAnalyzer,
    ErrorsAnalyzer
)

# Análise específica de violações
violations_analyzer = ViolationsAnalyzer('/path/to/project')
violations_report = violations_analyzer.analyze()

# Análise específica de templates
templates_analyzer = TemplatesAnalyzer('/path/to/project')
templates_report = templates_analyzer.analyze()

# Análise específica de erros
errors_analyzer = ErrorsAnalyzer('/path/to/project')
errors_report = errors_analyzer.analyze()
```

### Geração de Relatórios

```python
from codehealthanalyzer.reports import ReportGenerator, ReportFormatter

generator = ReportGenerator()
formatter = ReportFormatter()

# Gera relatório consolidado
full_report = generator.generate_full_report(
    violations=violations_report,
    templates=templates_report,
    errors=errors_report,
    output_dir='reports/'
)

# Converte para diferentes formatos
html_content = generator.generate_html_report(full_report, 'report.html')
markdown_content = formatter.to_markdown(full_report, 'report.md')
formatter.to_csv(full_report, 'report.csv')
```

### Utilitários

```python
from codehealthanalyzer.utils import (
    Categorizer,
    PathValidator,
    FileHelper,
    ColorHelper
)

# Categorização
categorizer = Categorizer()
category = categorizer.categorize_file(Path('src/main.py'))
priority = categorizer.determine_priority('file', {'lines': 150, 'type': 'python'})

# Validação
validator = PathValidator()
is_valid = validator.is_python_project('/path/to/project')
project_info = validator.get_project_info('/path/to/project')

# Helpers
file_helper = FileHelper()
data = file_helper.read_json('config.json')
file_helper.write_json(data, 'output.json')

# Cores para terminal
print(ColorHelper.success("Sucesso!"))
print(ColorHelper.error("Erro!"))
print(ColorHelper.warning("Aviso!"))
```

## 🧪 Testes

```bash
# Instala dependências de desenvolvimento
pip install -e ".[dev]"

# Executa testes
pytest

# Executa testes com cobertura
pytest --cov=codehealthanalyzer

# Executa linting
ruff check codehealthanalyzer/
black --check codehealthanalyzer/
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Diretrizes de Contribuição

- Siga o estilo de código existente
- Adicione testes para novas funcionalidades
- Atualize a documentação quando necessário
- Use commits semânticos

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- [Ruff](https://github.com/astral-sh/ruff) - Linter Python ultrarrápido
- [Click](https://click.palletsprojects.com/) - Framework para CLI
- [Rich](https://github.com/Textualize/rich) - Formatação rica para terminal

## 📞 Suporte

- 📧 Email: contato@luarco.com.br
- 🐛 Issues: [GitHub Issues](https://github.com/imparcialista/codehealthanalyzer/issues)
- 📖 Documentação: [ReadTheDocs](https://codehealthanalyzer.readthedocs.io/)

---

**Feito com ❤️ pela equipe Imparcialista**