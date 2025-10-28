# check_models.py
import google.generativeai as genai
import os

print("Tentando configurar a API...")

# 1. Configurar a API (igual ao outro script)
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("Erro: A variável de ambiente 'GEMINI_API_KEY' não foi definida.")
    print("Defina-a com: $env:GEMINI_API_KEY = 'sua_chave_api'")
    exit() # Sai do script

try:
    genai.configure(api_key=API_KEY)
    print("API configurada com sucesso.")
except Exception as e:
    print(f"Erro ao configurar a API: {e}")
    exit() # Sai do script

# 2. Listar os Modelos
print("\nBuscando modelos disponíveis para sua chave...")
print("-----------------------------------------------")

try:
    for model in genai.list_models():
        # Vamos checar quais modelos suportam o método 'generateContent'
        if 'generateContent' in model.supported_generation_methods:
            print(model.name)
except Exception as e:
    print(f"Ocorreu um erro ao listar os modelos: {e}")

print("-----------------------------------------------")
print("Busca concluída.")