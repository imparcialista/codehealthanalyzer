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

CodeHealthAnalyzer is a Python library for code health analysis focused on
three areas:

* size violations in modules, classes, functions, and templates
* inline CSS and JavaScript in HTML templates
* linting issues collected through Ruff

Key Features
------------

* **Stable Python API** with ``CodeAnalyzer`` and specialized analyzers
* **Complete CLI** with ``analyze``, ``violations``, ``templates``, ``errors``,
  ``score``, ``info``, ``dashboard``, ``format``, and ``lint``
* **Reports in JSON, HTML, Markdown, and CSV**
* **Optional FastAPI dashboard** for aggregated metrics
* **Typed report contract** and centralized versioning
* **JSON configuration** for limits, directories, and exclusions

Installation
------------

.. code-block:: bash

   pip install codehealthanalyzer

With dashboard support:

.. code-block:: bash

   pip install "codehealthanalyzer[web]"

Quick Start
-----------

**CLI (Command Line Interface)**

.. code-block:: bash

   cha analyze .
   cha analyze . --format all --output reports
   cha violations . --format csv
   cha templates . --config cha_config.json
   cha errors . --no-json --format markdown
   cha dashboard .

**Python API**

.. code-block:: python

   from codehealthanalyzer import CodeAnalyzer

   analyzer = CodeAnalyzer(
       ".",
       config={"target_dir": ".", "templates_dir": ["templates"]},
   )
   report = analyzer.generate_full_report(output_dir="reports")
   print(report["summary"]["quality_score"])

Configuration
-------------

Example ``cha_config.json``:

.. code-block:: json

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

Supported fields:

* ``limits``: overrides size thresholds
* ``target_dir``: directory analyzed by Ruff
* ``templates_dir``: string or list of template directories
* ``exclude_dirs``: string or list of extra directories to ignore
* ``ruff_fix``: runs ``ruff check --fix`` before collection
* ``no_default_excludes``: disables the default exclusions

Report detail modes for ``analyze``:

* ``--detail summary``: generates ``summary_report.json`` + domain files
* ``--detail standard``: adds ``analysis_report.json``
* ``--detail full``: adds ``full_report.json``

Report Contract
---------------

The consolidated report always contains:

.. code-block:: python

   {
       "metadata": {...},
       "summary": {...},
       "violations": {...},
       "templates": {...},
       "errors": {...},
       "priorities": [...],
       "quality_score": 0,
   }

Typed schemas live in ``codehealthanalyzer/schemas.py``.

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart

Indices and Tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
