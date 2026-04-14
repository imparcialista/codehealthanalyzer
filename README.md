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

Use `cha` como comando recomendado (alias curto de `codehealthanalyzer`).

```bash
cha analyze .
cha analyze . --format all --output reports
cha violations . --format csv
cha templates . --config cha_config.json
cha errors . --no-json --format markdown
cha dashboard .
```

### API Python

```python
from codehealthanalyzer import CodeAnalyzer

analyzer = CodeAnalyzer(".", config={"target_dir": ".", "templates_dir": ["templates"]})
report = analyzer.generate_full_report(output_dir="reports")
print(report["summary"]["quality_score"])
```

## Configuração

Exemplo de `cha_config.json`:

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

### Ordem de precedência

- Flags da CLI (maior prioridade)
- Arquivo `--config`
- Defaults da biblioteca

### Campos suportados

| Campo | Tipo | Padrão | O que controla |
|---|---|---|---|
| `limits` | objeto | limites internos | Limites de tamanho por tipo de arquivo/estrutura |
| `target_dir` | string | `"."` | Diretório alvo para análise de código (incluindo Ruff) |
| `templates_dir` | string ou lista | autodetecção | Diretórios HTML/Jinja a varrer |
| `exclude_dirs` | string ou lista | `[]` | Exclusões adicionais além das exclusões padrão |
| `ruff_fix` | boolean | `false` | Executa `ruff check --fix` antes da coleta de erros |
| `no_default_excludes` | boolean | `false` | Remove exclusões padrão (`tests`, `venv`, `dist`, etc.) |

### Configurações rápidas por cenário

Projeto Flask/Django com templates em múltiplas pastas:

```json
{
  "templates_dir": ["templates", "app/templates", "src/templates"],
  "exclude_dirs": ["migrations", "node_modules"]
}
```

Monorepo (analisar apenas um subprojeto):

```json
{
  "target_dir": "services/billing",
  "templates_dir": ["services/billing/templates"]
}
```

### Controle de detalhamento dos relatórios

No comando `analyze`, o JSON completo agora é opcional:

- `--detail summary`: gera resumo + arquivos por domínio (`violations/templates/errors`)
- `--detail standard` (padrão): idem + `analysis_report.json`
- `--detail full`: idem + `full_report.json`

Exemplos:

```bash
cha analyze . --config cha_config.json --detail summary
cha analyze . --detail full --format all --output reports
```

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
