import pandas as pd
import prov.model as prov
import os

# --- CONFIGURAÇÃO INICIAL DE PROVENIÊNCIA ---
d = prov.ProvDocument()
d.add_namespace('ex', 'http://example.org/')
# Define o próprio script como o Agente
script_name = os.path.basename(__file__) if '__file__' in locals() else 'etl_script.py'
a_script = d.agent(f'ex:{script_name}')

# Simulação das funções ausentes para tornar o script executável
def extrair_dados(caminho):
    """
    Extrai dados de um arquivo CSV.
    Cria um DataFrame de exemplo se o arquivo não existir.
    """
    print(f'Lendo dados de: {caminho}')
    try:
        df = pd.read_csv(caminho)
        print(f'✅ {len(df)} linhas lidas de {caminho}')
        return df
    except FileNotFoundError:
        print(f'Arquivo {caminho} não encontrado. Criando dados de exemplo.')
        data = {
            'cliente_id': [1, 2, 1, 3, 2, 4, 3, None],
            'produto_id': ['A', 'B', 'A', 'C', 'B', 'D', 'A', 'E'],
            'quantidade': [10, 5, 10, 2, 5, 1, 3, 8],
            'preco_unitario': [2.5, 10.0, 2.5, 5.0, 10.0, 15.0, 2.5, 1.0]
        }
        df = pd.DataFrame(data)
        # Salva o arquivo de exemplo para a próxima execução
        df.to_csv(caminho, index=False)
        print(f'✅ Arquivo de exemplo {caminho} criado e carregado.')
        return df

def transformar_dados(df):
    """
    Aplica transformações ao DataFrame.
    """
    if df is None:
        return None
    print('Iniciando transformação dos dados...')
    df_tratado = df.copy()
    # 1. Remove linhas com valores nulos
    linhas_antes = len(df_tratado)
    df_tratado.dropna(inplace=True)
    linhas_depois_na = len(df_tratado)
    print(f'  - {linhas_antes - linhas_depois_na} linhas com valores nulos removidas.')
    # 2. Remove duplicatas
    linhas_antes = len(df_tratado)
    df_tratado.drop_duplicates(inplace=True)
    linhas_depois_dup = len(df_tratado)
    print(f'  - {linhas_antes - linhas_depois_dup} linhas duplicadas removidas.')
    # 3. Cria uma nova coluna 'valor_total'
    df_tratado['valor_total'] = df_tratado['quantidade'] * df_tratado['preco_unitario']
    print("  - Coluna 'valor_total' criada.")
    # 4. Converte tipo da coluna para inteiro
    df_tratado['cliente_id'] = df_tratado['cliente_id'].astype(int)
    print("  - Coluna 'cliente_id' convertida para inteiro.")
    print('✅ Transformação concluída.')
    return df_tratado

def carregar_dados(df, caminho_saida):
    """
    Salva o DataFrame tratado em um novo arquivo CSV.
    """
    if df is None:
        print('Nenhum dado para salvar.')
        return
    print(f'Salvando arquivo tratado em: {caminho_saida}')
    try:
        df.to_csv(caminho_saida, index=False, encoding='utf-8')
        print(f'✅ Novo arquivo salvo com sucesso como {caminho_saida}')
    except Exception as e:
        print(f'Ocorreu um erro ao salvar o arquivo: {e}')

def main():
    """
    Orquestra o processo de ETL e a captura de proveniência.
    """
    arquivo_entrada = 'clientes_compras_grupo_1.csv'
    arquivo_saida = 'cliente_compras_grupo_1_tratado.csv'

    # =======================================================
    # === FASE 1: Extrair Dados (Extract)
    # =======================================================
    # --- Proveniência (Antes) ---
    act_extract = d.activity('ex:extrair_dados_csv')
    d.wasAssociatedWith(act_extract, a_script)
    e_input_file = d.entity('ex:arquivo_entrada', {'prov:location': arquivo_entrada, 'ex:format': 'csv'})
    act_extract.used(e_input_file)

    # --- Código Original ---
    df = extrair_dados(arquivo_entrada)

    # --- Proveniência (Depois) ---
    if df is not None:
        e_raw_df = d.entity('ex:dataframe_bruto', {
            'ex:rows': df.shape[0],
            'ex:columns': df.shape[1],
            'ex:column_names': str(df.columns.tolist()) # REGRA CRÍTICA DE ATRIBUTOS
        })
        d.wasGeneratedBy(e_raw_df, act_extract)
    else:
        e_raw_df = None # Para evitar erro se a extração falhar

    # =======================================================
    # === FASE 2: Transformar Dados (Transform)
    # =======================================================
    # --- Proveniência (Antes) ---
    act_transform = d.activity('ex:transformar_dados')
    d.wasAssociatedWith(act_transform, a_script)
    if e_raw_df:
        act_transform.used(e_raw_df)
    
    # --- Atributos da Atividade (parâmetros da transformação)
    act_transform.add_attributes({
        'ex:transformations': str(['dropna', 'drop_duplicates', 'add_valor_total', 'cast_cliente_id_int'])
    })

    # --- Código Original ---
    df_tratado = transformar_dados(df)

    # --- Proveniência (Depois) ---
    if df_tratado is not None:
        e_treated_df = d.entity('ex:dataframe_tratado', {
            'ex:rows': df_tratado.shape[0],
            'ex:columns': df_tratado.shape[1],
            'ex:column_names': str(df_tratado.columns.tolist())
        })
        d.wasGeneratedBy(e_treated_df, act_transform)
    else:
        e_treated_df = None

    # =======================================================
    # === FASE 3: Carregar Dados (Load)
    # =======================================================
    # --- Proveniência (Antes) ---
    act_load = d.activity('ex:carregar_dados_csv')
    d.wasAssociatedWith(act_load, a_script)
    if e_treated_df:
        act_load.used(e_treated_df)

    # --- Código Original ---
    carregar_dados(df_tratado, arquivo_saida)

    # --- Proveniência (Depois) ---
    e_output_file = d.entity('ex:arquivo_saida', {'prov:location': arquivo_saida, 'ex:format': 'csv'})
    d.wasGeneratedBy(e_output_file, act_load)

if __name__ == '__main__':
    main()
    # =======================================================
    # === SALVANDO O GRAFO DE PROVENIÊNCIA
    # =======================================================
    try:
        d.serialize('provenance_w3c.json', format='json')
        print("\nGrafo de Proveniência (W3C-PROV) salvo em 'provenance_w3c.json'.")
    except Exception as e:
        print(f"Erro ao salvar o grafo de proveniência: {e}")