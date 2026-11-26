import prov.model as prov
import json
from datetime import datetime, timezone

d = prov.ProvDocument()
d.add_namespace('ex', 'http://example.org/')
a_script = d.agent('ex:script_executor')
_step = 0

# Inicialização de 'dados'
_step += 1
t_start = datetime.now(timezone.utc)
dados = [1, 2, 3, 4, 5]
t_end = datetime.now(timezone.utc)
act_init_dados = d.activity(f'ex:init_dados_{_step}', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_init_dados, a_script)
e_dados = d.entity(f'ex:dados_v{_step}', {'prov:value': json.dumps(dados)})
d.wasGeneratedBy(e_dados, act_init_dados)

# Inicialização de 'resultado'
_step += 1
t_start = datetime.now(timezone.utc)
resultado = []
t_end = datetime.now(timezone.utc)
act_init_res = d.activity(f'ex:init_resultado_{_step}', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_init_res, a_script)
e_resultado_curr = d.entity(f'ex:resultado_v{_step}', {'prov:value': json.dumps(resultado)})
d.wasGeneratedBy(e_resultado_curr, act_init_res)

# Desdobramento dinâmico do laço (DAG garantido)
for idx, x in enumerate(dados):
    _step += 1
    t_start = datetime.now(timezone.utc)
    resultado.append(x * 2)
    t_end = datetime.now(timezone.utc)

    act_iter = d.activity(f'ex:append_iter_{idx}_{_step}', startTime=t_start, endTime=t_end)
    d.wasAssociatedWith(act_iter, a_script)

    e_item = d.entity(f'ex:item_x_{idx}_{_step}', {'prov:value': str(x)})
    d.wasDerivedFrom(e_item, e_dados)

    d.used(act_iter, e_resultado_curr)
    d.used(act_iter, e_item)

    e_resultado_next = d.entity(f'ex:resultado_v{_step}', {'prov:value': json.dumps(resultado)})
    d.wasGeneratedBy(e_resultado_next, act_iter)
    d.wasDerivedFrom(e_resultado_next, e_resultado_curr)
    d.wasDerivedFrom(e_resultado_next, e_item)
    e_resultado_curr = e_resultado_next

d.serialize('provenance_w3c.json', format='json')