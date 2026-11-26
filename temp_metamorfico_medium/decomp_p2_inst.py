import prov.model as prov
import json
from datetime import datetime, timezone

d = prov.ProvDocument()
d.add_namespace('ex', 'http://example.org/')
a_script = d.agent('ex:script_executor')

# Etapa 1: Inicialização de Dados
t_start = datetime.now(timezone.utc)
raw_data = [10, 20, 30] 
t_end = datetime.now(timezone.utc)

act_init = d.activity('ex:inicializar_dados', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_init, a_script)
e_raw_data = d.entity('ex:raw_data_v1', {'prov:value': json.dumps(raw_data)})
d.wasGeneratedBy(e_raw_data, act_init)

# Etapa 2: Processamento de Dados
t_start = datetime.now(timezone.utc)
processed = [x - 5 for x in raw_data]
t_end = datetime.now(timezone.utc)

act_process = d.activity('ex:processar_dados', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_process, a_script)
d.used(act_process, e_raw_data)
e_processed = d.entity('ex:processed_v1', {'prov:value': json.dumps(processed)})
d.wasGeneratedBy(e_processed, act_process)
d.wasDerivedFrom(e_processed, e_raw_data)

# Salvar proveniência
d.serialize('provenance_w3c.json', format='json')