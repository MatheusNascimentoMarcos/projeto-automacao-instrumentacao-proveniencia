# instrument_workflow.py

import os
import argparse
import google.generativeai as genai
from prompt_template import PROMPT_MESTRE_TEMPLATE # Importa o prompt do outro arquivo

def configure_api():
    """Configura a API do Gemini usando uma chave de ambiente."""
    API_KEY = os.environ.get("GEMINI_API_KEY")
    if not API_KEY:
        print("Erro: A variável de ambiente 'GEMINI_API_KEY' não foi definida.")
        print("Defina-a com: $env:GEMINI_API_KEY = 'sua_chave_api'")
        return False
    
    try:
        genai.configure(api_key=API_KEY)
        return True
    except Exception as e:
        print(f"Erro ao configurar a API: {e}")
        return False

def read_file(filepath):
    """Lê o conteúdo de um arquivo de código-fonte."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em {filepath}")
        return None
    except Exception as e:
        print(f"Erro ao ler o arquivo {filepath}: {e}")
        return None

def write_file(filepath, content):
    """Salva o conteúdo instrumentado em um novo arquivo."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n[SUCESSO] Código instrumentado salvo em: {filepath}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo {filepath}: {e}")

def clean_response_text(text):
    """Remove marcações de markdown (```) que o modelo pode adicionar."""
    if text.startswith("```python"):
        text = text[len("```python"):]
    if text.startswith("```"):
        text = text[len("```"):]
    if text.endswith("```"):
        text = text[:-len("```")]
    
    return text.strip()

def fix_ia_hallucinations(generated_code):
    """
    Esta função corrige "alucinações" conhecidas da IA.
    A biblioteca dfa_lib_python só entende NUMERIC e FILE.
    Qualquer tipo complexo (lista, string, etc.) será salvo como FILE.
    """
    print("Executando pós-processamento automatizado v2 (FILE) no código da IA...")

    # Converte tipos complexos/inventados para FILE, que aceita strings
    code = generated_code.replace("AttributeType.COLLECTION", "AttributeType.FILE")
    code = code.replace("AttributeType.STRING", "AttributeType.FILE")
    code = code.replace("AttributeType.LIST", "AttributeType.FILE")
    code = code.replace("AttributeType.BOOL", "AttributeType.FILE")
    code = code.replace("AttributeType.DICT", "AttributeType.FILE")

    return code

def generate_instrumentation(code_to_instrument):
    """
    Envia o código e o prompt mestre para a API do Gemini e retorna 
    o código instrumentado.
    """
    print("Iniciando a instrumentação com a IA do Gemini...")
    print("Isso pode levar alguns segundos...")
    
    # Define configurações de segurança menos restritivas
    # (Útil para geração de código, que pode ser sinalizado como "perigoso")
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    try:
        model = genai.GenerativeModel(
            'models/gemini-pro-latest', # Usando o nome exato da sua lista
            safety_settings=safety_settings
        )
        
        # Formata o prompt final injetando o código do usuário
        final_prompt = PROMPT_MESTRE_TEMPLATE.format(input_code=code_to_instrument)
        
        response = model.generate_content(final_prompt)
        
        # Limpa a resposta para obter apenas o código
        raw_code = clean_response_text(response.text)

        # Aplica a correção automatizada
        fixed_code = fix_ia_hallucinations(raw_code)

        return fixed_code

    except Exception as e:
        print(f"Erro durante a chamada da API do Gemini: {e}")
        return None

def main():
    """Função principal para orquestrar o processo via linha de comando."""
    
    # Configura o parser de argumentos
    parser = argparse.ArgumentParser(
        description="Automatiza a instrumentação de workflows científicos com IA (Gemini).",
        epilog="Exemplo de uso: python instrument_workflow.py meu_script.py script_instrumentado.py"
    )
    parser.add_argument("input_file", help="Caminho para o script Python a ser instrumentado.")
    parser.add_argument("output_file", help="Caminho onde o script instrumentado será salvo.")
    
    # 1. Parse os argumentos
    args = parser.parse_args()

    # 2. Configurar a API
    if not configure_api():
        return

    # 3. Ler o arquivo de entrada
    print(f"Lendo o script de entrada: {args.input_file}")
    original_code = read_file(args.input_file)
    if not original_code:
        print("Operação abortada.")
        return

    # 4. Gerar a instrumentação via IA
    instrumented_code = generate_instrumentation(original_code)
    
    # 5. Salvar o arquivo de saída
    if instrumented_code:
        write_file(args.output_file, instrumented_code)
    else:
        print("\n[FALHA] Não foi possível gerar o código instrumentado.")

if __name__ == "__main__":
    main()