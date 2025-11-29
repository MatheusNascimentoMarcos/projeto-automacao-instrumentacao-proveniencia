import prov.model as prov

# --- CONFIGURAÇÃO INICIAL DE PROVENIÊNCIA ---
d = prov.ProvDocument()
d.add_namespace('ex', 'http://example.org/')
# Define o próprio script como o Agente
a_script = d.agent('ex:list_processing_script')


# =======================================================
# === FASE 1: Definição de Dados Brutos
# =======================================================

# --- Código Original 1 ---
raw_data = [10, 20, 30]
# --- Fim do Bloco ---

# --- Captura de Proveniência (Fase 1) ---
# Entidade para a lista inicial em memória.
# O valor da lista é convertido para string para ser um atributo válido.
e_raw_data = d.entity('ex:raw_data_list', {'prov:value': str(raw_data)})
# A entidade inicial é atribuída ao agente do script.
d.wasAttributedTo(e_raw_data, a_script)


# =======================================================
# === FASE 2: Processamento com List Comprehension
# =======================================================

# --- Captura de Proveniência (Fase 2 - Atividade) ---
# A list comprehension é modelada como uma atividade de transformação.
a_transform = d.activity('ex:transform_list_comprehension')
d.wasAssociatedWith(a_transform, a_script)
# A atividade de transformação usa a lista de dados brutos.
a_transform.used(e_raw_data)

# --- Código Original 2 ---
processed = [x - 5 for x in raw_data]
# --- Fim do Bloco ---

# --- Captura de Proveniência (Fase 2 - Geração) ---
# Entidade para a lista processada resultante.
e_processed_data = d.entity('ex:processed_data_list', {'prov:value': str(processed)})
# A nova lista foi gerada pela atividade de transformação.
d.wasGeneratedBy(e_processed_data, a_transform)


# =======================================================
# === SALVANDO O GRAFO DE PROVENIÊNCIA
# =======================================================
d.serialize('provenance_w3c.json', format='json')