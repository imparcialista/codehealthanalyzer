# 🔍 CodeHealthAnalyzer

> A comprehensive Python library for code quality and health analysis

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[🇧🇷 Português](README.md) | 🇺🇸 English

## 🚀 Overview

CodeHealthAnalyzer is a modern and comprehensive Python library for code quality analysis. It combines multiple analysis tools into a unified interface, providing detailed insights into your code's health.

### ✨ Key Features

- **🚨 Violations Analysis**: Detects functions, classes, and modules that exceed size limits
- **🎨 Template Analysis**: Identifies inline CSS/JS in HTML templates that can be extracted
- **⚠️ Ruff Integration**: Analyzes linting errors and categorizes them by priority
- **📊 Quality Score**: Calculates a 0-100 score based on overall code health
- **🎯 Smart Prioritization**: Suggests actions based on problem criticality
- **📈 Multiple Reports**: Generates reports in JSON, HTML, Markdown, and CSV
- **🖥️ Friendly CLI**: Complete and intuitive command-line interface
- **🔧 Highly Configurable**: Customize limits, rules, and categories

## 📦 Installation

### Installation via pip (recommended)

```bash
# Basic installation
pip install codehealthanalyzer

# Installation with interactive web dashboard
pip install codehealthanalyzer[web]

# Complete installation (web + development)
pip install codehealthanalyzer[web,dev]
```

### Development Installation

```bash
git clone https://github.com/imparcialista/codehealthanalyzer.git
cd codehealthanalyzer
pip install -e .[web,dev]
```

### Dependencies

- Python 3.8+
- ruff >= 0.1.0
- click >= 8.0.0
- rich >= 12.0.0 (optional, for colored output)

## 🎯 Quick Start

### 🌐 Interactive Dashboard

```bash
# Start web dashboard with real-time metrics
codehealthanalyzer dashboard .

# Dashboard on specific host and port
codehealthanalyzer dashboard . --host 0.0.0.0 --port 8080

# Dashboard with auto-reload for development
codehealthanalyzer dashboard . --reload
```

**Dashboard Features:**
- 📊 Real-time metrics with automatic updates
- 📈 Interactive quality trend charts
- 🎯 Violations visualization by type
- 📋 Problem files table
- 🔄 WebSockets for instant updates
- 📱 Responsive and modern interface

### CLI (Command Line Interface)

```bash
# Complete analysis of current project
codehealthanalyzer analyze .

# Analysis with HTML output
codehealthanalyzer analyze . --format html --output reports/

# Quality score only
codehealthanalyzer score .

# Project information
codehealthanalyzer info .

# Specific violations analysis
codehealthanalyzer violations . --output violations.json
```

### Python API

```python
from codehealthanalyzer import CodeAnalyzer

# Initialize analyzer
analyzer = CodeAnalyzer('/path/to/project')

# Generate complete report
report = analyzer.generate_full_report(output_dir='reports/')

# Get quality score
score = analyzer.get_quality_score()
print(f"Quality Score: {score}/100")

# Individual analyses
violations = analyzer.analyze_violations()
templates = analyzer.analyze_templates()
errors = analyzer.analyze_errors()
```

## 📊 Example Output

```
📊 ANALYSIS SUMMARY
==================================================
✅ Quality Score: 85/100 - Excellent!
📁 Files analyzed: 124
⚠️  Files with violations: 8
🎨 Templates: 15
🔍 Ruff Errors: 0
🔥 High priority issues: 2

🎯 ACTION PRIORITIES:
1. 🔴 High Priority Violations (2)
2. 🟡 Templates with Too Much Inline CSS/JS (3)
```

## 🔧 Configuration

### JSON Configuration File

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

### Usage with Configuration

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

## 📈 Analysis Types

### 🚨 Violations Analysis

Detects:
- Functions too long (> 50 lines)
- Classes too large (> 500 lines)
- Modules too extensive (> 1000 lines)
- HTML templates too long (> 200 lines)

### 🎨 Template Analysis

Identifies:
- Inline CSS in `style` attributes
- Inline JavaScript in events (`onclick`, etc.)
- `<style>` tags with too much content
- `<script>` tags with too much code

### ⚠️ Error Analysis

Integrates with Ruff to detect:
- Syntax errors
- Style issues
- Unused imports
- Undefined variables
- Excessive complexity

## 📊 Quality Score

The score is calculated based on:
- **High priority violations**: -10 points each
- **Linting errors**: -2 points each
- **Problematic templates**: -5 points each
- **Base**: 100 points

### Interpretation
- **80-100**: 🟢 Excellent
- **60-79**: 🟡 Good
- **0-59**: 🔴 Needs improvement

## 🌐 Internationalization

### Language Support

CodeHealthAnalyzer supports multiple languages:
- **Portuguese (Brazil)**: Default language
- **English**: Full translation available

### Setting Language

```python
from codehealthanalyzer.i18n import set_language

# Set to English
set_language('en')

# Set to Portuguese (Brazil)
set_language('pt_BR')

# Auto-detect system language
from codehealthanalyzer.i18n import auto_configure_language
auto_configure_language()
```

### Environment Variable

```bash
# Set language via environment
export CODEHEALTHANALYZER_LANG=en
codehealthanalyzer analyze .
```

## 🛠️ Advanced API

### Individual Analyzers

```python
from codehealthanalyzer.analyzers import (
    ViolationsAnalyzer,
    TemplatesAnalyzer,
    ErrorsAnalyzer
)

# Specific violations analysis
violations_analyzer = ViolationsAnalyzer('/path/to/project')
violations_report = violations_analyzer.analyze()

# Specific templates analysis
templates_analyzer = TemplatesAnalyzer('/path/to/project')
templates_report = templates_analyzer.analyze()

# Specific errors analysis
errors_analyzer = ErrorsAnalyzer('/path/to/project')
errors_report = errors_analyzer.analyze()
```

### Report Generation

```python
from codehealthanalyzer.reports import ReportGenerator, ReportFormatter

generator = ReportGenerator()
formatter = ReportFormatter()

# Generate consolidated report
full_report = generator.generate_full_report(
    violations=violations_report,
    templates=templates_report,
    errors=errors_report,
    output_dir='reports/'
)

# Convert to different formats
html_content = generator.generate_html_report(full_report, 'report.html')
markdown_content = formatter.to_markdown(full_report, 'report.md')
formatter.to_csv(full_report, 'report.csv')
```

## 🧪 Testing

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=codehealthanalyzer

# Run linting
ruff check codehealthanalyzer/
black --check codehealthanalyzer/
```

## 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Contribution Guidelines

- Follow existing code style
- Add tests for new features
- Update documentation when necessary
- Use semantic commits

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ruff](https://github.com/astral-sh/ruff) - Ultra-fast Python linter
- [Click](https://click.palletsprojects.com/) - CLI framework
- [Rich](https://github.com/Textualize/rich) - Rich terminal formatting

## 📞 Support

- 📧 Email: contato@luarco.com.br
- 🐛 Issues: [GitHub Issues](https://github.com/imparcialista/codehealthanalyzer/issues)
- 📖 Documentation: [ReadTheDocs](https://codehealthanalyzer.readthedocs.io/)

---

**Made with ❤️ by the Imparcialista team**