import os
import re
import time
import pandas as pd
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def extract_id(url):
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
    return match.group(1) if match else None

def consolidate_grades():
    base_path = os.getcwd() # Or explicit /home/emanoel/proditec
    token_path = os.path.join(base_path, 'config/token.json')
    links_file = os.path.join(base_path, 'data/links_notas.txt')
    
    if not os.path.exists(token_path):
        print("Token missing.")
        return

    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    service = build('sheets', 'v4', credentials=creds)

    if not os.path.exists(links_file):
        print("Links file missing.")
        return

    with open(links_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    all_data = []

    print(f"Found {len(urls)} links. Starting consolidation...")

    for i, url in enumerate(urls):
        sheet_id = extract_id(url)
        if not sheet_id:
            print(f"Skipping invalid URL: {url}")
            continue
            
        try:
            # Get spreadsheet metadata to find sheet name
            meta = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
            title = meta['properties']['title']
            print(f"[{i+1}/{len(urls)}] Processing: {title} ({sheet_id})")
            
            # Read all data from the first visible sheet
            # Assuming the data is in the first sheet or we read 'A:Z'
            first_sheet_title = meta['sheets'][0]['properties']['title']
            
            result = service.spreadsheets().values().get(
                spreadsheetId=sheet_id, range=f"'{first_sheet_title}'!A:ZZ").execute()
            values = result.get('values', [])
            
            if not values:
                print(f"  - No data found in {first_sheet_title}")
                continue

            # Extract headers and data
            headers = values[0]
            data = values[1:]

            # Normalize row lengths
            max_cols = max(len(r) for r in values)
            if len(headers) < max_cols:
                # Extend headers if data has more columns
                headers.extend([f"Extra_Col_{i}" for i in range(len(headers), max_cols)])
            
            # Pad rows that are shorter than max_cols
            data_padded = []
            for row in data:
                if len(row) < max_cols:
                    row.extend([''] * (max_cols - len(row)))
                data_padded.append(row)
            
            # Ensure unique columns
            seen = {}
            new_headers = []
            for col in headers:
                if col not in seen:
                    seen[col] = 1
                    new_headers.append(col)
                else:
                    seen[col] += 1
                    new_headers.append(f"{col}_{seen[col]}")

            df = pd.DataFrame(data_padded, columns=new_headers)
            
            # Add Source Metadata
            df['Source_Sheet_Title'] = title
            df['Source_URL'] = url
            
            # Attempt to extract Turma/Grupo from Title if possible
            # e.g., "Turma A - Grupo 1"
            # Adjust regex based on actual titles seen in output
            
            all_data.append(df)
            
        except Exception as e:
            print(f"  - Error processing {url}: {e}")
        
        # Avoid rate limits
        time.sleep(2)

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        output_csv = os.path.join(base_path, 'data/grades_consolidados.csv')
        final_df.to_csv(output_csv, index=False)
        print(f"\nConsolidation Complete. Saved to {output_csv}")
        print(f"Total records: {len(final_df)}")
        print("Columns found:", final_df.columns.tolist())
    else:
        print("No data consolidated.")

if __name__ == '__main__':
    consolidate_grades()
