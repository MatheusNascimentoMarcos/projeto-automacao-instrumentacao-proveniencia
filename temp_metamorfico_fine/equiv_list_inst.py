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


# Inicialização da variável 'resultado' (representando o início da list comprehension)
_step += 1
t_start = datetime.now(timezone.utc)
resultado = []
t_end = datetime.now(timezone.utc)

act_init_res = d.activity(f'ex:init_resultado_{_step}', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_init_res, a_script)

e_resultado_curr = d.entity(f'ex:resultado_v{_step}', {'prov:value': json.dumps(resultado)})
d.wasGeneratedBy(e_resultado_curr, act_init_res)


# Desdobramento dinâmico da list comprehension: resultado = [x * 2 for x in dados]
for idx, x in enumerate(dados):
    _step += 1
    
    t_start = datetime.now(timezone.utc)
    valor_multiplicado = x * 2
    resultado.append(valor_multiplicado)
    t_end = datetime.now(timezone.utc)

    # Atividade iterativa
    act_iter = d.activity(f'ex:listcomp_iter_{idx}_{_step}', startTime=t_start, endTime=t_end)
    d.wasAssociatedWith(act_iter, a_script)

    # Entidade representando o elemento 'x' extraído de 'dados'
    e_x = d.entity(f'ex:item_x_{idx}_{_step}', {'prov:value': str(x)})
    d.wasDerivedFrom(e_x, e_dados)

    # Entidade representando a operação de multiplicação
    e_mult = d.entity(f'ex:valor_multiplicado_{idx}_{_step}', {'prov:value': str(valor_multiplicado)})
    d.wasGeneratedBy(e_mult, act_iter)
    d.wasDerivedFrom(e_mult, e_x)

    # Uso das entidades anteriores pela atividade
    d.used(act_iter, e_resultado_curr)
    d.used(act_iter, e_x)

    # Nova versão do acumulador 'resultado'
    e_resultado_next = d.entity(f'ex:resultado_v{_step}', {'prov:value': json.dumps(resultado)})
    d.wasGeneratedBy(e_resultado_next, act_iter)
    d.wasDerivedFrom(e_resultado_next, e_resultado_curr)
    d.wasDerivedFrom(e_resultado_next, e_mult)
    
    # Atualização da referência de versão atual
    e_resultado_curr = e_resultado_next

# Exportação do grafo de proveniência
d.serialize('provenance_w3c.json', format='json')