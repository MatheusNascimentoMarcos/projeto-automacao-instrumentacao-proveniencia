# Projeto de Automação de Instrumentação de Proveniência com IA

Este projeto demonstra um *wrapper* de IA (Gemini) que instrumenta automaticamente scripts Python com captura de proveniência, usando o padrão **W3C-PROV**.

O sistema é executado dentro de contêineres Docker para garantir um ambiente limpo, portátil e que resolva problemas de dependência (como os encontrados com o `DfAnalyzer`).

O fluxo de trabalho consiste em duas etapas principais:

1. **Geração:** o `instrument_workflow.py` usa a IA para ler um script (`meu_script.py`) e um dos **quatro templates de prompt** (`prompt_template_*.py`), escolhido pela granularidade desejada, e gerar um novo script (`script_instrumentado_prov.py`) que contém o código de proveniência.
2. **Execução e Depuração:** o `script_instrumentado_prov.py` é executado e gera o arquivo `provenance_w3c.json`, com o grafo de proveniência da execução para análise.

---

## 1. Estrutura do Projeto

| Arquivo | Função |
| :--- | :--- |
| `instrument_workflow.py` | Orquestra a chamada à API do Gemini e gera o script instrumentado. |
| `prompt_template_coarse.py` | Template de granularidade **grossa** (*black-box*). |
| `prompt_template_medium.py` | Template de granularidade **média** (híbrida). |
| `prompt_template_fine.py` | Template de granularidade **fina** (*white-box*). |
| `prompt_template_metamorphic.py` | Template **metamórfico**, orientado às Relações Metamórficas RM1 a RM6. |
| `teste_metamorfico_avancado.py` | Valida a ferramenta e o prompt com cenários sintéticos. Aceita `--level`. |
| `teste_cenario_real.py` | Valida o seu script de produção com mutações via AST. Aceita `--level`. |
| `mutator_engine_advanced.py` | Motor de mutações (AST). |
| `check_models.py` | Lista os modelos do Gemini disponíveis para a sua chave. |

Os quatro `prompt_template_*.py` precisam estar **na mesma pasta** do `instrument_workflow.py`.

---

## 2. Escolhendo a Granularidade

Todos os templates produzem proveniência W3C-PROV e respeitam as mesmas quatro invariantes ontológicas e causais: **Tipagem** (3.1), **Aciclicidade/DAG** (3.2), **Consistência Temporal** (3.3) e **Unicidade de Origem Primária** (3.4). O que muda é o nível de detalhe capturado.

| `--level` | Visão | O que captura | Quando usar |
| :--- | :--- | :--- | :--- |
| `coarse` | *Black-box*| Arquivos, APIs e modelos; cada etapa macro é uma Activity. Laços não são desdobrados. | Documentar o fluxo de arquivos e módulos de um pipeline, com baixo custo. |
| `medium` | Híbrida | I/O, parâmetros de configuração, DataFrames e resultados intermediários relevantes. Reatribuições geram versões (`_v1`, `_v2`). | Ligar resultados a parâmetros e datasets intermediários. |
| `fine` | *White-box* | Todas as variáveis e operações; cada iteração de laço é uma Activity, com IDs únicos. | Explicar o valor de variáveis individuais, iteração a iteração. |
| `metamorphic` (padrão) | Determinística e canônica | Cada operação semântica gera 1 Activity + 1 Entity, com IDs por contador global (`_uid`), timestamps nas arestas e agente único. | Quando o grafo será validado por Relações Metamórficas (RM1 a RM6). |

> **Atenção:** o custo aumenta com a granularidade. No nível `fine`, o grafo cresce com o número de iterações dos laços, o que encarece geração, execução e validação.

---

## 3. Pré-requisitos

* **Docker Desktop:** necessário para construir e executar o ambiente.
* **Chave de API do Google Gemini:** o *wrapper* de IA precisa de uma chave de API.

---

## 4. Fase de Setup (executar apenas uma vez)

O objetivo desta fase é construir a imagem Docker (`ia-prov-wrapper`), que contém o ambiente Python 3.11 e todas as bibliotecas necessárias (`prov`, `lxml`, `rdflib`, `google-generativeai` e, se for usar os validadores de grafo, `networkx`).

