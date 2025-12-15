import os.path
import pandas as pd
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def inspect_tab():
    creds = None
    base_path = '/home/emanoel/proditec'
    token_path = os.path.join(base_path, 'token.json')
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds:
        print("Credenciais não encontradas.")
        return

    try:
        service = build('sheets', 'v4', credentials=creds)
        spreadsheet_id = '1IldiJwcZFkxNEpZ5nUj0ZodGkf3QgUhY1VcLzklDNs8'
        aba_alvo = 'Turma-Grupo-Cursita-Zap' # Nome exato conforme listado anteriormente
        
        print(f"Lendo primeiras linhas da aba: {aba_alvo}")
        
        # Lê primeiras 10 linhas para inspeção
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=f"'{aba_alvo}'!A1:Z10").execute()
        values = result.get('values', [])
        
        if not values:
            print("Vazio.")
            return

        print("\n--- Primeiras 10 linhas ---")
        for i, row in enumerate(values):
            print(f"Linha {i+1}: {row}")
            
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == '__main__':
    inspect_tab()
