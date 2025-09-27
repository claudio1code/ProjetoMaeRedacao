# teste_gemini.py (VERSÃO FINAL COM O MODELO DA SUA LISTA)
import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.oauth2 import service_account

load_dotenv()
print("--- Iniciando teste da API do Google Gemini ---")
try:
    caminho_credenciais = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not caminho_credenciais:
        raise Exception("A variável GOOGLE_APPLICATION_CREDENTIALS não foi encontrada no .env")

    print(f"✅ Arquivo de credenciais encontrado: {caminho_credenciais}")
    creds = service_account.Credentials.from_service_account_file(caminho_credenciais)
    genai.configure(credentials=creds)
    print("✅ Biblioteca configurada com sucesso.")

    # Usando o nome exato da sua lista de modelos disponíveis
    model = genai.GenerativeModel('models/gemini-pro-latest')
    print("✅ Modelo 'models/gemini-pro-latest' inicializado.")

    print("...Enviando 'Olá, mundo!' para o Gemini...")
    response = model.generate_content("Olá, mundo!")

    print("\n🎉 SUCESSO! A conexão com a API do Gemini funcionou!")
    print("\nResposta da IA:", response.text)

except Exception as e:
    print(f"\n❌ FALHA! Ocorreu um erro durante o processo: {e}")