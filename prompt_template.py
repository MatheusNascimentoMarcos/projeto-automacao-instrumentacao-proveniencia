# prompt_template.py
# VERSÃO 4 - Treinada com W3C-PROV e com escaping de chaves {}

PROMPT_MESTRE_TEMPLATE = """
Você é um engenheiro de software especialista em proveniência de dados e instrumentação de workflows científicos. Sua tarefa é analisar um script em Python e inserir o código necessário para capturar a proveniência retrospectiva, seguindo o padrão W3C-PROV.

## Contexto e Conceitos
O padrão W3C-PROV modela a proveniência usando:
- **Entity**: Um dado (um arquivo, uma variável, um parâmetro).
- **Activity**: Um processo que transforma os dados (uma função, uma etapa do script).
- **Agent**: A pessoa ou software que executa a atividade.
- **wasGeneratedBy / used**: Relações que conectam Entidades e Atividades.

## Instruções (Chain of Thought)
Siga estes passos para instrumentar o código fornecido:
1.  **Importação**: Adicione `import prov.model as prov` no início do script.
2.  **Documento**: Crie um documento de proveniência: `d = prov.ProvDocument()`
3.  **Namespace**: Adicione um namespace para seus itens: `d.add_namespace('ex', 'http://example.org/')`
4.  **Agente**: Defina o próprio script como o Agente: `a_script = d.agent('ex:meu_script.py')`
5.  **Etapas (Activities)**: Para cada etapa lógica (Carregar, Calcular, Salvar), crie uma `Activity` (ex: `a_load = d.activity('ex:carregar_dados')`) e associe-a ao Agente (ex: `d.wasAssociatedWith(a_load, a_script)`).
6.  **Dados (Entities)**: Para cada variável importante (caminho de arquivo, dados brutos, média), crie uma `Entity`.
7.  **Links**: Use `d.wasGeneratedBy(output_entity, activity)` e `activity.used(input_entity)` para conectar o grafo.
8.  **Salvar**: No final, serialize o documento (ex: `d.serialize('provenance.json')`).
9.  **Não Interrompa o Código**: Insira o código de proveniência sem quebrar o fluxo do script original.
10. **REGRA CRÍTICA DE ATRIBUTOS:** Ao registrar quaisquer atributos (em `other_attributes` ou `attributes`), se o valor do atributo for uma lista Python `list`, você **DEVE** convertê-lo para um tipo imutável. Prefira convertê-lo para uma **string** usando `str(valor)`. Por exemplo, se um atributo é `'colunas': ['a', 'b']`, você deve registrá-lo como `'colunas': "['a', 'b']"`. Pois a biblioteca `prov` não aceita listas diretamente.

## Exemplo de Poucos Tiros (Few-shot Example)
(Este exemplo instrumenta o script de 'meu_script.py' usando 'w3c-prov')

### INPUT (Código Original):
```python
# meu_script.py
# Um script simples para calcular a média de uma lista de números.

import numpy as np

# --- Etapa 1: Carregar Dados (Simulado) ---
print("Iniciando workflow: Calculo de Média")
dados_brutos = [15.2, 16.1, 14.8, 15.5, 17.0]
caminho_arquivo_entrada = "data/raw_data.csv"
print(f"Dados carregados (simuladamente) de {{caminho_arquivo_entrada}}")


# --- Etapa 2: Processar Dados (Calcular Média) ---
soma = sum(dados_brutos)
contagem = len(dados_brutos)
media = np.mean(dados_brutos)

print(f"Média calculada: {{media}}")


# --- Etapa 3: Salvar Resultado (Simulado) ---
caminho_arquivo_saida = "results/media_final.txt"
print(f"Salvando resultado em {{caminho_arquivo_saida}}")
print("Workflow concluído.")

# meu_script.py
# Um script simples para calcular a média de uma lista de números,
# instrumentado com o padrão W3C-PROV.

import numpy as np
import prov.model as prov
import json # Para salvar os valores da lista

# --- CONFIGURAÇÃO INICIAL DE PROVENIÊNCIA ---
d = prov.ProvDocument()
d.add_namespace('ex', '[http://example.org/](http://example.org/)')
# Define o próprio script como o Agente
a_script = d.agent('ex:meu_script.py')


# =======================================================
# === FASE 1: Carregar Dados
# =======================================================
print("Iniciando workflow: Calculo de Média")

# --- Código Original 1 ---
dados_brutos = [15.2, 16.1, 14.8, 15.5, 17.0]
caminho_arquivo_entrada = "data/raw_data.csv"
# --- Fim do Bloco ---
print(f"Dados carregados (simuladamente) de {{caminho_arquivo_entrada}}")

# --- Captura de Proveniência (Fase 1) ---
a_load = d.activity('ex:carregar_dados')
d.wasAssociatedWith(a_load, a_script)
# Entidade para o arquivo de entrada
e_in_file = d.entity('ex:arquivo_entrada_csv', {{"prov:location": caminho_arquivo_entrada}})
# Entidade para os dados brutos (lista)
e_dados_brutos = d.entity('ex:dados_brutos_lista', {{"ex:value": json.dumps(dados_brutos)}})
# Link: a lista 'e_dados_brutos' foi gerada pela atividade 'a_load'
d.wasGeneratedBy(e_dados_brutos, a_load)
# Link: a atividade 'a_load' usou o arquivo 'e_in_file' (mesmo que simulado)
a_load.used(e_in_file)


# =======================================================
# === FASE 2: Processar Dados (Calcular Média)
# =======================================================

# --- Código Original 2 ---
soma = sum(dados_brutos)
contagem = len(dados_brutos)
media = np.mean(dados_brutos)
# --- Fim do Bloco ---
print(f"Média calculada: {{media}}")

# --- Captura de Proveniência (Fase 2) ---
a_calc = d.activity('ex:calcular_media')
d.wasAssociatedWith(a_calc, a_script)
# Entidade para a média calculada
e_media = d.entity('ex:media_calculada', {{"ex:value": media}})
# Link: a 'e_media' foi gerada pela atividade 'a_calc'
d.wasGeneratedBy(e_media, a_calc)
# Link: a atividade 'a_calc' usou a entidade 'e_dados_brutos' da etapa anterior
a_calc.used(e_dados_brutos)


# =======================================================
# === FASE 3: Salvar Resultado
# =======================================================

# --- Código Original 3 ---
caminho_arquivo_saida = "results/media_final.txt"
# --- Fim do Bloco ---
print(f"Salvando resultado em {{caminho_arquivo_saida}}")

# --- Captura de Proveniência (Fase 3) ---
a_save = d.activity('ex:salvar_resultado')
d.wasAssociatedWith(a_save, a_script)
# Entidade para o arquivo de saída
e_out_file = d.entity('ex:arquivo_saida_txt', {{"prov:location": caminho_arquivo_saida}})
# Link: o arquivo 'e_out_file' foi gerado pela atividade 'a_save'
d.wasGeneratedBy(e_out_file, a_save)
# Link: a atividade 'a_save' usou a 'e_media' da etapa anterior
a_save.used(e_media)


# =======================================================
# === SALVANDO O GRAFO DE PROVENIÊNCIA
# =======================================================
d.serialize('provenance_w3c.json', format='json')
print("Workflow concluído.")
print("Grafo de Proveniência (W3C-PROV) salvo em 'provenance_w3c.json'.")

###Tarefa
Agora, instrumente o seguinte script usando o padrão W3C-PROV (biblioteca 'prov'), como mostrado no exemplo. Retorne apenas o código Python completo e instrumentado, sem explicações, prefácios ou comentários adicionais.


##INPUT (Código Original):
{input_code}


##OUTPUT (Código Instrumentado Desejado):
"""