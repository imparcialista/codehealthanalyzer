"""Fixtures compartilhadas para todos os testes."""

import json

import pytest


@pytest.fixture
def minimal_project(tmp_path):
    """Projeto Python mínimo válido: um pacote com um arquivo simples."""
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("x = 1\n", encoding="utf-8")
    return tmp_path


@pytest.fixture
def empty_violations_report():
    return {
        "metadata": {
            "generated_at": "2024-01-01T00:00:00",
            "directory": ".",
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


@pytest.fixture
def empty_templates_report():
    return {
        "metadata": {
            "generated_at": "2024-01-01T00:00:00",
            "templates_paths": [],
            "total_templates": 0,
        },
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


@pytest.fixture
def empty_errors_report():
    return {
        "metadata": {
            "generated_at": "2024-01-01T00:00:00",
            "total_errors": 0,
            "total_files": 0,
        },
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


@pytest.fixture
def full_report():
    """FullReport completo para testes de formatter."""
    return {
        "metadata": {
            "generated_at": "2024-01-01T00:00:00",
            "version": "1.2.0",
            "analyzer": "CodeHealthAnalyzer",
        },
        "summary": {
            "quality_score": 80,
            "total_files": 3,
            "violation_files": 1,
            "warning_files": 1,
            "total_templates": 1,
            "total_errors": 2,
            "high_priority_issues": 1,
            "generated_at": "2024-01-01T00:00:00",
        },
        "violations": {
            "metadata": {
                "generated_at": "2024-01-01T00:00:00",
                "directory": ".",
                "total_files": 3,
                "violation_files": 1,
                "warning_files": 1,
            },
            "violations": [
                {
                    "file": "big_module.py",
                    "type": "Python",
                    "lines": 60,
                    "priority": "high",
                    "violations": ["function foo: 60 linhas (limite: 50)"],
                }
            ],
            "warnings": [
                {
                    "file": "medium_module.py",
                    "type": "Python",
                    "lines": 35,
                    "priority": "medium",
                    "violations": ["function bar: 35 linhas (limite: 30)"],
                }
            ],
            "statistics": {
                "total_files": 3,
                "violation_files": 1,
                "warning_files": 1,
                "high_priority": 1,
                "medium_priority": 1,
                "python_files": 3,
                "html_files": 0,
            },
        },
        "templates": {
            "metadata": {
                "generated_at": "2024-01-01T00:00:00",
                "templates_paths": ["templates"],
                "total_templates": 1,
            },
            "templates": [
                {
                    "file": "index.html",
                    "priority": "low",
                    "category": "Template",
                    "total_css_chars": 100,
                    "total_js_chars": 200,
                    "css": 100,
                    "js": 200,
                    "css_inline": [],
                    "css_style_tags": [],
                    "js_inline": [],
                    "js_script_tags": [],
                    "recommendations": [],
                }
            ],
            "statistics": {
                "total_templates": 1,
                "total_css_chars": 100,
                "total_js_chars": 200,
                "high_priority": 0,
                "medium_priority": 0,
                "templates_with_css": 1,
                "templates_with_js": 1,
            },
        },
        "errors": {
            "metadata": {
                "generated_at": "2024-01-01T00:00:00",
                "total_errors": 2,
                "total_files": 1,
            },
            "errors": [
                {
                    "file": "/proj/foo.py",
                    "priority": "medium",
                    "category": "Erros de Importação",
                    "error_count": 2,
                    "errors": [],
                }
            ],
            "statistics": {
                "high_priority": 0,
                "medium_priority": 1,
                "low_priority": 0,
                "syntax_errors": 0,
                "style_errors": 0,
                "critical_errors": 0,
            },
        },
        "priorities": [
            {
                "title": "Violações de código de alta prioridade",
                "priority": "high",
                "count": 1,
            }
        ],
        "quality_score": 80,
    }


@pytest.fixture
def ruff_json_output():
    """Saída JSON simulada do ruff com erros F401 e E302."""
    return json.dumps(
        [
            {
                "filename": "/proj/foo.py",
                "location": {"row": 1, "column": 0},
                "code": "F401",
                "message": "'os' imported but unused",
                "rule": "unused-import",
            },
            {
                "filename": "/proj/foo.py",
                "location": {"row": 5, "column": 0},
                "code": "E302",
                "message": "expected 2 blank lines, got 1",
                "rule": "expected-two-blank-lines",
            },
            {
                "filename": "/proj/bar.py",
                "location": {"row": 3, "column": 0},
                "code": "F821",
                "message": "undefined name 'boom'",
                "rule": "undefined-name",
            },
        ]
    )
