import prov.model as prov

# --- CONFIGURAÇÃO INICIAL DE PROVENIÊNCIA ---
d = prov.ProvDocument()
d.add_namespace('ex', 'http://example.org/')
# Define o próprio script como o Agente
a_script = d.agent('ex:simple_arithmetic.py')


# =======================================================
# === PROCESSAMENTO DE 'a'
# =======================================================

# --- Código Original ---
a = 10
# --- Captura de Proveniência (Entidade Inicial) ---
# Trata a atribuição inicial como uma Entidade base atribuída ao script.
e_a_initial = d.entity('ex:a_initial', {'prov:value': str(a)})
d.wasAttributedTo(e_a_initial, a_script)


# --- Código Original ---
# a = a + 5
# --- Captura de Proveniência (Atividade de Soma) ---
# A operação de soma é uma Atividade que usa o valor anterior de 'a'.
act_add = d.activity('ex:add_five_to_a')
d.wasAssociatedWith(act_add, a_script)
act_add.used(e_a_initial)
a = a + 5 # O código original é executado aqui
# O novo valor de 'a' é uma nova Entidade gerada pela Atividade de soma.
e_a_final = d.entity('ex:a_final', {'prov:value': str(a)})
d.wasGeneratedBy(e_a_final, act_add)


# =======================================================
# === PROCESSAMENTO DE 'b'
# =======================================================

# --- Código Original ---
b = 20
# --- Captura de Proveniência (Entidade Inicial) ---
# Trata a atribuição inicial de 'b' como uma Entidade base.
e_b_initial = d.entity('ex:b_initial', {'prov:value': str(b)})
d.wasAttributedTo(e_b_initial, a_script)


# --- Código Original ---
# b = b * 2
# --- Captura de Proveniência (Atividade de Multiplicação) ---
# A operação de multiplicação é uma Atividade que usa o valor inicial de 'b'.
act_multiply = d.activity('ex:multiply_b_by_two')
d.wasAssociatedWith(act_multiply, a_script)
act_multiply.used(e_b_initial)
b = b * 2 # O código original é executado aqui
# O novo valor de 'b' é uma nova Entidade gerada pela Atividade de multiplicação.
e_b_final = d.entity('ex:b_final', {'prov:value': str(b)})
d.wasGeneratedBy(e_b_final, act_multiply)


# =======================================================
# === SALVANDO O GRAFO DE PROVENIÊNCIA
# =======================================================
d.serialize('provenance_w3c.json', format='json')