Instalação
==========

Requisitos
----------

* Python 3.8 ou superior
* Ruff disponível no ambiente para a análise de erros
* Sistema operacional: Windows, macOS ou Linux

Instalação via pip
------------------

A forma mais simples de instalar o CodeHealthAnalyzer é através do pip:

.. code-block:: bash

   pip install codehealthanalyzer

Para usar o dashboard web:

.. code-block:: bash

   pip install "codehealthanalyzer[web]"

Instalação para Desenvolvimento
-------------------------------

Se você deseja contribuir para o projeto ou usar a versão mais recente:

.. code-block:: bash

   git clone https://github.com/imparcialista/codehealthanalyzer.git
   cd codehealthanalyzer
   pip install -e ".[dev,web]"

Instalação com Dependências Extras
-----------------------------------

Para instalar apenas dependências de desenvolvimento:

.. code-block:: bash

   pip install codehealthanalyzer[dev]

Para instalar com dependências de documentação:

.. code-block:: bash

   pip install codehealthanalyzer[docs]

Verificação da Instalação
-------------------------

Para verificar se a instalação foi bem-sucedida:

.. code-block:: bash

   codehealthanalyzer --version
   # ou
   python -c "import codehealthanalyzer; print(codehealthanalyzer.__version__)"

Se for usar análise de erros, valide o Ruff:

.. code-block:: bash

   ruff --version

Dependências
------------

O CodeHealthAnalyzer depende principalmente das seguintes bibliotecas:

* **ruff** (>=0.1.0): Linter Python ultrarrápido
* **click** (>=8.0.0): Framework para criação de interfaces de linha de comando
* **rich** (>=12.0.0): Biblioteca para formatação rica no terminal

Para o dashboard, a extra ``web`` instala FastAPI, Uvicorn e Jinja2.
