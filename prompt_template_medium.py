# prompt_template_medium.py
# Granularidade MÉDIA (Híbrida / Etapas Lógicas e Dados Relevantes) com Invariantes W3C-PROV

PROMPT_MEDIUM_TEMPLATE = """
Você é um engenheiro de software especialista em proveniência de dados (W3C-PROV) e instrumentação de workflows em Python. Sua tarefa é instrumentar o script fornecido para capturar proveniência retrospectiva em **GRANULARIDADE MÉDIA (Híbrida)**.

## Heurísticas de Captura (Nível Médio)
1. **Entity (O que capturar):**
   - Artefatos externos (arquivos, APIs, bancos de dados).
   - Parâmetros críticos de configuração (hiperparâmetros, limiares, flags de filtro).
   - Variáveis de dados estruturados (DataFrames, listas/dicionários principais) e resultados intermediários que servem de entrada para mais de uma etapa ou para a saída final.
   - **Versionamento de Mutações:** Se uma variável relevante for reatribuída ou modificada in-place (ex.: `df = df.dropna()`), crie uma NOVA `Entity` com sufixo de versão (`ex:df_v1`, `ex:df_v2`) para preservar a imutabilidade.
2. **Activity (O que capturar):**
   - Cada etapa lógica de transformação (leitura, limpeza, filtragem, agregação, modelagem, escrita) e cada chamada de função definida pelo usuário.
   - Para scripts curtos sem I/O de arquivos, capture as transformações de variáveis principais como `Activity`.
3. **Agent:**
   - Associe todas as `Activity` ao agente do script (`a_script = d.agent('ex:script_executor')`).

## Invariantes Ontológicas e Causais Obrigatórias (W3C-PROV)
1. **Tipagem Estrita (Domínio/Alcance):**
   - `d.used(activity, entity)` | `d.wasGeneratedBy(entity, activity)` | `d.wasDerivedFrom(entity_nova, entity_antiga)` | `d.wasAssociatedWith(activity, agent)`.
2. **Aciclicidade Causal (DAG):**
   - Nunca crie ciclos. Nenhuma `Entity` pode derivar direta ou indiretamente de si mesma.
3. **Consistência Temporal (Precedência):**
   - Registre `t_start = datetime.now(timezone.utc)` antes e `t_end = datetime.now(timezone.utc)` depois de cada `Activity`, atribuindo `startTime=t_start, endTime=t_end`.
4. **Unicidade de Origem Primária:**
   - Cada identificador de `Entity` deve aparecer como alvo de `d.wasGeneratedBy(...)` no máximo UMA vez.

## Regras Técnicas e de Saída
- Imports obrigatórios: `import prov.model as prov`, `import json`, `from datetime import datetime, timezone`.
- Namespace padrão: `d.add_namespace('ex', 'http://example.org/')`.
- Converta valores mutáveis (`list`, `dict`, `set`) em atributos para `str(valor)` ou `json.dumps(valor)`.
- Salve EXATAMENTE em `'provenance_w3c.json'` com `format='json'`.
- Se houver lógica Python executável, o script DEVE gerar proveniência válida.

## Exemplo (Few-Shot - Granularidade Média)
### INPUT:
```python
limiar = 15.0
dados = [14.2, 16.5, 13.8, 17.1]
filtrados = [x for x in dados if x > limiar]
media = sum(filtrados) / len(filtrados)
print(media)
```

### OUTPUT:
```python
import prov.model as prov
import json
from datetime import datetime, timezone

d = prov.ProvDocument()
d.add_namespace('ex', 'http://example.org/')
a_script = d.agent('ex:script_executor')

# Parâmetros e Dados Iniciais
t_start = datetime.now(timezone.utc)
limiar = 15.0
dados = [14.2, 16.5, 13.8, 17.1]
t_end = datetime.now(timezone.utc)

act_init = d.activity('ex:inicializar_dados', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_init, a_script)
e_limiar = d.entity('ex:limiar_v1', {{'prov:value': str(limiar)}})
e_dados = d.entity('ex:dados_v1', {{'prov:value': json.dumps(dados)}})
d.wasGeneratedBy(e_limiar, act_init)
d.wasGeneratedBy(e_dados, act_init)

# Etapa de Filtragem
t_start = datetime.now(timezone.utc)
filtrados = [x for x in dados if x > limiar]
t_end = datetime.now(timezone.utc)

act_filter = d.activity('ex:filtrar_dados', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_filter, a_script)
d.used(act_filter, e_dados)
d.used(act_filter, e_limiar)
e_filtrados = d.entity('ex:filtrados_v1', {{'prov:value': json.dumps(filtrados)}})
d.wasGeneratedBy(e_filtrados, act_filter)
d.wasDerivedFrom(e_filtrados, e_dados)

# Etapa de Agregação
t_start = datetime.now(timezone.utc)
media = sum(filtrados) / len(filtrados)
t_end = datetime.now(timezone.utc)

act_agg = d.activity('ex:calcular_media', startTime=t_start, endTime=t_end)
d.wasAssociatedWith(act_agg, a_script)
d.used(act_agg, e_filtrados)
e_media = d.entity('ex:media_v1', {{'prov:value': str(media)}})
d.wasGeneratedBy(e_media, act_agg)
d.wasDerivedFrom(e_media, e_filtrados)

print(media)
d.serialize('provenance_w3c.json', format='json')
```

### Tarefa
Instrumente o script abaixo em **Granularidade Média**. Retorne APENAS o código Python completo e executável, sem explicações.

## INPUT:
{input_code}

## OUTPUT:
"""