1. Abra um terminal PowerShell.
2. Navegue até a pasta que contém o `Dockerfile` (o simplificado, criado para o `w3c-prov`).
3. Execute:

```powershell
docker build -t ia-prov-wrapper .
```

Na primeira vez, o processo pode demorar alguns minutos.

---

## 5. Fase de Execução (Geração e Depuração)

Este é o fluxo de trabalho principal. Execute-o a partir da sua pasta de projeto.

### Passo 1: Abra o terminal e navegue até a pasta do projeto

Abra um PowerShell e navegue até a pasta que contém `instrument_workflow.py`, os quatro `prompt_template_*.py` e o seu script.

```powershell
cd "Caminho da sua pasta com os docs de instrumentação"
```

### Passo 2: Configure a chave de API

A chave só é válida para esta janela do terminal.

```powershell
$env:GEMINI_API_KEY = 'SUA_CHAVE_API_COMECA_COM_AIza...'
```

### Passo 3: Geração do script (Execução 1)

Este comando inicia o contêiner, espelha a sua pasta local e executa o `instrument_workflow.py` para gerar o script instrumentado. Use `--level` para escolher a granularidade (`coarse`, `medium`, `fine` ou `metamorphic`). Se omitido, o padrão é `metamorphic`.

```powershell
docker run -it --rm -e GEMINI_API_KEY=$env:GEMINI_API_KEY -v "${PWD}:/app" ia-prov-wrapper python3 instrument_workflow.py meu_script.py script_instrumentado_prov.py --level fine
```

**Sobre o espelhamento (`-v "${PWD}:/app"`):**

* `"${PWD}"` é a pasta local atual (por exemplo, `Docs Matheus`).
* `:/app` é a pasta de destino dentro do contêiner.

Isso permite que o contêiner leia o `meu_script.py` e salve o `script_instrumentado_prov.py` de volta no diretório local.

**Saída esperada:**

```text
Lendo o script de entrada: meu_script.py
Iniciando a instrumentação com a IA do Gemini (nível: fine)...
Isso pode levar alguns segundos...

[SUCESSO] Código instrumentado salvo em: script_instrumentado_prov.py
```

### Passo 4: Depuração do script (Execução 2)

Com o `script_instrumentado_prov.py` na sua pasta, execute-o dentro do contêiner:

```powershell
docker run -it --rm -v "${PWD}:/app" ia-prov-wrapper python3 script_instrumentado_prov.py
```

**Saída esperada:** a saída do script de exemplo (cálculo de média), seguida da confirmação de que o grafo foi salvo.

```text
Iniciando workflow: Calculo de Média
Dados carregados (simuladamente) de data/raw_data.csv
Média calculada: 15.719999999999999
Salvando resultado em results/media_final.txt
Workflow concluído.
```

Ao final, o grafo de proveniência (W3C-PROV) é salvo em `provenance_w3c.json`, no diretório de trabalho.

### Dica: comparando níveis de granularidade

Cada execução do script instrumentado sobrescreve o `provenance_w3c.json`. Para comparar níveis, use nomes de saída distintos e renomeie o JSON entre as execuções:

```powershell
# Geração com nomes distintos por nível
docker run -it --rm -e GEMINI_API_KEY=$env:GEMINI_API_KEY -v "${PWD}:/app" ia-prov-wrapper python3 instrument_workflow.py meu_script.py script_instrumentado_coarse.py --level coarse
docker run -it --rm -e GEMINI_API_KEY=$env:GEMINI_API_KEY -v "${PWD}:/app" ia-prov-wrapper python3 instrument_workflow.py meu_script.py script_instrumentado_fine.py --level fine

# Execução e preservação do grafo de cada nível
docker run -it --rm -v "${PWD}:/app" ia-prov-wrapper python3 script_instrumentado_coarse.py
Rename-Item provenance_w3c.json provenance_coarse.json

docker run -it --rm -v "${PWD}:/app" ia-prov-wrapper python3 script_instrumentado_fine.py
Rename-Item provenance_w3c.json provenance_fine.json
```

---

# 🧪 Validação Metamórfica de Instrumentação de Proveniência (Fase 2)

Esta seção descreve o framework de testes automatizados que valida a robustez e a consistência do **Agente de Instrumentação W3C-PROV** (baseado em LLM/Gemini).

