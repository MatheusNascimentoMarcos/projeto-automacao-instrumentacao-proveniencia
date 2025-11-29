import prov.model as prov

# --- CONFIGURAÇÃO INICIAL DE PROVENIÊNCIA ---
d = prov.ProvDocument()
d.add_namespace('ex', 'http://example.org/')

# Define o próprio script como o Agente que executa as atividades
a_script = d.agent('ex:data_processing_script.py')


# =======================================================
# === FASE 1: Definição dos Dados Brutos
# =======================================================

# --- Código Original ---
raw_data = [10, 20, 30]

# --- Captura de Proveniência (Fase 1) ---
# Trata a lista inicial como uma Entidade.
# Como é a fonte inicial, é atribuída diretamente ao Agente.
e_raw_data = d.entity('ex:raw_data_list', {'ex:value': str(raw_data)})
d.wasAttributedTo(e_raw_data, a_script)


# =======================================================
# === FASE 2: Processamento via List Comprehension
# =======================================================

# --- Captura de Proveniência (Fase 2) ---
# A list comprehension é uma Atividade de transformação.
a_process = d.activity('ex:transform_list_comprehension')
d.wasAssociatedWith(a_process, a_script)

# --- Código Original ---
processed = [x - 5 for x in raw_data]

# --- Captura de Proveniência (Fase 2 - Continuação) ---
# A nova lista 'processed' é uma Entidade gerada pela Atividade.
e_processed_data = d.entity('ex:processed_data_list', {'ex:value': str(processed)})
d.wasGeneratedBy(e_processed_data, a_process)

# Liga a Atividade à sua Entidade de entrada.
a_process.used(e_raw_data)


# =======================================================
# === SALVANDO O GRAFO DE PROVENIÊNCIA
# =======================================================
d.serialize('provenance_w3c.json', format='json')