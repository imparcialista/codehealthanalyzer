"""Setup script para CodeHealthAnalyzer.

Este script permite instalar a biblioteca CodeHealthAnalyzer usando pip.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Lê o README para a descrição longa
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8') if (this_directory / "README.md").exists() else ""

# Lê os requirements
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="codehealthanalyzer",
    version="1.0.0",
    author="Luarco Team",
    author_email="contato@luarco.com.br",
    description="Biblioteca Python para análise de qualidade e saúde de código",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/imparcialista/codehealthanalyzer",
    packages=find_packages(include=['codehealthanalyzer', 'codehealthanalyzer.*']),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements or [
        "ruff>=0.1.0",
        "click>=8.0.0",
        "rich>=12.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "codehealthanalyzer=codehealthanalyzer.cli.main:main",
            "cha=codehealthanalyzer.cli.main:main",  # Alias curto
        ],
    },
    include_package_data=True,
    package_data={
        "codehealthanalyzer": [
            "*.md",
            "*.txt",
            "*.json",
        ],
    },
    keywords=[
        "code-quality",
        "static-analysis",
        "code-health",
        "linting",
        "python",
        "html",
        "css",
        "javascript",
        "ruff",
        "analysis",
        "metrics",
        "reporting",
    ],
    project_urls={
        "Bug Reports": "https://github.com/imparcialista/codehealthanalyzer/issues",
        "Source": "https://github.com/imparcialista/codehealthanalyzer",
        "Documentation": "https://codehealthanalyzer.readthedocs.io/",
    },
)