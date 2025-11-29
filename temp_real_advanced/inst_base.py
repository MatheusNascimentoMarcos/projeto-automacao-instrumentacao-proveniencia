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
    Orquestra o processo de ETL e captura a proveniência.
    """
    # --- CONFIGURAÇÃO INICIAL DE PROVENIÊNCIA ---
    d = prov.ProvDocument()
    d.add_namespace('ex', 'http://example.org/etl_workflow/')
    a_script = d.agent('ex:etl_script.py', {'prov:type': 'prov:SoftwareAgent'})

    arquivo_entrada = 'clientes_compras_grupo_1.csv'
    arquivo_saida = 'cliente_compras_grupo_1_tratado.csv'

    # --- PROV: Entidade do arquivo de entrada ---
    e_input_file = d.entity('ex:input_csv', {
        'prov:location': arquivo_entrada,
        'ex:format': 'text/csv',
        'ex:delimiter': ';'
    })

    # =======================================================
    # === ETAPA 1: Extração
    # =======================================================
    df = extrair_dados(arquivo_entrada)
    
    if df is not None:
        # --- PROV: Captura da atividade de extração ---
        a_extract = d.activity('ex:extrair_dados')
        d.wasAssociatedWith(a_extract, a_script)
        
        # PROV: Entidade para o DataFrame bruto em memória
        initial_shape = df.shape
        # Converte a lista de colunas para string, conforme a regra
        initial_cols_str = str(df.columns.tolist())
        e_raw_df = d.entity('ex:raw_dataframe', {
            'ex:rows': initial_shape[0],
            'ex:columns': initial_shape[1],
            'ex:column_names': initial_cols_str
        })
        
        # PROV: Links para a extração
        a_extract.used(e_input_file)
        d.wasGeneratedBy(e_raw_df, a_extract)

        # =======================================================
        # === ETAPA 2: Transformação
        # =======================================================
        df_tratado = transformar_dados(df)
        
        if df_tratado is not None:
            # --- PROV: Captura da atividade de transformação ---
            # Atributos descrevem as operações realizadas
            transformation_steps = [
                "correct_UF_based_on_municipio",
                "recalculate_total_paid",
                "filter_null_cpf",
                "filter_null_name"
            ]
            a_transform = d.activity('ex:transformar_dados', other_attributes={
                'ex:steps_count': len(transformation_steps),
                'ex:steps_list': str(transformation_steps) # Converte lista para string
            })
            d.wasAssociatedWith(a_transform, a_script)
            
            # PROV: Entidade para o DataFrame tratado
            final_shape = df_tratado.shape
            final_cols_str = str(df_tratado.columns.tolist())
            e_transformed_df = d.entity('ex:transformed_dataframe', {
                'ex:rows': final_shape[0],
                'ex:columns': final_shape[1],
                'ex:column_names': final_cols_str
            })

            # PROV: Links para a transformação
            a_transform.used(e_raw_df)
            d.wasGeneratedBy(e_transformed_df, a_transform)

            # =======================================================
            # === ETAPA 3: Carga
            # =======================================================
            carregar_dados(df_tratado, arquivo_saida)
            
            # --- PROV: Captura da atividade de carga/salvamento ---
            a_load = d.activity('ex:carregar_dados')
            d.wasAssociatedWith(a_load, a_script)
            
            # PROV: Entidade para o arquivo de saída
            e_output_file = d.entity('ex:output_csv', {
                'prov:location': arquivo_saida,
                'ex:format': 'text/csv'
            })
            
            # PROV: Links para a carga
            a_load.used(e_transformed_df)
            d.wasGeneratedBy(e_output_file, a_load)

    # =======================================================
    # === SALVANDO O GRAFO DE PROVENIÊNCIA
    # =======================================================
    try:
        d.serialize('provenance_w3c.json', format='json')
        print("\nGrafo de Proveniência (W3C-PROV) salvo em 'provenance_w3c.json'.")
    except Exception as e:
        print(f"\nErro ao salvar o grafo de proveniência: {e}")


if __name__ == "__main__":
    main()