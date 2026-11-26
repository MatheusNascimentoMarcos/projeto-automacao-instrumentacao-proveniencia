# prompt_template_coarse.py
# Granularidade GROSSA (Coarse-Grained / Black-Box) com Invariantes W3C-PROV

PROMPT_COARSE_TEMPLATE = """
Você é um engenheiro de software especialista em proveniência de dados (W3C-PROV) e instrumentação de workflows em Python. Sua tarefa é instrumentar o script fornecido para capturar proveniência retrospectiva em **GRANULARIDADE GROSSA (Coarse-Grained / Black-Box)**.

## Heurísticas de Captura (Nível Grosso)
1. **Entity (O que capturar):**
   - Capture APENAS artefatos de fronteira: arquivos lidos/escritos, conexões/respostas de APIs, datasets carregados/salvos, modelos treinados e resultados finais exibidos (`print`) ou persistidos.
   - **IGNORE** variáveis temporárias, contadores, índices de laços e cálculos intermediários simples (`sum`, `len`, slicing).
2. **Activity (O que capturar):**
   - Modele cada **função de alto nível** ou **bloco lógico macro** (ex.: Carregamento, Pré-processamento, Treinamento, Exportação) como uma única `Activity` caixa-preta.
   - Laços (`for`/`while`) internos a uma etapa macro NÃO devem ser desdobrados; encapsule o bloco inteiro em uma única `Activity`.
3. **Agent:**
   - Defina o script como o `Agent` principal (`a_script = d.agent('ex:script_executor')`).

## Invariantes Ontológicas e Causais Obrigatórias (W3C-PROV)
1. **Tipagem Estrita (Domínio/Alcance):**
   - `d.used(activity, entity)` -> SEMPRE de `Activity` para `Entity`.
   - `d.wasGeneratedBy(entity, activity)` -> SEMPRE de `Entity` para `Activity`.
   - `d.wasDerivedFrom(entity_nova, entity_origem)` -> SEMPRE de `Entity` para `Entity`.
   - `d.wasAssociatedWith(activity, agent)` -> SEMPRE de `Activity` para `Agent`.
2. **Aciclicidade Causal (DAG):**
   - O grafo deve ser estritamente acíclico. Nunca reutilize o mesmo identificador de `Entity` ou `Activity`.
3. **Consistência Temporal (Precedência):**
   - Capture `t_start = datetime.now(timezone.utc)` ANTES da etapa macro e `t_end = datetime.now(timezone.utc)` DEPOIS.
   - Passe `startTime=t_start, endTime=t_end` em `d.activity(...)`. Garanta que toda `Entity` seja gerada antes ou no mesmo instante em que for consumida.
4. **Unicidade de Origem Primária:**
   - Cada `Entity` pode ter no máximo UMA relação `wasGeneratedBy`. Se um arquivo ou dataset for sobrescrito, crie uma nova `Entity` (ex.: `ex:dataset_v2`) e ligue-a à anterior via `d.wasDerivedFrom(e_v2, e_v1)`.

## Regras Técnicas e de Saída
- Use `import prov.model as prov` e `from datetime import datetime, timezone`.
- Namespace padrão: `d.add_namespace('ex', 'http://example.org/')`.
- **Atributos:** Converta listas/dicionários Python para string (`str(val)` ou `json.dumps(val)`) antes de passar como atributo à biblioteca `prov`.
- Salve o grafo EXATAMENTE em `'provenance_w3c.json'` usando `d.serialize('provenance_w3c.json', format='json')`.
- Não altere a semântica nem interrompa a execução do código original.

## Exemplo (Few-Shot - Granularidade Grossa)
### INPUT:
```python
import numpy as np

dados = [15.2, 16.1, 14.8, 15.5, 17.0]
caminho_in = "data/raw.csv"

soma = 0
for x in dados:
    soma += x
media = soma / len(dados)

caminho_out = "results/media.txt"
print(f"Média: {{media}} salva em {{caminho_out}}")
```

### OUTPUT:
```python
import numpy as np
import prov.model as prov
import json
from datetime import datetime, timezone

d = prov.ProvDocument()
d.add_namespace('ex', 'http://example.org/')
a_script = d.agent('ex:script_executor')

# Etapa Macro 1: Carregamento
t_start = datetime.now(timezone.utc)
dados = [15.2, 16.1, 14.8, 15.5, 17.0]
caminho_in = "data/raw.csv"
t_end = datetime.now(timezone.utc)

act_load = d.activity('ex:carregar_dados', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_load, a_script)
e_in = d.entity('ex:arquivo_entrada', {{'prov:location': caminho_in}})
e_dados = d.entity('ex:dados_brutos', {{'ex:value': json.dumps(dados)}})
d.used(act_load, e_in)
d.wasGeneratedBy(e_dados, act_load)
d.wasDerivedFrom(e_dados, e_in)

# Etapa Macro 2: Processamento (laço encapsulado como caixa-preta)
t_start = datetime.now(timezone.utc)
soma = 0
for x in dados:
    soma += x
media = soma / len(dados)
t_end = datetime.now(timezone.utc)

act_proc = d.activity('ex:calcular_media', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_proc, a_script)
e_media = d.entity('ex:media_final', {{'prov:value': str(media)}})
d.used(act_proc, e_dados)
d.wasGeneratedBy(e_media, act_proc)
d.wasDerivedFrom(e_media, e_dados)

# Etapa Macro 3: Saída
t_start = datetime.now(timezone.utc)
caminho_out = "results/media.txt"
print(f"Média: {{media}} salva em {{caminho_out}}")
t_end = datetime.now(timezone.utc)

act_save = d.activity('ex:salvar_resultado', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_save, a_script)
e_out = d.entity('ex:arquivo_saida', {{'prov:location': caminho_out}})
d.used(act_save, e_media)
d.wasGeneratedBy(e_out, act_save)
d.wasDerivedFrom(e_out, e_media)

d.serialize('provenance_w3c.json', format='json')
```

### Tarefa
Instrumente o script abaixo em **Granularidade Grossa**. Retorne APENAS o código Python completo e executável, sem explicações ou comentários fora do código.

## INPUT:
{input_code}

## OUTPUT:
"""
