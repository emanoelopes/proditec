
import os
import sys
import logging
import argparse

# Helper to add project root to python path MUST be before src imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.i18n import i18n, t
from src.core.avamec import AvamecScraper
from src.core.full_scraper import AvamecFullScraper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description=t('app.title'))
    parser.add_argument('--lang', type=str, default='pt_BR', help='Language (pt_BR, en)')
    parser.add_argument('--scraper', type=str, choices=['basic', 'full'], help='Run Avamec scraper')
    
    args = parser.parse_args()
    
    # Initialize I18n
    i18n.set_locale(args.lang)
    logger.info(t('app.starting'))
    
    if args.scraper:
        logger.info(t('scraper.start'))
        if args.scraper == 'full':
            scraper = AvamecFullScraper()
            scraper.run()
        else:
            scraper = AvamecScraper()
            if scraper.login():
                scraper.scrape_grades("180", "Turma B")
            scraper.close()
    
    if not args.scraper:
        print("Use --help to see available commands")

if __name__ == "__main__":
    main()
