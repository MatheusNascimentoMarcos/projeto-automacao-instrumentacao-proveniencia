# meu_script.py
# Um script simples para calcular a média de uma lista de números,
# instrumentado com o padrão W3C-PROV.

import numpy as np
import prov.model as prov
import json # Para salvar os valores da lista

# --- CONFIGURAÇÃO INICIAL DE PROVENIÊNCIA ---
d = prov.ProvDocument()
d.add_namespace('ex', 'http://example.org/')
# Define o próprio script como o Agente
a_script = d.agent('ex:meu_script.py')


# =======================================================
# === FASE 1: Carregar Dados
# =======================================================
print("Iniciando workflow: Calculo de Média")

# --- Código Original 1 ---
# Em um workflow real, isso leria de um arquivo.
dados_brutos = [15.2, 16.1, 14.8, 15.5, 17.0]
caminho_arquivo_entrada = "data/raw_data.csv"
# --- Fim do Bloco ---
print(f"Dados carregados (simuladamente) de {caminho_arquivo_entrada}")

# --- Captura de Proveniência (Fase 1) ---
a_load = d.activity('ex:carregar_dados')
d.wasAssociatedWith(a_load, a_script)
# Entidade para o arquivo de entrada
e_in_file = d.entity('ex:arquivo_entrada_csv', {"prov:location": caminho_arquivo_entrada})
# Entidade para os dados brutos (lista)
e_dados_brutos = d.entity('ex:dados_brutos_lista', {"ex:value": json.dumps(dados_brutos)})
# Link: a lista 'e_dados_brutos' foi gerada pela atividade 'a_load'
d.wasGeneratedBy(e_dados_brutos, a_load)
# Link: a atividade 'a_load' usou o arquivo 'e_in_file' (mesmo que simulado)
a_load.used(e_in_file)


# =======================================================
# === FASE 2: Processar Dados (Calcular Média)
# =======================================================

# --- Código Original 2 ---
# O código principal do workflow
soma = sum(dados_brutos)
contagem = len(dados_brutos)
media = np.mean(dados_brutos) # Usando numpy para parecer mais científico
# --- Fim do Bloco ---
print(f"Média calculada: {media}")

# --- Captura de Proveniência (Fase 2) ---
a_calc = d.activity('ex:calcular_media')
d.wasAssociatedWith(a_calc, a_script)
# Entidade para a média calculada
e_media = d.entity('ex:media_calculada', {"ex:value": media})
# Link: a 'e_media' foi gerada pela atividade 'a_calc'
d.wasGeneratedBy(e_media, a_calc)
# Link: a atividade 'a_calc' usou a entidade 'e_dados_brutos' da etapa anterior
a_calc.used(e_dados_brutos)


# =======================================================
# === FASE 3: Salvar Resultado
# =======================================================

# --- Código Original 3 ---
# Em um workflow real, isso salvaria em um arquivo de texto ou CSV.
caminho_arquivo_saida = "results/media_final.txt"
# --- Fim do Bloco ---
print(f"Salvando resultado em {caminho_arquivo_saida}")

# --- Captura de Proveniência (Fase 3) ---
a_save = d.activity('ex:salvar_resultado')
d.wasAssociatedWith(a_save, a_script)
# Entidade para o arquivo de saída
e_out_file = d.entity('ex:arquivo_saida_txt', {"prov:location": caminho_arquivo_saida})
# Link: o arquivo 'e_out_file' foi gerado pela atividade 'a_save'
d.wasGeneratedBy(e_out_file, a_save)
# Link: a atividade 'a_save' usou a 'e_media' da etapa anterior
a_save.used(e_media)


# =======================================================
# === SALVANDO O GRAFO DE PROVENIÊNCIA
# =======================================================
print("Workflow concluído.")
d.serialize('provenance.json', format='json')
print("Grafo de Proveniência (W3C-PROV) salvo em 'provenance.json'.")