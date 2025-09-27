import os.path
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload

# Importa a lógica que já construímos!
from logica_ia import analisar_imagem_com_gemini_multimodal, criar_documento_docx

# Se modificar esses escopos, delete o arquivo token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]

# --- CONFIGURAÇÃO ---
# Cole aqui os IDs das pastas que você criou no seu Google Drive
ID_PASTA_ENTRADA = "1c_8ybbo6HAhMxlOeNKX71PPF8TfySKx-"
ID_PASTA_SAIDA = "16xRIPkBY8gRp9vNzxgH1Ex4GhTnkzbed"
# --------------------

def autenticar():
    """Realiza a autenticação com a API do Google Drive."""
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
    """Função principal que orquestra todo o processo de automação."""
    print("Iniciando assistente de correção em lote...")
    creds = autenticar()

    try:
        service = build("drive", "v3", credentials=creds)
        print("✅ Autenticação com Google Drive bem-sucedida.")

        # 1. Lista os arquivos na pasta de entrada
        query = f"'{ID_PASTA_ENTRADA}' in parents and (mimeType='image/jpeg' or mimeType='image/png')"
        results = service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
        items = results.get("files", [])

        if not items:
            print("ℹ️ Nenhuma nova redação encontrada para corrigir.")
            return

        print(f"✅ Encontradas {len(items)} redações para corrigir.\n")

        # 2. Itera sobre cada arquivo, corrige e faz o upload
        for item in items:
            file_id = item["id"]
            file_name = item["name"]
            print(f"--- Processando: {file_name} ---")

            # Download do arquivo
            print("   1/4 - Baixando imagem do Drive...")
            request = service.files().get_media(fileId=file_id)
            file_bytes = request.execute()

            # Análise com a IA
            print("   2/4 - Enviando para análise da IA Multimodal...")
            analise_completa = analisar_imagem_com_gemini_multimodal(file_bytes)
            if "❌" in analise_completa:
                print(f"   ❗️ Erro na análise da IA para {file_name}. Pulando arquivo.")
                continue
            
            # Geração do DOCX
            print("   3/4 - Gerando relatório .docx...")
            arquivo_docx_bytes = criar_documento_docx(analise_completa)
            
            # Upload do DOCX para a pasta de saída
            print("   4/4 - Enviando relatório corrigido para o Drive...")
            file_metadata = {
                "name": f"correcao_{os.path.splitext(file_name)[0]}.docx",
                "parents": [ID_PASTA_SAIDA]
            }
            media = MediaIoBaseUpload(io.BytesIO(arquivo_docx_bytes.getvalue()), mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            service.files().create(body=file_metadata, media_body=media, fields="id").execute()
            print(f"   ✅ Relatório de '{file_name}' salvo com sucesso na pasta de correções!\n")

            # (Opcional) Mover o arquivo original para uma pasta de "Processados"
            # service.files().update(fileId=file_id, addParents='ID_PASTA_PROCESSADOS', removeParents=ID_PASTA_ENTRADA).execute()


    except HttpError as error:
        print(f"Ocorreu um erro na API: {error}")

if __name__ == "__main__":
    main()
