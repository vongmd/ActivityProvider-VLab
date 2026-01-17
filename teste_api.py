import requests
import json
import sys

# ==============================================================================
# CONFIGURAÇÃO DO TESTE
# ==============================================================================

# --- MODO 1: TESTE LOCAL (No teu computador) ---
url_local = 'http://127.0.0.1:5000/analytics_url'

# --- MODO 2: TESTE ONLINE (No Render) ---
  url_online = 'https://activityprovider-vlab.onrender.com/analytics_url'

# ==============================================================================
# ESCOLHA O ALVO (Descomenta o que queres usar)
# ==============================================================================

# alvo_atual = url_local       # <--- Usa este para testar no PC
alvo_atual = url_online      # <--- Usa este para testar o Deploy

# ==============================================================================

payload = {
    "activityID": "TESTE_FINAL_RENDER",
    "Inven!RAstdID": "ALUNO_VALIDACAO",
    "json_params": {"mode": "test"}
}

print(f"\n A INICIAR TESTE DE API...")
print(f" Alvo: {alvo_atual}")
print("-" * 50)

try:
    # Envia o POST
    resposta = requests.post(alvo_atual, json=payload)

    # Analisa a resposta
    if resposta.status_code == 200:
        print(" SUCESSO! O servidor no Render respondeu corretamente.")
        print("\n Conteúdo da Resposta:")
        print(json.dumps(resposta.json(), indent=2))
        
    elif resposta.status_code == 405:
        print(" ERRO 405: Method Not Allowed.")
        print("A rota existe mas rejeitou o método. Confirma se é POST.")
        
    elif resposta.status_code == 404:
        print(" ERRO 404: Not Found.")
        print("O URL está errado. Verifica se copiaste bem do Render.")
        
    else:
        print(f" Resposta inesperada: Código {resposta.status_code}")
        print(resposta.text)

except requests.exceptions.ConnectionError:
    print(" FALHA DE CONEXÃO.")
    print("Verifica se o URL está correto e se o site no Render já acabou de carregar.")

print("-" * 50)