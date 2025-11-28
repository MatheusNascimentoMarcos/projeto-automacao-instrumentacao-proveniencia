# Projeto de Automação de Instrumentação de Proveniência com IA

Este projeto demonstra um *wrapper* de IA (Gemini) que instrumenta automaticamente scripts Python com captura de proveniência, usando o padrão industrial **W3C-PROV**.

O sistema é executado inteiramente dentro de contêineres Docker para garantir um ambiente de execução limpo, portátil e que resolva problemas de dependência (como os encontrados com o `DfAnalyzer`).

O fluxo de trabalho consiste em duas etapas principais:
1.  **Geração:** O `instrument_workflow.py` usa a IA para ler um script (`meu_script.py`) e um gabarito (`prompt_template.py`) para gerar um novo script (`script_instrumentado_prov.py`) que contém o código de proveniência.
2.  **Execução e Depuração:** O `script_instrumentado_prov.py` gerado é executado, e ele, por sua vez, gera um arquivo `provenance.json` que contém o grafo de proveniência da execução para análise.

---

## 1. Pré-requisitos

* **Docker Desktop:** É necessário para construir e executar o ambiente.
* **Chave de API do Google Gemini:** O *wrapper* de IA precisa de uma chave de API para funcionar.

---

## 2. Fase de Setup (Executar Apenas Uma Vez)

O objetivo desta fase é construir a imagem Docker (`ia-prov-wrapper`) que contém o ambiente Python 3.11 e todas as bibliotecas necessárias (`prov`, `lxml`, `rdflib`, `google-generativeai`, etc.).

1.  Abra um terminal PowerShell.
2.  Navegue até a pasta que contém o `Dockerfile` (o simplificado que criamos para o `w3c-prov`):
3.  Execute o comando `docker build`: docker build -t ia-prov-wrapper .
    *(Este processo pode demorar alguns minutos da primeira vez)*

---

## 3. Fase de Execução (Geração e Depuração)

### Este é o fluxo de trabalho principal. Você deve executá-lo a partir da sua pasta de projeto.

```powershell

# Passo 1: Abra o Terminal e Navegue

Abra um terminal PowerShell e navegue até a pasta que contém seus scripts Python (`instrument_workflow.py`, `prompt_template.py` v4, etc.).

cd "Caminho da sua pasta com os docs de instrumentação"

#Passo 2: Configure a Chave de API
#Configure sua chave de API do Gemini. Ela só é válida para esta janela do terminal.

$env:GEMINI_API_KEY = 'SUA_CHAVE_API_COMECA_COM_AIza...'

#Passo 3: Geração do Script (Execução 1)
#Execute este comando. Ele irá iniciar o contêiner, espelhar sua pasta local, e executar o instrument_workflow.py para gerar o script instrumentado.

docker run -it --rm -e GEMINI_API_KEY=$env:GEMINI_API_KEY -v "${PWD}:/app" ia-prov-wrapper python3 instrument_workflow.py meu_script.py script_instrumentado_prov.py

''' 
Explicação do "Espelhamento" (-v "${PWD}:/app"):

 "${PWD}": Da pasta local (Ex.: Docs Matheus).

 :/app: A pasta de destino dentro do contêiner.

Isso permite que o contêiner leia o meu_script.py e salve o script_instrumentado_prov.py de volta no diretório local.

Saída Esperada:

Lendo o script de entrada: meu_script.py
Iniciando a instrumentação com a IA do Gemini...
[SUCESSO] Código instrumentado salvo em: script_instrumentado_prov.py
'''

#Passo 4: Depuração do Script (Execução 2)
##Agora que o script_instrumentado_prov.py existe na sua pasta, execute este segundo comando para executá-lo dentro do contêiner.
docker run -it --rm -v "${PWD}:/app" ia-prov-wrapper python3 script_instrumentado_prov.py

#Saída Esperada (A Depuração): Você verá a saída do script sendo executado, provando que a instrumentação foi bem-sucedida, assim como a execução do exemplo de calculo da média abaixo:

'''Iniciando workflow: Calculo de Média
Dados carregados (simuladamente) de data/raw_data.csv
Média calculada: 15.719999999999999
Salvando resultado em results/media_final.txt
Workflow concluído.
Grafo de Proveniência (W3C-PROV) salvo em provenance.json no diretório com os arquivos do workflow de instrumentação.
'''

```powershell

