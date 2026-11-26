#!/usr/bin/env python
# coding: utf-8

# # Script ETL - Tratamento de Dados de Clientes e Compras
# 
# Este script converte o notebook 'ETL.ipynb' para um arquivo Python executável.
# Ele lê um arquivo CSV, aplica várias transformações de limpeza de dados
# e salva o resultado em um novo arquivo CSV.

import pandas as pd
import prov.model as prov
import json
from datetime import datetime, timezone

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
        
    except Exception as e:
        print(f"Ocorreu um erro ao salvar o arquivo: {e}")

def main():
    """
    Orquestra o processo de ETL com captura de proveniência em granularidade grossa.
    """
    d = prov.ProvDocument()
    d.add_namespace('ex', 'http://example.org/')
    a_script = d.agent('ex:script_executor')

    arquivo_entrada = 'clientes_compras_grupo_1.csv'
    arquivo_saida = 'cliente_compras_grupo_1_tratado.csv'

    # Etapa Macro 1: Extração
    t_start = datetime.now(timezone.utc)
    df = extrair_dados(arquivo_entrada)
    t_end = datetime.now(timezone.utc)
    
    act_ext = d.activity('ex:extrair_dados', startTime=t_start, endTime=t_end)
    d.wasAssociatedWith(act_ext, a_script)
    e_in = d.entity('ex:arquivo_entrada', {'prov:location': arquivo_entrada})
    d.used(act_ext, e_in)
    
    if df is not None:
        e_df_raw = d.entity('ex:df_bruto', {'ex:shape': str(df.shape)})
        d.wasGeneratedBy(e_df_raw, act_ext)
        d.wasDerivedFrom(e_df_raw, e_in)

    # Etapa Macro 2: Transformação
    t_start = datetime.now(timezone.utc)
    df_tratado = transformar_dados(df)
    t_end = datetime.now(timezone.utc)
    
    act_transf = d.activity('ex:transformar_dados', startTime=t_start, endTime=t_end)
    d.wasAssociatedWith(act_transf, a_script)
    
    if df is not None:
        d.used(act_transf, e_df_raw)
        
    if df_tratado is not None:
        e_df_tratado = d.entity('ex:df_tratado', {'ex:shape': str(df_tratado.shape)})
        d.wasGeneratedBy(e_df_tratado, act_transf)
        if df is not None:
            d.wasDerivedFrom(e_df_tratado, e_df_raw)
    
    # Etapa Macro 3: Carga
    t_start = datetime.now(timezone.utc)
    carregar_dados(df_tratado, arquivo_saida)
    t_end = datetime.now(timezone.utc)
    
    act_load = d.activity('ex:carregar_dados', startTime=t_start, endTime=t_end)
    d.wasAssociatedWith(act_load, a_script)
    
    if df_tratado is not None:
        d.used(act_load, e_df_tratado)
        e_out = d.entity('ex:arquivo_saida', {'prov:location': arquivo_saida})
        d.wasGeneratedBy(e_out, act_load)
        d.wasDerivedFrom(e_out, e_df_tratado)

    d.serialize('provenance_w3c.json', format='json')

if __name__ == "__main__":
    main()