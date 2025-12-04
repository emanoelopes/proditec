import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import csv

# --- CONFIGURATION ---
# ID of the 'controle_interno_ti' spreadsheet
CONTROL_SPREADSHEET_ID = 'YOUR_CONTROL_SPREADSHEET_ID_HERE'

# ID of the folder containing the city sheets
TARGET_FOLDER_ID = 'YOUR_TARGET_FOLDER_ID_HERE'

# Name of the tab in 'controle_interno_ti' with the list of cities
CONTROL_TAB_NAME = 'Sheet1' # Change if different

# Column index (0-based) for City Name in Control Sheet
CONTROL_CITY_COL_INDEX = 0 

# Service Account File
SERVICE_ACCOUNT_FILE = 'service_account.json'

# Scopes
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def authenticate():
    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        gc = gspread.authorize(creds)
        drive_service = build('drive', 'v3', credentials=creds)
        return gc, drive_service
    except Exception as e:
        print(f"Authentication Error: {e}")
        return None, None

def get_expected_cities(gc):
    try:
        sh = gc.open_by_key(CONTROL_SPREADSHEET_ID)
        ws = sh.worksheet(CONTROL_TAB_NAME)
        cities = ws.col_values(CONTROL_CITY_COL_INDEX + 1)
        # Assume header is row 1, so skip it
        return [c.strip() for c in cities[1:] if c.strip()]
    except Exception as e:
        print(f"Error reading control sheet: {e}")
        return []

def get_folder_files(drive_service):
    files = []
    page_token = None
    try:
        while True:
            response = drive_service.files().list(
                q=f"'{TARGET_FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false",
                fields="nextPageToken, files(id, name, capabilities)",
                pageToken=page_token
            ).execute()
            files.extend(response.get('files', []))
            page_token = response.get('nextPageToken')
            if not page_token:
                break
        return files
    except Exception as e:
        print(f"Error listing folder files: {e}")
        return []

def verify_file(gc, drive_service, file_id, file_name, expected_city):
    issues = []
    
    # 1. Check Name
    if file_name != expected_city:
        issues.append(f"Name Mismatch: Expected '{expected_city}', Found '{file_name}'")

    # 2. Check Permissions (Drive API)
    try:
        # We need to get specific fields to check copyRequiresWriterPermission
        f = drive_service.files().get(fileId=file_id, fields="copyRequiresWriterPermission").execute()
        if not f.get('copyRequiresWriterPermission'):
            issues.append("Permission Issue: Viewers can download/copy")
    except Exception as e:
        issues.append(f"Permission Check Error: {e}")

    # 3. Check Content (Sheets API)
    try:
        sh = gc.open_by_key(file_id)
        
        # Check 'Status de confirmação de matrícula'!A1
        try:
            status_ws = sh.worksheet('Status de confirmação de matrícula')
            val_a1 = status_ws.acell('A1').value
            if val_a1 != expected_city:
                issues.append(f"Content Mismatch: 'Status'!A1 is '{val_a1}', expected '{expected_city}'")
        except gspread.exceptions.WorksheetNotFound:
            issues.append("Missing Tab: 'Status de confirmação de matrícula'")

        # Check 'Dados para tabelas'!A2 Formula
        try:
            dados_ws = sh.worksheet('Dados para tabelas')
            # gspread .formula attribute might be needed, or just check value if formula works
            # acell returns Cell object, .input_value gives the formula
            cell_a2 = dados_ws.acell('A2')
            if "SORT(UNIQUE('Pré-inscrição'!E2:E))" not in cell_a2.input_value:
                 issues.append(f"Formula Mismatch: 'Dados'!A2 is '{cell_a2.input_value}'")
        except gspread.exceptions.WorksheetNotFound:
            issues.append("Missing Tab: 'Dados para tabelas'")

        # Check Hidden Tabs
        visible_tabs = [ws.title for ws in sh.worksheets() if not ws.hidden]
        if len(visible_tabs) > 1 or (len(visible_tabs) == 1 and visible_tabs[0] != 'Status de confirmação de matrícula'):
             issues.append(f"Hidden Tabs Issue: Visible tabs are {visible_tabs}")

    except Exception as e:
        issues.append(f"Content Check Error: {e}")

    return issues

def main():
    gc, drive_service = authenticate()
    if not gc: return

    print("Fetching expected cities...")
    expected_cities = get_expected_cities(gc)
    print(f"Expected {len(expected_cities)} cities.")

    print("Fetching files from folder...")
    files = get_folder_files(drive_service)
    file_map = {f['name']: f for f in files}
    print(f"Found {len(files)} files in folder.")

    results = []

    print("Starting verification...")
    for city in expected_cities:
        print(f"Verifying: {city}")
        if city not in file_map:
            results.append({'City': city, 'Status': 'MISSING', 'Issues': 'File not found'})
            continue
        
        file_info = file_map[city]
        issues = verify_file(gc, drive_service, file_info['id'], file_info['name'], city)
        
        if issues:
            results.append({'City': city, 'Status': 'FAIL', 'Issues': '; '.join(issues)})
        else:
            results.append({'City': city, 'Status': 'PASS', 'Issues': ''})

    # Write Report
    with open('verification_report.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['City', 'Status', 'Issues'])
        writer.writeheader()
        writer.writerows(results)

    print("Verification complete. Check 'verification_report.csv'.")

if __name__ == '__main__':
    main()
