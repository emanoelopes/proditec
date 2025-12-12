import time
import random
import logging
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WhatsAppBot:
    def __init__(self):
        self.driver = None
        self.wait = None

    def start(self):
        """Initializes the Chrome driver and opens WhatsApp Web."""
        logging.info("Starting WhatsApp Bot...")
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless") # Headless mode doesn't work well for WA Web login
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 60)
        
        logging.info("Opening WhatsApp Web...")
        self.driver.get("https://web.whatsapp.com/")
        
        try:
            # Wait for the user to scan the QR code.
            # We look for an element that appears only after login, e.g., the side pane.
            logging.info("Please scan the QR code if not already logged in.")
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="side"]')))
            logging.info("Login detected!")
        except Exception as e:
            logging.error(f"Login failed or timeout: {e}")
            self.stop()
            raise

    def stop(self):
        """Closes the browser."""
        if self.driver:
            logging.info("Stopping bot...")
            self.driver.quit()
            self.driver = None

    def send_message(self, phone, message):
        """
        Sends a message to a specific phone number.
        
        Args:
            phone (str): The phone number in international format (e.g., "5511999999999").
            message (str): The message content.
        """
        if not self.driver:
            raise RuntimeError("Bot is not running. Call start() first.")

        try:
            # Random delay before starting new action to mimic human behavior
            # Increased delay to avoid ban (8-15 seconds)
            time.sleep(random.uniform(8, 15))
            
            # Format URL to open chat with specific number
            encoded_message = urllib.parse.quote(message)
            url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
            self.driver.get(url)
            
            # Wait for the chat to load and the send button to be clickable
            # Note: The 'send' button can be tricky. Usually pressing ENTER on the message box is more reliable.
            # We wait for the message input box to ensure the page loaded.
            
            # Wait for the input box where the pre-filled message is
            input_box_xpath = '//*[@id="main"]//footer//*[@role="textbox"]'
            
            # Sometimes an alert appears if the number is invalid
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, input_box_xpath))
                )
            except Exception:
                logging.warning(f"Could not open chat for {phone}. Number might be invalid.")
                return False

            video_recording_delay = 1
            time.sleep(video_recording_delay)

            # Locate the input box (it should already have the text)
            input_box = self.driver.find_element(By.XPATH, input_box_xpath)
            
            # Random delay before sending
            time.sleep(random.uniform(3, 6))
            
            # Press Enter to send
            input_box.send_keys(Keys.ENTER)
            
            logging.info(f"Message sent to {phone}")
            
            # Wait a bit after sending to ensure it goes through before navigating away
            time.sleep(random.uniform(5, 8))
            return True

        except Exception as e:
            logging.error(f"Failed to send message to {phone}: {e}")
            return False
