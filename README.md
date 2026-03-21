# CodeHealthAnalyzer

Biblioteca Python para análise de saúde de código com foco em três frentes:

- violações de tamanho em módulos, classes, funções e templates
- CSS/JS inline em templates HTML
- erros de linting coletados via Ruff

## O que a biblioteca entrega hoje

- API Python com `CodeAnalyzer`, `ViolationsAnalyzer`, `TemplatesAnalyzer` e `ErrorsAnalyzer`
- CLI com os comandos `analyze`, `violations`, `templates`, `errors`, `score`, `info`, `dashboard`, `format` e `lint`
- relatórios em `json`, `html`, `markdown` e `csv`
- dashboard FastAPI opcional com métricas agregadas
- contrato de relatório tipado e versão centralizada

## Instalação

```bash
pip install codehealthanalyzer
```

Com dashboard:

```bash
pip install "codehealthanalyzer[web]"
```

Para desenvolvimento:

```bash
pip install -e ".[dev,web]"
```

## Uso rápido

### CLI

```bash
codehealthanalyzer analyze .
codehealthanalyzer analyze . --format all --output reports
codehealthanalyzer violations . --format csv
codehealthanalyzer templates . --config config.json
codehealthanalyzer errors . --no-json --format markdown
codehealthanalyzer dashboard .
```

### API Python

```python
from codehealthanalyzer import CodeAnalyzer

analyzer = CodeAnalyzer(".", config={"target_dir": ".", "templates_dir": ["templates"]})
report = analyzer.generate_full_report(output_dir="reports")
print(report["summary"]["quality_score"])
```

## Configuração

Exemplo de `config.json`:

```json
{
  "limits": {
    "python_function": { "yellow": 30, "red": 50 },
    "python_class": { "yellow": 300, "red": 500 },
    "python_module": { "yellow": 500, "red": 1000 },
    "html_template": { "yellow": 150, "red": 200 },
    "test_file": { "yellow": 400, "red": 600 }
  },
  "target_dir": ".",
  "templates_dir": ["templates", "app/templates"],
  "exclude_dirs": ["legacy", "vendor"],
  "ruff_fix": false,
  "no_default_excludes": false
}
```

Campos suportados:

- `limits`: sobrescreve limites de tamanho
- `target_dir`: diretório analisado pelo Ruff
- `templates_dir`: string ou lista de diretórios de templates
- `exclude_dirs`: string ou lista de diretórios extras a ignorar
- `ruff_fix`: roda `ruff check --fix` antes da coleta
- `no_default_excludes`: desabilita as exclusões padrão

## Contrato de relatório

O relatório consolidado sempre contém:

```python
{
    "metadata": {...},
    "summary": {...},
    "violations": {...},
    "templates": {...},
    "errors": {...},
    "priorities": [...],
    "quality_score": 0,
}
```

Os schemas tipados ficam em `codehealthanalyzer/schemas.py`.

## Desenvolvimento

```bash
pytest -q
ruff check codehealthanalyzer tests
black --check codehealthanalyzer tests
isort --check-only codehealthanalyzer tests
```

## Limitações atuais

- a análise de erros depende do executável `ruff` estar disponível no ambiente
- o dashboard mostra métricas agregadas, não histórico persistente completo
- a análise de templates é baseada em heurísticas simples de HTML e regex
