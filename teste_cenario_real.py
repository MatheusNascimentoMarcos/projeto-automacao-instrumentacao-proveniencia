import os
import json
import subprocess
import shutil
import glob
import sys

# --- IMPORTAÇÃO DO MOTOR DE MUTAÇÃO ---
try:
    from mutator_engine_advanced import (
        mutar_equivalencia_sintatica,
        mutar_permutacao_blocos,
        mutar_decomposicao,
    )
except ImportError:
    print("❌ ERRO: Arquivo 'mutator_engine_advanced.py' não encontrado.")
    sys.exit(1)

# --- CONFIGURAÇÃO ---
SCRIPT_ALVO = "ETL.py"  # O script real que vamos estressar

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("⚠️  AVISO: GEMINI_API_KEY não encontrada. Use 'export GEMINI_API_KEY=...'")

IMG_NAME = "ia-prov-wrapper"
CURRENT_DIR = os.getcwd()
DIR_TESTES = "temp_real_advanced"

# --- SOLUÇÃO DE PERMISSÃO (Docker User Mirror) ---
try:
    user_id = str(os.getuid())
    group_id = str(os.getgid())
    USER_FLAG = ["--user", f"{user_id}:{group_id}"]
except AttributeError:
    # Windows não tem getuid, mas geralmente não precisa dessa flag
    USER_FLAG = []

# Base do comando Docker
DOCKER_BASE_CMD = [
    "docker",
    "run",
    "--rm",
    "-e",
    f"GEMINI_API_KEY={api_key}",
    "-v",
    f"{CURRENT_DIR}:/app",
] + USER_FLAG  # Adiciona a identidade do usuário


def setup():
    if os.path.exists(DIR_TESTES):
        shutil.rmtree(DIR_TESTES)
    os.makedirs(DIR_TESTES)


def cleanup():
    # Deixei comentado para você poder investigar a pasta se der erro
    # shutil.rmtree(DIR_TESTES)
    pass


def to_linux_path(path):
    return path.replace("\\", "/")


def extrair_metricas_prov(caminho_json):
    if not caminho_json or not os.path.exists(caminho_json):
        return 0, 0
    try:
        with open(caminho_json, "r") as f:
            d = json.load(f)
        return len(d.get("activity", {})), len(d.get("entity", {}))
    except Exception:
        return 0, 0


def executar_pipeline(nome_arq, step_name):
    """
    1. Instrumenta o código (Input -> Input_Inst).
    2. Copia dados (CSVs).
    3. Executa o código instrumentado dentro da pasta temp.
    """
    nome_script_inst = f"inst_{nome_arq}"

    # Caminhos Relativos (para o Docker usar dentro de /app)
    path_in_docker = to_linux_path(os.path.join(DIR_TESTES, nome_arq))
    path_out_docker = to_linux_path(os.path.join(DIR_TESTES, nome_script_inst))

    print(f"   ➤ Instrumentando {nome_arq}...")

    # 1. INSTRUMENTAÇÃO
    cmd_inst = DOCKER_BASE_CMD + [
        IMG_NAME,
        "python3",
        "instrument_workflow.py",
        path_in_docker,
        path_out_docker,
    ]
    res_inst = subprocess.run(cmd_inst)

    if res_inst.returncode != 0:
        print(f"   ❌ ERRO FATAL: Falha na instrumentação de {nome_arq}")
        return None

    # 2. PREPARAÇÃO DE DADOS (Cópia dos CSVs)
    # Procura CSVs na raiz e copia para dentro da pasta temp
    csvs = glob.glob("*.csv")
    for csv in csvs:
        shutil.copy(csv, os.path.join(DIR_TESTES, csv))

    # 3. EXECUÇÃO
    # Verifica se o arquivo foi criado
    if not os.path.exists(os.path.join(DIR_TESTES, nome_script_inst)):
        print(f"   ❌ Arquivo instrumentado não encontrado.")
        return None

    print(f"   ▶️ Executando script gerado...")

    # Definimos o WORKDIR do Docker para ser a pasta temp (/app/temp_real_advanced)
    # Isso garante que ele ache os CSVs e salve o provenance.json lá dentro
    workdir_docker = f"/app/{DIR_TESTES}"

    cmd_exec = (
        [
            "docker",
            "run",
            "--rm",
            "-e",
            f"GEMINI_API_KEY={api_key}",
            "-v",
            f"{CURRENT_DIR}:/app",
            "-w",
            workdir_docker,  # <--- RODA DENTRO DA PASTA TEMP
        ]
        + USER_FLAG
        + [IMG_NAME, "python3", nome_script_inst]  # <--- MANTÉM PERMISSÃO DO USUÁRIO
    )

    res_exec = subprocess.run(cmd_exec)
    if res_exec.returncode != 0:
        print(
            f"   ⚠️  Aviso: O script instrumentado retornou erro (mas pode ter gerado grafo)."
        )

    # 4. RECUPERAR JSON
    # Como rodamos com -w, o JSON nasce dentro de DIR_TESTES
    json_esperado = os.path.join(DIR_TESTES, "provenance_w3c.json")
    json_final = os.path.join(DIR_TESTES, f"prov_{step_name}.json")

    # Verifica provenance_w3c.json
    if os.path.exists(json_esperado):
        if os.path.exists(json_final):
            os.remove(json_final)
        os.rename(json_esperado, json_final)
        return json_final

    # Verifica provenance.json (fallback)
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
        print("   ⚠️  INCONCLUSIVO: Original falhou.")
    elif ao == am and eo == em:
        print("   ✅ SUCESSO: Estrutura idêntica.")
    elif abs(ao - am) <= 1:  # Tolerância pequena
        print("   ✅ SUCESSO (Tolerância): Variação aceitável.")
    else:
        print("   ❌ FALHA: A mutação alterou drasticamente a proveniência.")


