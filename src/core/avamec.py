import os
import time
import logging
import json
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup, NavigableString
from src.utils.i18n import t

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

AVAMEC_URL = "https://avamecinterativo.mec.gov.br/app/login"
AVAMEC_USER = os.getenv('AVAMEC_USER') # Assuming this key, will fallback or error if missing
AVAMEC_PASSWORD = os.getenv('AVAMEC_PASSWORD')

class AvamecScraper:
    def __init__(self):
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless") # Commented out for debugging/visual confirmation
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        
        logger.info("Setting up Chrome driver...")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

    def login(self):
        if not AVAMEC_USER or not AVAMEC_PASSWORD:
            logger.error("Credentials not found in .env file. Please set AVAMEC_USER and AVAMEC_PASSWORD.")
            return False

        try:
            logger.info(t('scraper.browsing', url=AVAMEC_URL))
            self.driver.get(AVAMEC_URL)

            # Wait for the login form to appear
            wait = WebDriverWait(self.driver, 20)
            
            # Try to find the username field
            logger.info("Looking for username field...")
            # Strategy 1: standard name or id
            # Strategy 2: Material UI label association
            username_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='login']")))
            
            logger.info("Looking for password field...")
            password_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='password']")
            
            logger.info("Entering credentials...")
            username_input.clear()
            username_input.send_keys(AVAMEC_USER)
            password_input.clear()
            password_input.send_keys(AVAMEC_PASSWORD)

            # Check for reCAPTCHA (just logging warning for now)
            if "recaptcha" in self.driver.page_source.lower():
                logger.warning("reCAPTCHA detected! Manual intervention might be required.")

            logger.info("Clicking login button...")
            # Try to find the submit button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()

            # Wait for navigation to dashboard
            logger.info("Waiting for dashboard...")
            wait.until(EC.url_contains("/app/dashboard"))
            logger.info("Login successful!")
            return True

        except Exception as e:
            logger.error(f"Login failed: {e}")
            # Save screenshot for debugging
            self.driver.save_screenshot("login_failed.png")
            logger.info("Saved screenshot to login_failed.png")
            # Print page source for debugging
            with open("login_failed_source.html", "w") as f:
                f.write(self.driver.page_source)
            return False

    def close(self):
        if self.driver:
            self.driver.quit()

    def scrape_grades(self, course_id, course_name):
        """
        Scrapes grades for a specific course (Turma).
        """
        logger.info(f"Scraping grades for {course_name} (ID: {course_id})...")
        
        # Navigate to Gradebook
        gradebook_url = f"https://avamecinterativo.mec.gov.br/app/dashboard/environments/{course_id}/gradebook"
        self.driver.get(gradebook_url)
        wait = WebDriverWait(self.driver, 20)
        
        try:
            # Wait for activity list to load
            logger.info("Waiting for activity list...")
            # Select all activity links in the gradebook list
            # The structure seems to be a list of buttons/links. 
            # Based on analysis: button.MuiButtonBase-root.MuiCardActionArea-root
            # We need to be careful to select the right ones.
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.MuiCardActionArea-root")))
            
            activities = self.driver.find_elements(By.CSS_SELECTOR, "button.MuiCardActionArea-root")
            activity_links = []
            
            # Extract links first to avoid stale element exceptions
            for activity in activities:
                # The click might be intercepted or we can just get the href if it's an anchor, 
                # but it seems to be a button that triggers navigation.
                # Let's try to find an anchor inside or get the text to identify it.
                try:
                    title_element = activity.find_element(By.CSS_SELECTOR, "span.MuiCardHeader-title")
                    title = title_element.text
                    activity_links.append((title, activity))
                except:
                    continue
            
            logger.info(f"Found {len(activity_links)} activities.")
            
            all_grades = []

            # Iterate through activities (we might need to re-find elements after navigation)
            for i in range(len(activity_links)):
                # Re-find activities to avoid StaleElementReferenceException
                self.driver.get(gradebook_url)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.MuiCardActionArea-root")))
                activities = self.driver.find_elements(By.CSS_SELECTOR, "button.MuiCardActionArea-root")
                
                if i >= len(activities):
                    break
                    
                current_activity = activities[i]
                
                try:
                    title_element = current_activity.find_element(By.CSS_SELECTOR, "span.MuiCardHeader-title")
                    activity_title = title_element.text
                except:
                    activity_title = f"Activity {i+1}"
                
                logger.info(f"Scraping activity: {activity_title}")
                current_activity.click()
                
                # Wait for the grades table/grid to load
                # Based on analysis: div.MuiBox-root.jss954.MuiTableContainer-root (classes might be dynamic)
                # Look for the "NOTAS" tab content or just wait for inputs
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.MuiTableContainer-root")))
                    
                    # Scroll to load all students
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(3) # Wait for lazy load
                    
                    # Extract data
                    # The structure is tricky: Text Node (Name) -> TDs (Grades)
                    # We'll parse the HTML with BeautifulSoup for easier handling of this non-standard structure
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                    
                    container = soup.find('div', class_='MuiTableContainer-root')
                    if not container:
                        logger.warning(f"Could not find table container for {activity_title}")
                        continue
                        
                    # The container has a table inside? Or just divs?
                    # Analysis said: "Student Row: It's not a standard <tr>... names appear as text nodes"
                    # Let's look for the table body or rows
                    # If it's a standard table:
                    table = container.find('table')
                    if table:
                        rows = table.find_all('tr')
                        for row in rows:
                            cols = row.find_all('td')
                            if not cols: continue
                            # Extract name and grades
                            # This part depends heavily on the specific table structure found
                            pass
                    else:
                        # Non-standard structure handling
                        # Let's try to find all inputs and infer structure
                        # Or find the names. Names seem to be in a specific class?
                        # "Student's Name: Text nodes directly within div...MuiTableContainer-root"
                        # This implies a very flat structure.
                        
                        # Alternative: Use Selenium to find all inputs and their preceding text
                        # This is robust but slow.
                        pass
                    # Parse the content
                    container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.MuiTableContainer-root")))
                    container_html = container.get_attribute('innerHTML')
                    soup = BeautifulSoup(container_html, 'html.parser')
                    
                    students_data = []
                    current_student = None
                    grades = []
                    
                    # Iterate through children to find text nodes (names) and TDs (grades)
                    for child in soup.contents:
                        if isinstance(child, NavigableString):
                            lines = str(child).split('\n')
                            for line in lines:
                                text = line.strip()
                                if not text: continue
                                
                                # Heuristic: Name is longer than 3 chars, not a header, not a number
                                if len(text) > 3 and "Atividade" not in text and "Nome" not in text and not text.replace('.', '', 1).isdigit():
                                    if current_student and grades:
                                        students_data.append({'name': current_student, 'grades': grades})
                                    current_student = text
                                    grades = []
                        elif child.name == 'td':
                            input_tag = child.find('input')
                            if input_tag:
                                grades.append(input_tag.get('value', ''))
                    
                    # Add last student
                    if current_student and grades:
                        students_data.append({'name': current_student, 'grades': grades})
                    
                    logger.info(f"Extracted {len(students_data)} students from {activity_title}")
                    
                    # Save to file
                    output_file = f"grades_{course_id}_{i}.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(students_data, f, ensure_ascii=False, indent=2)
                    logger.info(f"Saved grades to {output_file}")
                    
                    # Break after first activity for testing
                    break
                    
                except Exception as e:
                    logger.error(f"Error scraping {activity_title}: {e}")
                    
        except Exception as e:
            logger.error(f"Error processing gradebook for {course_name}: {e}")

if __name__ == "__main__":
    scraper = AvamecScraper()
    try:
        if scraper.login():
            # Scrape Turma A (179)
            # scraper.scrape_grades("179", "Turma A")
            # Scrape Turma B (180)
            scraper.scrape_grades("180", "Turma B")
    finally:
        scraper.close()