Como usamos IA generativa para escrever código, não existe um "gabarito" único (Problema do Oráculo). Por isso usamos **Testes Metamórficos**: verificamos se as **relações lógicas** da proveniência se mantêm quando o código-fonte sofre mutações.

## Como os testes funcionam

Os dois scripts de teste rodam **no host** (`python teste_*.py`) e disparam o Docker por `subprocess`. Em cada cenário, eles:

1. instrumentam o código original ou mutante com `instrument_workflow.py --level <nível>`, dentro do contêiner;
2. executam o script instrumentado, também dentro do contêiner;
3. leem o `provenance_w3c.json` gerado e comparam o número de Activities e Entities.

Por isso, `instrument_workflow.py` e os quatro `prompt_template_*.py` precisam estar na pasta do projeto, que é montada em `/app`.

### Escolhendo o nível nos testes

Os dois scripts aceitam `--level` (`coarse`, `medium`, `fine` ou `metamorphic`). Se omitido, usam a variável de ambiente `PROV_LEVEL` e, na falta dela, `metamorphic`.

```powershell
python teste_metamorfico_avancado.py --level fine
python teste_cenario_real.py --level coarse

# ou, via variável de ambiente (vale para a janela atual do terminal)
$env:PROV_LEVEL = 'medium'
python teste_cenario_real.py
```

Cada nível usa uma pasta temporária própria (`temp_metamorfico_<nível>` e `temp_real_advanced_<nível>`), então os resultados de níveis diferentes não se sobrescrevem. As pastas **não são apagadas** ao final (a limpeza está comentada de propósito), para que você possa inspecionar os scripts instrumentados e os grafos.

Para rodar todos os níveis em sequência:

```powershell
foreach ($l in 'coarse','medium','fine','metamorphic') { python teste_cenario_real.py --level $l }
```

## Estrutura dos testes

| Arquivo | Objetivo | Tipo de teste |
| :--- | :--- | :--- |
| `teste_metamorfico_avancado.py` | Valida a **ferramenta** e o **prompt** com cenários sintéticos, para garantir que a IA entende conceitos básicos de Python. | Teste de unidade / *harness* |
| `teste_cenario_real.py` | Valida o seu **script de produção** (`ETL.py`, com *fallback* para `meu_script.py`) aplicando mutações ao código real. | Teste de integração / mutação |
| `mutator_engine_advanced.py` | O motor das mutações. Usa AST (*Abstract Syntax Tree*) para reescrever código Python com segurança. | Biblioteca de apoio |
| `check_models.py` | Lista os modelos do Gemini disponíveis para a sua chave. Use-o se a chamada falhar com "modelo não encontrado" e ajuste o nome do modelo em `instrument_workflow.py`. | Utilitário |

---

## 1. Teste de Ferramenta (`teste_metamorfico_avancado.py`)

Gera pequenos códigos Python sintéticos em tempo de execução para verificar se o template de prompt está calibrado.

### Relações metamórficas testadas

1. **Equivalência sintática (loop vs. comprehension):**
   * *Cenário:* compara um `for` com `append` e uma *list comprehension* (`[x * 2 for x in dados]`).
   * *Expectativa depende do nível*, porque os níveis tratam laços de formas diferentes:

   | Nível | Critério de sucesso | Motivo |
   | :--- | :--- | :--- |
   | `coarse`, `medium` | Mesmo número de Activities nos dois códigos | Laços não são desdobrados. |
   | `fine`, `metamorphic` | `Activities(loop) >= Activities(comprehension) > 0` | Cada iteração do laço vira uma Activity; a comprehension é uma única operação. A divergência é esperada, não é falha da IA. |

2. **Permutação de blocos independentes:**
   * *Cenário:* troca a ordem de duas sequências de operações que não dependem uma da outra (`a = 10; a = a + 5` e `b = 20; b = b * 2`).
   * *Expectativa:* mesmo número de Activities e Entities, o que mostra que a IA entende fluxo de dados e não apenas a sequência de linhas.
3. **Decomposição (*split*):**
   * *Cenário:* o script completo é comparado com duas partes, e a parte 2 repete a declaração de `raw_data` para ser executável sozinha.
   * *Expectativa:* `Atividades(Parte 1) + Atividades(Parte 2) ≈ Atividades(Script Completo)`, com tolerância de até 2. A diferença vem da inicialização repetida em cada parte.

