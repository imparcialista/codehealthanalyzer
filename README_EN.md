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

```bash
codehealthanalyzer analyze .
codehealthanalyzer analyze . --format all --output reports
codehealthanalyzer violations . --format csv
codehealthanalyzer templates . --config config.json
codehealthanalyzer errors . --no-json --format markdown
codehealthanalyzer dashboard .
```

### Python API

```python
from codehealthanalyzer import CodeAnalyzer

analyzer = CodeAnalyzer(".", config={"target_dir": ".", "templates_dir": ["templates"]})
report = analyzer.generate_full_report(output_dir="reports")
print(report["summary"]["quality_score"])
```

## Configuration

Example `config.json`:

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

Supported fields:

- `limits`: overrides size thresholds
- `target_dir`: directory analyzed by Ruff
- `templates_dir`: string or list of template directories
- `exclude_dirs`: string or list of extra directories to ignore
- `ruff_fix`: runs `ruff check --fix` before collection
- `no_default_excludes`: disables the default exclude list

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
