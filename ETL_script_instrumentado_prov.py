#!/usr/bin/env python
# coding: utf-8

# # Script ETL - Tratamento de Dados de Clientes e Compras
# 
# Este script converte o notebook 'ETL.ipynb' para um arquivo Python executável.
# Ele lê um arquivo CSV, aplica várias transformações de limpeza de dados
# e salva o resultado em um novo arquivo CSV.

import pandas as pd
import prov.model as prov

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
    # --- CONFIGURAÇÃO INICIAL DE PROVENIÊNCIA ---
    d = prov.ProvDocument()
    d.add_namespace('ex', 'http://example.org/')
    a_script = d.agent('ex:etl_script.py', {'prov:type': 'prov:SoftwareAgent'})

    # --- Definição das variáveis de arquivo
    arquivo_entrada = 'clientes_compras_grupo_1.csv'
    arquivo_saida = 'cliente_compras_grupo_1_tratado.csv'

    # =======================================================
    # === FASE 1: Extração (Extract)
    # =======================================================
    df = extrair_dados(arquivo_entrada)

    # --- Captura de Proveniência (Fase 1) ---
    if df is not None:
        a_extract = d.activity('ex:extrair_dados')
        d.wasAssociatedWith(a_extract, a_script)

        e_input_file = d.entity('ex:arquivo_entrada', {'prov:location': arquivo_entrada})
        
        e_raw_df = d.entity('ex:dataframe_bruto', {
            'ex:shape': str(df.shape),
            'ex:columns': str(df.columns.tolist()) # Regra Crítica: Converte lista para string
        })
        
        a_extract.used(e_input_file)
        d.wasGeneratedBy(e_raw_df, a_extract)
    
    # =======================================================
    # === FASE 2: Transformação (Transform)
    # =======================================================
    df_tratado = transformar_dados(df)
    
    # --- Captura de Proveniência (Fase 2) ---
    if df_tratado is not None:
        a_transform = d.activity('ex:transformar_dados')
        d.wasAssociatedWith(a_transform, a_script)
        
        # Entidade para as regras de transformação (parâmetros)
        e_rules = d.entity('ex:regras_transformacao', {
            'ex:correcao_uf': str({"Rio de Janeiro": "RJ", "Fortaleza": "CE"}),
            'ex:filtro_cpf': 'CPF do cliente notna and not empty',
            'ex:filtro_nome': 'Nome do cliente notna and not empty'
        })

        e_transformed_df = d.entity('ex:dataframe_tratado', {
            'ex:shape': str(df_tratado.shape),
            'ex:columns': str(df_tratado.columns.tolist()) # Regra Crítica: Converte lista para string
        })
        
        a_transform.used(e_raw_df)
        a_transform.used(e_rules)
        d.wasGeneratedBy(e_transformed_df, a_transform)

    # =======================================================
    # === FASE 3: Carga (Load)
    # =======================================================
    carregar_dados(df_tratado, arquivo_saida)
    
    # --- Captura de Proveniência (Fase 3) ---
    if df_tratado is not None:
        a_load = d.activity('ex:carregar_dados')
        d.wasAssociatedWith(a_load, a_script)
        
        e_output_file = d.entity('ex:arquivo_saida', {'prov:location': arquivo_saida})
        
        a_load.used(e_transformed_df)
        d.wasGeneratedBy(e_output_file, a_load)
        
    # =======================================================
    # === SALVANDO O GRAFO DE PROVENIÊNCIA
    # =======================================================
    try:
        d.serialize('provenance.json', format='json')
        print("Grafo de Proveniência (W3C-PROV) salvo em 'provenance.json'.")
    except Exception as e:
        print(f"Erro ao salvar o grafo de proveniência: {e}")


if __name__ == "__main__":
    main()