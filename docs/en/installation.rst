Installation
============

Requirements
------------

* Python 3.8+
* Ruff available in the environment for error analysis
* Operating system: Windows, macOS, or Linux

Install via pip
---------------

.. code-block:: bash

   pip install codehealthanalyzer

With dashboard support:

.. code-block:: bash

   pip install "codehealthanalyzer[web]"

Development install
-------------------

.. code-block:: bash

   git clone https://github.com/imparcialista/codehealthanalyzer.git
   cd codehealthanalyzer
   pip install -e ".[dev,web]"

Validate installation
---------------------

.. code-block:: bash

   cha --version
   python -c "import codehealthanalyzer; print(codehealthanalyzer.__version__)"

If you plan to run error analysis, also validate Ruff:

.. code-block:: bash

   ruff --version
