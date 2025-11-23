import os
import json
import subprocess
import shutil

# --- CONFIGURAÇÃO ---

# 1. Recupera a API Key do ambiente Windows
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("⚠️  AVISO: A variável GEMINI_API_KEY não foi encontrada.")
    print("   Execute '$env:GEMINI_API_KEY = ...' no PowerShell antes.")

# 2. Configuração do Docker
IMG_NAME = "ia-prov-wrapper"
CURRENT_DIR = os.getcwd()
DIR_TESTES = "temp_metamorfico"

# Comando base do Docker (com volume montado e API Key)
DOCKER_BASE_CMD = [
    "docker", "run",
    "--rm",
    "-e", f"GEMINI_API_KEY={api_key}",
    "-v", f"{CURRENT_DIR}:/app",
    IMG_NAME
]

def setup():
    if os.path.exists(DIR_TESTES):
        shutil.rmtree(DIR_TESTES)
    os.makedirs(DIR_TESTES)

def cleanup():
    # Comente a linha abaixo para inspecionar os arquivos após o teste
    #shutil.rmtree(DIR_TESTES)
    pass

def extrair_metricas_prov(caminho_json):
    """Lê o JSON e conta Atividades e Entidades. Retorna (0,0) se o arquivo não existir."""
    # CORREÇÃO: Se o caminho for None (arquivo não gerado), retorna 0
    if caminho_json is None:
        return 0, 0
        
    try:
        with open(caminho_json, 'r') as f:
            dados = json.load(f)
        n_activities = len(dados.get('activity', {}))
        n_entities = len(dados.get('entity', {}))
        return n_activities, n_entities
    except (FileNotFoundError, json.JSONDecodeError):
        # Se o arquivo existir mas estiver vazio ou corrompido
        return 0, 0

def to_linux_path(path):
    """Converte caminhos do Windows (\\) para Linux (/) para o Docker."""
    return path.replace("\\", "/")

def executar_instrumentacao(nome_script_entrada, nome_script_saida):
    """
    Versão DEBUG: Mostra o output do terminal para encontrarmos o erro.
    """
    path_entrada_rel = os.path.join(DIR_TESTES, nome_script_entrada)
    path_saida_rel = os.path.join(DIR_TESTES, nome_script_saida)

    arg_entrada = to_linux_path(path_entrada_rel)
    arg_saida = to_linux_path(path_saida_rel)
    
    print(f"   ➤ Rodando IA em: {nome_script_entrada}...")
    
    # --- PASSO 1: Rodar a Instrumentação (IA) ---
    # REMOVI O DEVNULL AQUI PARA VERMOS O ERRO DA API
    cmd_instrumentacao = DOCKER_BASE_CMD + [
        "python3", "instrument_workflow.py", arg_entrada, arg_saida
    ]
    result_ia = subprocess.run(cmd_instrumentacao) # Sem capture_output para imprimir direto
    
    if result_ia.returncode != 0:
        print(f"   ❌ ERRO FATAL: O instrument_workflow.py falhou no arquivo {nome_script_entrada}!")
        return None

    # --- PASSO 2: Rodar o Script Gerado ---
    print(f"   ➤ Executando script gerado: {nome_script_saida}...")
    cmd_execucao = DOCKER_BASE_CMD + ["python3", arg_saida]
    
    # REMOVI O DEVNULL AQUI TAMBÉM
    result_exec = subprocess.run(cmd_execucao)
    
    if result_exec.returncode != 0:
        print(f"   ❌ ERRO FATAL: O script gerado contém erros de sintaxe ou falta biblioteca!")
    
    # --- PASSO 3: Organizar o Resultado ---
    json_padrao = "provenance_w3c.json"
    json_destino = os.path.join(DIR_TESTES, f"prov_{nome_script_entrada}.json")
    
    if os.path.exists(json_padrao):
        if os.path.exists(json_destino):
            os.remove(json_destino)
        shutil.move(json_padrao, json_destino)
        return json_destino
    elif os.path.exists("provenance.json"):
        shutil.move("provenance.json", json_destino)
        return json_destino
        
    print(f"   ⚠️  AVISO: Nenhum JSON foi gerado para {nome_script_entrada}.")
    return None

