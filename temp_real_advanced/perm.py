import pandas as pd

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
if __name__ == '__main__':
    main()

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
    Orquestra o processo de ETL.
    """
    arquivo_entrada = 'clientes_compras_grupo_1.csv'
    arquivo_saida = 'cliente_compras_grupo_1_tratado.csv'
    df = extrair_dados(arquivo_entrada)
    df_tratado = transformar_dados(df)
    carregar_dados(df_tratado, arquivo_saida)