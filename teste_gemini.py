# teste_gemini.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

print("--- Iniciando teste da API do Google Gemini (usando Conta de Serviço) ---")

try:
    # 1. Pega o CAMINHO para o arquivo de credenciais a partir do .env
    caminho_credenciais = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not caminho_credenciais:
        raise Exception("A variável GOOGLE_APPLICATION_CREDENTIALS (arquivo .json) não foi encontrada no .env")

    print(f"✅ Credenciais da Conta de Serviço encontradas!")

    # 2. Configura a biblioteca para usar o ARQUIVO DE CREDENCIAIS
    #    Esta é a mudança fundamental que alinha o teste com o resto do projeto.
    genai.configure(credentials_file=caminho_credenciais)
    print("✅ Biblioteca configurada com sucesso via Conta de Serviço.")

    # 3. Inicializa o modelo
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    print("✅ Modelo 'gemini-1.5-pro-latest' inicializado.")

    # 4. Envia uma mensagem de teste
    print("...Enviando 'Olá, mundo!' para o Gemini...")
    response = model.generate_content("Olá, mundo!")

    # 5. Se tudo deu certo, mostra a resposta
    print("\n🎉 SUCESSO! A conexão com a API do Gemini funcionou!")
    print("\nResposta da IA:", response.text)

except Exception as e:
    print(f"\n❌ FALHA! Ocorreu um erro durante o processo: {e}")
    print("\n➡️ Dica: Verifique se o arquivo .json referenciado no .env existe e se a 'Generative Language API' está ativada no seu projeto do Google Cloud.")
