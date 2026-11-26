#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import prov.model as prov
import json
from datetime import datetime, timezone

def extrair_dados(caminho_arquivo, d, a_script):
    """
    Carrega os dados do arquivo CSV inicial.
    """
    print(f"Iniciando a leitura do arquivo: {caminho_arquivo}")
    t_start = datetime.now(timezone.utc)
    try:
        df = pd.read_csv(caminho_arquivo, encoding="utf-8", delimiter=";")
        t_end = datetime.now(timezone.utc)
        print(f"Número de tuplas/atributos inicial: {df.shape}")
        
        e_caminho = d.entity('ex:caminho_entrada_v1', {'prov:value': caminho_arquivo})
        act_read = d.activity('ex:extrair_dados', startTime=t_start, endTime=t_end)
        d.wasAssociatedWith(act_read, a_script)
        d.used(act_read, e_caminho)
        
        e_df = d.entity('ex:df_v1', {'prov:type': 'pandas.DataFrame', 'shape': str(df.shape)})
        d.wasGeneratedBy(e_df, act_read)
        d.wasDerivedFrom(e_df, e_caminho)
        
        return df, e_df
    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        print("Por favor, coloque o arquivo no mesmo diretório do script.")
        return None, None
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao ler o arquivo: {e}")
        return None, None

def transformar_dados(df, e_df, d, a_script):
    """
    Aplica as regras de limpeza e transformação no DataFrame.
    """
    if df is None:
        return None, None

    print("Iniciando transformações...")

    # 1. Corrigir coluna 'UF' com base no 'Município'
    print("Corrigindo 'UF' com base no 'Município'...")
    t_start = datetime.now(timezone.utc)
    correcoes_estado = {
        "Rio de Janeiro": "RJ",
        "Fortaleza": "CE",
    }
    df['UF'] = df['Município'].map(correcoes_estado).fillna(df['UF'])
    t_end = datetime.now(timezone.utc)

    act_t1 = d.activity('ex:corrigir_uf', startTime=t_start, endTime=t_end)
    d.wasAssociatedWith(act_t1, a_script)
    d.used(act_t1, e_df)
    
    e_correcoes = d.entity('ex:correcoes_estado_v1', {'prov:value': json.dumps(correcoes_estado)})
    d.used(act_t1, e_correcoes)
    
    e_df2 = d.entity('ex:df_v2', {'prov:type': 'pandas.DataFrame', 'shape': str(df.shape)})
    d.wasGeneratedBy(e_df2, act_t1)
    d.wasDerivedFrom(e_df2, e_df)

    # 2. Recalcular 'Valor total pago'
    print("Recalculando 'Valor total pago'...")
    t_start = datetime.now(timezone.utc)
    df['Valor total pago'] = (df['Preço unitário'] * df['Quantidade comprada']) + df['Taxa de entrega']
    t_end = datetime.now(timezone.utc)

    act_t2 = d.activity('ex:recalcular_valor_total', startTime=t_start, endTime=t_end)
    d.wasAssociatedWith(act_t2, a_script)
    d.used(act_t2, e_df2)
    
    e_df3 = d.entity('ex:df_v3', {'prov:type': 'pandas.DataFrame', 'shape': str(df.shape)})
    d.wasGeneratedBy(e_df3, act_t2)
    d.wasDerivedFrom(e_df3, e_df2)

    # 3. Remover linhas com 'CPF do cliente' nulo ou vazio
    print("Removendo registros com 'CPF do cliente' nulo ou vazio...")
    t_start = datetime.now(timezone.utc)
    df = df[df["CPF do cliente"].notna() & (df["CPF do cliente"] != "")]
    t_end = datetime.now(timezone.utc)
    print(f"Número de tuplas/atributos após filtro de CPF: {df.shape}")

    act_t3 = d.activity('ex:filtrar_cpf', startTime=t_start, endTime=t_end)
    d.wasAssociatedWith(act_t3, a_script)
    d.used(act_t3, e_df3)
    
    e_df4 = d.entity('ex:df_v4', {'prov:type': 'pandas.DataFrame', 'shape': str(df.shape)})
    d.wasGeneratedBy(e_df4, act_t3)
    d.wasDerivedFrom(e_df4, e_df3)

    # 4. Remover linhas com 'Nome do cliente' nulo ou vazio
    print("Removendo registros com 'Nome do cliente' nulo ou vazio...")
    t_start = datetime.now(timezone.utc)
    df = df[df["Nome do cliente"].notna() & (df["Nome do cliente"] != "")]
    t_end = datetime.now(timezone.utc)
    print(f"Número final de tuplas/atributos: {df.shape}")

    act_t4 = d.activity('ex:filtrar_nome', startTime=t_start, endTime=t_end)
    d.wasAssociatedWith(act_t4, a_script)
    d.used(act_t4, e_df4)
    
    e_df5 = d.entity('ex:df_v5', {'prov:type': 'pandas.DataFrame', 'shape': str(df.shape)})
    d.wasGeneratedBy(e_df5, act_t4)
    d.wasDerivedFrom(e_df5, e_df4)
    
    print("Transformações concluídas.")
    return df, e_df5

def carregar_dados(df, e_df, caminho_saida, d, a_script):
    """
    Salva o DataFrame tratado em um novo arquivo CSV.
    """
    if df is None:
        print("Nenhum dado para salvar.")
        return

    print(f"Salvando arquivo tratado em: {caminho_saida}")
    t_start = datetime.now(timezone.utc)
    try:
        df.to_csv(caminho_saida, index=False, encoding="utf-8")
        t_end = datetime.now(timezone.utc)
        print(f"✅ Novo arquivo salvo com sucesso como {caminho_saida}")
        
        e_saida = d.entity('ex:caminho_saida_v1', {'prov:value': caminho_saida})
        act_load = d.activity('ex:carregar_dados', startTime=t_start, endTime=t_end)
        d.wasAssociatedWith(act_load, a_script)
        d.used(act_load, e_df)
        d.used(act_load, e_saida)
        
        e_arquivo = d.entity('ex:arquivo_tratado_v1', {'prov:type': 'File', 'path': caminho_saida})
        d.wasGeneratedBy(e_arquivo, act_load)
        d.wasDerivedFrom(e_arquivo, e_df)
        
    except Exception as e:
        print(f"Ocorreu um erro ao salvar o arquivo: {e}")

def main():
    """
    Orquestra o processo de ETL.
    """
    d = prov.ProvDocument()
    d.add_namespace('ex', 'http://example.org/')
    a_script = d.agent('ex:script_executor')

    arquivo_entrada = 'clientes_compras_grupo_1.csv'
    arquivo_saida = 'cliente_compras_grupo_1_tratado.csv'

    # Extração
    df, e_df = extrair_dados(arquivo_entrada, d, a_script)
    
    if df is not None:
        # Transformação
        df_tratado, e_df_tratado = transformar_dados(df, e_df, d, a_script)
        
        # Carga
        carregar_dados(df_tratado, e_df_tratado, arquivo_saida, d, a_script)
    
    d.serialize('provenance_w3c.json', format='json')

if __name__ == "__main__":
    main()