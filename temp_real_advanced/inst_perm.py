import pandas as pd
import prov.model as prov

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
    Orquestra o processo de ETL e captura a proveniência.
    """
    # --- CONFIGURAÇÃO INICIAL DE PROVENIÊNCIA ---
    d = prov.ProvDocument()
    d.add_namespace('ex', 'http://example.org/')
    a_script = d.agent('ex:etl_script.py', {'prov:type': 'prov:SoftwareAgent'})

    # --- Definição das variáveis de arquivo ---
    arquivo_entrada = 'clientes_compras_grupo_1.csv'
    arquivo_saida = 'cliente_compras_grupo_1_tratado.csv'

    # =======================================================
    # === FASE 1: Extrair Dados
    # =======================================================
    df = extrair_dados(arquivo_entrada)

    # --- Captura de Proveniência (Fase 1) ---
    if df is not None:
        act_extract = d.activity('ex:extrair_dados')
        d.wasAssociatedWith(act_extract, a_script)

        e_input_file = d.entity('ex:arquivo_entrada_csv', {'prov:location': arquivo_entrada})
        e_raw_df = d.entity('ex:dataframe_bruto', {
            'ex:shape': str(df.shape),
            'ex:columns': str(list(df.columns))
        })

        act_extract.used(e_input_file)
        d.wasGeneratedBy(e_raw_df, act_extract)
    else:
        # Se a extração falhar, encerra o script e salva o que tem.
        print("Falha na extração. Encerrando o workflow.")
        d.serialize('provenance_w3c.json', format='json')
        print("Grafo de Proveniência (parcial) salvo em 'provenance_w3c.json'.")
        return

    # =======================================================
    # === FASE 2: Transformar Dados
    # =======================================================
    df_tratado = transformar_dados(df)

    # --- Captura de Proveniência (Fase 2) ---
    if df_tratado is not None:
        act_transform = d.activity('ex:transformar_dados', other_attributes={
            'ex:regras_aplicadas': str(['correcao_uf_por_municipio', 'recalculo_valor_total', 'filtro_cpf_nulo', 'filtro_nome_nulo'])
        })
        d.wasAssociatedWith(act_transform, a_script)

        e_transformed_df = d.entity('ex:dataframe_tratado', {
            'ex:shape': str(df_tratado.shape),
            'ex:columns': str(list(df_tratado.columns))
        })

        # A atividade de transformação usou o dataframe bruto
        act_transform.used(e_raw_df)
        # E gerou o dataframe tratado
        d.wasGeneratedBy(e_transformed_df, act_transform)
    else:
        print("Falha na transformação. Encerrando o workflow.")
        d.serialize('provenance_w3c.json', format='json')
        print("Grafo de Proveniência (parcial) salvo em 'provenance_w3c.json'.")
        return

    # =======================================================
    # === FASE 3: Carregar Dados
    # =======================================================
    carregar_dados(df_tratado, arquivo_saida)

    # --- Captura de Proveniência (Fase 3) ---
    act_load = d.activity('ex:carregar_dados')
    d.wasAssociatedWith(act_load, a_script)

    e_output_file = d.entity('ex:arquivo_saida_csv', {'prov:location': arquivo_saida})

    # A atividade de carregamento usou o dataframe tratado
    act_load.used(e_transformed_df)
    # E gerou o arquivo de saída
    d.wasGeneratedBy(e_output_file, act_load)

    # =======================================================
    # === SALVANDO O GRAFO DE PROVENIÊNCIA
    # =======================================================
    d.serialize('provenance_w3c.json', format='json')
    print("Grafo de Proveniência (W3C-PROV) salvo em 'provenance_w3c.json'.")

if __name__ == '__main__':
    main()