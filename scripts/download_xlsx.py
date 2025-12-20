import os
import io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# This scope might need 'drive.readonly' or 'drive'. 
# If the current token only has 'spreadsheets.readonly', this will fail.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly'] 

def download_xlsx():
    base_path = '/home/emanoel/proditec'
    token_path = os.path.join(base_path, 'token.json')
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # ID of the suspicious spreadsheet that failed as a native sheet
    file_id = '1s9JhF0oUVI0iXSsbSlQ1TIvH5L1T9mGQ' 
    output_file = os.path.join(base_path, 'performance_data.xlsx')

    try:
        service = build('drive', 'v3', credentials=creds)
        print(f"Attempting to download file ID: {file_id}")
        
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(output_file, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")
            
        print(f"Download Complete: {output_file}")
        
    except Exception as e:
        print(f"Error downloading file: {e}")
        # Identify if it's a scope issue
        if "Insufficient Permission" in str(e):
            print("CRITICAL: The current token does not have Drive Read permissions.")

if __name__ == '__main__':
    download_xlsx()
