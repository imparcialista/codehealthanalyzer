Guia de Início Rápido
=====================

Este guia cobre o fluxo mínimo para instalar, executar a CLI e consumir a
API Python da versão atual da biblioteca.

Primeiro Uso
------------

Após a instalação, rode uma análise simples no diretório atual:

.. code-block:: bash

   cd /caminho/para/seu/projeto
   cha analyze .

Comandos Básicos da CLI
-----------------------

**Análise completa**

.. code-block:: bash

   cha analyze . --format all --output reports

**Score de qualidade**

.. code-block:: bash

   cha score .

**Informações do projeto**

.. code-block:: bash

   cha info .

**Análises específicas**

.. code-block:: bash

   # Apenas violações de tamanho
   cha violations . --format csv

   # Apenas templates HTML
   cha templates . --config cha_config.json

   # Apenas erros de linting
   cha errors . --no-json --format markdown

**Dashboard**

.. code-block:: bash

   cha dashboard .

Uso da API Python
-----------------

**Exemplo básico**

.. code-block:: python

   from codehealthanalyzer import CodeAnalyzer

   analyzer = CodeAnalyzer('.')
   score = analyzer.get_quality_score()
   print(f"Score: {score}/100")

**Análise completa**

.. code-block:: python

   from codehealthanalyzer import CodeAnalyzer

   analyzer = CodeAnalyzer(
       "/caminho/para/projeto",
       config={"target_dir": ".", "templates_dir": ["templates"]},
   )
   report = analyzer.generate_full_report(output_dir="reports")
   violations = analyzer.analyze_violations()
   templates = analyzer.analyze_templates()
   errors = analyzer.analyze_errors()

**Com configuração personalizada**

.. code-block:: python

   config = {
       "limits": {
           "python_function": {"yellow": 30, "red": 50},
           "python_class": {"yellow": 300, "red": 500},
       },
       "templates_dir": ["templates", "app/templates"],
       "exclude_dirs": ["legacy", "vendor"],
   }

   analyzer = CodeAnalyzer('.', config)
   report = analyzer.generate_full_report()

Interpretando os Resultados
---------------------------

**Score de qualidade**

* **80-100**: excelente
* **60-79**: bom, com melhorias recomendadas
* **0-59**: precisa de ação

**Prioridades**

* **Alta**: problemas críticos para manutenção
* **Média**: correções importantes, mas não urgentes
* **Baixa**: otimizações e refinamentos

**Saída consolidada**

O relatório completo inclui:

* ``summary`` com score e contagens agregadas
* ``violations`` com arquivos problemáticos e warnings
* ``templates`` com CSS/JS inline encontrados
* ``errors`` com issues coletadas do Ruff
* ``priorities`` com ações ordenadas por criticidade

Próximos Passos
---------------

1. Personalize limites e exclusões no arquivo JSON de configuração.
2. Integre os comandos da CLI ao CI do projeto.
3. Use os formatos HTML, Markdown e CSV conforme o público do relatório.
4. Acople a API Python em scripts internos ou pipelines.

Erros comuns
------------

``Error: Invalid value for '--config' ... Path 'cha_config.json' does not exist``

* Crie o arquivo no diretório atual ou use caminho absoluto em ``--config``.
