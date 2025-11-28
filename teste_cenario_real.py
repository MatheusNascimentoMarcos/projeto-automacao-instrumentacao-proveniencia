import os
import json
import subprocess
import shutil
import glob

# --- CORREÇÃO DO IMPORT: Aponta para o motor que você já tem ---
from mutator_engine_advanced import mutar_equivalencia_sintatica, mutar_permutacao_blocos, mutar_decomposicao

# --- CONFIGURAÇÃO ---
# Se o seu script se chama ETL.py, mude aqui. Se for meu_script.py, mantenha.
SCRIPT_ALVO = "ETL.py" 

api_key = os.environ.get("GEMINI_API_KEY")
IMG_NAME = "ia-prov-wrapper"
CURRENT_DIR = os.getcwd()
DIR_TESTES = "temp_real_advanced"
# Instala pandas e prov antes de rodar, caso falte na imagem
DOCKER_BASE_CMD = ["docker", "run", "--rm", "-e", f"GEMINI_API_KEY={api_key}", "-v", f"{CURRENT_DIR}:/app", IMG_NAME]

def setup():
    if os.path.exists(DIR_TESTES): shutil.rmtree(DIR_TESTES)
    os.makedirs(DIR_TESTES)

def cleanup():
    # Comente a linha abaixo se quiser ver os arquivos gerados (debug)
    # shutil.rmtree(DIR_TESTES) 
    pass

def to_linux_path(path): return path.replace("\\", "/")

def extrair_metricas_prov(caminho_json):
    if not caminho_json or not os.path.exists(caminho_json): return 0, 0
    try:
        with open(caminho_json, 'r') as f: d = json.load(f)
        return len(d.get('activity', {})), len(d.get('entity', {}))
    except: return 0, 0

import glob # Adicione isso no topo imports

def executar_pipeline(nome_arq, step_name):
    """Roda Instrumentação e Execução, garantindo diretórios corretos"""
    # Nomes de arquivo (apenas o nome, sem pasta, pois vamos mudar o workdir)
    nome_script_inst = f"inst_{nome_arq}"
    
    # Caminhos completos para a fase de instrumentação
    path_in_abs = to_linux_path(os.path.join(DIR_TESTES, nome_arq))
    path_out_abs = to_linux_path(os.path.join(DIR_TESTES, nome_script_inst))
    
    print(f"   ➤ Instrumentando {nome_arq}...")
    
    # 1. INSTRUMENTAÇÃO (Roda na raiz, lendo/escrevendo na temp)
    cmd_inst = DOCKER_BASE_CMD + ["python3", "instrument_workflow.py", path_in_abs, path_out_abs]
    res_inst = subprocess.run(cmd_inst) # stdout=subprocess.DEVNULL se quiser silenciar
    
    if res_inst.returncode != 0:
        print(f"   ❌ ERRO FATAL: Falha na instrumentação de {nome_arq}")
        return None
    
    # 2. PREPARAÇÃO DO AMBIENTE (Copiar CSVs para a pasta temp)
    # Isso é vital para o script rodar sem erro de FileNotfound
    csvs = [f for f in os.listdir('.') if f.endswith('.csv')]
    for csv in csvs:
        shutil.copy(csv, os.path.join(DIR_TESTES, csv))

    # 3. EXECUÇÃO (Roda DENTRO da pasta temp)
    if os.path.exists(os.path.join(DIR_TESTES, nome_script_inst)):
        print(f"   ▶️ Executando script gerado...")
        
        # TRUQUE DO DOCKER: -w define o diretório de trabalho DENTRO do container
        # Assim, o 'provenance_w3c.json' será salvo dentro de /app/temp_real_advanced
        workdir_docker = f"/app/{DIR_TESTES}"
        
        cmd_exec = [
            "docker", "run", "--rm",
            "-e", f"GEMINI_API_KEY={api_key}",
            "-v", f"{CURRENT_DIR}:/app",
            "-w", workdir_docker,  # <--- MUDANÇA CHAVE: Roda dentro da pasta temp
            IMG_NAME,
            "python3", nome_script_inst # Roda apenas o nome do arquivo
        ]
        
        # Roda e captura erro se houver
        res_exec = subprocess.run(cmd_exec) 
        if res_exec.returncode != 0:
            print(f"   ⚠️  Aviso: O script instrumentado falhou na execução.")

    # 4. RECUPERAR JSON (Agora ele deve estar na pasta temp)
    json_esperado = os.path.join(DIR_TESTES, "provenance_w3c.json")
    json_final = os.path.join(DIR_TESTES, f"prov_{step_name}.json")
    
    # Verifica se o arquivo existe
    if os.path.exists(json_esperado):
        if os.path.exists(json_final): os.remove(json_final)
        os.rename(json_esperado, json_final)
        return json_final
        
    # Fallback: Tenta achar 'provenance.json' caso a IA tenha errado o nome
    json_alternativo = os.path.join(DIR_TESTES, "provenance.json")
    if os.path.exists(json_alternativo):
        os.rename(json_alternativo, json_final)
        return json_final
    
    return None