```

# 🧪 Validação Metamórfica de Instrumentação de Proveniência - FASE 2

Este repositório contém um framework de testes automatizados projetado para validar a robustez e a consistência do **Agente de Instrumentação W3C-PROV** (baseado em LLM/Gemini).

Como utilizamos Inteligência Artificial Generativa para escrever código, não existe um "gabarito" único (Problema do Oráculo). Por isso, utilizamos a técnica de **Testes Metamórficos** para verificar se as **relações lógicas** da proveniência se mantêm mesmo quando o código fonte sofre mutações.

## 📂 Estrutura dos Testes

O framework é dividido em dois níveis de validação:

| Arquivo | Objetivo | Tipo de Teste |
| :--- | :--- | :--- |
| **`teste_metamorfico_avancado.py`** | Valida a **FERRAMENTA** e o **PROMPT**. Usa cenários sintéticos (cenários de testes genéricos) para garantir que a IA entende conceitos básicos de Python. | Teste de Unidade / Harness |
| **`teste_cenario_real.py`** | Valida seu **SCRIPT DE PRODUÇÃO** (`ETL.py`, `meu_script.py`). Aplica mutações matemáticas e lógicas no seu código real. | Teste de Integração / Mutação |
| **`mutator_engine_advanced.py`** | O "cérebro" das mutações. Usa AST (Abstract Syntax Tree) para reescrever código Python de forma segura. | Biblioteca de Apoio |

-----

## 1\. Teste de Ferramenta (`teste_metamorfico_avancado.py`)

Este script gera pequenos códigos Python "falsos" em tempo de execução para testar se o Prompt Template está calibrado corretamente.

### Relações Metamórficas Testadas:

1.  **Equivalência Sintática (Loop vs. Comprehension):**
      * *Cenário:* Compara um loop `for` tradicional com uma `list comprehension` (`[x for x in y]`).
      * *Expectativa:* Ambos devem gerar o mesmo número de Atividades de processamento no grafo PROV.
2.  **Permutação de Blocos Independentes:**
      * *Cenário:* Troca a ordem de declaração de variáveis que não dependem uma da outra.
      * *Expectativa:* O grafo de proveniência deve ter a mesma topologia (mesmo número de nós), provando que a IA entende fluxo de dados e não apenas sequência de linhas.
3.  **Decomposição (Split):**
      * *Cenário:* Quebra um script em duas partes e soma os resultados.
      * *Expectativa:* `Atividades(Parte 1) + Atividades(Parte 2) ≈ Atividades(Script Completo)`.

-----

## 2\. Teste de Cenário Real (`teste_cenario_real.py`)

Este script pega o seu arquivo de produção (ex: `ETL.py`) e cria "Mutantes" — versões alteradas logicamente — para desafiar a IA.

### Mutações Aplicadas (via AST):

1.  **Mutação Sintática (Comutatividade):**
      * Altera operações matemáticas (`a + b` $\to$ `b + a`) e comparações (`x < y` $\to$ `y > x`).
      * *Objetivo:* Verificar se a IA entende a semântica da operação, independentemente de como foi escrita.
2.  **Permutação de Blocos Segura:**
      * O motor analisa as dependências de cada linha. Se a `Linha A` e a `Linha B` não compartilham variáveis, elas são trocadas de lugar.
      * *Objetivo:* Verificar se a captura de proveniência é robusta a refatorações de código.
3.  **Decomposição (Corte Cirúrgico):**
      * Corta o script ao meio, mantendo os imports na segunda metade.
      * *Objetivo:* Verificar se a IA consegue instrumentar fragmentos parciais de código.

-----

## 🚀 Como Executar

Certifique-se de que o Docker está rodando e que sua `GEMINI_API_KEY` está configurada.

### Passo 1: Validar a Ferramenta

Execute para garantir que a IA está "sã" e o prompt está funcionando:

```powershell
python teste_metamorfico_avancado.py
```

### Passo 2: Validar seu Script

Edite o arquivo `teste_cenario_real.py` e ajuste a variável `SCRIPT_ALVO` para o nome do seu arquivo (ex: `ETL.py`). Depois execute:

```powershell
python teste_cenario_real.py
```

-----

## 📊 Interpretando os Resultados

Os scripts exibem relatórios coloridos no terminal. Veja como ler:

  * **✅ SUCESSO:**

      * As métricas (número de Atividades e Entidades) do código Original e do Mutante são idênticas.
      * Isso significa que a IA foi **robusta** e entendeu a lógica perfeitamente.

  * **✅ SUCESSO (Tolerância / Variação Mínima):**

      * Houve uma pequena diferença (ex: 1 atividade a mais), mas dentro do aceitável.
      * Comum em Decomposição, onde a IA pode criar uma atividade extra de "Carga" para consertar um script quebrado.

  * **⚠️ INCONCLUSIVO:**

      * Geralmente ocorre quando o script instrumentado pela IA falha ao executar (ex: Erro de `FileNotFound` ou `KeyError` no Pandas).
      * **Importante:** Mesmo com erro de execução, o teste verifica se o grafo foi gerado. Se o grafo existe, a **instrumentação funcionou**, apenas o código do usuário (ou a mutação) estava incompleto.

  * **❌ FALHA:**

      * Diferença drástica entre o Original e o Mutante (ex: Original tem 5 atividades, Mutante tem 0).
      * Indica que a IA se confundiu ou "alucinou" devido à mudança no código. Sugere necessidade de ajuste no `prompt_template.py`.

-----

## 🛠️ Manutenção e Ajustes

  * **Motor de Mutação:** O arquivo `mutator_engine_advanced.py` pode ser expandido para incluir novas regras (ex: trocar loops `for` por `while`).
  * **Prompt:** Se os testes começarem a falhar muito, revise as "Diretrizes de Sensibilidade" no `prompt_template.py`.