---

## 2. Teste de Cenário Real (`teste_cenario_real.py`)

Pega o seu arquivo de produção (por padrão `ETL.py`) e cria **mutantes**, versões alteradas logicamente, para desafiar a IA. O primeiro passo é sempre uma execução **base** do script original, cujas métricas servem de referência.

### Mutações aplicadas (via AST)

1. **Equivalência sintática:**
   * *Comutatividade:* `a + b` → `b + a` e `a * b` → `b * a`.
   * *Inversão de comparação:* `x < y` → `y > x` (e equivalentes para `<=`, `>`, `>=`, `==`, `!=`).
   * *Atribuição aumentada desfeita:* `x += 1` → `x = x + 1`.
   * *Objetivo:* verificar se a IA entende a semântica da operação, independentemente de como foi escrita.
   * *Salvaguarda:* a comutatividade **não é aplicada** a expressões com literais de string, f-strings ou coleções (`"a" + x`, `[1] + y`), porque a troca alteraria o resultado.
   * *Limitação:* o motor não infere tipos. Se `a` e `b` forem variáveis que guardam strings ou listas, a troca de `a + b` ainda pode mudar o resultado. Nesses casos, uma FALHA pode vir do mutante e não da IA.
2. **Permutação de blocos segura:**
   * O motor analisa as dependências de leitura e escrita de cada instrução de nível superior e troca instruções **adjacentes** que não compartilham variáveis (até 3 passadas). Imports nunca são movidos.
   * A análise é **conservadora**: uma chamada de método (`lista.append(...)`, `df.dropna(...)`) conta como escrita no objeto; atribuições em índice ou atributo (`d['k'] = v`, `obj.x = v`) contam como escrita em `d`/`obj`; e chamadas de I/O (`print`, `open`, `input`, e métodos como `read_*`, `write*`, `to_*`) nunca são reordenadas entre si, o que preserva a ordem das saídas.
   * Se nenhuma troca segura existir, o teste informa que o código é muito acoplado e pula esta etapa.
   * *Limitação:* dependências por arquivo (escrever um arquivo por um caminho e lê-lo por outro nome de variável) não são detectadas.
3. **Decomposição (corte cirúrgico):**
   * Divide o script ao meio, mantendo os imports nas duas partes.
   * A parte 2 pode usar variáveis definidas na parte 1 e então falhar na execução (`NameError`). Isso não invalida o teste: se o grafo foi gerado, a instrumentação funcionou. Por isso a tolerância é de até 2 Activities.
   * *Objetivo:* verificar se a IA instrumenta fragmentos parciais de código.

> **Observação:** como as mutações passam por `ast.unparse`, os comentários do código original são removidos e a formatação é normalizada nos mutantes. A comparação com a base, portanto, também exercita a insensibilidade a comentários e espaçamento (parte da RM1).

---

## 3. Relação com as Relações Metamórficas RM1 a RM6

O template `metamorphic` foi desenhado para o pipeline de validação metamórfica, em que o grafo é comparado por um verificador topológico. A tabela mostra o que os testes atuais cobrem:

| Relação | Descrição | Cobertura atual |
| :--- | :--- | :--- |
| **RM1** | Isomorfismo sob refatoração de nomes, comentários e comutatividade | Coberta pela equivalência sintática (mutação via AST) |
| **RM2** | Isomorfismo sob permutação de blocos independentes | Coberta pela permutação de blocos (ambos os scripts) |
| **RM3** | Expansão: o grafo original permanece como subgrafo, com delta previsível | Parcial: o teste de decomposição compara contagens, não subgrafos |
| **RM4** | Redução / poda de ramos não executados | Não coberta |
| **RM5** | Inversão de etapas independentes e precedência temporal (Inv. 3.3) | Não coberta: a permutação muda a ordem, mas os timestamps não são verificados |
| **RM6** | Laço vs. versão desdobrada (Inv. 3.2 e 3.4) | Não coberta: o teste loop vs. comprehension é outra relação |

