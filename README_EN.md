# CodeHealthAnalyzer

Python library for code health analysis focused on three areas:

- size violations in modules, classes, functions, and templates
- inline CSS/JS in HTML templates
- linting errors collected through Ruff

## What the library provides today

- Python API with `CodeAnalyzer`, `ViolationsAnalyzer`, `TemplatesAnalyzer`, and `ErrorsAnalyzer`
- CLI with the commands `analyze`, `violations`, `templates`, `errors`, `score`, `info`, `dashboard`, `format`, and `lint`
- reports in `json`, `html`, `markdown`, and `csv`
- optional FastAPI dashboard with aggregated metrics
- typed report contracts and centralized versioning

## Installation

```bash
pip install codehealthanalyzer
```

With dashboard support:

```bash
pip install "codehealthanalyzer[web]"
```

For development:

```bash
pip install -e ".[dev,web]"
```

## Quick start

### CLI

Use `cha` as the recommended command (short alias for `codehealthanalyzer`).

```bash
cha analyze .
cha analyze . --format all --output reports
cha violations . --format csv
cha templates . --config cha_config.json
cha errors . --no-json --format markdown
cha dashboard .
```

### Python API

```python
from codehealthanalyzer import CodeAnalyzer

analyzer = CodeAnalyzer(".", config={"target_dir": ".", "templates_dir": ["templates"]})
report = analyzer.generate_full_report(output_dir="reports")
print(report["summary"]["quality_score"])
```

## Configuration

Example `cha_config.json`:

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

### Precedence order

- CLI flags (highest priority)
- `--config` file
- Library defaults

### Supported fields

| Field | Type | Default | What it controls |
|---|---|---|---|
| `limits` | object | internal thresholds | Size thresholds by structure/file type |
| `target_dir` | string | `"."` | Target directory for code analysis (including Ruff) |
| `templates_dir` | string or list | auto-detection | HTML/Jinja template directories to scan |
| `exclude_dirs` | string or list | `[]` | Extra excludes beyond the default exclude list |
| `ruff_fix` | boolean | `false` | Runs `ruff check --fix` before error collection |
| `no_default_excludes` | boolean | `false` | Disables default excludes (`tests`, `venv`, `dist`, etc.) |

### Quick config recipes

Flask/Django project with templates in multiple directories:

```json
{
  "templates_dir": ["templates", "app/templates", "src/templates"],
  "exclude_dirs": ["migrations", "node_modules"]
}
```

Monorepo (analyze a single service):

```json
{
  "target_dir": "services/billing",
  "templates_dir": ["services/billing/templates"]
}
```

### Report detail control

For `analyze`, full JSON is optional:

- `--detail summary`: summary + domain files (`violations/templates/errors`)
- `--detail standard` (default): same + `analysis_report.json`
- `--detail full`: same + `full_report.json`

Generated files by mode:

- `summary`: `summary_report.json`, `violations_report.json`, `templates_report.json`, `errors_report.json`
- `standard`: everything from `summary` + `analysis_report.json`
- `full`: everything from `standard` + `full_report.json`

Examples:

```bash
cha analyze . --config cha_config.json --detail summary
cha analyze . --detail full --format all --output reports
```

## Troubleshooting

`Error: Invalid value for '--config' ... Path 'cha_config.json' does not exist`
- Create the file in the current directory or pass an absolute path with `--config`.

`WARNING: Ignoring invalid distribution ~odehealthanalyzer`
- This usually means stale package metadata in `site-packages`; remove `~odehealthanalyzer*` directories.

## Report contract

The consolidated report always contains:

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

Typed schemas live in `codehealthanalyzer/schemas.py`.

## Development

```bash
pytest -q
ruff check codehealthanalyzer tests
black --check codehealthanalyzer tests
isort --check-only codehealthanalyzer tests
```

## Current limitations

- error analysis depends on the `ruff` executable being available in the environment
- the dashboard exposes aggregated metrics, not full persisted history
- template analysis is based on lightweight HTML and regex heuristics
