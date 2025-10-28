# meu_script.py
# Um script simples para calcular a média de uma lista de números.

import numpy as np

# --- Etapa 1: Carregar Dados (Simulado) ---
# Em um workflow real, isso leria de um arquivo.
print("Iniciando workflow: Calculo de Média")
dados_brutos = [15.2, 16.1, 14.8, 15.5, 17.0]
caminho_arquivo_entrada = "data/raw_data.csv"
print(f"Dados carregados (simuladamente) de {caminho_arquivo_entrada}")


# --- Etapa 2: Processar Dados (Calcular Média) ---
# O código principal do workflow
soma = sum(dados_brutos)
contagem = len(dados_brutos)
media = np.mean(dados_brutos) # Usando numpy para parecer mais científico

print(f"Média calculada: {media}")


# --- Etapa 3: Salvar Resultado (Simulado) ---
# Em um workflow real, isso salvaria em um arquivo de texto ou CSV.
caminho_arquivo_saida = "results/media_final.txt"
print(f"Salvando resultado em {caminho_arquivo_saida}")
print("Workflow concluído.")