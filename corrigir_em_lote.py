# corrigir_em_lote.py
import os.path
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload

from logica_ia import analisar_imagem_com_gemini_multimodal, criar_documento_docx
from gerador_docx import extrair_nome_aluno

SCOPES = ["https://www.googleapis.com/auth/drive"]
ID_PASTA_ENTRADA = "1c_8ybbo6HAhMxlOeNKX71PPF8TfySKx-"
ID_PASTA_SAIDA = "16xRIPkBY8gRp9vNzxgH1Ex4GhTnkzbed"

def autenticar():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def main():
    print("Iniciando assistente de correção em lote...")
    creds = autenticar()
    try:
        service = build("drive", "v3", credentials=creds)
        print("✅ Autenticação com Google Drive bem-sucedida.")

        query = f"'{ID_PASTA_ENTRADA}' in parents and (mimeType='image/jpeg' or mimeType='image/png')"
        results = service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
        items = results.get("files", [])

        if not items:
            print("ℹ️ Nenhuma nova redação encontrada para corrigir.")
            return
        print(f"✅ Encontradas {len(items)} redações para corrigir.\n")

        for item in items:
            file_id = item["id"]
            file_name = item["name"]
            print(f"--- Processando: {file_name} ---")

            print("   1/4 - Baixando imagem do Drive...")
            request = service.files().get_media(fileId=file_id)
            file_bytes = request.execute()

            print("   2/4 - Enviando para análise da IA...")
            analise_completa = analisar_imagem_com_gemini_multimodal(file_bytes)
            if "❌" in analise_completa:
                print(f"   ❗️ Erro na análise da IA para {file_name}. Motivo: {analise_completa}")
                continue

            print("   3/4 - Gerando relatório .docx...")
            arquivo_docx_bytes = criar_documento_docx(analise_completa)
            
            # --- CORREÇÃO DE ERRO ---
            # Verifica se o arquivo foi criado com sucesso antes de prosseguir
            if arquivo_docx_bytes is None:
                print(f"   ❗️ Falha ao gerar o arquivo .docx para {file_name}. Pulando upload.")
                continue
            
            print("   4/4 - Enviando relatório corrigido para o Drive...")
            nome_aluno = extrair_nome_aluno(analise_completa)
            nome_arquivo_final = f"correcao_{nome_aluno.replace(' ', '_')}.docx"
            file_metadata = {
                "name": nome_arquivo_final,
                "parents": [ID_PASTA_SAIDA]
            }
            media = MediaIoBaseUpload(io.BytesIO(arquivo_docx_bytes.getvalue()), mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            service.files().create(body=file_metadata, media_body=media, fields="id").execute()
            print(f"   ✅ Relatório de '{nome_aluno}' salvo com sucesso!\n")

    except HttpError as error:
        print(f"Ocorreu um erro na API: {error}")

if __name__ == "__main__":
    main()