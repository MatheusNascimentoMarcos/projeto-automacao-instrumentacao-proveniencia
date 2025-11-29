import pandas as pd

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
if __name__ == '__main__':
    main()