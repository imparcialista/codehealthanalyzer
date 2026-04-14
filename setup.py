"""Setup script para CodeHealthAnalyzer.

Este script permite instalar a biblioteca CodeHealthAnalyzer usando pip.
"""

from pathlib import Path

from setuptools import find_namespace_packages, setup

about = {}
exec(
    (Path(__file__).parent / "codehealthanalyzer" / "version.py").read_text(
        encoding="utf-8"
    ),
    about,
)

# Lê o README para a descrição longa (português + inglês)
this_directory = Path(__file__).parent
readme_pt = (
    (this_directory / "README.md").read_text(encoding="utf-8")
    if (this_directory / "README.md").exists()
    else ""
)
readme_en = (
    (this_directory / "README_EN.md").read_text(encoding="utf-8")
    if (this_directory / "README_EN.md").exists()
    else ""
)

# Combina ambas as versões
if readme_pt and readme_en:
    long_description = readme_pt + "\n\n---\n\n" + readme_en
elif readme_pt:
    long_description = readme_pt
elif readme_en:
    long_description = readme_en
else:
    long_description = ""

# Lê os requirements
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, "r", encoding="utf-8") as f:
        requirements = [
            line.strip() for line in f if line.strip() and not line.startswith("#")
        ]

setup(
    name="codehealthanalyzer",
    version=about["__version__"],
    author="Luarco Team",
    author_email="contato@luarco.com.br",
    description="Biblioteca Python para análise de qualidade e saúde de código",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/imparcialista/codehealthanalyzer",
    packages=find_namespace_packages(
        include=["codehealthanalyzer", "codehealthanalyzer.*"],
        exclude=[
            "codehealthanalyzer.web.static",
            "codehealthanalyzer.web.static.*",
            "codehealthanalyzer.web.templates",
        ],
    ),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
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
    install_requires=[
        "ruff>=0.1.0,<2.0",
        "click>=8.0.0,<10.0",
        "rich>=12.0.0,<14.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0,<9.0",
            "pytest-cov>=4.0.0,<7.0",
            "pytest-mock>=3.0.0,<4.0",
            "black>=22.0.0,<25.0",
            "isort>=5.0.0,<6.0",
            "bandit>=1.7.4,<2.0",
            "nox>=2024.4.15",
            "mypy>=1.0.0,<2.0",
            "httpx>=0.24.0,<1.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "web": [
            "fastapi>=0.104.0,<1.0",
            "uvicorn[standard]>=0.24.0,<1.0",
            "jinja2>=3.1.0,<4.0",
            "python-multipart>=0.0.6,<1.0",
            "websockets>=12.0,<14.0",
        ],
    },
    license_files=[],
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
            # Web assets and templates for dashboard
            "web/templates/*.html",
            "web/static/css/*.css",
            "web/static/js/*.js",
        ],
    },
    data_files=[
        ("share/codehealthanalyzer/locale/en/LC_MESSAGES", ["locale/en/LC_MESSAGES/codehealthanalyzer.po"]),
        ("share/codehealthanalyzer/locale/pt_BR/LC_MESSAGES", ["locale/pt_BR/LC_MESSAGES/codehealthanalyzer.po"]),
    ],
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
