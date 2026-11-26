import prov.model as prov
import json
from datetime import datetime, timezone

d = prov.ProvDocument()
d.add_namespace('ex', 'http://example.org/')
a_script = d.agent('ex:script_executor')

# Etapa Macro 1: Inicialização dos dados
t_start = datetime.now(timezone.utc)
dados = [1, 2, 3, 4, 5]
t_end = datetime.now(timezone.utc)

act_init = d.activity('ex:inicializar_dados', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_init, a_script)
e_dados = d.entity('ex:dados_entrada', {'ex:value': json.dumps(dados)})
d.wasGeneratedBy(e_dados, act_init)

# Etapa Macro 2: Processamento (laço encapsulado como caixa-preta)
t_start = datetime.now(timezone.utc)
resultado = []
for x in dados:
    resultado.append(x * 2)
t_end = datetime.now(timezone.utc)

act_proc = d.activity('ex:processar_dados', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_proc, a_script)
e_resultado = d.entity('ex:resultado_processamento', {'ex:value': json.dumps(resultado)})
d.used(act_proc, e_dados)
d.wasGeneratedBy(e_resultado, act_proc)
d.wasDerivedFrom(e_resultado, e_dados)

d.serialize('provenance_w3c.json', format='json')