def comparar_resultados(orig_metrics, mut_metrics, nome_teste):
    ao, eo = orig_metrics
    am, em = mut_metrics
    print(f"\n📊 [{nome_teste}]")
    print(f"   Original: {ao} Ativ / {eo} Ent")
    print(f"   Mutante : {am} Ativ / {em} Ent")
    
    if ao == 0:
        print("   ⚠️  INCONCLUSIVO: Original não gerou proveniência (Script falhou ao rodar).")
    elif ao == am and eo == em:
        print("   ✅ SUCESSO: Estrutura idêntica.")
    elif abs(ao - am) <= 1:
        print("   ✅ SUCESSO (Tolerância): Variação mínima.")
    else:
        print("   ❌ FALHA: A mutação alterou drasticamente a proveniência.")

def main():
    setup()
    try:
        if not os.path.exists(SCRIPT_ALVO):
            print(f"❌ ERRO: O arquivo '{SCRIPT_ALVO}' não foi encontrado nesta pasta.")
            return

        print(f"🔵 Iniciando Testes Avançados em: {SCRIPT_ALVO}")
        with open(SCRIPT_ALVO, 'r', encoding='utf-8') as f: original_code = f.read()
        
        # Salva Original
        with open(os.path.join(DIR_TESTES, "base.py"), 'w', encoding='utf-8') as f: f.write(original_code)
        
        # --- EXECUÇÃO BASE ---
        print("\n--- 1. BASE LINE ---")
        json_base = executar_pipeline("base.py", "base")
        met_base = extrair_metricas_prov(json_base)

        # --- TESTE 1: EQUIVALÊNCIA SINTÁTICA ---
        print("\n--- 2. EQUIVALÊNCIA SINTÁTICA ---")
        print("   🧬 Gerando mutante (a+b -> b+a)...")
        code_synt = mutar_equivalencia_sintatica(original_code)
        with open(os.path.join(DIR_TESTES, "synt.py"), 'w', encoding='utf-8') as f: f.write(code_synt)
        
        json_synt = executar_pipeline("synt.py", "synt")
        met_synt = extrair_metricas_prov(json_synt)
        comparar_resultados(met_base, met_synt, "Equivalência Sintática")

        # --- TESTE 2: PERMUTAÇÃO DE BLOCOS ---
        print("\n--- 3. PERMUTAÇÃO DE BLOCOS ---")
        print("   🧬 Gerando mutante (Reordenar linhas independentes)...")
        code_perm = mutar_permutacao_blocos(original_code)
        
        if code_perm.strip() == original_code.strip():
             print("   ℹ️ Código muito acoplado. Nenhuma permutação segura encontrada.")
        else:
            with open(os.path.join(DIR_TESTES, "perm.py"), 'w', encoding='utf-8') as f: f.write(code_perm)
            json_perm = executar_pipeline("perm.py", "perm")
            met_perm = extrair_metricas_prov(json_perm)
            comparar_resultados(met_base, met_perm, "Permutação de Blocos")

        # --- TESTE 3: DECOMPOSIÇÃO ---
        print("\n--- 4. DECOMPOSIÇÃO ---")
        print("   🧬 Gerando mutante (Split)...")
        p1, p2 = mutar_decomposicao(original_code)
        with open(os.path.join(DIR_TESTES, "part1.py"), 'w', encoding='utf-8') as f: f.write(p1)
        with open(os.path.join(DIR_TESTES, "part2.py"), 'w', encoding='utf-8') as f: f.write(p2)
        
        json_p1 = executar_pipeline("part1.py", "part1")
        json_p2 = executar_pipeline("part2.py", "part2")
        
        m1 = extrair_metricas_prov(json_p1)
        m2 = extrair_metricas_prov(json_p2)
        soma_ativ = m1[0] + m2[0]
        
        print(f"\n📊 [Decomposição]")
        print(f"   Original: {met_base[0]} Atividades")
        print(f"   Soma P1+P2: {soma_ativ} Atividades")
        
        if abs(met_base[0] - soma_ativ) <= 2 and met_base[0] > 0:
            print("   ✅ SUCESSO: A soma das partes reflete o todo.")
        elif met_base[0] == 0:
             print("   ⚠️  INCONCLUSIVO: Original falhou.")
        else:
            print("   ❌ FALHA: Inconsistência na decomposição.")

    finally:
        cleanup()
        print("\nTeste Finalizado.")

if __name__ == "__main__":
    main()