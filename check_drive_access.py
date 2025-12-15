import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/drive.readonly']

def list_files():
    creds = None
    base_path = '/home/emanoel/proditec'
    token_path = os.path.join(base_path, 'token.json')
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    if not creds or not creds.valid:
        print("Credenciais inválidas ou expiradas.")
        return

    try:
        service = build('drive', 'v3', credentials=creds)
        
        # Tenta listar os ultimos 10 arquivos
        results = service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('Nenhum arquivo encontrado.')
        else:
            print('Arquivos encontrados no Drive:')
            for item in items:
                print(u'{0} ({1})'.format(item['name'], item['id']))
                
        # Tenta pegar info específica da planilha
        file_id = '1IldiJwcZFkxNEpZ5nUj0ZodGkf3QgUhY1VcLzklDNs8'
        print(f"\nVerificando acesso ao arquivo ID: {file_id}")
        try:
            file = service.files().get(fileId=file_id).execute()
            print(f"Sucesso! Nome do arquivo: {file.get('name')}")
        except Exception as e:
            print(f"Erro ao acessar arquivo específico: {str(e)}")

    except Exception as e:
        print(f"Erro geral: {e}")

if __name__ == '__main__':
    list_files()
