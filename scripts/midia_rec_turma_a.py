import logging
import os
import os.path
import pickle
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='automation.log'
)

# Load environment variables
load_dotenv()

# Get credentials from environment variables
USERNAME = os.getenv('AVAMEC_USERNAME')
PASSWORD = os.getenv('AVAMEC_PASSWORD')

# Validate credentials are available
if not USERNAME or not PASSWORD:
    raise ValueError("Missing credentials. Please set AVAMEC_USERNAME and AVAMEC_PASSWORD in .env file")

def setup_driver():
    """Configure and return Firefox WebDriver"""
    options = webdriver.FirefoxOptions()
    # options.add_argument('--headless')  # Uncomment to run in headless mode
    options.profile = '/home/emanoel/.mozilla/firefox/xfddl5q0.avamec'  # Update with your profile path
    return webdriver.Firefox(options=options)

def wait_for_element(driver, by, value, timeout=10):
    """Wait for element to be present and return it"""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )

def save_cookies(driver, path):
    """Save browser cookies to file"""
    if not os.path.exists('cookies'):
        os.makedirs('cookies')
    with open(path, 'wb') as file:
        pickle.dump(driver.get_cookies(), file)
    logging.info("Cookies saved successfully")

def load_cookies(driver, path):
    """Load cookies into browser session"""
    if os.path.exists(path):
        with open(path, 'rb') as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                # Skip cookies with SameSite=None and missing 'secure'
                if cookie.get('sameSite') == 'None' and not cookie.get('secure', False):
                    continue
                driver.add_cookie(cookie)
        logging.info("Cookies loaded successfully")
        return True
    return False

def perform_login(driver):
    """Handle login process including CAPTCHA"""
    login_field = wait_for_element(driver, By.CSS_SELECTOR, "input[type='text']")
    login_field.send_keys(USERNAME)
    
    password_field = wait_for_element(driver, By.CSS_SELECTOR, "input[type='password']")
    password_field.send_keys(PASSWORD)
    logging.info("Login credentials entered")
    time.sleep(1)  # Wait for any potential CAPTCHA to load
    
    # Handle CAPTCHA
    print("Por favor, resolva o CAPTCHA manualmente.")
    print("Pressione Enter após resolver o CAPTCHA...")
    input()
    
    login_button = wait_for_element(driver, By.CSS_SELECTOR, "button[type='submit']")
    driver.execute_script("arguments[0].scrollIntoView();", login_button)
    time.sleep(1)
    login_button.click()
    logging.info("Login submitted")
    
    # Wait for login to complete
    time.sleep(5)

def automate_web_task():
    """Main automation function"""
    driver = None
    cookies_path = 'cookies/avamec_session.pkl'
    
    try:
        driver = setup_driver()
        logging.info("Browser started successfully")

        # Navigate to website
        base_url = "https://avamecinterativo.mec.gov.br"
        driver.get(base_url)
        
        # Try to load existing session
        if load_cookies(driver, cookies_path):
            logging.info("Attempting to use saved session")
            driver.refresh()  # Refresh page with loaded cookies
            
            # Check if still logged in by looking for a logged-in-only element
            try:
                wait_for_element(driver, By.CSS_SELECTOR, ".user-profile", timeout=5)
                logging.info("Successfully restored previous session")
            except TimeoutException:
                logging.info("Session expired, logging in again")
                perform_login(driver)
        else:
            logging.info("No saved session found, performing fresh login")
            perform_login(driver)
        
        # Save cookies after successful login
        save_cookies(driver, cookies_path)
        
        # Navigate to dashboard
        dashboard_url = "https://avamecinterativo.mec.gov.br/dashboard/environments"
        driver.get(dashboard_url)

        # Acessar a turma A
        turma_a_url = "https://avamecinterativo.mec.gov.br/dashboard/environments/179"
        logging.info(f"Navegando para a Turma A: {turma_a_url}")
        driver.get(turma_a_url)

        # Acessar a sala de aprendizagem do grupo 1, em uma nova aba
        driver.execute_script("window.open('');")  # Open a new tab
        driver.switch_to.window(driver.window_handles[1])  # Switch to the new tab
        logging.info("New tab opened for Sala de Aprendizagem do Grupo 1")
        sala_aprendizagem_1_a = "https://avamecinterativo.mec.gov.br/app/dashboard/environments/179/courses/7114"
        logging.info(f"Navegando para a sala de aprendizagem do grupo 1: {sala_aprendizagem_1_a}")
        driver.get(sala_aprendizagem_1_a)

        # Acessar a sala 3
        sala_3_1_a = "https://avamecinterativo.mec.gov.br/app/dashboard/spaces/79549"
        logging.info(f"Navegando para a sala 3: {sala_3_1_a}")
        driver.get(sala_3_1_a)
        time.sleep(5)  # Wait for page to load
        logging.info("Navegou para a sala 3 com sucesso")
        

        # Keep browser open for manual interaction
        print("\nNavegação concluída. Pressione Enter para fechar o navegador...")
        input()

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        if driver:
            driver.quit()
            logging.info("Browser closed")

if __name__ == "__main__":
    automate_web_task()