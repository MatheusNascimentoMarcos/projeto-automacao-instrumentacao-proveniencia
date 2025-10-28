# prompt_template.py

PROMPT_MESTRE_TEMPLATE = """
Você é um engenheiro de software especialista em proveniência de dados e instrumentação de workflows científicos. Sua tarefa é analisar um script em Python e inserir o código necessário para capturar a proveniência prospectiva e retrospectiva, seguindo o padrão da ferramenta DfAnalyzer.

## Contexto e Conceitos
[cite_start]A proveniência prospectiva descreve o plano de execução com `Transformations` e `Sets` de entrada/saída [cite: 8, 28-29].
A proveniência retrospectiva registra a execução real com `Tasks` e `DataSets` contendo valores concretos.
[cite_start]As `Tasks` retrospectivas devem ter uma dependência das `Transformations` prospectivas correspondentes [cite: 81-82].

## Instruções (Chain of Thought)
Siga estes passos para instrumentar o código fornecido:
1.  **Análise Prospectiva**: Leia todo o script e identifique as principais etapas lógicas (atividades). Para cada etapa, crie um objeto `Transformation`.
2.  [cite_start]**Definição de Entradas/Saídas Prospectivas**: Para cada `Transformation`, defina os `Sets` de entrada e saída, especificando os nomes e tipos dos atributos [cite: 32, 34-35, 42].
3.  **Análise Retrospectiva**: Mapeie cada `Transformation` para uma `Task` no código, usando o nome da transformação.
4.  **Instrumentação do Código**: Insira as chamadas `task.begin()` e `task.end()` nos locais apropriados do código original para delimitar a execução de cada tarefa.
5.  **Captura de Dados Reais**: Identifique as variáveis que contêm os dados de entrada e saída reais e use-as para criar os `DataSets` e adicioná-los à Task com `task.add_dataset()`.
6.  **Dependências**: Certifique-se de que as `Tasks` que dependem de resultados anteriores (como a soma que depende da extração) incluam o parâmetro `dependency=...` na sua criação.

## Exemplo de Poucos Tiros (Few-shot Example)
(Este exemplo é baseado fielmente no tutorial em anexo)

### INPUT (Código Original):
```python
# Script que soma dois números fixos
PRIMEIRO_NUMERO = 5
SEGUNDO_NUMERO = 1
RESULTADO_SOMA = PRIMEIRO_NUMERO + SEGUNDO_NUMERO
print(f"O resultado é: {{RESULTADO_SOMA}}")

### OUTPUT (Código Instrumentado):
# Importações necessárias da biblioteca de proveniência
from dfanalyzer import Transformation, Set, SetType, Attribute, AttributeType, Dataflow
from dfanalyzer import Task, DataSet, Element

# --- CONFIGURAÇÃO INICIAL DO DATAFLOW ---
# (Assumimos que 'df' é um objeto Dataflow global ou passado como parâmetro)
# Para este exemplo, vamos instanciar:
df = Dataflow()
# (O tutorial infere que o dataflow é salvo e seu tag é recuperado)
df.save()
dataflow_tag = df.tag

# =======================================================
# === FASE 1: PROVENIÊNCIA PROSPECTIVA (O PLANO)
# =======================================================

# --- Transformação 1: Extrair Números ---
tf1 = Transformation("Extrair Numeros") # 
tf1_input = Set("iExtrair Numeros", SetType.INPUT,
                [Attribute("SOMA_FILE", AttributeType.FILE)]) #
tf1_output = Set("oExtrair Numeros", SetType.OUTPUT,
                 [cite_start][Attribute("PRIMEIRO_NUMERO", AttributeType.NUMERIC), # [cite: 34-35]
                  Attribute("SEGUNDO_NUMERO", AttributeType.NUMERIC)]) #
df.add_transformation(tf1) #
df.add_set(tf1_input, tf1) #
df.add_set(tf1_output, tf1) #


# --- Transformação 2: Executar Soma ---
tf2 = Transformation("ExecutarSoma") #
tf1_output.set_type(SetType.INPUT) # A saída de tf1 é a entrada de tf2
tf1_output.dependency = tf1.tag #
tf2_output = Set("oExecutarSoma", SetType.OUTPUT,
                 [Attribute("RESULTADO_SOMA", AttributeType.NUMERIC)]) #
df.add_transformation(tf2) #
df.add_set(tf1_output, tf2) #
df.add_set(tf2_output, tf2) #

df.save()
print("Proveniência Prospectiva salva.")

# =======================================================
# === FASE 2: PROVENIÊNCIA RETROSPECTIVA (A EXECUÇÃO)
# =======================================================

# --- Task 1: Execução de "Extrair Numeros" ---
# (Simulando a leitura de um arquivo)
[cite_start]t1 = Task(1, dataflow_tag, "Extrair Numeros") # [cite: 51-52]
# Embora o script original não leia um arquivo, simulamos a entrada esperada
[cite_start]t1_input = DataSet("iExtrair Numeros", [Element(["/path/numeros"])]) # [cite: 52-53]
t1.add_dataset(t1_input) # 
t1.begin() #

# --- Bloco de Código Original 1 ---
PRIMEIRO_NUMERO = 5 #
SEGUNDO_NUMERO = 1 #
# --- Fim do Bloco de Código ---

[cite_start]t1_output = DataSet("oExtrair Numeros", [Element([PRIMEIRO_NUMERO, SEGUNDO_NUMERO])]) # [cite: 58-59, 62]
t1.add_dataset(t1_output) #
t1.end() #

# --- Task 2: Execução de "ExecutarSoma" ---
t2 = Task(2, dataflow_tag, "ExecutarSoma", dependency=t1) #
t2.begin() #

# --- Bloco de Código Original 2 ---
RESULTADO_SOMA = PRIMEIRO_NUMERO + SEGUNDO_NUMERO #
# --- Fim do Bloco de Código ---

[cite_start]t2_output = DataSet("oExecutarSoma", [Element([RESULTADO_SOMA])]) # [cite: 74-75]
t2.add_dataset(t2_output) #
t2.end() #

df.save()
print(f"Proveniência Retrospectiva salva. O resultado é: {{RESULTADO_SOMA}}")

### Tarefa
Agora, instrumente o seguinte script. Retorne apenas o código Python completo e instrumentado, sem explicações, prefácios ou comentários adicionais.

### INPUT (Código Original):
```python
{input_code}
```

### OUTPUT (Código Instrumentado Desejado):
"""