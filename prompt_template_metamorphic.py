# prompt_template_metamorphic.py
# VERSÃO METAMÓRFICA - Otimizada para Invariantes W3C-PROV (3.1-3.4) e Relações Metamórficas (RM1-RM6)

PROMPT_METAMORPHIC_TEMPLATE = """
Você é um engenheiro de software especialista em proveniência de dados no padrão W3C-PROV e em verificação formal de grafos causais.
Sua tarefa é instrumentar o script Python fornecido inserindo código `prov` de forma **estritamente determinística, canônica e em conformidade com invariantes ontológicas e relações metamórficas**.

## 1. CONTRATO CANÔNICO PARA RELAÇÕES METAMÓRFICAS (CRÍTICO)
O grafo gerado será validado automaticamente por um comparador topológico (NetworkX `DiGraphMatcher`). Para garantir estabilidade entre o script original e versões mutadas, obedeça rigorosamente a estas 6 regras:

1. **Invariância a Refatoração e Permutação (RM1 / RM2 - Isomorfismo):**
   - A estrutura do grafo (número de nós e arestas) deve depender EXCLUSIVAMENTE das operações de fluxo de dados executadas, NUNCA de nomes de variáveis, comentários, espaçamento ou ordem de blocos independentes.
   - Use **exatamente 1 Agente fixo** (`a_script = d.agent('ex:script_agent')`) associado a TODAS as `Activity`.
   - **Proibição de fusão arbitrária:** Nunca agrupe duas operações independentes na mesma `Activity`, nem divida uma mesma operação em múltiplas `Activity` extras. Cada atribuição/transformação semântica de dado corresponde a exatamente 1 `Activity`.

2. **Determinismo de Expansão (RM3 - Subgrafo com Delta Consistente):**
   - Cada nova instrução de I/O, log ou transformação de dado adicionada ao código DEVE acrescentar exatamente o seu padrão canônico (`1 Activity + 1 Entity` gerada, conectadas às entradas usadas), preservando intactos os nós e arestas das operações pré-existentes.

3. **Instrumentação Estritamente Dinâmica / Podagem (RM4 - Redução de Subgrafo):**
   - **NUNCA** pré-declare `Entity` ou `Activity` no topo do script.
   - Insira o código de captura **imediatamente ao redor da instrução real** e **dentro** do mesmo bloco condicional (`if`/`elif`/`else`) ou função. Se um ramo não for executado ou uma entrada for removida do código, nenhum nó ou aresta correspondente a ele pode existir no grafo.
   - Registre `d.used(act, ent)` SOMENTE para entidades efetivamente lidas pela instrução daquela `Activity`.

4. **Precedência Temporal Real (RM5 / Invariante 3.3):**
   - Use o helper `_now()` (`datetime.now(timezone.utc)`).
   - Capture `t_start = _now()` ANTES da instrução original e `t_end = _now()` DEPOIS.
   - Registre sempre `d.activity(act_id, startTime=t_start, endTime=t_end)`, `d.used(act, ent, time=t_start)` e `d.wasGeneratedBy(ent_out, act, time=t_end)`.
   - Isso garante matematicamente que `t_generation(E) <= t_usage(E)`, mesmo quando blocos independentes têm sua ordem invertida.

5. **Desdobramento de Laços/Recursão e Aciclicidade (RM6 / Invariantes 3.2 e 3.4):**
   - O grafo DEVE ser um **DAG estrito** (`nx.is_directed_acyclic_graph == True`).
   - Cada `Entity` DEVE ter no máximo **1 aresta `wasGeneratedBy`** (Unicidade de Origem Primária).
   - Utilize o gerador de IDs únicos `_uid(prefix)` baseado em contador global. Para variáveis mutadas em laços (`for`/`while`), recursões ou reatribuições, crie SEMPRE uma nova `Entity` (mantendo a referência da versão atual em uma variável Python, ex.: `e_x = d.entity(_uid('ent'), ...)`), conectando-a à versão anterior via `d.wasDerivedFrom(e_x_nova, e_x_antiga)`.
   - Assim, um laço de N iterações e o mesmo código desdobrado (*loop unrolling*) produzirão grafos **estruturalmente isomórficos e 100% acíclicos**.

6. **Tipagem Ontológica Estrita (Invariante 3.1):**
   - `d.used(activity, entity, time=...)` -> EXCLUSIVAMENTE `(Activity -> Entity)`
   - `d.wasGeneratedBy(entity, activity, time=...)` -> EXCLUSIVAMENTE `(Entity -> Activity)`
   - `d.wasDerivedFrom(entity_gerada, entity_usada)` -> EXCLUSIVAMENTE `(Entity -> Entity)`
   - `d.wasAssociatedWith(activity, agent)` -> EXCLUSIVAMENTE `(Activity -> Agent)`
   - NUNCA inverta a ordem dos argumentos.

## 2. REGRAS DE IMPLEMENTAÇÃO PYTHON
- Inclua sempre o bloco de infraestrutura (helpers `_now` e `_uid`) no topo do script.
- Namespace padrão: `d.add_namespace('ex', 'http://example.org/')`.
- **Atributos Seguros:** Qualquer valor passado em atributos de `d.entity(...)` deve ser imutável; converta listas, dicts e objetos com `str(val)` ou `json.dumps(val, default=str)`.
- **Arquivo de Saída:** Salve obrigatoriamente no final do script com `d.serialize('provenance_w3c.json', format='json')`.
- **Integridade Funcional:** Não altere saídas (`print`), retornos ou lógica de negócio do script original.

## 3. EXEMPLO CANÔNICO (FEW-SHOT)
### INPUT:
```python
x = 10
y = 20
for i in range(2):
    x = x + y
if x > 100:
    z = x * 2
else:
    z = x - 5
print(z)
```

### OUTPUT:
```python
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
    return f'ex:{{prefix}}_{{_prov_counter}}'

def _now():
    return datetime.now(timezone.utc)
# ----------------------------------------

# Operação 1: Inicialização de x
t_start = _now()
x = 10
t_end = _now()
act = d.activity(_uid('act'), startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act, a_script)
e_x = d.entity(_uid('ent'), {{'prov:value': str(x)}})
d.wasGeneratedBy(e_x, act, time=t_end)

# Operação 2: Inicialização de y
t_start = _now()
y = 20
t_end = _now()
act = d.activity(_uid('act'), startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act, a_script)
e_y = d.entity(_uid('ent'), {{'prov:value': str(y)}})
d.wasGeneratedBy(e_y, act, time=t_end)

# Operação 3: Laço desdobrado dinamicamente (satisfaz RM6 / Inv. 3.2 e 3.4)
for i in range(2):
    t_start = _now()
    x = x + y
    t_end = _now()
    act = d.activity(_uid('act'), startTime=t_start, endTime=t_end)
    d.wasAssociatedWith(act, a_script)
    d.used(act, e_x, time=t_start)
    d.used(act, e_y, time=t_start)
    e_x_new = d.entity(_uid('ent'), {{'prov:value': str(x)}})
    d.wasGeneratedBy(e_x_new, act, time=t_end)
    d.wasDerivedFrom(e_x_new, e_x)
    d.wasDerivedFrom(e_x_new, e_y)
    e_x = e_x_new

# Operação 4: Condicional dinâmica (satisfaz RM4 - ramo não executado não gera nós)
if x > 100:
    t_start = _now()
    z = x * 2
    t_end = _now()
    act = d.activity(_uid('act'), startTime=t_start, endTime=t_end)
    d.wasAssociatedWith(act, a_script)
    d.used(act, e_x, time=t_start)
    e_z = d.entity(_uid('ent'), {{'prov:value': str(z)}})
    d.wasGeneratedBy(e_z, act, time=t_end)
    d.wasDerivedFrom(e_z, e_x)
else:
    t_start = _now()
    z = x - 5
    t_end = _now()
    act = d.activity(_uid('act'), startTime=t_start, endTime=t_end)
    d.wasAssociatedWith(act, a_script)
    d.used(act, e_x, time=t_start)
    e_z = d.entity(_uid('ent'), {{'prov:value': str(z)}})
    d.wasGeneratedBy(e_z, act, time=t_end)
    d.wasDerivedFrom(e_z, e_x)

print(z)
d.serialize('provenance_w3c.json', format='json')
```

## 4. TAREFA
Instrumente o script Python abaixo seguindo rigorosamente o Contrato Canônico W3C-PROV. Retorne APENAS o código Python completo e executável, sem explicações, prefácios ou blocos de texto adicionais.

## INPUT:
{input_code}

## OUTPUT:
"""
