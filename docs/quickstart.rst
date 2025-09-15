Guia de Início Rápido
=====================

Este guia irá ajudá-lo a começar a usar o CodeHealthAnalyzer rapidamente.

Primeiro Uso
------------

Após a instalação, você pode começar a usar o CodeHealthAnalyzer imediatamente:

.. code-block:: bash

   # Navegar para o diretório do seu projeto
   cd /caminho/para/seu/projeto

   # Executar análise básica
   codehealthanalyzer analyze .

Comandos Básicos da CLI
-----------------------

**Análise Completa**

.. code-block:: bash

   codehealthanalyzer analyze . --format json --output reports/

**Score de Qualidade**

.. code-block:: bash

   codehealthanalyzer score .

**Informações do Projeto**

.. code-block:: bash

   codehealthanalyzer info .

**Análises Específicas**

.. code-block:: bash

   # Apenas violações de tamanho
   codehealthanalyzer violations .

   # Apenas templates HTML
   codehealthanalyzer templates .

   # Apenas erros de linting
   codehealthanalyzer errors .

Uso da API Python
-----------------

**Exemplo Básico**

.. code-block:: python

   from codehealthanalyzer import CodeAnalyzer

   # Criar analisador
   analyzer = CodeAnalyzer('.')

   # Obter score de qualidade
   score = analyzer.get_quality_score()
   print(f"Score: {score}/100")

**Análise Completa**

.. code-block:: python

   from codehealthanalyzer import CodeAnalyzer

   analyzer = CodeAnalyzer('/caminho/para/projeto')
   
   # Gerar relatório completo
   report = analyzer.generate_full_report(output_dir='reports')
   
   # Acessar dados específicos
   violations = analyzer.analyze_violations()
   templates = analyzer.analyze_templates()
   errors = analyzer.analyze_errors()

**Com Configuração Personalizada**

.. code-block:: python

   config = {
       'limits': {
           'python_function': {'yellow': 25, 'red': 40},
           'python_class': {'yellow': 250, 'red': 400}
       }
   }
   
   analyzer = CodeAnalyzer('.', config)
   report = analyzer.generate_full_report()

Interpretando os Resultados
---------------------------

**Score de Qualidade**

* **80-100**: 🟢 Excelente - Código de alta qualidade
* **60-79**: 🟡 Bom - Algumas melhorias recomendadas
* **0-59**: 🔴 Precisa melhorar - Ação necessária

**Prioridades**

* **Alta**: Problemas que afetam funcionalidade ou manutenibilidade
* **Média**: Melhorias recomendadas para qualidade
* **Baixa**: Otimizações opcionais

**Tipos de Violações**

* **Função longa**: Mais de 50 linhas
* **Classe grande**: Mais de 500 linhas
* **Módulo extenso**: Mais de 1000 linhas
* **Template longo**: Mais de 200 linhas

Próximos Passos
---------------

1. **Configuração**: Personalize limites e regras no arquivo de configuração
2. **Integração**: Adicione ao seu pipeline de CI/CD
3. **Relatórios**: Explore diferentes formatos de saída (HTML, Markdown, CSV)
4. **Automação**: Use a API Python para integração personalizada

Veja a seção :doc:`configuration` para mais detalhes sobre personalização.