# meu_script.py
# Um script simples para calcular a média de uma lista de números,
# instrumentado com o padrão W3C-PROV.

import numpy as np
import prov.model as prov
import json

# --- CONFIGURAÇÃO INICIAL DE PROVENIÊNCIA ---
d = prov.ProvDocument()
d.add_namespace('ex', 'http://example.org/')
a_script = d.agent('ex:meu_script.py')

# --- Etapa 1: Carregar Dados (Simulado) ---
# Em um workflow real, isso leria de um arquivo.
print("Iniciando workflow: Calculo de Média")
dados_brutos = [15.2, 16.1, 14.8, 15.5, 17.0]
caminho_arquivo_entrada = "data/raw_data.csv"
print(f"Dados carregados (simuladamente) de {caminho_arquivo_entrada}")

# --- Captura de Proveniência (Etapa 1) ---
a_load = d.activity('ex:carregar_dados')
d.wasAssociatedWith(a_load, a_script)
e_in_file = d.entity('ex:arquivo_entrada_csv', {'prov:location': caminho_arquivo_entrada})
e_dados_brutos = d.entity('ex:dados_brutos_lista', {'ex:value': json.dumps(dados_brutos)})
d.wasGeneratedBy(e_dados_brutos, a_load)
a_load.used(e_in_file)


# --- Etapa 2: Processar Dados (Calcular Média) ---
# O código principal do workflow
soma = sum(dados_brutos)
contagem = len(dados_brutos)
media = np.mean(dados_brutos) # Usando numpy para parecer mais científico

print(f"Média calculada: {media}")

# --- Captura de Proveniência (Etapa 2) ---
a_calc = d.activity('ex:calcular_media')
d.wasAssociatedWith(a_calc, a_script)
e_media = d.entity('ex:media_calculada', {'ex:value': media})
d.wasGeneratedBy(e_media, a_calc)
a_calc.used(e_dados_brutos)


# --- Etapa 3: Salvar Resultado (Simulado) ---
# Em um workflow real, isso salvaria em um arquivo de texto ou CSV.
caminho_arquivo_saida = "results/media_final.txt"
print(f"Salvando resultado em {caminho_arquivo_saida}")

# --- Captura de Proveniência (Etapa 3) ---
a_save = d.activity('ex:salvar_resultado')
d.wasAssociatedWith(a_save, a_script)
e_out_file = d.entity('ex:arquivo_saida_txt', {'prov:location': caminho_arquivo_saida})
d.wasGeneratedBy(e_out_file, a_save)
a_save.used(e_media)


# --- FINALIZAÇÃO E SALVAMENTO DA PROVENIÊNCIA ---
print("Workflow concluído.")
d.serialize('provenance.json', format='json')
print("Grafo de Proveniência (W3C-PROV) salvo em 'provenance.json'.")