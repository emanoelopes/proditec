#!/usr/bin/env python3
"""
Scraper para extrair 'Situação parcial' do Avamec
Visão Agrupada: https://avamecinterativo.mec.gov.br/app/dashboard/environments/180/courses/7145/gradebook
"""

import sys
import os
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def scrape_avamec_status():
    """Extrai situação parcial de todos os alunos do Avamec"""
    
    base_dir = os.getcwd()
    cookie_file = os.path.join(base_dir, 'data/avamec_cookies.json')
    output_file = os.path.join(base_dir, 'data/avamec_status_situacao.json')
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # chrome_options.add_argument('--headless')  # Descomente para modo headless
    
    driver = None
    
    try:
        print("=" * 80)
        print("SCRAPER DE SITUAÇÃO PARCIAL - AVAMEC")
        print("=" * 80)
        print()
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        driver.get("https://avamecinterativo.mec.gov.br/app/dashboard/environments/180/courses/7145/gradebook")
        
        # Tentar carregar cookies se existirem
        if os.path.exists(cookie_file):
            print("📂 Carregando cookies salvos...")
            with open(cookie_file, 'r') as f:
                cookies = json.load(f)
                for cookie in cookies:
                    driver.add_cookie(cookie)
            driver.refresh()
            time.sleep(3)
        else:
            print("⚠️ Arquivo de cookies não encontrado.")
            print("ℹ️  Faça login manualmente e o script salvará os cookies.")
            input("Pressione ENTER após fazer login...")
            
            # Salvar cookies
            cookies = driver.get_cookies()
            with open(cookie_file, 'w') as f:
                json.dump(cookies, f)
            print("✅ Cookies salvos!")
        
        # Aguardar página carregar
        print("\n⏳ Aguardando página carregar...")
        time.sleep(5)
        
        # Verificar se está logado
        if "login" in driver.current_url.lower():
            print("❌ Não está logado. Faça login e execute novamente.")
            input("Pressione ENTER após fazer login...")
            driver.get("https://avamecinterativo.mec.gov.br/app/dashboard/environments/180/courses/7145/gradebook")
            time.sleep(5)
        
        print("✅ Página do livro de notas carregada!")
        print("📊 Extraindo dados da situação parcial...")
        
        # Aqui você vai extrair os dados da tabela
        # A estrutura exata depende do HTML do Avamec
        # Exemplo genérico:
        
        wait = WebDriverWait(driver, 20)
        
        # Tentar encontrar a tabela de notas
        # Ajuste os seletores conforme necessário
        students_data = []
        
        try:
            # Exemplo: procurar linhas de alunos
            # VOCÊ PRECISA AJUSTAR ESTES SELETORES PARA O HTML REAL DO AVAMEC
            rows = wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "table tbody tr")
            ))
            
            print(f"📝 Encontradas {len(rows)} linhas na tabela")
            
            for idx, row in enumerate(rows):
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    
                    if len(cells) < 2:
                        continue
                    
                    # Ajuste os índices conforme a estrutura real
                    # Exemplo: [Nome, Turma, Grupo, Situação parcial]
                    student_name = cells[0].text.strip()
                    situacao = cells[-1].text.strip()  # Última coluna (ajuste conforme necessário)
                    
                    if student_name:
                        students_data.append({
                            'nome': student_name,
                            'situacao_parcial': situacao,
                            'data_extracao': datetime.now().isoformat()
                        })
                    
                except Exception as e:
                    print(f"⚠️ Erro ao processar linha {idx}: {e}")
                    continue
            
        except Exception as e:
            print(f"❌ Erro ao extrair tabela: {e}")
            print("\n💡 IMPORTANTE: Você precisa ajustar os seletores CSS no script")
            print("   para corresponder ao HTML real da página do Avamec.")
            print("\n   Inspecione a página e atualize os seletores em:")
            print("   scripts/scrape_avamec_status.py")
        
        # Salvar dados
        if students_data:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'data_extracao': datetime.now().isoformat(),
                    'total_alunos': len(students_data),
                    'alunos': students_data
                }, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Dados salvos em: {output_file}")
            print(f"📊 Total de alunos extraídos: {len(students_data)}")
        else:
            print("\n⚠️ Nenhum dado foi extraído.")
            print("Você precisa ajustar os seletores CSS no script.")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            print("\n🔄 Fechando navegador em 5 segundos...")
            time.sleep(5)
            driver.quit()

if __name__ == "__main__":
    scrape_avamec_status()
