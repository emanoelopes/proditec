import os.path
import pandas as pd
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def get_b_g4_data():
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
        aba_alvo = 'Turma-Grupo-Cursita-Zap'
        
        print(f"Baixando dados da aba: {aba_alvo}")
        
        # Pega todos os dados
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=f"'{aba_alvo}'!A:E").execute()
        values = result.get('values', [])
        
        if not values:
            print("Nenhum dado encontrado.")
            return

        # Cabeçalhos manuais baseados na inspeção
        # A: Turma/Periodo
        # B: Grupo
        # C: Nome
        # D: Email
        # E: Zap
        headers = ['desc_turma', 'grupo', 'nome', 'email', 'whatsapp']
        
        # Cria DataFrame ignorando a primeira linha (cabeçalho real da planilha)
        df = pd.DataFrame(values[1:], columns=headers)
        
        print(f"Total de registros encontrados: {len(df)}")
        
        # Filtro
        # 1. Coluna 'desc_turma' contendo 'Turma B' (case insensitive)
        # 2. Coluna 'grupo' sendo '4'
        filtered = df[
            (df['desc_turma'].astype(str).str.contains('Turma B', case=False)) &
            (df['grupo'].astype(str).str.strip() == '4')
        ]
        
        if not filtered.empty:
            print(f"\n--- Cursistas Encontrados (Turma B - Grupo 4): {len(filtered)} ---")
            
            # Exibe no console
            print(filtered[['nome', 'email', 'whatsapp']].to_string(index=False))
            
            # Salva
            output_csv = os.path.join(base_path, 'cursistas_grupo4_turmab.csv')
            filtered.to_csv(output_csv, index=False)
            print(f"\nLista salva com sucesso em: {output_csv}")
        else:
            print("\nNenhum cursista encontrado com os filtros:")
            print("- Turma contendo 'Turma B'")
            print("- Grupo igual a '4'")
            
            # Debug: mostra valores únicos para ajudar a entender o porquê
            print("\nValores encontrados na coluna A (Turma):")
            print(df[df['desc_turma'].str.contains('Turma', na=False)]['desc_turma'].unique())
            print("\nValores encontrados na coluna B (Grupo):")
            print(df['grupo'].unique())

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == '__main__':
    get_b_g4_data()
