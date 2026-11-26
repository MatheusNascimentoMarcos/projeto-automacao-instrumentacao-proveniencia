import prov.model as prov
import json
from datetime import datetime, timezone

# --- INFRAESTRUTURA CANÔNICA W3C-PROV ---
d = prov.ProvDocument()
d.add_namespace('ex', 'http://example.org/')
a_script = d.agent('ex:script_agent')
_prov_counter = 0

def _uid(prefix):
    global _prov_counter
    _prov_counter += 1
    return f'ex:{prefix}_{_prov_counter}'

def _now():
    return datetime.now(timezone.utc)
# ----------------------------------------

t_start = _now()
dados = [1, 2, 3, 4, 5]
t_end = _now()
act = d.activity(_uid('act'), startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act, a_script)
e_dados = d.entity(_uid('ent'), {'prov:value': str(dados)})
d.wasGeneratedBy(e_dados, act, time=t_end)

t_start = _now()
resultado = [x * 2 for x in dados]
t_end = _now()
act = d.activity(_uid('act'), startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act, a_script)
d.used(act, e_dados, time=t_start)
e_resultado = d.entity(_uid('ent'), {'prov:value': str(resultado)})
d.wasGeneratedBy(e_resultado, act, time=t_end)
d.wasDerivedFrom(e_resultado, e_dados)

d.serialize('provenance_w3c.json', format='json')