import os.path
import pandas as pd
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def inspect_data():
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
        
        # 1. Listar todas as abas
        print("--- Abas disponíveis ---")
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        for sheet in spreadsheet.get('sheets', []):
            print(f" - {sheet['properties']['title']} (ID: {sheet['properties']['sheetId']})")

        # 2. Ler coluna de grupos da primeira aba
        print("\n--- Análise da Coluna 'grupo' ---")
        # Lê cabeçalho para achar o índice da coluna
        header_result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range='A1:ZZ1').execute()
        headers = [h.strip().lower() for h in header_result.get('values', [])[0]]
        
        if 'grupo' in headers:
            # Pega todos os dados
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id, range='A:ZZ').execute()
            values = result.get('values', [])[1:] # Pula header
            
            # Cria dataframe simples
            df = pd.DataFrame(values, columns=headers)
            
            unique_groups = df['grupo'].unique()
            print(f"Valores únicos na coluna 'grupo':\n{unique_groups}")
            
            # Tenta ver se alguém do Grupo 4 está listado
            g4 = df[df['grupo'].astype(str).str.contains('4')]
            if not g4.empty:
                 print(f"\nExemplo de cursista do Grupo 4:\n{g4[['nome_cursista', 'email_cursista']].head(1).to_string(index=False)}")
        else:
            print("Coluna 'grupo' não encontrada no header.")

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == '__main__':
    inspect_data()
