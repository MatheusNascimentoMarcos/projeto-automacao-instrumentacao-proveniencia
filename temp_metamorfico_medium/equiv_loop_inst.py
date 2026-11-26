import prov.model as prov
import json
from datetime import datetime, timezone

d = prov.ProvDocument()
d.add_namespace('ex', 'http://example.org/')
a_script = d.agent('ex:script_executor')

# Etapa de Inicialização
t_start = datetime.now(timezone.utc)
dados = [1, 2, 3, 4, 5]
resultado = []
t_end = datetime.now(timezone.utc)

act_init = d.activity('ex:inicializacao', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_init, a_script)
e_dados = d.entity('ex:dados_v1', {'prov:value': json.dumps(dados)})
e_resultado_v1 = d.entity('ex:resultado_v1', {'prov:value': json.dumps(resultado)})
d.wasGeneratedBy(e_dados, act_init)
d.wasGeneratedBy(e_resultado_v1, act_init)

# Etapa de Processamento (Multiplicação)
t_start = datetime.now(timezone.utc)
for x in dados:
    resultado.append(x * 2)
t_end = datetime.now(timezone.utc)

act_proc = d.activity('ex:processar_multiplicacao', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_proc, a_script)
d.used(act_proc, e_dados)
d.used(act_proc, e_resultado_v1)

e_resultado_v2 = d.entity('ex:resultado_v2', {'prov:value': json.dumps(resultado)})
d.wasGeneratedBy(e_resultado_v2, act_proc)
d.wasDerivedFrom(e_resultado_v2, e_dados)
d.wasDerivedFrom(e_resultado_v2, e_resultado_v1)

# Serialização
d.serialize('provenance_w3c.json', format='json')