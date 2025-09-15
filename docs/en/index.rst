CodeHealthAnalyzer Documentation
=================================

.. image:: https://img.shields.io/badge/python-3.8+-blue.svg
   :target: https://python.org
   :alt: Python Version

.. image:: https://img.shields.io/badge/license-MIT-green.svg
   :target: https://github.com/imparcialista/codehealthanalyzer/blob/main/LICENSE
   :alt: License

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code Style

CodeHealthAnalyzer is a modern and comprehensive Python library for code quality analysis. 
It combines multiple analysis tools into a unified interface, providing detailed insights 
about your code's health.

Key Features
------------

* **🚨 Violations Analysis**: Detects functions, classes, and modules that exceed size limits
* **🎨 Template Analysis**: Identifies inline CSS/JS in HTML templates that can be extracted
* **⚠️ Ruff Integration**: Analyzes linting errors and categorizes them by priority
* **📊 Quality Score**: Calculates a 0-100 score based on overall code health
* **🎯 Smart Prioritization**: Suggests actions based on problem criticality
* **📈 Multiple Reports**: Generates reports in JSON, HTML, Markdown, and CSV
* **🖥️ Friendly CLI**: Complete and intuitive command-line interface
* **🔧 Highly Configurable**: Customize limits, rules, and categories

Installation
------------

.. code-block:: bash

   pip install codehealthanalyzer

Quick Start
-----------

**CLI (Command Line Interface)**

.. code-block:: bash

   # Complete analysis of current project
   codehealthanalyzer analyze .

   # Analysis with HTML output
   codehealthanalyzer analyze . --format html --output reports/

   # Quality score only
   codehealthanalyzer score .

**Python API**

.. code-block:: python

   from codehealthanalyzer import CodeAnalyzer

   # Initialize analyzer
   analyzer = CodeAnalyzer('/path/to/project')

   # Generate complete report
   report = analyzer.generate_full_report(output_dir='reports/')

   # Get quality score
   score = analyzer.get_quality_score()
   print(f"Quality Score: {score}/100")

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   api
   cli
   configuration
   examples
   contributing
   changelog

API Reference
-------------

.. toctree::
   :maxdepth: 2
   :caption: API Reference:

   api/codehealthanalyzer
   api/analyzers
   api/reports
   api/utils

Indices and Tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`