import os
import sys
import logging
import argparse
from datetime import datetime

# Setup Env - Must be before src imports
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if base_dir not in sys.path:
    sys.path.append(base_dir)

from src.core.avamec import AvamecScraper
from src.core.full_scraper import AvamecFullScraper
from src.core.consolidate_grades import consolidate_grades
from scripts.download_sheets_selenium import download_sheets_selenium
from src.utils.i18n import i18n, t

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.getcwd(), 'data', 'update_pipeline.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_pipeline(full_scrape=False):
    logger.info("Starting Grade Update Pipeline")
    
    # 1. Avamec Scraping
    logger.info("Step 1: Scraping Avamec...")
    try:
        if full_scrape:
            logger.info("Running Full Scraper...")
            scraper = AvamecFullScraper()
            scraper.run()
        else:
            logger.info("Running Basic Scraper (Turma B)...")
            scraper = AvamecScraper()
            if scraper.login():
                scraper.scrape_grades("180", "Turma B")
            scraper.close()
        logger.info("Avamec scraping completed.")
    except Exception as e:
        logger.error(f"Error during Avamec scraping: {e}", exc_info=True)
        # We might want to continue even if one part fails, or abort. 
        # For now, let's continue to try downloading sheets.

    # 2. Google Sheets Download
    logger.info("Step 2: Downloading Google Sheets...")
    try:
        download_sheets_selenium()
        logger.info("Google Sheets download completed.")
    except Exception as e:
        logger.error(f"Error during Google Sheets download: {e}", exc_info=True)

    # 3. Consolidation
    logger.info("Step 3: Consolidating Data...")
    try:
        consolidate_grades()
        logger.info("Data consolidation completed.")
    except Exception as e:
        logger.error(f"Error during consolidation: {e}", exc_info=True)

    logger.info("Pipeline finished.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update Grade Data Pipeline")
    parser.add_argument('--full', action='store_true', help='Run full Avamec scrape (all courses)')
    parser.add_argument('--lang', type=str, default='pt_BR', help='Language')
    
    args = parser.parse_args()
    
    # Setup Env
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if base_dir not in sys.path:
        sys.path.append(base_dir)
        
    i18n.set_locale(args.lang)
    
    run_pipeline(full_scrape=args.full)
