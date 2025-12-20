import os.path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/drive.readonly']

def check_spreadsheet_type():
    creds = None
    base_path = '/home/emanoel/proditec'
    token_path = os.path.join(base_path, 'token.json')
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds:
        print("Credenciais não encontradas.")
        return

    try:
        # Try Drive API to see mimeType
        service_drive = build('drive', 'v3', credentials=creds)
        file_id = '1s9JhF0oUVI0iXSsbSlQ1TIvH5L1T9mGQ'
        
        file_meta = service_drive.files().get(fileId=file_id, fields='id, name, mimeType').execute()
        print(f"File Name: {file_meta.get('name')}")
        print(f"Mime Type: {file_meta.get('mimeType')}")
        
        if file_meta.get('mimeType') == 'application/vnd.google-apps.spreadsheet':
            print("This is a native Google Sheet.")
            
            # Now try Sheets API
            service_sheets = build('sheets', 'v4', credentials=creds)
            print("Fetching Sheets metadata...")
            sheet_metadata = service_sheets.spreadsheets().get(spreadsheetId=file_id).execute()
            for sheet in sheet_metadata.get('sheets', []):
                print(f"- Tab: {sheet['properties']['title']}")
        else:
            print("This is NOT a native Google Sheet (likely XLSX).")
            # If it is XLSX, we might need to export/download it.
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_spreadsheet_type()
