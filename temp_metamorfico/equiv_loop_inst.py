import prov.model as prov

# --- CONFIGURAÇÃO INICIAL DE PROVENIÊNCIA ---
d = prov.ProvDocument()
d.add_namespace('ex', 'http://example.org/')
# Define o próprio script como o Agente
a_script = d.agent('ex:simple_loop_script.py')


# =======================================================
# === FASE 1: Definição dos Dados de Entrada
# =======================================================

# --- Código Original 1 ---
dados = [1, 2, 3, 4, 5]
# --- Fim do Bloco ---

# --- Captura de Proveniência (Fase 1) ---
# Trata a lista inicial 'dados' como uma Entidade.
# Como não foi gerada por uma atividade, associamos diretamente ao Agente.
# De acordo com a regra de atributos, convertemos a lista para string.
e_dados_iniciais = d.entity('ex:lista_inicial_dados', {
    'prov:value': str(dados),
    'ex:description': 'Lista de inteiros usada como entrada.'
})
d.wasAttributedTo(e_dados_iniciais, a_script)


# =======================================================
# === FASE 2: Processamento e Transformação (Loop)
# =======================================================

# --- Captura de Proveniência (Fase 2 - Início da Atividade) ---
# Trata o loop 'for' como uma Atividade que transforma os dados.
act_processamento = d.activity('ex:dobrar_elementos_loop', other_attributes={
    'ex:description': 'Itera sobre a lista de entrada e multiplica cada elemento por 2.'
})
d.wasAssociatedWith(act_processamento, a_script)
# Liga a atividade à sua entrada: o processamento 'usou' a lista inicial.
act_processamento.used(e_dados_iniciais)


# --- Código Original 2 ---
resultado = []
for x in dados:
    resultado.append(x * 2)
# --- Fim do Bloco ---

# --- Captura de Proveniência (Fase 2 - Fim da Atividade) ---
# A lista 'resultado' é uma nova Entidade que foi gerada pela atividade.
# De acordo com a regra de atributos, convertemos a lista para string.
e_resultado_final = d.entity('ex:lista_resultado_final', {
    'prov:value': str(resultado),
    'ex:description': 'Lista de saída com os elementos dobrados.'
})
# Liga a entidade de saída à atividade que a gerou.
d.wasGeneratedBy(e_resultado_final, act_processamento)


# =======================================================
# === SALVANDO O GRAFO DE PROVENIÊNCIA
# =======================================================
d.serialize('provenance_w3c.json', format='json')