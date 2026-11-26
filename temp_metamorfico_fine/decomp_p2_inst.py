import prov.model as prov
import json
from datetime import datetime, timezone

d = prov.ProvDocument()
d.add_namespace('ex', 'http://example.org/')
a_script = d.agent('ex:script_executor')
_step = 0

# Inicialização da lista original (domínio da list comprehension)
_step += 1
t_start = datetime.now(timezone.utc)
raw_list = [10, 20, 30]
t_end = datetime.now(timezone.utc)

act_init_raw = d.activity(f'ex:init_raw_list_{_step}', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_init_raw, a_script)
e_raw_list = d.entity(f'ex:raw_list_v{_step}', {'prov:value': json.dumps(raw_list)})
d.wasGeneratedBy(e_raw_list, act_init_raw)

# Inicialização da lista processada (acumulador interno da list comprehension)
_step += 1
t_start = datetime.now(timezone.utc)
processed = []
t_end = datetime.now(timezone.utc)

act_init_proc = d.activity(f'ex:init_processed_{_step}', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_init_proc, a_script)
e_processed_curr = d.entity(f'ex:processed_v{_step}', {'prov:value': json.dumps(processed)})
d.wasGeneratedBy(e_processed_curr, act_init_proc)

# Desdobramento dinâmico da iteração (DAG garantido para a list comprehension)
for idx, x in enumerate(raw_list):
    _step += 1
    t_start = datetime.now(timezone.utc)
    res = x - 5
    processed.append(res)
    t_end = datetime.now(timezone.utc)

    act_iter = d.activity(f'ex:list_comp_iter_{idx}_{_step}', startTime=t_start, endTime=t_end)
    d.wasAssociatedWith(act_iter, a_script)

    e_x = d.entity(f'ex:x_{idx}_{_step}', {'prov:value': str(x)})
    d.wasDerivedFrom(e_x, e_raw_list)

    d.used(act_iter, e_processed_curr)
    d.used(act_iter, e_x)

    e_res = d.entity(f'ex:res_{idx}_{_step}', {'prov:value': str(res)})
    d.wasGeneratedBy(e_res, act_iter)
    d.wasDerivedFrom(e_res, e_x)

    e_processed_next = d.entity(f'ex:processed_v{_step}', {'prov:value': json.dumps(processed)})
    d.wasGeneratedBy(e_processed_next, act_iter)
    d.wasDerivedFrom(e_processed_next, e_processed_curr)
    d.wasDerivedFrom(e_processed_next, e_res)
    
    e_processed_curr = e_processed_next

d.serialize('provenance_w3c.json', format='json')