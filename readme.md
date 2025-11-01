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

### Passo 1: Abra o Terminal e Navegue

Abra um terminal PowerShell e navegue até a pasta que contém seus scripts Python (`instrument_workflow.py`, `prompt_template.py` v4, etc.).

```powershell
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