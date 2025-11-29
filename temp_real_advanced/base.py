#!/usr/bin/env python
# coding: utf-8

# # Script ETL - Tratamento de Dados de Clientes e Compras
# 
# Este script converte o notebook 'ETL.ipynb' para um arquivo Python executável.
# Ele lê um arquivo CSV, aplica várias transformações de limpeza de dados
# e salva o resultado em um novo arquivo CSV.

import pandas as pd
# A biblioteca 'google.colab.files' é específica do ambiente Google Colab
# e não é usada neste script padrão.
# from google.colab import files

def extrair_dados(caminho_arquivo):
    """
    Carrega os dados do arquivo CSV inicial.
    """
    print(f"Iniciando a leitura do arquivo: {caminho_arquivo}")
    try:
        df = pd.read_csv(caminho_arquivo, encoding="utf-8", delimiter=";")
        print(f"Número de tuplas/atributos inicial: {df.shape}")
        return df
    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        print("Por favor, coloque o arquivo no mesmo diretório do script.")
        return None
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao ler o arquivo: {e}")
        return None

def transformar_dados(df):
    """
    Aplica as regras de limpeza e transformação no DataFrame.
    """
    if df is None:
        return None

    print("Iniciando transformações...")

    # 1. Corrigir coluna 'UF' com base no 'Município'
    print("Corrigindo 'UF' com base no 'Município'...")
    correcoes_estado = {
        "Rio de Janeiro": "RJ",
        "Fortaleza": "CE",
    }
    df['UF'] = df['Município'].map(correcoes_estado).fillna(df['UF'])

    # 2. Recalcular 'Valor total pago'
    # Garante que o valor esteja correto (Preço * Quantidade) + Taxa
    print("Recalculando 'Valor total pago'...")
    df['Valor total pago'] = (df['Preço unitário'] * df['Quantidade comprada']) + df['Taxa de entrega']

    # 3. Remover linhas com 'CPF do cliente' nulo ou vazio
    print("Removendo registros com 'CPF do cliente' nulo ou vazio...")
    df = df[df["CPF do cliente"].notna() & (df["CPF do cliente"] != "")]
    print(f"Número de tuplas/atributos após filtro de CPF: {df.shape}")

    # 4. Remover linhas com 'Nome do cliente' nulo ou vazio
    print("Removendo registros com 'Nome do cliente' nulo ou vazio...")
    df = df[df["Nome do cliente"].notna() & (df["Nome do cliente"] != "")]
    print(f"Número final de tuplas/atributos: {df.shape}")
    
    print("Transformações concluídas.")
    return df

def carregar_dados(df, caminho_saida):
    """
    Salva o DataFrame tratado em um novo arquivo CSV.
    """
    if df is None:
        print("Nenhum dado para salvar.")
        return

    print(f"Salvando arquivo tratado em: {caminho_saida}")
    try:
        df.to_csv(caminho_saida, index=False, encoding="utf-8")
        print(f"✅ Novo arquivo salvo com sucesso como {caminho_saida}")
        
        # A linha abaixo é específica do Google Colab e foi comentada.
        # files.download(output_file)
        
    except Exception as e:
        print(f"Ocorreu um erro ao salvar o arquivo: {e}")

def main():
    """
    Orquestra o processo de ETL.
    """
    arquivo_entrada = 'clientes_compras_grupo_1.csv'
    arquivo_saida = 'cliente_compras_grupo_1_tratado.csv'

    # Extração
    df = extrair_dados(arquivo_entrada)
    
    # Transformação
    df_tratado = transformar_dados(df)
    
    # Carga
    carregar_dados(df_tratado, arquivo_saida)

if __name__ == "__main__":
    main()