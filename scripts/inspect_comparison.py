import os.path
import pandas as pd
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def inspect_tabs():
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
        spreadsheet_id = '1s9JhF0oUVI0iXSsbSlQ1TIvH5L1T9mGQ'
        
        # Read "[wa] números inválidos"
        tab_invalid = "[wa] números inválidos"
        print(f"Reading {tab_invalid}...")
        res_invalid = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=f"'{tab_invalid}'!A1:Z5").execute()
        vals_invalid = res_invalid.get('values', [])
        
        if vals_invalid:
            print("Headers (Invalid Tab):", vals_invalid[0])
            if len(vals_invalid) > 1:
                print("First row:", vals_invalid[1])
        else:
            print(f"{tab_invalid} seems empty.")

        # Read "planilha4"
        tab_p4 = "Planilha4" # User wrote 'planilha4', but often capitalization differs. I'll try exact first.
        # Actually, let's list sheet names first to be sure.
        sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = sheet_metadata.get('sheets', '')
        print("\nAvailable Tabs:")
        for sheet in sheets:
            print(f"- {sheet['properties']['title']}")
            if sheet['properties']['title'].lower() == 'planilha4':
                tab_p4 = sheet['properties']['title']

        print(f"\nReading {tab_p4}...")
        res_p4 = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=f"'{tab_p4}'!A1:Z5").execute()
        vals_p4 = res_p4.get('values', [])
        
        if vals_p4:
            print("Headers (Planilha4):", vals_p4[0])
            if len(vals_p4) > 1:
                print("First row:", vals_p4[1])
        else:
            print(f"{tab_p4} seems empty.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    inspect_tabs()
