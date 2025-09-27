# logica_ia.py

import os
from dotenv import load_dotenv
from io import BytesIO
import google.generativeai as genai
from google.oauth2 import service_account
from PIL import Image

# Importa a função correta
from gerador_docx import criar_relatorio_avancado_docx

# Carrega as variáveis de ambiente
load_dotenv()

def carregar_prompt(caminho_arquivo="prompt.txt"):
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ ERRO ao carregar prompt: {e}")
        return None

def analisar_imagem_com_gemini_multimodal(conteudo_imagem_bytes):
    try:
        caminho_credenciais = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not caminho_credenciais:
            return "❌ Credenciais do Google não encontradas no arquivo .env."

        creds = service_account.Credentials.from_service_account_file(caminho_credenciais)
        genai.configure(credentials=creds)

        prompt_mestre = carregar_prompt()
        if not prompt_mestre:
            return "❌ ERRO CRÍTICO: Não foi possível carregar o prompt.txt."

        imagem = Image.open(BytesIO(conteudo_imagem_bytes))
        model = genai.GenerativeModel('models/gemini-2.5-flash-image-preview')
        
        response = model.generate_content([prompt_mestre, imagem])
        return response.text
    except Exception as e:
        return f"❌ Ocorreu um erro ao conectar com a API do Gemini: {e}"

def criar_documento_docx(analise_completa_ia):
    """
    Chama o módulo especialista para criar o relatório avançado.
    Esta função agora está corrigida.
    """
    try:
        # A lógica de separar o texto não é mais necessária aqui.
        # A função criar_relatorio_avancado_docx agora faz todo o trabalho.
        return criar_relatorio_avancado_docx(analise_completa_ia)
    except Exception as e:
        # Este print agora mostrará o erro vindo de criar_relatorio_avancado_docx
        print(f"❌ Erro ao chamar o gerador de DOCX: {e}")
        return None