import prov.model as prov
import json
from datetime import datetime, timezone

d = prov.ProvDocument()
d.add_namespace('ex', 'http://example.org/')
a_script = d.agent('ex:script_executor')

# Etapa Macro 1: Execução de Cálculos
t_start = datetime.now(timezone.utc)

a = 10
a = a + 5
b = 20
b = b * 2

t_end = datetime.now(timezone.utc)

act_exec = d.activity('ex:executar_calculos', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_exec, a_script)

e_a = d.entity('ex:resultado_a', {'prov:value': str(a)})
d.wasGeneratedBy(e_a, act_exec)

e_b = d.entity('ex:resultado_b', {'prov:value': str(b)})
d.wasGeneratedBy(e_b, act_exec)

d.serialize('provenance_w3c.json', format='json')