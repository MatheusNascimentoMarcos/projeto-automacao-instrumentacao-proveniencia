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
b = 20
t_end = _now()
act = d.activity(_uid('act'), startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act, a_script)
e_b = d.entity(_uid('ent'), {'prov:value': str(b)})
d.wasGeneratedBy(e_b, act, time=t_end)

t_start = _now()
b = b * 2
t_end = _now()
act = d.activity(_uid('act'), startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act, a_script)
d.used(act, e_b, time=t_start)
e_b_new = d.entity(_uid('ent'), {'prov:value': str(b)})
d.wasGeneratedBy(e_b_new, act, time=t_end)
d.wasDerivedFrom(e_b_new, e_b)
e_b = e_b_new

t_start = _now()
a = 10
t_end = _now()
act = d.activity(_uid('act'), startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act, a_script)
e_a = d.entity(_uid('ent'), {'prov:value': str(a)})
d.wasGeneratedBy(e_a, act, time=t_end)

t_start = _now()
a = a + 5
t_end = _now()
act = d.activity(_uid('act'), startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act, a_script)
d.used(act, e_a, time=t_start)
e_a_new = d.entity(_uid('ent'), {'prov:value': str(a)})
d.wasGeneratedBy(e_a_new, act, time=t_end)
d.wasDerivedFrom(e_a_new, e_a)
e_a = e_a_new

d.serialize('provenance_w3c.json', format='json')