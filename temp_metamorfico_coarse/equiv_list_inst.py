import prov.model as prov
import json
from datetime import datetime, timezone

d = prov.ProvDocument()
d.add_namespace('ex', 'http://example.org/')
a_script = d.agent('ex:script_executor')

# Etapa Macro 1: Carregamento / Definição de Dados
t_start = datetime.now(timezone.utc)
dados = [1, 2, 3, 4, 5]
t_end = datetime.now(timezone.utc)

act_load = d.activity('ex:carregar_dados', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_load, a_script)
e_dados = d.entity('ex:dados_entrada', {'ex:value': json.dumps(dados)})
d.wasGeneratedBy(e_dados, act_load)

# Etapa Macro 2: Processamento
t_start = datetime.now(timezone.utc)
resultado = [x * 2 for x in dados]
t_end = datetime.now(timezone.utc)

act_proc = d.activity('ex:processar_dados', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_proc, a_script)
e_resultado = d.entity('ex:resultado_final', {'prov:value': json.dumps(resultado)})
d.used(act_proc, e_dados)
d.wasGeneratedBy(e_resultado, act_proc)
d.wasDerivedFrom(e_resultado, e_dados)

d.serialize('provenance_w3c.json', format='json')