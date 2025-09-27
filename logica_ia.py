# logica_ia.py

import os
from dotenv import load_dotenv
from io import BytesIO
import google.generativeai as genai
from PIL import Image

# Importa o nosso especialista em gerar relatórios
from gerador_docx import criar_relatorio_avancado_docx

# Carrega as variáveis de ambiente
load_dotenv()

def carregar_prompt(caminho_arquivo="prompt.txt"):
    """Lê e retorna o conteúdo do arquivo de prompt detalhado."""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ ERRO ao carregar prompt: {e}")
        return None

# --- FUNÇÃO 4: Analisar a Redação com Gemini (Usando Conta de Serviço) ---
def analisar_redacao_com_gemini(texto_redacao):
    """
    Envia o texto da redação para a API do Google Gemini,
    usando as credenciais da Conta de Serviço para garantir a permissão.
    """
    try:
        # Pega o CAMINHO do arquivo .json a partir do nosso arquivo .env
        caminho_credenciais = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not caminho_credenciais:
            return "❌ Credenciais do Google (arquivo .json) não encontradas no arquivo .env."

        # Autentica usando o arquivo de credenciais
        genai.configure(credentials_file=caminho_credenciais)
        
        prompt_mestre = carregar_prompt()
        if not prompt_mestre:
            return "❌ ERRO CRÍTICO: Não foi possível carregar o prompt.txt."

        prompt_final = f"{prompt_mestre}\n\n--- REDAÇÃO PARA ANÁLISE ---\n\n{texto_redacao}"

        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content(prompt_final)
        
        return response.text
    except Exception as e:
        return f"❌ Ocorreu um erro ao conectar com a API do Gemini: {e}"
    
def criar_documento_docx(analise_completa_ia):
    """
    Chama o módulo especialista para criar o relatório avançado.
    Adaptação: extrai o texto transcrito da própria análise da IA.
    """
    try:
        # Tenta separar o texto transcrito da análise
        partes = analise_completa_ia.split("### **Análise da Redação**")
        if len(partes) < 2:
            # Fallback se o formato não for o esperado
            texto_transcrito = "Não foi possível extrair o texto transcrito da análise."
            texto_analise = analise_completa_ia
        else:
            texto_transcrito = partes[0].replace("### Texto Transcrito", "").strip()
            texto_analise = "### **Análise da Redação**" + partes[1]
        
        print("Gerando relatório avançado com destaques...")
        return criar_relatorio_avancado_docx(texto_transcrito, texto_analise)
    except Exception as e:
        print(f"❌ Erro ao chamar o gerador de DOCX: {e}")
        return None

