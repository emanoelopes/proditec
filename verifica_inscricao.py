import logging
import os
import os.path
import pandas as pd
import shutil
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

def baixar_relatorios_cursistas(driver, xlsx_path, pasta_destino="relatorios_turma_a"):
    """
    Baixa os relatórios dos cursistas listados em um arquivo xlsx.
    
    Args:
        driver: Selenium WebDriver já autenticado e na página de membros da turma A.
        xlsx_path (str): Caminho para o arquivo xlsx com a coluna 'NOME_CURSISTA'.
        pasta_destino (str): Pasta onde os relatórios serão salvos.
    """
    # Cria pasta de destino se não existir
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
    
    # Lê o arquivo xlsx
    df = pd.read_excel(xlsx_path)
    nomes = df['NOME_CURSISTA'].dropna().unique()
    
    for nome in nomes:
        try:
            # Pesquisa pelo nome do cursista
            search_input = wait_for_element(driver, By.ID, "search-input")
            search_input.clear()
            search_input.send_keys(nome)
            time.sleep(2)  # Aguarda resultados aparecerem
            
            # Clica no resultado do membro
            resultado = wait_for_element(driver, By.CSS_SELECTOR, ".jss312 > p:nth-child(1)")
            resultado.click()
            time.sleep(2)
            
            # Clica no botão "Baixar Relatório"
            try:
                botao_relatorio = wait_for_element(driver, By.XPATH, "/html/body/div/div[2]/div/div/div/div[2]/div[2]/div/div[2]/div[1]/button[1]/p")
            except TimeoutException:
                botao_relatorio = wait_for_element(driver, By.CSS_SELECTOR, "button.jss188:nth-child(1) > p:nth-child(2)")
            botao_relatorio.click()
            logging.info(f"Relatório solicitado para: {nome}")
            
            # Aguarda o download (ajuste conforme necessário)
            time.sleep(5)
            
            # Localiza o arquivo baixado na pasta padrão de downloads
            # (Ajuste o caminho conforme seu sistema)
            download_dir = os.getenv('DOWNLOAD_DIR', os.path.expanduser("~/Downloads"))
            arquivos = [f for f in os.listdir(download_dir) if f.endswith(".xlsx")]
            if not arquivos:
                logging.warning(f"Nenhum arquivo .xlsx encontrado para {nome}")
                continue
            arquivo_baixado = max([os.path.join(download_dir, f) for f in arquivos], key=os.path.getctime)
            
            # Renomeia e move o arquivo para a pasta destino
            novo_nome = f"{os.path.splitext(os.path.basename(arquivo_baixado))[0]}_{nome}.xlsx"
            novo_caminho = os.path.join(pasta_destino, novo_nome)
            shutil.move(arquivo_baixado, novo_caminho)
            logging.info(f"Relatório salvo: {novo_caminho}")
            
        except Exception as e:
            logging.error(f"Erro ao baixar relatório para {nome}: {e}")

# Exemplo de uso:
# baixar_relatorios_cursistas(driver, "cursistas_turma_a.xlsx")

if __name__ == "__main__":
    driver = setup_driver()
    driver.get("https://avamecinterativo.mec.gov.br/app/dashboard/environments/179/edit")
    perform_login(driver)
    # Após login e navegação, indique o arquivo xlsx desejado:
    xlsx_path = os.getenv('XLSX_CURSISTAS_PATH', '2025.2 Lista Original- Confirmação de matrícula.xlsx')
    baixar_relatorios_cursistas(driver, xlsx_path)
    driver.quit()