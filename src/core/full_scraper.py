import os
import time
import json
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AvamecFullScraper:
    def __init__(self):
        options = webdriver.ChromeOptions()
        # IMPORTANT: No headless mode - we need maximized window
        # options.add_argument("--headless") 
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--start-maximized")
        options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.wait = WebDriverWait(self.driver, 20)

    def load_cookies(self, domain):
        try:
            with open('data/avamec_cookies.txt', 'r') as f:
                cookie_str = f.read().strip()
                
            self.driver.get(domain)
            
            for item in cookie_str.split(';'):
                if '=' in item:
                    name, value = item.strip().split('=', 1)
                    self.driver.add_cookie({'name': name, 'value': value})
            logger.info("Cookies loaded.")
            self.driver.refresh()
            time.sleep(2)
        except Exception as e:
            logger.error(f"Error loading cookies: {e}")

    def scrape_course(self, course_id, course_name):
        logger.info(f"Processing {course_name} ({course_id})...")
        base_url = f"https://avamecinterativo.mec.gov.br/app/dashboard/environments/{course_id}"
        self.driver.get(base_url)
        time.sleep(5)
        
        # Maximize window
        self.driver.maximize_window()
        time.sleep(2)
        
        # Find groups
        elements = self.driver.find_elements(By.XPATH, "//a[.//p[contains(text(), 'Salas de aprendizagem - Grupo')]]")
        
        groups_found = []
        for el in elements:
            try:
                text_el = el.find_element(By.XPATH, ".//p")
                text = text_el.text
                groups_found.append(text)
            except:
                continue
                
        logger.info(f"Found {len(groups_found)} groups in {course_name}")
        
        course_data = []
        
        for group_name in groups_found:
            logger.info(f"Scraping {group_name}...")
            self.driver.get(base_url)
            time.sleep(3)
            
            try:
                xpath = f"//a[.//p[contains(text(), '{group_name}')]]"
                el = self.driver.find_element(By.XPATH, xpath)
                el.click()
            except Exception as e:
                logger.error(f"Could not click {group_name}: {e}")
                continue
                
            time.sleep(3)
            current_url = self.driver.current_url
            
            # Go to Gradebook
            gradebook_url = f"{current_url}/gradebook"
            self.driver.get(gradebook_url)
            
            try:
                self.wait.until(EC.presence_of_element_located((By.XPATH, "//table")))
                time.sleep(3)
                
                # Click "Visão agrupada" button
                try:
                    # Find button by text content
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    for btn in buttons:
                        if "agrupada" in btn.text.lower():
                            btn.click()
                            logger.info("Clicked 'Visão agrupada'")
                            time.sleep(5)
                            break
                except Exception as e:
                    logger.warning(f"Could not click grouped view: {e}")
                
                # Extract data using JavaScript for reliability
                script = """
                (() => {
                    const table = document.querySelector('table');
                    if (!table) return {error: "No table found"};
                    
                    // Get headers
                    const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.innerText.trim().replace(/\\s+/g, ' '));
                    
                    // Get all student rows
                    const rows = Array.from(table.querySelectorAll('tbody tr'));
                    const students = [];
                    
                    for (const row of rows) {
                        const cells = Array.from(row.querySelectorAll('td')).map(td => td.innerText.trim().replace(/\\s+/g, ' '));
                        if (cells.length === 0) continue;
                        
                        const studentData = {
                            name: cells[0],
                            grades: {}
                        };
                        
                        for (let i = 1; i < headers.length && i < cells.length; i++) {
                            studentData.grades[headers[i]] = cells[i] || "";
                        }
                        
                        students.push(studentData);
                    }
                    
                    return {headers, students};
                })();
                """
                
                result = self.driver.execute_script(script)
                
                if 'error' in result:
                    logger.error(f"Script error: {result['error']}")
                    continue
                    
                logger.info(f"Extracted {len(result.get('students', []))} students from {group_name}")
                
                for student in result.get('students', []):
                    student_data = {
                        "turma": course_name,
                        "grupo": group_name,
                        "name": student['name'],
                        "grades": student['grades']
                    }
                    course_data.append(student_data)
            
            except Exception as e:
                logger.error(f"Gradebook failed for {group_name}: {e}")
                
        return course_data

    def run(self):
        self.load_cookies("https://avamecinterativo.mec.gov.br/")
        
        all_data = []
        # Turma A (179), Turma B (180)
        all_data.extend(self.scrape_course("179", "Turma A"))
        all_data.extend(self.scrape_course("180", "Turma B"))
        
        output_file = "data/avamec_data_full.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(all_data)} student records to {output_file}")    
        self.driver.quit()

if __name__ == "__main__":
    AvamecFullScraper().run()