As comparações atuais usam **contagem de Activities e Entities**. Contagens iguais são necessárias para o isomorfismo, mas não suficientes. Verificações mais fortes, e as quatro invariantes dfinidasno documento de estabelecimento das RM's são o próximo passo natural.

---

## 🚀 Como executar os testes

Certifique-se de que o Docker está rodando, que a imagem `ia-prov-wrapper` foi construída e que a `GEMINI_API_KEY` está configurada.

### Passo 1: Validar a ferramenta

Garante que a IA está respondendo bem e que o prompt do nível escolhido funciona:

```powershell
python teste_metamorfico_avancado.py --level metamorphic
```

### Passo 2: Validar o seu script

Edite o `teste_cenario_real.py` e ajuste a variável `SCRIPT_ALVO` para o nome do seu arquivo (ex.: `ETL.py`). Se o arquivo não existir, o teste tenta usar `meu_script.py`. Depois execute:

```powershell
python teste_cenario_real.py --level metamorphic
```

Se o seu script lê CSVs, coloque-os na raiz do projeto: o teste copia os `*.csv` da raiz para a pasta temporária antes de executar.

---

## 📊 Interpretando os resultados

Os scripts exibem relatórios coloridos no terminal:

* **✅ SUCESSO:**
  * As métricas (número de Activities e Entities) do código original e do mutante são idênticas, ou atendem ao critério do nível (veja o teste de equivalência sintática).
  * A IA foi robusta e entendeu a lógica.
* **✅ SUCESSO (tolerância):**
  * Houve uma pequena diferença (até 1 Activity na comparação com o mutante; até 2 na decomposição), mas dentro do aceitável.
  * Comum na decomposição, em que a inicialização de dados pode se repetir nas duas partes.
* **⚠️ INCONCLUSIVO:**
  * Ocorre quando a base (script original) não gera grafo, por exemplo por falha de execução (`FileNotFound`, `KeyError` no Pandas).
  * Se o script instrumentado falha mas o grafo é gerado, o teste continua: a **instrumentação funcionou** e apenas o código do usuário (ou a mutação) estava incompleto.
* **❌ FALHA:**
  * Diferença drástica entre original e mutante (ex.: original com 5 Activities, mutante com 0).
  * Indica que a IA se confundiu ou "alucinou" com a mudança no código, ou que o mutante alterou a semântica (veja as limitações das mutações). Sugere ajuste no template de prompt usado.

> **Compare níveis com cuidado:** o número absoluto de Activities cresce com a granularidade (`fine` e `metamorphic` desdobram laços). Compare sempre original e mutante **dentro do mesmo nível**, nunca entre níveis diferentes.

### Sobre o arquivo de proveniência

Todos os templates salvam o grafo em `provenance_w3c.json`. Um `provenance.json` na raiz do projeto é sobra do template original (sem timestamps nem `wasDerivedFrom`) e **é ignorado** pelos testes. O `teste_metamorfico_avancado.py` também apaga um `provenance_w3c.json` residual antes de cada execução, para nunca atribuir o grafo de um cenário a outro.

---

## 🛠️ Manutenção e Ajustes

* **Motor de mutação:** o `mutator_engine_advanced.py` pode ser expandido com novas regras (ex.: trocar loops `for` por `while`). Ao adicionar uma mutação, garanta que ela preserva a semântica do código, ou os resultados serão FALHAS falsas.
* **Prompts:** se os testes começarem a falhar com frequência, revise as **Heurísticas de Captura** e o **Contrato Canônico** do template correspondente ao nível usado (`prompt_template_coarse.py`, `prompt_template_medium.py`, `prompt_template_fine.py` ou `prompt_template_metamorphic.py`).
* **Modelo do Gemini:** o nome do modelo está fixo em `instrument_workflow.py` (`models/gemini-pro-latest`). Use `python check_models.py` para listar os disponíveis.
* **Novos níveis:** para criar uma nova granularidade, adicione o template em um novo arquivo, importe-o no `instrument_workflow.py`, registre-o no dicionário `TEMPLATES` e inclua o nome em `VALID_LEVELS` nos dois scripts de teste.
* **Escaping de chaves:** os templates passam por `.format()`, então qualquer chave literal dentro deles deve ser duplicada (`{{ }}`). O único placeholder com chave simples é `{input_code}`.
