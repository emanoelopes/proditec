import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os

def baixar_planilha(json_credencial, sheet_id, output_csv):
    try:
        if not os.path.exists(json_credencial):
            raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {json_credencial}")

        scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        creds = Credentials.from_service_account_file(json_credencial, scopes=scopes)
        gc = gspread.authorize(creds)

        print(f"Abrindo planilha: {sheet_id}")
        sh = gc.open_by_key(sheet_id)
        worksheet = sh.get_worksheet(0) # Pega a primeira aba

        print("Baixando dados...")
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        
        df.to_csv(output_csv, index=False)
        print(f'Dados salvos com sucesso em {output_csv}')
        print(f"Colunas encontradas: {list(df.columns)}")
        return df

    except Exception as e:
        print(f"Erro: {e}")
        return None

if __name__ == "__main__":
    # Caminho relativo pois o arquivo está no root
    json_credencial = '/home/emanoel/proditec/credencial.json' 
    sheet_id = '1IldiJwcZFkxNEpZ5nUj0ZodGkf3QgUhY1VcLzklDNs8'
    output_file = '/home/emanoel/proditec/temp_cursistas.csv'
    
    baixar_planilha(json_credencial, sheet_id, output_file)
