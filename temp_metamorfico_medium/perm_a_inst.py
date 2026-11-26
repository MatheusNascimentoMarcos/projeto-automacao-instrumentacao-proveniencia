import prov.model as prov
import json
from datetime import datetime, timezone

d = prov.ProvDocument()
d.add_namespace('ex', 'http://example.org/')
a_script = d.agent('ex:script_executor')

# Inicialização da variável 'a'
t_start = datetime.now(timezone.utc)
a = 10
t_end = datetime.now(timezone.utc)

act_init_a = d.activity('ex:inicializar_a', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_init_a, a_script)
e_a_v1 = d.entity('ex:a_v1', {'prov:value': str(a)})
d.wasGeneratedBy(e_a_v1, act_init_a)

# Mutação da variável 'a'
t_start = datetime.now(timezone.utc)
a = a + 5
t_end = datetime.now(timezone.utc)

act_add_a = d.activity('ex:adicionar_a', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_add_a, a_script)
d.used(act_add_a, e_a_v1)
e_a_v2 = d.entity('ex:a_v2', {'prov:value': str(a)})
d.wasGeneratedBy(e_a_v2, act_add_a)
d.wasDerivedFrom(e_a_v2, e_a_v1)

# Inicialização da variável 'b'
t_start = datetime.now(timezone.utc)
b = 20
t_end = datetime.now(timezone.utc)

act_init_b = d.activity('ex:inicializar_b', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_init_b, a_script)
e_b_v1 = d.entity('ex:b_v1', {'prov:value': str(b)})
d.wasGeneratedBy(e_b_v1, act_init_b)

# Mutação da variável 'b'
t_start = datetime.now(timezone.utc)
b = b * 2
t_end = datetime.now(timezone.utc)

act_mult_b = d.activity('ex:multiplicar_b', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_mult_b, a_script)
d.used(act_mult_b, e_b_v1)
e_b_v2 = d.entity('ex:b_v2', {'prov:value': str(b)})
d.wasGeneratedBy(e_b_v2, act_mult_b)
d.wasDerivedFrom(e_b_v2, e_b_v1)

d.serialize('provenance_w3c.json', format='json')