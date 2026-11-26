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

# Operação 1: Atribuição com list comprehension
t_start = _now()
processed = [x - 5 for x in [10, 20, 30]]
t_end = _now()

act = d.activity(_uid('act'), startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act, a_script)
e_processed = d.entity(_uid('ent'), {'prov:value': str(processed)})
d.wasGeneratedBy(e_processed, act, time=t_end)

d.serialize('provenance_w3c.json', format='json')