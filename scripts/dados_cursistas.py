import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

def baixar_planilha_por_id(json_credencial, sheet_id, output_csv):
    # Autenticação usando credencial de serviço
    scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    creds = Credentials.from_service_account_file(json_credencial, scopes=scopes)
    gc = gspread.authorize(creds)

    # Abre a planilha pelo ID
    sh = gc.open_by_key(sheet_id)
    worksheet = sh.get_worksheet(0)  # primeira aba

    # Pega todos os dados
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    df.to_csv(output_csv, index=False)
    print(f'Dados salvos em {output_csv}')

# Exemplo de uso
if __name__ == "__main__":
    json_credencial = '/home/emanoel/Dropbox/avamec/automacao/credencial.json'  # caminho para seu arquivo de credencial
    sheet_id = '1IldiJwcZFkxNEpZ5nUj0ZodGkf3QgUhY1VcLzklDNs8'  # substitua pelo ID da sua planilha
    try:
        baixar_planilha_por_id(json_credencial, sheet_id, 'dados_cursistas.csv')
    except Exception as e:
        print(f"Não foi possível baixar a planilha: {e}")