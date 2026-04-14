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

CodeHealthAnalyzer é uma biblioteca Python para análise de saúde de código
com foco em três frentes:

* violações de tamanho em módulos, classes, funções e templates
* CSS e JavaScript inline em templates HTML
* erros de linting coletados via Ruff

Principais Funcionalidades
--------------------------

* **API Python estável** com ``CodeAnalyzer`` e analyzers especializados
* **CLI completa** com ``analyze``, ``violations``, ``templates``, ``errors``,
  ``score``, ``info``, ``dashboard``, ``format`` e ``lint``
* **Relatórios em JSON, HTML, Markdown e CSV**
* **Dashboard FastAPI opcional** para métricas agregadas
* **Contrato de relatório tipado** e versão centralizada
* **Configuração por JSON** para limites, diretórios e exclusões

Instalação
----------

.. code-block:: bash

   pip install codehealthanalyzer

Com dashboard:

.. code-block:: bash

   pip install "codehealthanalyzer[web]"

Uso Rápido
----------

**CLI (Interface de Linha de Comando)**

.. code-block:: bash

   # Análise completa do projeto atual
   cha analyze .

   cha analyze . --format all --output reports
   cha violations . --format csv
   cha templates . --config cha_config.json
   cha errors . --no-json --format markdown
   cha dashboard .

**API Python**

.. code-block:: python

   from codehealthanalyzer import CodeAnalyzer

   analyzer = CodeAnalyzer(
       ".",
       config={"target_dir": ".", "templates_dir": ["templates"]},
   )
   report = analyzer.generate_full_report(output_dir="reports")
   print(report["summary"]["quality_score"])

Configuração
------------

Exemplo de ``cha_config.json``:

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

Campos suportados:

* ``limits``: sobrescreve limites de tamanho
* ``target_dir``: diretório analisado pelo Ruff
* ``templates_dir``: string ou lista de diretórios de templates
* ``exclude_dirs``: string ou lista de diretórios extras a ignorar
* ``ruff_fix``: roda ``ruff check --fix`` antes da coleta
* ``no_default_excludes``: desabilita as exclusões padrão

Detalhamento de relatório no comando ``analyze``:

* ``--detail summary``: gera ``summary_report.json`` + arquivos por domínio
* ``--detail standard``: adiciona ``analysis_report.json``
* ``--detail full``: adiciona ``full_report.json``

Contrato de Relatório
---------------------

O relatório consolidado sempre contém:

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

Os schemas tipados ficam em ``codehealthanalyzer/schemas.py``.

Índice
------

.. toctree::
   :maxdepth: 2
   :caption: Conteúdo:

   installation
   quickstart

.. toctree::
   :hidden:

   en/index

Índices e Tabelas
-----------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
