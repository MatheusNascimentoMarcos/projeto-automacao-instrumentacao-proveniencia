import prov.model as prov
import json
from datetime import datetime, timezone

d = prov.ProvDocument()
d.add_namespace('ex', 'http://example.org/')
a_script = d.agent('ex:script_executor')

# Etapa de Inicialização dos Dados
t_start = datetime.now(timezone.utc)
dados = [1, 2, 3, 4, 5]
t_end = datetime.now(timezone.utc)

act_init = d.activity('ex:inicializar_dados', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_init, a_script)
e_dados = d.entity('ex:dados_v1', {'prov:value': json.dumps(dados)})
d.wasGeneratedBy(e_dados, act_init)

# Etapa de Transformação
t_start = datetime.now(timezone.utc)
resultado = [x * 2 for x in dados]
t_end = datetime.now(timezone.utc)

act_transf = d.activity('ex:transformar_dados', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_transf, a_script)
d.used(act_transf, e_dados)
e_resultado = d.entity('ex:resultado_v1', {'prov:value': json.dumps(resultado)})
d.wasGeneratedBy(e_resultado, act_transf)
d.wasDerivedFrom(e_resultado, e_dados)

d.serialize('provenance_w3c.json', format='json')