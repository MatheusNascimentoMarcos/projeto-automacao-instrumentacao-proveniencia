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

# Desdobramento da list comprehension: processed = [x - 5 for x in raw_data]
# Passo 1: Inicialização do acumulador interno
_step += 1
t_start = datetime.now(timezone.utc)
processed = []
t_end = datetime.now(timezone.utc)
act_init_proc = d.activity(f'ex:init_processed_acc_{_step}', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_init_proc, a_script)
e_processed_curr = d.entity(f'ex:processed_v{_step}', {'prov:value': json.dumps(processed)})
d.wasGeneratedBy(e_processed_curr, act_init_proc)

# Passo 2: Iteração do laço interno da compreensão de lista
for idx, x in enumerate(raw_data):
    _step += 1
    t_start = datetime.now(timezone.utc)
    
    # Execução aritmética e acumulação
    val = x - 5
    processed.append(val)
    
    t_end = datetime.now(timezone.utc)

    # Registro da Atividade (Iteração)
    act_iter = d.activity(f'ex:listcomp_iter_{idx}_{_step}', startTime=t_start, endTime=t_end)
    d.wasAssociatedWith(act_iter, a_script)

    # Entidade para o item extraído
    e_item = d.entity(f'ex:raw_item_{idx}_{_step}', {'prov:value': str(x)})
    d.wasDerivedFrom(e_item, e_raw_data)

    # Entidade para o resultado da operação aritmética intermediária (x - 5)
    e_calc = d.entity(f'ex:calc_val_{idx}_{_step}', {'prov:value': str(val)})
    d.wasGeneratedBy(e_calc, act_iter)
    d.wasDerivedFrom(e_calc, e_item)

    # Dependências da iteração
    d.used(act_iter, e_processed_curr)
    d.used(act_iter, e_item)

    # Geração da nova versão do acumulador da lista
    e_processed_next = d.entity(f'ex:processed_v{_step}', {'prov:value': json.dumps(processed)})
    d.wasGeneratedBy(e_processed_next, act_iter)
    d.wasDerivedFrom(e_processed_next, e_processed_curr)
    d.wasDerivedFrom(e_processed_next, e_calc)
    
    # Atualização dinâmica SSA (Imutabilidade em nível de mapeamento lógico)
    e_processed_curr = e_processed_next

# Finalização e Serialização
d.serialize('provenance_w3c.json', format='json')