def criar_arquivo(nome, conteudo):
    with open(os.path.join(DIR_TESTES, nome), 'w') as f:
        f.write(conteudo)

# --- CENÁRIOS DE TESTE (Mantidos iguais) ---

def teste_equivalencia_sintatica():
    print("\n🔵 [1/3] Testando Equivalência Sintática (Loop vs List Comprehension)...")
    
    # REMOVIDO: import prov.model as prov
    code_a = """
dados = [1, 2, 3, 4, 5]
resultado = []
for x in dados:
    resultado.append(x * 2)
"""
    code_b = """
dados = [1, 2, 3, 4, 5]
resultado = [x * 2 for x in dados]
"""
    criar_arquivo("equiv_loop.py", code_a)
    criar_arquivo("equiv_list.py", code_b)
    
    json_a = executar_instrumentacao("equiv_loop.py", "equiv_loop_inst.py")
    json_b = executar_instrumentacao("equiv_list.py", "equiv_list_inst.py")
    
    act_a, ent_a = extrair_metricas_prov(json_a)
    act_b, ent_b = extrair_metricas_prov(json_b)
    
    print(f"   Loop: {act_a} Atividades | List Comp: {act_b} Atividades")
    
    if act_a == act_b and act_a > 0:
        print("✅ SUCESSO: Estrutura consistente.")
    else:
        print("❌ FALHA: Estrutura inconsistente ou zero.")

def teste_permutacao_blocos():
    print("\n🔵 [2/3] Testando Permutação de Blocos...")
    
    # REMOVIDO: import prov.model as prov
    code_a = """
a = 10
a = a + 5
b = 20
b = b * 2
"""
    code_b = """
b = 20
b = b * 2
a = 10
a = a + 5
"""
    criar_arquivo("perm_a.py", code_a)
    criar_arquivo("perm_b.py", code_b)
    
    json_a = executar_instrumentacao("perm_a.py", "perm_a_inst.py")
    json_b = executar_instrumentacao("perm_b.py", "perm_b_inst.py")
    
    act_a, ent_a = extrair_metricas_prov(json_a)
    act_b, ent_b = extrair_metricas_prov(json_b)
    
    if act_a == act_b and ent_a == ent_b and act_a > 0:
        print(f"✅ SUCESSO: Grafo mantido ({act_a} nós).")
    else:
        print(f"❌ FALHA: A: {act_a} vs B: {act_b}")

def teste_decomposicao():
    print("\n🔵 [3/3] Testando Decomposição...")
    
    # REMOVIDO: import prov.model as prov
    code_full = """
raw_data = [10, 20, 30]
processed = [x - 5 for x in raw_data]
"""
    code_p1 = """
raw_data = [10, 20, 30]
"""
    code_p2 = """
raw_data = [10, 20, 30] 
processed = [x - 5 for x in raw_data]
"""
    
    criar_arquivo("decomp_full.py", code_full)
    criar_arquivo("decomp_p1.py", code_p1)
    criar_arquivo("decomp_p2.py", code_p2)
    
    json_full = executar_instrumentacao("decomp_full.py", "decomp_full_inst.py")
    json_p1 = executar_instrumentacao("decomp_p1.py", "decomp_p1_inst.py")
    json_p2 = executar_instrumentacao("decomp_p2.py", "decomp_p2_inst.py")
    
    act_full, _ = extrair_metricas_prov(json_full)
    act_p1, _ = extrair_metricas_prov(json_p1)
    act_p2, _ = extrair_metricas_prov(json_p2)
    
    soma_partes = act_p1 + act_p2
    
    print(f"   Completo: {act_full} | Soma Partes: {soma_partes}")
    
    if abs(act_full - soma_partes) <= 2 and act_full > 0:
        print("✅ SUCESSO: Decomposição coerente.")
    else:
        print("❌ FALHA: Inconsistência na decomposição.")

# --- MAIN ---
if __name__ == "__main__":
    setup()
    try:
        teste_equivalencia_sintatica()
        teste_permutacao_blocos()
        teste_decomposicao()
    finally:
        cleanup()
        print("\nTeste finalizado.")