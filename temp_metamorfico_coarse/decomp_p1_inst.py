import prov.model as prov
import json
from datetime import datetime, timezone

d = prov.ProvDocument()
d.add_namespace('ex', 'http://example.org/')
a_script = d.agent('ex:script_executor')

# Etapa Macro 1: Inicialização de Dados
t_start = datetime.now(timezone.utc)

raw_data = [10, 20, 30]

t_end = datetime.now(timezone.utc)

act_init = d.activity('ex:inicializar_dados', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_init, a_script)

e_raw_data = d.entity('ex:raw_data', {'ex:value': json.dumps(raw_data)})
d.wasGeneratedBy(e_raw_data, act_init)

d.serialize('provenance_w3c.json', format='json')