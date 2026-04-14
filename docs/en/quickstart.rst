Quick Start
===========

First run
---------

After installation, run a simple analysis in your current project:

.. code-block:: bash

   cd /path/to/your/project
   cha analyze .

Core CLI commands
-----------------

.. code-block:: bash

   cha analyze . --format all --output reports
   cha score .
   cha info .
   cha violations . --format csv
   cha templates . --config cha_config.json
   cha errors . --no-json --format markdown
   cha dashboard .

Python API
----------

.. code-block:: python

   from codehealthanalyzer import CodeAnalyzer

   analyzer = CodeAnalyzer(
       ".",
       config={"target_dir": ".", "templates_dir": ["templates"]},
   )
   report = analyzer.generate_full_report(output_dir="reports")
   print(report["summary"]["quality_score"])

Report detail levels
--------------------

.. code-block:: bash

   cha analyze . --detail summary
   cha analyze . --detail standard
   cha analyze . --detail full

Generated files by level:

* ``summary``: ``summary_report.json`` + domain files
* ``standard``: ``summary`` + ``analysis_report.json``
* ``full``: ``standard`` + ``full_report.json``

Common error
------------

``Error: Invalid value for '--config' ... Path 'cha_config.json' does not exist``

* Create ``cha_config.json`` in the current directory, or pass an absolute path.
