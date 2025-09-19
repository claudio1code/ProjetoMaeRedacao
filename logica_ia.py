# logica_ia.py

import os
from dotenv import load_dotenv
from io import BytesIO

# --- Bibliotecas das APIs ---
from openai import OpenAI
from google.cloud import vision
from google.oauth2 import service_account
import google.generativeai as genai

# --- Bibliotecas para Imagem e DOCX ---
from PIL import Image, ImageEnhance, ImageFilter

# --- Importa nosso especialista em gerar relatórios ---
from gerador_docx import criar_relatorio_avancado_docx

# Carrega as variáveis de ambiente
load_dotenv()

def pre_processar_imagem(conteudo_da_imagem_bytes):
    """Aplica filtros na imagem para melhorar a qualidade do OCR."""
    try:
        print("Aplicando pré-processamento na imagem...")
        img = Image.open(BytesIO(conteudo_da_imagem_bytes))
        img = img.convert('L') # Converte para preto e branco
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0) # Aumenta o contraste
        img = img.filter(ImageFilter.SHARPEN) # Aumenta a nitidez
        buffer_saida = BytesIO()
        img.save(buffer_saida, format='PNG')
        print("✅ Pré-processamento concluído!")
        return buffer_saida.getvalue()
    except Exception as e:
        print(f"❌ Erro no pré-processamento: {e}")
        return conteudo_da_imagem_bytes

def extrair_texto_da_imagem(conteudo_da_imagem_processada):
    """Envia a imagem JÁ PROCESSADA para a API do Google Cloud Vision."""
    try:
        caminho_credenciais = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not caminho_credenciais:
            raise Exception("Credenciais do Google não encontradas no arquivo .env")
            
        credenciais = service_account.Credentials.from_service_account_file(caminho_credenciais)
        client = vision.ImageAnnotatorClient(credentials=credenciais)
        image = vision.Image(content=conteudo_da_imagem_processada)
        response = client.document_text_detection(image=image)
        
        if response.error.message:
            raise Exception(f"Erro da API do Google: {response.error.message}")
            
        return response.full_text_annotation.text
    except Exception as e:
        return f"❌ Erro ao extrair texto da imagem: {e}"

def carregar_prompt(caminho_arquivo="prompt.txt"):
    """Lê e retorna o conteúdo do arquivo de prompt detalhado."""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f: return f.read()
    except: return None

def analisar_redacao_com_ia(texto, modelo="gpt-4o"):
    """Envia o texto da redação para a API da OpenAI."""
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key: return "❌ Chave da API da OpenAI não encontrada."
        
        client = OpenAI(api_key=api_key)
        prompt = carregar_prompt()
        if not prompt: return "❌ Erro: arquivo prompt.txt não encontrado."
        
        prompt_final = f"{prompt}\n\n--- REDAÇÃO PARA ANÁLISE ---\n\n{texto}"
        
        resp = client.chat.completions.create(model=modelo, messages=[{"role": "user", "content": prompt_final}])
        return resp.choices[0].message.content
    except Exception as e:
        return f"❌ Erro ao conectar com a API da OpenAI: {e}"

def analisar_redacao_com_gemini(texto):
    """Envia o texto da redação para a API do Google Gemini."""
    try:
        api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
        if not api_key: return "❌ Chave da API do Gemini não encontrada."

        genai.configure(api_key=api_key)
        prompt = carregar_prompt()
        if not prompt: return "❌ Erro: arquivo prompt.txt não encontrado."

        prompt_final = f"{prompt}\n\n--- REDAÇÃO PARA ANÁLISE ---\n\n{texto}"
        
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        resp = model.generate_content(prompt_final)
        return resp.text
    except Exception as e:
        return f"❌ Erro ao conectar com a API do Gemini: {e}"

def criar_documento_docx(texto_original, texto_corrigido):
    """
    Chama o novo módulo especialista para criar o relatório avançado com destaques.
    """
    print("Gerando relatório avançado com destaques...")
    return criar_relatorio_avancado_docx(texto_original, texto_corrigido)
