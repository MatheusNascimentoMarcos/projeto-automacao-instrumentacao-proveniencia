# instrument_workflow.py

import os
import argparse
import google.generativeai as genai

from prompt_template_coarse import PROMPT_COARSE_TEMPLATE
from prompt_template_medium import PROMPT_MEDIUM_TEMPLATE
from prompt_template_fine import PROMPT_FINE_TEMPLATE
from prompt_template_metamorphic import PROMPT_METAMORPHIC_TEMPLATE

# Seletor de granularidade: nível -> template de prompt
TEMPLATES = {
    "coarse": PROMPT_COARSE_TEMPLATE,
    "medium": PROMPT_MEDIUM_TEMPLATE,
    "fine": PROMPT_FINE_TEMPLATE,
    "metamorphic": PROMPT_METAMORPHIC_TEMPLATE,
}


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
    text = text.strip()
    if text.startswith("```python"):
        text = text[len("```python"):]
    elif text.startswith("```"):
        text = text[len("```"):]
    if text.endswith("```"):
        text = text[:-len("```")]

    return text.strip()


def build_prompt(code_to_instrument, level):
    """
    Monta o prompt final para o nível de granularidade escolhido.

    Os templates têm as chaves literais dos exemplos escapadas ({{ }}),
    então devem passar por .format(). O código do usuário é injetado como
    valor, portanto chaves dentro dele não causam KeyError.
    """
    template = TEMPLATES[level]
    return template.format(input_code=code_to_instrument)


def generate_instrumentation(code_to_instrument, level):
    """
    Envia o código e o prompt do nível escolhido para a API do Gemini
    e retorna o código instrumentado.
    """
    print(f"Iniciando a instrumentação com a IA do Gemini (nível: {level})...")
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
            'models/gemini-pro-latest',
            safety_settings=safety_settings
        )

        final_prompt = build_prompt(code_to_instrument, level)

        response = model.generate_content(final_prompt)

        # Limpa a resposta para obter apenas o código
        raw_code = clean_response_text(response.text)

        return raw_code

    except Exception as e:
        print(f"Erro durante a chamada da API do Gemini: {e}")
        return None


def main():
    """Função principal para orquestrar o processo via linha de comando."""

    parser = argparse.ArgumentParser(
        description="Automatiza a instrumentação de workflows científicos com IA (Gemini).",
        epilog=(
            "Exemplo de uso: python instrument_workflow.py meu_script.py "
            "script_instrumentado.py --level fine"
        ),
    )
    parser.add_argument("input_file", help="Caminho para o script Python a ser instrumentado.")
    parser.add_argument("output_file", help="Caminho onde o script instrumentado será salvo.")
    parser.add_argument(
        "--level",
        choices=list(TEMPLATES.keys()),
        default="metamorphic",
        help="Granularidade do template de prompt (padrão: metamorphic).",
    )

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
    instrumented_code = generate_instrumentation(original_code, args.level)

    # 5. Salvar o arquivo de saída
    if instrumented_code:
        write_file(args.output_file, instrumented_code)
    else:
        print("\n[FALHA] Não foi possível gerar o código instrumentado.")


if __name__ == "__main__":
    main()