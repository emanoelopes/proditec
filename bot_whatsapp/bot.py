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
from selenium.common.exceptions import TimeoutException
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
            # Wait for the input box where the pre-filled message is
            input_box_xpath = '//*[@id="main"]//footer//*[@role="textbox"]'
            
            # Sometimes an alert appears if the number is invalid
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, input_box_xpath))
                )
            except TimeoutException:
                # Timeout occurred. Determine why.
                logging.warning(f"Timeout waiting for chat with {phone}. Checking for errors...")
                
                # Check 1: Invalid Number Modal
                # The text usually contains "Phone number shared via url is invalid." or "The phone number... is not on WhatsApp"
                # The modal usually comes from a div with role="dialog" or text matching invalid number
                try:
                    invalid_xpath = '//*[contains(text(), "VALID")]' # Generic check for "invalid" text might be risky, but specific text depends on locale
                    # Better to check for the specific popup structure if possible, but text is often reliably present in the UI
                    # Portuguese: "O número de telefone... não é válido"
                    # English: "Phone number shared via url is invalid"
                    
                    # We will check if the main chat window is NOT present but we are still on the page
                    if len(self.driver.find_elements(By.XPATH, '//*[@data-testid="popup-controls-ok"]')) > 0:
                         # This is the "OK" button on the invalid number popup
                         click_ok = self.driver.find_element(By.XPATH, '//*[@data-testid="popup-controls-ok"]')
                         click_ok.click()
                         logging.warning(f"Invalid number detected for {phone}.")
                         return False
                except Exception:
                    pass

                # Check 2: Disconnected / Logged Out (QR Code page)
                # If the side pane is gone, we are likely logged out.
                if len(self.driver.find_elements(By.XPATH, '//*[@id="side"]')) == 0:
                    logging.warning("WhatsApp Web session disconnected! Waiting for QR Code scan...")
                    
                    # Wait for user to scan QR code again
                    while True:
                        try:
                            # Check if back online
                            if len(self.driver.find_elements(By.XPATH, '//*[@id="side"]')) > 0:
                                logging.info("Re-connection successful! Resuming...")
                                # Retry sending the message to this user
                                # We need to reload the url because we might be on a landing page
                                self.driver.get(url)
                                break
                            time.sleep(2)
                        except Exception as e:
                            logging.error(f"Error while waiting for login: {e}")
                            time.sleep(2)
                            
                    # After breaking the loop, we recurse to try sending again
                    # Be careful with recursion depth, but typically this happens once or twice
                    # Recurse:
                    return self.send_message(phone, message)
                
                logging.warning(f"Could not open chat for {phone}. Reason unknown (not invalid, not disconnected). Skipping.")
                return False
            except Exception as e:
                logging.warning(f"Could not open chat for {phone}. Error: {e}")
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
