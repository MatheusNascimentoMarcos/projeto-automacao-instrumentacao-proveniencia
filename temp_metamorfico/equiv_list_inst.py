import prov.model as prov
import json

# --- CONFIGURAÇÃO INICIAL DE PROVENIÊNCIA ---
d = prov.ProvDocument()
d.add_namespace('ex', 'http://example.org/')
# O próprio script é o agente que realiza as ações
a_script = d.agent('ex:list_comprehension_script.py')

# --- ETAPA 1: GERAÇÃO DE DADOS INICIAIS ---
# Ativando o modo de alta sensibilidade: A variável é uma Entidade.
# Código Original
dados = [1, 2, 3, 4, 5]

# Captura de Proveniência (Entidade Inicial)
# A lista 'dados' é uma entidade de dados.
# REGRA DE ATRIBUTO: Convertemos a lista para string para ser um atributo válido.
e_dados_iniciais = d.entity('ex:lista_inicial', {'prov:value': str(dados)})
# Atribuímos a criação desta entidade ao nosso agente (o script)
d.wasAttributedTo(e_dados_iniciais, a_script)


# --- ETAPA 2: TRANSFORMAÇÃO (LIST COMPREHENSION) ---
# Ativando o modo de alta sensibilidade: O loop/compreensão é uma Atividade.
# Captura de Proveniência (Atividade de Processamento)
a_transformacao = d.activity('ex:multiplicar_elementos_por_dois')
d.wasAssociatedWith(a_transformacao, a_script)
# A atividade de transformação usou a lista inicial de dados
a_transformacao.used(e_dados_iniciais)

# Código Original
resultado = [x * 2 for x in dados]

# Captura de Proveniência (Entidade Gerada)
# A lista 'resultado' é uma nova entidade gerada pela atividade.
# REGRA DE ATRIBUTO: Convertemos a lista para string.
e_resultado_final = d.entity('ex:lista_resultado', {'prov:value': str(resultado)})
# Ligamos a entidade de resultado à atividade que a gerou
d.wasGeneratedBy(e_resultado_final, a_transformacao)


# --- ETAPA 3: SALVAR O GRAFO DE PROVENIÊNCIA ---
d.serialize('provenance_w3c.json', format='json')