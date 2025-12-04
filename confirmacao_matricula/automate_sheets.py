import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import time

# --- CONFIGURATION ---
# Replace with your actual Master Spreadsheet ID
MASTER_SPREADSHEET_ID = 'YOUR_MASTER_SPREADSHEET_ID_HERE'

# Name of the file containing your Service Account keys
SERVICE_ACCOUNT_FILE = 'service_account.json'

# Name of the tab containing the list of cities
CITIES_TAB_NAME = 'Lista de Cidades' 
# Column index (0-based) where "Cidade - ESTADO" is located (e.g., 0 for Column A)
CITY_COLUMN_INDEX = 0

# Email to share the new sheets with (e.g., your personal email)
# Leave empty if you don't want to share automatically
SHARE_WITH_EMAIL = 'your_email@example.com'

# Scopes required
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def authenticate():
    """Authenticates using the service account file."""
    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        gc = gspread.authorize(creds)
        drive_service = build('drive', 'v3', credentials=creds)
        return gc, drive_service
    except FileNotFoundError:
        print(f"Error: Could not find {SERVICE_ACCOUNT_FILE}. Please make sure it is in the same directory.")
        return None, None
    except Exception as e:
        print(f"Authentication Error: {e}")
        return None, None

def get_cities(gc, spreadsheet_id):
    """Reads the list of cities from the master spreadsheet."""
    try:
        sh = gc.open_by_key(spreadsheet_id)
        worksheet = sh.worksheet(CITIES_TAB_NAME)
        # Assuming cities are in the first column, starting from row 2 (header)
        cities = worksheet.col_values(CITY_COLUMN_INDEX + 1)[1:] 
        return [c for c in cities if c] # Filter empty strings
    except Exception as e:
        print(f"Error reading cities: {e}")
        return []

def copy_spreadsheet(drive_service, master_id, new_name):
    """Copies the master spreadsheet."""
    try:
        body = {'name': new_name}
        new_file = drive_service.files().copy(fileId=master_id, body=body).execute()
        return new_file['id']
    except Exception as e:
        print(f"Error copying spreadsheet: {e}")
        return None

def update_spreadsheet(gc, spreadsheet_id, city_name):
    """Updates the new spreadsheet with city-specific data."""
    try:
        sh = gc.open_by_key(spreadsheet_id)
        
        # 3. Update 'Status de confirmação de matrícula' with City Name
        # Assuming the cell to update is A1 or similar. 
        # INSTRUCTION: "Vá em 'Status de confirmação de matrícula' e coloque a 'CIDADE - ESTADO' correta"
        # I will assume cell B1 or A1. Let's assume A1 for now or search for a placeholder if I could.
        # Given the prompt doesn't specify the cell, I'll assume A1 for now.
        status_tab = sh.worksheet('Status de confirmação de matrícula')
        status_tab.update_acell('A1', city_name) # REPLACE 'A1' IF NEEDED
        
        # 2.3 Verify formula in 'Dados para tabelas'!A2
        # =SORT(UNIQUE('Pré-inscrição'!E2:E))
        # We can just re-write it to be sure.
        try:
            dados_tab = sh.worksheet('Dados para tabelas')
            dados_tab.update_acell('A2', "=SORT(UNIQUE('Pré-inscrição'!E2:E))")
        except gspread.exceptions.WorksheetNotFound:
            print("Warning: 'Dados para tabelas' tab not found.")

        # 3.1 Hide all tabs except 'Status de confirmação de matrícula'
        for ws in sh.worksheets():
            if ws.title != 'Status de confirmação de matrícula':
                ws.hide()
                
        print(f"Updated content for {city_name}")
        return True
    except Exception as e:
        print(f"Error updating spreadsheet {spreadsheet_id}: {e}")
        return False

def set_permissions(drive_service, file_id):
    """
    Removes 'Viewers and commenters can see the option to download, print, and copy'.
    And shares with the same people (if copying didn't already).
    """
    try:
        # 4. Disable download/print/copy for viewers
        drive_service.files().update(
            fileId=file_id,
            body={'copyRequiresWriterPermission': True}
        ).execute()
        
        # Note: "Compartilhar com as mesmas pessoas" is usually a manual checkbox when copying.
        # The API copy method doesn't automatically copy permissions unless we explicitly handle it,
        # but usually we'd just add the specific users needed. 
        # If we need to copy permissions, we'd need to list them from master and add them here.
        # For now, we'll assume the user (Service Account) is the owner and that's enough for the script.
        # You might need to share it with your personal account to see it.
        
        if SHARE_WITH_EMAIL and SHARE_WITH_EMAIL != 'your_email@example.com':
            drive_service.permissions().create(
                fileId=file_id,
                body={
                    'type': 'user',
                    'role': 'writer',
                    'emailAddress': SHARE_WITH_EMAIL
                }
            ).execute()
            print(f"Shared with {SHARE_WITH_EMAIL}")
        
        print(f"Permissions updated for {file_id}")
    except Exception as e:
        print(f"Error setting permissions: {e}")

def main():
    gc, drive_service = authenticate()
    if not gc:
        return

    cities = get_cities(gc, MASTER_SPREADSHEET_ID)
    if not cities:
        print("No cities found or error reading cities.")
        return

    print(f"Found {len(cities)} cities. Starting process...")

    for city in cities:
        print(f"Processing: {city}")
        
        # 1. Copy and Rename
        new_id = copy_spreadsheet(drive_service, MASTER_SPREADSHEET_ID, city)
        if not new_id:
            continue
            
        # 2 & 3. Update Content and Hide Tabs
        update_spreadsheet(gc, new_id, city)
        
        # 4. Permissions
        set_permissions(drive_service, new_id)
        
        print(f"Done: {city} (ID: {new_id})")
        print("-" * 20)
        
        # Avoid hitting rate limits
        time.sleep(2)

if __name__ == '__main__':
    main()
