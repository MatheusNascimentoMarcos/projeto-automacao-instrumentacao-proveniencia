import prov.model as prov
import json
from datetime import datetime, timezone

d = prov.ProvDocument()
d.add_namespace('ex', 'http://example.org/')
a_script = d.agent('ex:script_executor')

# Etapa Macro 1: Definição/Carregamento
t_start = datetime.now(timezone.utc)
raw_data = [10, 20, 30] 
t_end = datetime.now(timezone.utc)

act_load = d.activity('ex:carregar_dados', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_load, a_script)
e_raw_data = d.entity('ex:dados_brutos', {'ex:value': json.dumps(raw_data)})
d.wasGeneratedBy(e_raw_data, act_load)

# Etapa Macro 2: Processamento
t_start = datetime.now(timezone.utc)
processed = [x - 5 for x in raw_data]
t_end = datetime.now(timezone.utc)

act_proc = d.activity('ex:processar_dados', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_proc, a_script)
e_processed = d.entity('ex:dados_processados', {'ex:value': json.dumps(processed)})
d.used(act_proc, e_raw_data)
d.wasGeneratedBy(e_processed, act_proc)
d.wasDerivedFrom(e_processed, e_raw_data)

d.serialize('provenance_w3c.json', format='json')