import pandas as pd
import prov.model as prov

def extrair_dados(caminho_arquivo, d, a_script):
    """
    Carrega os dados do arquivo CSV inicial e captura a proveniência da extração.
    """
    print(f'Iniciando a leitura do arquivo: {caminho_arquivo}')
    
    # --- Captura de Proveniência (Entidade de Entrada) ---
    e_input_file = d.entity('ex:arquivo_entrada', {'prov:location': caminho_arquivo})
    
    # --- Atividade de Extração ---
    a_extract = d.activity('ex:extrair_dados')
    d.wasAssociatedWith(a_extract, a_script)
    a_extract.used(e_input_file)
    
    try:
        df = pd.read_csv(caminho_arquivo, encoding='utf-8', delimiter=';')
        print(f'Número de tuplas/atributos inicial: {df.shape}')
        
        # --- Captura de Proveniência (Entidade Gerada) ---
        e_raw_df = d.entity('ex:dataframe_bruto', {
            'ex:shape': str(df.shape),
            'ex:columns': str(df.columns.tolist()) # Regra Crítica: Converte lista para string
        })
        d.wasGeneratedBy(e_raw_df, a_extract)
        
        return df, e_raw_df
        
    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        print('Por favor, coloque o arquivo no mesmo diretório do script.')
        # Registra a falha na atividade
        a_extract.add_attributes({'ex:status': 'falha', 'ex:erro': 'FileNotFoundError'})
        return None, None
    except Exception as e:
        print(f'Ocorreu um erro inesperado ao ler o arquivo: {e}')
        # Registra a falha na atividade
        a_extract.add_attributes({'ex:status': 'falha', 'ex:erro': str(e)})
        return None, None

def transformar_dados(df, e_raw_df, d, a_script):
    """
    Aplica as regras de limpeza e transformação no DataFrame e captura a proveniência.
    """
    if df is None:
        return None, None
        
    print('Iniciando transformações...')
    
    # --- Atividade de Transformação ---
    a_transform = d.activity('ex:transformar_dados', other_attributes={
        'ex:passo_1': "Corrigir 'UF' com base no 'Município'",
        'ex:passo_2': "Recalcular 'Valor total pago'",
        'ex:passo_3': "Remover registros com 'CPF do cliente' nulo",
        'ex:passo_4': "Remover registros com 'Nome do cliente' nulo"
    })
    d.wasAssociatedWith(a_transform, a_script)
    a_transform.used(e_raw_df)

    # --- Lógica de Transformação Original ---
    print("Corrigindo 'UF' com base no 'Município'...")
    correcoes_estado = {'Rio de Janeiro': 'RJ', 'Fortaleza': 'CE'}
    df['UF'] = df['Município'].map(correcoes_estado).fillna(df['UF'])
    
    print("Recalculando 'Valor total pago'...")
    df['Valor total pago'] = df['Taxa de entrega'] + df['Quantidade comprada'] * df['Preço unitário']
    
    print("Removendo registros com 'CPF do cliente' nulo ou vazio...")
    df = df[df['CPF do cliente'].notna() & ('' != df['CPF do cliente'])]
    print(f'Número de tuplas/atributos após filtro de CPF: {df.shape}')
    
    print("Removendo registros com 'Nome do cliente' nulo ou vazio...")
    df = df[df['Nome do cliente'].notna() & ('' != df['Nome do cliente'])]
    print(f'Número final de tuplas/atributos: {df.shape}')
    print('Transformações concluídas.')
    
    # --- Captura de Proveniência (Entidade Gerada) ---
    e_transformed_df = d.entity('ex:dataframe_tratado', {
        'ex:shape': str(df.shape),
        'ex:columns': str(df.columns.tolist()) # Regra Crítica: Converte lista para string
    })
    d.wasGeneratedBy(e_transformed_df, a_transform)
    
    return df, e_transformed_df

def carregar_dados(df, e_transformed_df, caminho_saida, d, a_script):
    """
    Salva o DataFrame tratado em um novo arquivo CSV e captura a proveniência.
    """
    if df is None:
        print('Nenhum dado para salvar.')
        return
        
    print(f'Salvando arquivo tratado em: {caminho_saida}')
    
    # --- Atividade de Carga/Salvamento ---
    a_load = d.activity('ex:carregar_dados')
    d.wasAssociatedWith(a_load, a_script)
    a_load.used(e_transformed_df)
    
    # --- Entidade de Saída ---
    e_output_file = d.entity('ex:arquivo_saida', {'prov:location': caminho_saida})
    d.wasGeneratedBy(e_output_file, a_load)
    
    try:
        df.to_csv(caminho_saida, index=False, encoding='utf-8')
        print(f'✅ Novo arquivo salvo com sucesso como {caminho_saida}')
        a_load.add_attributes({'ex:status': 'sucesso'})
    except Exception as e:
        print(f'Ocorreu um erro ao salvar o arquivo: {e}')
        a_load.add_attributes({'ex:status': 'falha', 'ex:erro': str(e)})

def main():
    """
    Orquestra o processo de ETL e a captura de proveniência.
    """
    # --- CONFIGURAÇÃO INICIAL DE PROVENIÊNCIA ---
    d = prov.ProvDocument()
    d.add_namespace('ex', 'http://example.org/etl_workflow')
    a_script = d.agent('ex:etl_script.py', {'prov:type': 'prov:SoftwareAgent'})

    # --- Execução do Workflow ---
    arquivo_entrada = 'clientes_compras_grupo_1.csv'
    arquivo_saida = 'cliente_compras_grupo_1_tratado.csv'
    
    df, e_raw_df = extrair_dados(arquivo_entrada, d, a_script)
    
    if df is not None:
        df_tratado, e_transformed_df = transformar_dados(df, e_raw_df, d, a_script)
        carregar_dados(df_tratado, e_transformed_df, arquivo_saida, d, a_script)
    
    # --- SALVANDO O GRAFO DE PROVENIÊNCIA ---
    try:
        d.serialize('provenance_w3c.json', format='json')
        print("Grafo de Proveniência (W3C-PROV) salvo em 'provenance_w3c.json'.")
    except Exception as e:
        print(f"Erro ao salvar o arquivo de proveniência: {e}")

if '__main__' == __name__:
    main()