import prov.model as prov

# --- CONFIGURAÇÃO INICIAL DE PROVENIÊNCIA ---
d = prov.ProvDocument()
d.add_namespace('ex', 'http://example.org/')
# Define o próprio script como o Agente
a_script = d.agent('ex:simple_arithmetic_script')

# --- ETAPA 1: Processamento da variável 'b' ---

# --- Bloco Original 1.1 ---
b = 20
# --- Fim do Bloco ---
# Captura de Proveniência: Entidade inicial para 'b'
e_b_initial = d.entity('ex:b_initial', {'prov:value': str(b)})
d.wasAttributedTo(e_b_initial, a_script) # Valor definido pelo agente (script)

# --- Bloco Original 1.2 ---
b = b * 2
# --- Fim do Bloco ---
# Captura de Proveniência: Atividade de multiplicação
a_multiply = d.activity('ex:multiplicar_b_por_2')
d.wasAssociatedWith(a_multiply, a_script)
a_multiply.used(e_b_initial) # A atividade usou o valor inicial de 'b'
e_b_final = d.entity('ex:b_final', {'prov:value': str(b)})
d.wasGeneratedBy(e_b_final, a_multiply) # O novo valor de 'b' foi gerado pela atividade

# --- ETAPA 2: Processamento da variável 'a' ---

# --- Bloco Original 2.1 ---
a = 10
# --- Fim do Bloco ---
# Captura de Proveniência: Entidade inicial para 'a'
e_a_initial = d.entity('ex:a_initial', {'prov:value': str(a)})
d.wasAttributedTo(e_a_initial, a_script) # Valor definido pelo agente (script)

# --- Bloco Original 2.2 ---
a = a + 5
# --- Fim do Bloco ---
# Captura de Proveniência: Atividade de soma
a_add = d.activity('ex:somar_a_com_5')
d.wasAssociatedWith(a_add, a_script)
a_add.used(e_a_initial) # A atividade usou o valor inicial de 'a'
e_a_final = d.entity('ex:a_final', {'prov:value': str(a)})
d.wasGeneratedBy(e_a_final, a_add) # O novo valor de 'a' foi gerado pela atividade


# --- SALVANDO O GRAFO DE PROVENIÊNCIA ---
d.serialize('provenance_w3c.json', format='json')