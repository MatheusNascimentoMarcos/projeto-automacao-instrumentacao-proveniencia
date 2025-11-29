import pandas as pd
import prov.model as prov
import datetime

def extrair_dados(caminho_arquivo):
    """
    Carrega os dados do arquivo CSV inicial.
    """
    print(f'Iniciando a leitura do arquivo: {caminho_arquivo}')
    try:
        df = pd.read_csv(caminho_arquivo, encoding='utf-8', delimiter=';')
        print(f'Número de tuplas/atributos inicial: {df.shape}')
        return df
    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        print('Por favor, coloque o arquivo no mesmo diretório do script.')
        return None
    except Exception as e:
        print(f'Ocorreu um erro inesperado ao ler o arquivo: {e}')
        return None

def transformar_dados(df):
    """
    Aplica as regras de limpeza e transformação no DataFrame.
    """
    if df is None:
        return None
    print('Iniciando transformações...')
    print("Corrigindo 'UF' com base no 'Município'...")
    correcoes_estado = {'Rio de Janeiro': 'RJ', 'Fortaleza': 'CE'}
    df['UF'] = df['Município'].map(correcoes_estado).fillna(df['UF'])
    print("Recalculando 'Valor total pago'...")
    df['Valor total pago'] = df['Preço unitário'] * df['Quantidade comprada'] + df['Taxa de entrega']
    print("Removendo registros com 'CPF do cliente' nulo ou vazio...")
    df = df[df['CPF do cliente'].notna() & (df['CPF do cliente'] != '')]
    print(f'Número de tuplas/atributos após filtro de CPF: {df.shape}')
    print("Removendo registros com 'Nome do cliente' nulo ou vazio...")
    df = df[df['Nome do cliente'].notna() & (df['Nome do cliente'] != '')]
    print(f'Número final de tuplas/atributos: {df.shape}')
    print('Transformações concluídas.')
    return df

# Bloco principal de execução com instrumentação de proveniência
if __name__ == "__main__":
    # --- CONFIGURAÇÃO INICIAL DE PROVENIÊNCIA ---
    d = prov.ProvDocument()
    d.add_namespace('ex', 'http://example.org/')
    d.set_default_namespace('http://example.org/')
    
    # Agente: O próprio script que está executando
    a_script = d.agent('ex:etl_script.py', {'prov:type': 'prov:SoftwareAgent'})

    # Parâmetros de entrada
    arquivo_entrada_path = 'dados_vendas.csv'

    # Entidade para o arquivo de entrada
    e_input_file = d.entity('ex:arquivo_entrada', {
        'prov:location': arquivo_entrada_path,
        'prov:type': 'ex:Dataset'
    })
    d.wasAttributedTo(e_input_file, a_script)

    # =======================================================
    # === FASE 1: Extração
    # =======================================================
    start_time_extract = datetime.datetime.now()
    df_raw = extrair_dados(arquivo_entrada_path)
    end_time_extract = datetime.datetime.now()

    # Só continua se a extração foi bem-sucedida
    if df_raw is not None:
        # --- Captura de Proveniência (Fase 1) ---
        a_extract = d.activity(
            'ex:extrair_dados_csv',
            start_time_extract,
            end_time_extract
        )
        d.wasAssociatedWith(a_extract, a_script)

        e_raw_df = d.entity('ex:dataframe_bruto', {
            'prov:type': 'ex:DataFrame',
            'ex:num_rows': df_raw.shape[0],
            'ex:num_cols': df_raw.shape[1],
            'ex:columns': str(df_raw.columns.tolist()) # CRÍTICO: Lista convertida para string
        })

        # Links de proveniência da extração
        d.wasGeneratedBy(e_raw_df, a_extract)
        a_extract.used(e_input_file)

        # =======================================================
        # === FASE 2: Transformação
        # =======================================================
        start_time_transform = datetime.datetime.now()
        df_clean = transformar_dados(df_raw.copy()) # Usar cópia para garantir a integridade do df_raw
        end_time_transform = datetime.datetime.now()

        if df_clean is not None:
            # --- Captura de Proveniência (Fase 2) ---
            correcoes = {'Rio de Janeiro': 'RJ', 'Fortaleza': 'CE'}
            a_transform = d.activity(
                'ex:transformar_limpar_dados',
                start_time_transform,
                end_time_transform,
                other_attributes={
                    'ex:mapeamento_uf': str(correcoes), # CRÍTICO: Dicionário convertido para string
                    'ex:coluna_calculada': 'Valor total pago',
                    'ex:filtros_aplicados': str(['CPF do cliente', 'Nome do cliente']) # CRÍTICO: Lista convertida para string
                }
            )
            d.wasAssociatedWith(a_transform, a_script)

            e_clean_df = d.entity('ex:dataframe_limpo', {
                'prov:type': 'ex:DataFrame',
                'ex:num_rows': df_clean.shape[0],
                'ex:num_cols': df_clean.shape[1],
                'ex:columns': str(df_clean.columns.tolist()) # CRÍTICO: Lista convertida para string
            })

            # Links de proveniência da transformação
            d.wasGeneratedBy(e_clean_df, a_transform)
            a_transform.used(e_raw_df)

            # =======================================================
            # === SALVANDO O GRAFO DE PROVENIÊNCIA
            # =======================================================
            try:
                d.serialize('provenance_w3c.json', format='json')
                print("\nWorkflow concluído.")
                print("Grafo de Proveniência (W3C-PROV) salvo em 'provenance_w3c.json'.")
            except Exception as e:
                print(f"Erro ao salvar o arquivo de proveniência: {e}")
        else:
            print("A etapa de transformação falhou. A proveniência não foi salva.")
    else:
        print("A etapa de extração falhou. O workflow foi interrompido.")