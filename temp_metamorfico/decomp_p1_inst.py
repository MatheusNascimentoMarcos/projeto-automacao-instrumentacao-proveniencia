import prov.model as prov
import json

# --- CONFIGURAÇÃO INICIAL DE PROVENIÊNCIA ---
# Cria um novo documento de proveniência
d = prov.ProvDocument()
# Define um namespace para os elementos
d.add_namespace('ex', 'http://example.org/')
# Define o próprio script como o Agente
a_script = d.agent('ex:simple_assignment_script')


# --- Código Original ---
raw_data = [10, 20, 30]


# --- Captura de Proveniência ---
# Em um script simples, a própria inicialização dos dados é um evento de proveniência.
# A atividade é a "criação" ou "definição" dos dados.
a_create = d.activity('ex:criar_dados_brutos')
d.wasAssociatedWith(a_create, a_script)

# A lista `raw_data` é a Entidade gerada.
# O valor da lista é convertido para string, conforme a regra de atributos.
e_raw_data = d.entity('ex:lista_dados_brutos', {'ex:value': str(raw_data)})

# A entidade `e_raw_data` foi gerada pela atividade de criação.
d.wasGeneratedBy(e_raw_data, a_create)


# --- SALVANDO O GRAFO DE PROVENIÊNCIA ---
# Serializa o documento de proveniência para o arquivo JSON especificado.
d.serialize('provenance_w3c.json', format='json')