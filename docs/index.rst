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

CodeHealthAnalyzer é uma biblioteca Python moderna e abrangente para análise de qualidade de código. 
Ela combina múltiplas ferramentas de análise em uma interface unificada, fornecendo insights detalhados 
sobre a saúde do seu código.

Principais Funcionalidades
--------------------------

* **🚨 Análise de Violações**: Detecta funções, classes e módulos que excedem limites de tamanho
* **🎨 Análise de Templates**: Identifica CSS/JS inline em templates HTML que podem ser extraídos
* **⚠️ Integração com Ruff**: Analisa erros de linting e os categoriza por prioridade
* **📊 Score de Qualidade**: Calcula um score de 0-100 baseado na saúde geral do código
* **🎯 Priorização Inteligente**: Sugere ações baseadas na criticidade dos problemas
* **📈 Relatórios Múltiplos**: Gera relatórios em JSON, HTML, Markdown e CSV
* **🖥️ CLI Amigável**: Interface de linha de comando completa e intuitiva
* **🔧 Altamente Configurável**: Personalize limites, regras e categorias

Instalação
----------

.. code-block:: bash

   pip install codehealthanalyzer

Uso Rápido
----------

**CLI (Interface de Linha de Comando)**

.. code-block:: bash

   # Análise completa do projeto atual
   codehealthanalyzer analyze .

   # Análise com saída em HTML
   codehealthanalyzer analyze . --format html --output reports/

   # Apenas score de qualidade
   codehealthanalyzer score .

**API Python**

.. code-block:: python

   from codehealthanalyzer import CodeAnalyzer

   # Inicializa o analisador
   analyzer = CodeAnalyzer('/path/to/project')

   # Gera relatório completo
   report = analyzer.generate_full_report(output_dir='reports/')

   # Obtém score de qualidade
   score = analyzer.get_quality_score()
   print(f"Score de Qualidade: {score}/100")

Índice
------

.. toctree::
   :maxdepth: 2
   :caption: Conteúdo:

   installation
   quickstart
   api
   cli
   configuration
   examples
   contributing
   changelog

Referência da API
-----------------

.. toctree::
   :maxdepth: 2
   :caption: API Reference:

   api/codehealthanalyzer
   api/analyzers
   api/reports
   api/utils

Índices e Tabelas
-----------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`