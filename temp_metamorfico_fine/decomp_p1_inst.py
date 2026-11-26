import prov.model as prov
import json
from datetime import datetime, timezone

d = prov.ProvDocument()
d.add_namespace('ex', 'http://example.org/')
a_script = d.agent('ex:script_executor')
_step = 0

# Inicialização de 'raw_data'
_step += 1
t_start = datetime.now(timezone.utc)
raw_data = [10, 20, 30]
t_end = datetime.now(timezone.utc)

act_init_raw = d.activity(f'ex:init_raw_data_{_step}', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_init_raw, a_script)

e_raw_data = d.entity(f'ex:raw_data_v{_step}', {'prov:value': json.dumps(raw_data)})
d.wasGeneratedBy(e_raw_data, act_init_raw)

d.serialize('provenance_w3c.json', format='json')