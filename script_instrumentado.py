# meu_script_instrumentado.py
# Um script simples para calcular a média de uma lista de números, instrumentado com DfAnalyzer.

import numpy as np
from dfanalyzer import Transformation, Set, SetType, Attribute, AttributeType, Dataflow
from dfanalyzer import Task, DataSet, Element

# --- CONFIGURAÇÃO INICIAL DO DATAFLOW ---
df = Dataflow()
df.save()
dataflow_tag = df.tag

# =======================================================
# === FASE 1: PROVENIÊNCIA PROSPECTIVA (O PLANO)
# =======================================================

# --- Transformação 1: Carregar Dados ---
tf1 = Transformation("Carregar Dados")
tf1_input = Set("iCarregar Dados", SetType.INPUT,
                [Attribute("CAMINHO_ARQUIVO_ENTRADA", AttributeType.FILE)])
tf1_output = Set("oCarregar Dados", SetType.OUTPUT,
                 [Attribute("DADOS_BRUTOS", AttributeType.COLLECTION)])
df.add_transformation(tf1)
df.add_set(tf1_input, tf1)
df.add_set(tf1_output, tf1)

# --- Transformação 2: Calcular Media ---
tf2 = Transformation("Calcular Media")
tf1_output.set_type(SetType.INPUT)
tf1_output.dependency = tf1.tag
tf2_output = Set("oCalcular Media", SetType.OUTPUT,
                 [Attribute("MEDIA", AttributeType.NUMERIC)])
df.add_transformation(tf2)
df.add_set(tf1_output, tf2)
df.add_set(tf2_output, tf2)

# --- Transformação 3: Salvar Resultado ---
tf3 = Transformation("Salvar Resultado")
tf2_output.set_type(SetType.INPUT)
tf2_output.dependency = tf2.tag
tf3_output = Set("oSalvar Resultado", SetType.OUTPUT,
                 [Attribute("CAMINHO_ARQUIVO_SAIDA", AttributeType.FILE)])
df.add_transformation(tf3)
df.add_set(tf2_output, tf3)
df.add_set(tf3_output, tf3)

df.save()
print("Proveniência Prospectiva salva.")

# =======================================================
# === FASE 2: PROVENIÊNCIA RETROSPECTIVA (A EXECUÇÃO)
# =======================================================

print("Iniciando workflow: Calculo de Média")

# --- Task 1: Execução de "Carregar Dados" ---
t1 = Task(1, dataflow_tag, "Carregar Dados")
caminho_arquivo_entrada = "data/raw_data.csv"
t1_input = DataSet("iCarregar Dados", [Element([caminho_arquivo_entrada])])
t1.add_dataset(t1_input)
t1.begin()

# --- Bloco de Código Original 1 ---
dados_brutos = [15.2, 16.1, 14.8, 15.5, 17.0]
print(f"Dados carregados (simuladamente) de {caminho_arquivo_entrada}")
# --- Fim do Bloco de Código ---

t1_output = DataSet("oCarregar Dados", [Element([dados_brutos])])
t1.add_dataset(t1_output)
t1.end()

# --- Task 2: Execução de "Calcular Media" ---
t2 = Task(2, dataflow_tag, "Calcular Media", dependency=t1)
t2.begin()

# --- Bloco de Código Original 2 ---
soma = sum(dados_brutos)
contagem = len(dados_brutos)
media = np.mean(dados_brutos)
print(f"Média calculada: {media}")
# --- Fim do Bloco de Código ---

t2_output = DataSet("oCalcular Media", [Element([media])])
t2.add_dataset(t2_output)
t2.end()

# --- Task 3: Execução de "Salvar Resultado" ---
t3 = Task(3, dataflow_tag, "Salvar Resultado", dependency=t2)
t3.begin()

# --- Bloco de Código Original 3 ---
caminho_arquivo_saida = "results/media_final.txt"
print(f"Salvando resultado em {caminho_arquivo_saida}")
# --- Fim do Bloco de Código ---

t3_output = DataSet("oSalvar Resultado", [Element([caminho_arquivo_saida])])
t3.add_dataset(t3_output)
t3.end()

df.save()
print("Proveniência Retrospectiva salva.")
print("Workflow concluído.")