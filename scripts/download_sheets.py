import os
import requests
import time

def download_sheets():
    links_file = 'links_notas.txt'
    cookies_file = 'google_cookies.txt'
    output_dir = 'data/sheets'
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(cookies_file, 'r') as f:
        cookie_string = f.read().strip()
        
    # Parse cookies
    cookies = {}
    for item in cookie_string.split(';'):
        if '=' in item:
            name, value = item.strip().split('=', 1)
            cookies[name] = value
            
    with open(links_file, 'r') as f:
        links = [l.strip() for l in f.readlines() if l.strip()]
        
    for i, link in enumerate(links):
        try:
            # Extract ID
            if '/d/' in link:
                sheet_id = link.split('/d/')[1].split('/')[0]
            else:
                print(f"Skipping invalid link: {link}")
                continue
                
            export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
            print(f"Downloading {i+1}/{len(links)}: {sheet_id}...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(export_url, cookies=cookies, headers=headers)
            
            if response.status_code == 200:
                # Calculate size in KB
                size_kb = len(response.content) / 1024
                print(f"  Success! Size: {size_kb:.2f} KB")
                
                # Check if it looks like a login page (small size or specific text)
                if size_kb < 50 and "<!DOCTYPE html>" in response.text and "accounts.google.com" in response.text:
                     print("  WARNING: Downloaded content seems to be a login page, not CSV.")
                
                output_path = os.path.join(output_dir, f"sheet_{sheet_id}.csv")
                with open(output_path, 'wb') as f_out:
                    f_out.write(response.content)
            else:
                print(f"  Failed: {response.status_code}")
                
            time.sleep(1) # Be nice
            
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    download_sheets()
