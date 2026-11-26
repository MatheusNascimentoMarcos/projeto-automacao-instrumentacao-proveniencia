#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import prov.model as prov
import json
from datetime import datetime, timezone

# Inicialização Global da Proveniência (W3C-PROV)
d = prov.ProvDocument()
d.add_namespace('ex', 'http://example.org/')
a_script = d.agent('ex:script_executor')
_step = 0

def extrair_dados(caminho_arquivo, e_caminho_arquivo):
    """
    Carrega os dados do arquivo CSV inicial.
    """
    global _step, d, a_script
    print(f"Iniciando a leitura do arquivo: {caminho_arquivo}")
    try:
        _step += 1
        t_start = datetime.now(timezone.utc)
        df = pd.read_csv(caminho_arquivo, encoding="utf-8", delimiter=";")
        t_end = datetime.now(timezone.utc)
        
        act_read = d.activity(f'ex:read_csv_{_step}', startTime=t_start, endTime=t_end)
        d.wasAssociatedWith(act_read, a_script)
        d.used(act_read, e_caminho_arquivo)
        
        e_df = d.entity(f'ex:df_v{_step}', {'prov:type': 'DataFrame', 'shape': str(df.shape)})
        d.wasGeneratedBy(e_df, act_read)
        d.wasDerivedFrom(e_df, e_caminho_arquivo)

        print(f"Número de tuplas/atributos inicial: {df.shape}")
        return df, e_df
    
    except FileNotFoundError as e:
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        print("Por favor, coloque o arquivo no mesmo diretório do script.")
        return None, None
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao ler o arquivo: {e}")
        return None, None

def transformar_dados(df, e_df):
    """
    Aplica as regras de limpeza e transformação no DataFrame.
    """
    global _step, d, a_script
    if df is None:
        return None, e_df

    print("Iniciando transformações...")
    e_df_curr = e_df

    # 1. Corrigir coluna 'UF' com base no 'Município'
    print("Corrigindo 'UF' com base no 'Município'...")
    _step += 1
    t_start = datetime.now(timezone.utc)
    correcoes_estado = {
        "Rio de Janeiro": "RJ",
        "Fortaleza": "CE",
    }
    df['UF'] = df['Município'].map(correcoes_estado).fillna(df['UF'])
    t_end = datetime.now(timezone.utc)

    act_t1 = d.activity(f'ex:transform_uf_{_step}', startTime=t_start, endTime=t_end)
    d.wasAssociatedWith(act_t1, a_script)
    
    e_correcoes = d.entity(f'ex:correcoes_estado_v{_step}', {'prov:value': json.dumps(correcoes_estado)})
    d.wasGeneratedBy(e_correcoes, act_t1)
    
    d.used(act_t1, e_df_curr)
    d.used(act_t1, e_correcoes)

    e_df_next = d.entity(f'ex:df_v{_step}', {'prov:type': 'DataFrame', 'shape': str(df.shape)})
    d.wasGeneratedBy(e_df_next, act_t1)
    d.wasDerivedFrom(e_df_next, e_df_curr)
    d.wasDerivedFrom(e_df_next, e_correcoes)
    
    e_df_curr = e_df_next

    # 2. Recalcular 'Valor total pago'
    print("Recalculando 'Valor total pago'...")
    _step += 1
    t_start = datetime.now(timezone.utc)
    df['Valor total pago'] = (df['Preço unitário'] * df['Quantidade comprada']) + df['Taxa de entrega']
    t_end = datetime.now(timezone.utc)

    act_t2 = d.activity(f'ex:calc_total_{_step}', startTime=t_start, endTime=t_end)
    d.wasAssociatedWith(act_t2, a_script)
    d.used(act_t2, e_df_curr)

    e_df_next = d.entity(f'ex:df_v{_step}', {'prov:type': 'DataFrame', 'shape': str(df.shape)})
    d.wasGeneratedBy(e_df_next, act_t2)
    d.wasDerivedFrom(e_df_next, e_df_curr)
    
    e_df_curr = e_df_next

    # 3. Remover linhas com 'CPF do cliente' nulo ou vazio
    print("Removendo registros com 'CPF do cliente' nulo ou vazio...")
    _step += 1
    t_start = datetime.now(timezone.utc)
    df = df[df["CPF do cliente"].notna() & (df["CPF do cliente"] != "")]
    t_end = datetime.now(timezone.utc)

    act_t3 = d.activity(f'ex:filter_cpf_{_step}', startTime=t_start, endTime=t_end)
    d.wasAssociatedWith(act_t3, a_script)
    d.used(act_t3, e_df_curr)

    e_df_next = d.entity(f'ex:df_v{_step}', {'prov:type': 'DataFrame', 'shape': str(df.shape)})
    d.wasGeneratedBy(e_df_next, act_t3)
    d.wasDerivedFrom(e_df_next, e_df_curr)
    
    e_df_curr = e_df_next
    print(f"Número de tuplas/atributos após filtro de CPF: {df.shape}")

    # 4. Remover linhas com 'Nome do cliente' nulo ou vazio
    print("Removendo registros com 'Nome do cliente' nulo ou vazio...")
    _step += 1
    t_start = datetime.now(timezone.utc)
    df = df[df["Nome do cliente"].notna() & (df["Nome do cliente"] != "")]
    t_end = datetime.now(timezone.utc)

    act_t4 = d.activity(f'ex:filter_nome_{_step}', startTime=t_start, endTime=t_end)
    d.wasAssociatedWith(act_t4, a_script)
    d.used(act_t4, e_df_curr)

    e_df_next = d.entity(f'ex:df_v{_step}', {'prov:type': 'DataFrame', 'shape': str(df.shape)})
    d.wasGeneratedBy(e_df_next, act_t4)
    d.wasDerivedFrom(e_df_next, e_df_curr)
    
    e_df_curr = e_df_next
    print(f"Número final de tuplas/atributos: {df.shape}")
    
    print("Transformações concluídas.")
    return df, e_df_curr

