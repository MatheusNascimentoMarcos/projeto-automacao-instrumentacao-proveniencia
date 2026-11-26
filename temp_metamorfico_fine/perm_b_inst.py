import prov.model as prov
import json
from datetime import datetime, timezone

d = prov.ProvDocument()
d.add_namespace('ex', 'http://example.org/')
a_script = d.agent('ex:script_executor')
_step = 0

# b = 20
_step += 1
t_start = datetime.now(timezone.utc)
b = 20
t_end = datetime.now(timezone.utc)

act_init_b = d.activity(f'ex:init_b_{_step}', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_init_b, a_script)

e_b_curr = d.entity(f'ex:b_v{_step}', {'prov:value': str(b)})
d.wasGeneratedBy(e_b_curr, act_init_b)


# b = b * 2
_step += 1
t_start = datetime.now(timezone.utc)
b = b * 2
t_end = datetime.now(timezone.utc)

act_mult_b = d.activity(f'ex:mult_b_{_step}', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_mult_b, a_script)
d.used(act_mult_b, e_b_curr)

e_b_next = d.entity(f'ex:b_v{_step}', {'prov:value': str(b)})
d.wasGeneratedBy(e_b_next, act_mult_b)
d.wasDerivedFrom(e_b_next, e_b_curr)
e_b_curr = e_b_next


# a = 10
_step += 1
t_start = datetime.now(timezone.utc)
a = 10
t_end = datetime.now(timezone.utc)

act_init_a = d.activity(f'ex:init_a_{_step}', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_init_a, a_script)

e_a_curr = d.entity(f'ex:a_v{_step}', {'prov:value': str(a)})
d.wasGeneratedBy(e_a_curr, act_init_a)


# a = a + 5
_step += 1
t_start = datetime.now(timezone.utc)
a = a + 5
t_end = datetime.now(timezone.utc)

act_add_a = d.activity(f'ex:add_a_{_step}', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_add_a, a_script)
d.used(act_add_a, e_a_curr)

e_a_next = d.entity(f'ex:a_v{_step}', {'prov:value': str(a)})
d.wasGeneratedBy(e_a_next, act_add_a)
d.wasDerivedFrom(e_a_next, e_a_curr)
e_a_curr = e_a_next


d.serialize('provenance_w3c.json', format='json')