def main():
    global SCRIPT_ALVO  # <--- MOVIDO PARA CÁ (CORREÇÃO)

    setup()
    try:
        if not os.path.exists(SCRIPT_ALVO):
            print(f"❌ ERRO: O arquivo '{SCRIPT_ALVO}' não existe.")
            # Tenta usar o meu_script.py se o ETL não existir
            if os.path.exists("meu_script.py"):
                print("   -> Usando 'meu_script.py' como fallback.")
                SCRIPT_ALVO = "meu_script.py"
            else:
                return

        print(f"🔵 Iniciando Testes Avançados em: {SCRIPT_ALVO}")
        with open(SCRIPT_ALVO, "r", encoding="utf-8") as f:
            original_code = f.read()

        # Salva Base
        with open(os.path.join(DIR_TESTES, "base.py"), "w", encoding="utf-8") as f:
            f.write(original_code)

        # --- 1. BASE LINE ---
        print("\n--- 1. BASE LINE (Script Original) ---")
        json_base = executar_pipeline("base.py", "base")
        met_base = extrair_metricas_prov(json_base)
        print(f"   Métricas Base: {met_base[0]} Atividades, {met_base[1]} Entidades")

        # --- 2. EQUIVALÊNCIA SINTÁTICA ---
        print("\n--- 2. EQUIVALÊNCIA SINTÁTICA ---")
        code_synt = mutar_equivalencia_sintatica(original_code)
        with open(os.path.join(DIR_TESTES, "synt.py"), "w", encoding="utf-8") as f:
            f.write(code_synt)

        json_synt = executar_pipeline("synt.py", "synt")
        met_synt = extrair_metricas_prov(json_synt)
        comparar_resultados(met_base, met_synt, "Equivalência Sintática")

        # --- 3. PERMUTAÇÃO DE BLOCOS ---
        print("\n--- 3. PERMUTAÇÃO DE BLOCOS ---")
        code_perm = mutar_permutacao_blocos(original_code)

        if code_perm.strip() == original_code.strip():
            print("   ℹ️ Código muito acoplado. Nenhuma permutação segura encontrada.")
        else:
            with open(os.path.join(DIR_TESTES, "perm.py"), "w", encoding="utf-8") as f:
                f.write(code_perm)
            json_perm = executar_pipeline("perm.py", "perm")
            met_perm = extrair_metricas_prov(json_perm)
            comparar_resultados(met_base, met_perm, "Permutação de Blocos")

        # --- 4. DECOMPOSIÇÃO ---
        print("\n--- 4. DECOMPOSIÇÃO ---")
        p1, p2 = mutar_decomposicao(original_code)

        with open(os.path.join(DIR_TESTES, "part1.py"), "w", encoding="utf-8") as f:
            f.write(p1)
        with open(os.path.join(DIR_TESTES, "part2.py"), "w", encoding="utf-8") as f:
            f.write(p2)

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