def carregar_dados(df, e_df, caminho_saida, e_caminho_saida):
    """
    Salva o DataFrame tratado em um novo arquivo CSV.
    """
    global _step, d, a_script
    if df is None:
        print("Nenhum dado para salvar.")
        return

    print(f"Salvando arquivo tratado em: {caminho_saida}")
    try:
        _step += 1
        t_start = datetime.now(timezone.utc)
        df.to_csv(caminho_saida, index=False, encoding="utf-8")
        t_end = datetime.now(timezone.utc)

        act_save = d.activity(f'ex:save_csv_{_step}', startTime=t_start, endTime=t_end)
        d.wasAssociatedWith(act_save, a_script)
        d.used(act_save, e_df)
        d.used(act_save, e_caminho_saida)

        e_file_out = d.entity(f'ex:arquivo_gerado_{_step}', {'prov:type': 'File', 'path': caminho_saida})
        d.wasGeneratedBy(e_file_out, act_save)
        d.wasDerivedFrom(e_file_out, e_df)

        print(f"✅ Novo arquivo salvo com sucesso como {caminho_saida}")
        
    except Exception as e:
        print(f"Ocorreu um erro ao salvar o arquivo: {e}")

def main():
    """
    Orquestra o processo de ETL.
    """
    global _step, d, a_script
    
    # Inicialização de Variáveis de Caminho
    _step += 1
    t_start = datetime.now(timezone.utc)
    arquivo_entrada = 'clientes_compras_grupo_1.csv'
    t_end = datetime.now(timezone.utc)
    
    act_init_in = d.activity(f'ex:init_arquivo_entrada_{_step}', startTime=t_start, endTime=t_end)
    d.wasAssociatedWith(act_init_in, a_script)
    e_arq_in = d.entity(f'ex:arquivo_entrada_v{_step}', {'prov:value': arquivo_entrada})
    d.wasGeneratedBy(e_arq_in, act_init_in)

    _step += 1
    t_start = datetime.now(timezone.utc)
    arquivo_saida = 'cliente_compras_grupo_1_tratado.csv'
    t_end = datetime.now(timezone.utc)
    
    act_init_out = d.activity(f'ex:init_arquivo_saida_{_step}', startTime=t_start, endTime=t_end)
    d.wasAssociatedWith(act_init_out, a_script)
    e_arq_out = d.entity(f'ex:arquivo_saida_v{_step}', {'prov:value': arquivo_saida})
    d.wasGeneratedBy(e_arq_out, act_init_out)

    # Extração
    df, e_df = extrair_dados(arquivo_entrada, e_arq_in)
    
    # Transformação
    df_tratado, e_df_tratado = transformar_dados(df, e_df)
    
    # Carga
    carregar_dados(df_tratado, e_df_tratado, arquivo_saida, e_arq_out)

    # Serialização da Proveniência
    d.serialize('provenance_w3c.json', format='json')

if __name__ == "__main__":
    main()