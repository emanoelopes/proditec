import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_sheets_selenium():
    links_file = 'data/links_notas.txt'
    output_dir = os.path.abspath('data/sheets')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Set download directory
    prefs = {
        "download.default_directory": output_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Load Cookies
    try:
        driver.get("https://docs.google.com")
        with open('data/google_cookies.txt', 'r') as f:
            cookie_str = f.read().strip()
            
        for item in cookie_str.split(';'):
            if '=' in item:
                name, value = item.strip().split('=', 1)
                try:
                    driver.add_cookie({'name': name, 'value': value, 'domain': '.google.com'})
                except:
                    # Try logging domain
                    pass
        logger.info("Cookies loaded.")
        driver.refresh()
    except Exception as e:
        logger.error(f"Error loading cookies: {e}")

    with open(links_file, 'r') as f:
        links = [l.strip() for l in f.readlines() if l.strip()]

    for i, link in enumerate(links):
        try:
            if '/d/' in link:
                sheet_id = link.split('/d/')[1].split('/')[0]
            else:
                continue

            msg = f"Downloading {i+1}/{len(links)}: {sheet_id}"
            logger.info(msg)
            
            # Use specific export URL
            export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
            driver.get(export_url)
            
            # Wait for download to finish
            time.sleep(5) 
            
            logger.info(f"Current URL: {driver.current_url}")
            if "accounts.google.com" in driver.current_url:
                logger.error("Redirected to login page!")
            
            # Check directory for new file
            # Google export usually names it "{Sheet Name}.csv" or "spreadsheet.csv"
            # We want to rename it to sheet_{id}.csv
            
            files = sorted([os.path.join(output_dir, f) for f in os.listdir(output_dir)], key=os.path.getmtime)
            if files:
                latest_file = files[-1]
                # Check if it was created just now
                if time.time() - os.path.getmtime(latest_file) < 20: 
                    new_name = os.path.join(output_dir, f"sheet_{sheet_id}.csv")
                    if os.path.exists(new_name):
                        os.remove(new_name)
                    os.rename(latest_file, new_name)
                    logger.info(f"Saved to {new_name}")
                else:
                    logger.warning("No new file detected.")
            
        except Exception as e:
            logger.error(f"Error downloading {link}: {e}")

    driver.quit()

if __name__ == "__main__":
    download_sheets_selenium()
