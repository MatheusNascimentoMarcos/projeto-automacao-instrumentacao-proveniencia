# prompt_template_fine.py
# Granularidade FINA (Fine-Grained / White-Box) com Desdobramento de Laços e Invariantes W3C-PROV

PROMPT_FINE_TEMPLATE = """
Você é um engenheiro de software especialista em proveniência de dados (W3C-PROV) e instrumentação de código Python em nível de instrução. Sua tarefa é instrumentar o script fornecido para capturar proveniência retrospectiva em **GRANULARIDADE FINA (Fine-Grained / White-Box)**.

## Heurísticas de Captura (Nível Fino)
1. **Entity (O que capturar):**
   - Capture TODA variável em memória que participa de fluxo de dados (inteiros, floats, strings, listas, dicionários, objetos) e artefatos externos.
   - **Imutabilidade por Versão (SSA Dinâmico):** Cada nova atribuição ou atualização de uma variável `var` DEVE gerar uma nova `Entity` com identificador único incremental (ex.: `f"ex:var_v{{step}}"`), mantendo um mapeamento em memória (`ent_map['var'] = e_nova`) para rastrear a versão ativa.
2. **Activity (O que capturar):**
   - Capture cada operação aritmética, lógica, chamada de função, expressão de atribuição e **cada iteração individual** de laços (`for`/`while`) ou chamadas recursivas como uma `Activity` distinta com ID único (ex.: `f"ex:loop_iter_{{idx}}"`).
   - Capture desvios condicionais (`if`/`else`) apenas no ramo efetivamente executado em tempo de execução.
3. **Agent:**
   - Associe todas as `Activity` ao agente `a_script = d.agent('ex:script_executor')`.

## Invariantes Ontológicas e Causais Obrigatórias (W3C-PROV)
1. **Tipagem Estrita (Domínio/Alcance):**
   - `d.used(activity, entity)` | `d.wasGeneratedBy(entity, activity)` | `d.wasDerivedFrom(e_nova, e_antiga)` | `d.wasAssociatedWith(activity, agent)`.
2. **Aciclicidade Causal (DAG - CRÍTICO EM LAÇOS):**
   - Em laços (`for`/`while`) e recursões, NUNCA reutilize o mesmo ID de `Activity` ou `Entity` entre iterações.
   - Use um contador incremental (ex.: `_prov_step += 1`) para desdobrar o laço em uma cadeia causal linear (`e_acc_v0 -> act_iter_1 -> e_acc_v1 -> act_iter_2 -> e_acc_v2`), garantindo 100% de aciclicidade.
3. **Consistência Temporal (Precedência):**
   - Registre `t_start = datetime.now(timezone.utc)` antes e `t_end = datetime.now(timezone.utc)` depois de cada operação/iteração, passando `startTime=t_start, endTime=t_end` em `d.activity(...)`.
4. **Unicidade de Origem Primária:**
   - Cada ID de `Entity` deve ser gerado por no máximo UMA `Activity`. Atualizações de acumuladores criam novas versões ligadas à versão anterior por `d.wasDerivedFrom(e_novo, e_anterior)`.

## Regras Técnicas e de Saída
- Imports obrigatórios: `import prov.model as prov`, `import json`, `from datetime import datetime, timezone`.
- Namespace padrão: `d.add_namespace('ex', 'http://example.org/')`.
- Converta listas/dicionários em atributos para string (`str(val)` ou `json.dumps(val)`).
- Salve EXATAMENTE em `'provenance_w3c.json'` com `format='json'`.

## Exemplo (Few-Shot - Granularidade Fina com Desdobramento de Laço)
### INPUT:
```python
valores = [2, 4, 6]
total = 0
for v in valores:
    total = total + v
print(total)
```

### OUTPUT:
```python
import prov.model as prov
import json
from datetime import datetime, timezone

d = prov.ProvDocument()
d.add_namespace('ex', 'http://example.org/')
a_script = d.agent('ex:script_executor')
_step = 0

# Inicialização de 'valores'
_step += 1
t_start = datetime.now(timezone.utc)
valores = [2, 4, 6]
t_end = datetime.now(timezone.utc)
act_init_val = d.activity(f'ex:init_valores_{{_step}}', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_init_val, a_script)
e_valores = d.entity(f'ex:valores_v{{_step}}', {{'prov:value': json.dumps(valores)}})
d.wasGeneratedBy(e_valores, act_init_val)

# Inicialização de 'total'
_step += 1
t_start = datetime.now(timezone.utc)
total = 0
t_end = datetime.now(timezone.utc)
act_init_tot = d.activity(f'ex:init_total_{{_step}}', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_init_tot, a_script)
e_total_curr = d.entity(f'ex:total_v{{_step}}', {{'prov:value': str(total)}})
d.wasGeneratedBy(e_total_curr, act_init_tot)

# Desdobramento dinâmico do laço (DAG garantido)
for idx, v in enumerate(valores):
    _step += 1
    t_start = datetime.now(timezone.utc)
    total = total + v
    t_end = datetime.now(timezone.utc)

    act_iter = d.activity(f'ex:soma_iter_{{idx}}_{{_step}}', startTime=t_start, endTime=t_end)
    d.wasAssociatedWith(act_iter, a_script)

    e_item = d.entity(f'ex:item_{{idx}}_{{_step}}', {{'prov:value': str(v)}})
    d.wasDerivedFrom(e_item, e_valores)

    d.used(act_iter, e_total_curr)
    d.used(act_iter, e_item)

    e_total_next = d.entity(f'ex:total_v{{_step}}', {{'prov:value': str(total)}})
    d.wasGeneratedBy(e_total_next, act_iter)
    d.wasDerivedFrom(e_total_next, e_total_curr)
    d.wasDerivedFrom(e_total_next, e_item)
    e_total_curr = e_total_next

print(total)
d.serialize('provenance_w3c.json', format='json')
```

### Tarefa
Instrumente o script abaixo em **Granularidade Fina**, desdobrando laços/recursões sem fechar ciclos. Retorne APENAS o código Python completo e executável, sem explicações.

## INPUT:
{input_code}

## OUTPUT:
"""
