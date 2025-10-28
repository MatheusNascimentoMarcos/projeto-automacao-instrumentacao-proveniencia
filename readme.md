# Automação de Instrumentação de Proveniência com IA

Este projeto utiliza um modelo de linguagem de larga escala (Gemini) para automatizar a instrumentação de scripts científicos em Python, inserindo o código necessário para captura de proveniência com base na biblioteca **DfAnalyzer**.

O *wrapper* de automação (`instrument_workflow.py`) lê um script Python simples, envia-o para a IA junto com um "gabarito" (`prompt_template.py`), e gera um novo script (`script_instrumentado.py`) que é totalmente instrumentado com as chamadas de proveniência prospectiva e retrospectiva.

## Estrutura dos Arquivos

* `instrument_workflow.py`: O script "wrapper" principal que orquestra a automação.
* `prompt_template.py`: O "gabarito" (prompt mestre) que ensina a IA como instrumentar o código.
* `meu_script.py`: Um script de exemplo (entrada) a ser instrumentado.
* `check_models.py`: Um script utilitário para listar modelos de IA disponíveis.
* `TutorialSomaDfAnalyzer-1.pdf`: A documentação de referência para a biblioteca `DfAnalyzer`.

---

## 1. Configuração do Ambiente

Para executar este projeto, é necessária uma configuração de ambiente muito específica, pois a biblioteca `DfAnalyzer` não está disponível no `pip` e requer Python 3.11.

### Passo 1: Pré-requisitos
* **Python 3.11**: O Python 3.13 (ou superior) apresentou problemas de incompatibilidade. Certifique-se de ter o [Python 3.11](https://www.python.org/downloads/release/python-3119/) instalado.

### Passo 2: Criar e Ativar o Ambiente Virtual
Estes comandos criam um ambiente virtual (`.venv`) usando especificamente o Python 3.11.

```powershell
# 1. Criar o .venv com Python 3.11
py -3.11 -m venv .venv

# 2. Ativar o .venv
.\.venv\Scripts\Activate.ps1
(O seu terminal deve agora mostrar (.venv) no início do prompt)


----------- Ignorar Esta parte das instruções por enquanto ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""Passo 3: Instalar o DfAnalyzer (Instalação Manual)
A biblioteca DfAnalyzer de Vítor Silva não está no pip (o pip install dfanalyzer instala um pacote incorreto de outro autor).

Download: Baixe o código-fonte da branch main diretamente do GitLab:

Link de Download: https://gitlab.com/ssvitor/dataflow_analyzer/-/archive/main/dataflow_analyzer-main.zip

Copiar: Descompacte o ZIP. Navegue até a pasta dataflow_analyzer-main e depois entre na pasta DfAnalyzer-Client.

Copie a pasta dfanalyzer (minúscula) que está lá dentro.

Colar: Cole a pasta dfanalyzer (que você acabou de copiar) dentro da pasta site-packages do seu ambiente virtual.

Caminho de Destino: .\.venv\Lib\site-packages\

Passo 4: Corrigir o Pacote DfAnalyzer
O pacote copiado manualmente precisa de um pequeno ajuste para que os imports funcionem.

Abra o arquivo (que estará em branco): .\.venv\Lib\site-packages\dfanalyzer\__init__.py

Adicione esta única linha a ele e salve:

Python

from .dfanalyzer import *""""
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Passo 5: Instalar Dependências (Pip)
Com o DfAnalyzer no lugar, instale as bibliotecas restantes (incluindo as dependências do DfAnalyzer e do wrapper).

PowerShell

# (Com o .venv ainda ativo)
pip install google-generativeai numpy pandas
2. Configuração da API do Gemini
O wrapper requer uma chave de API do Google Gemini.

Obtenha sua chave no Google AI Studio.

Configure a chave no seu terminal PowerShell. Este comando deve ser executado em cada nova janela do terminal que você usar.

PowerShell

$env:GEMINI_API_KEY = 'SUA_CHAVE_API_COMECA_COM_AIza...'
3. Rodando o Wrapper de Instrumentação
Com o ambiente e a chave configurados, você pode executar o wrapper.

O comando usa o instrument_workflow.py para ler o meu_script.py e gerar o script_instrumentado.py.

PowerShell

# (Com o .venv ainda ativo)
python instrument_workflow.py meu_script.py script_instrumentado.py
Você verá a seguinte saída no console:

Lendo o script de entrada: meu_script.py
Iniciando a instrumentação com a IA do Gemini...
Isso pode levar alguns segundos...
[SUCESSO] Código instrumentado salvo em: script_instrumentado.py
4. Validando o Script Instrumentado
Após a geração, você pode validar o script instrumentado executando-o.

Importante: Use o caminho explícito do python.exe do .venv para garantir que ele encontre as bibliotecas instaladas manualmente.

PowerShell

# (Com o .venv ainda ativo)
.\.venv\Scripts\python.exe script_instrumentado.py
A saída deve mostrar os prints originais do seu script, misturados com os prints da biblioteca de proveniência, provando que a instrumentação foi bem-sucedida.

Proveniência Prospectiva salva.
Iniciando workflow: Calculo de Média
...
Média calculada: 15.72
...
Proveniência Retrospectiva salva.
Workflow concluído.

---
