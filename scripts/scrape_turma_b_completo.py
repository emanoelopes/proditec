#!/usr/bin/env python3
"""
Scraper COMPLETO - Extrai situação parcial de TODOS os grupos da Turma B
Navega por todos os 10 grupos automaticamente
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

def scrape_all_turma_b():
    """Extrai situação parcial de todos os 10 grupos da Turma B"""
    
    base_dir = os.getcwd()
    cookie_file = os.path.join(base_dir, 'data/avamec_cookies.json')
    output_file = os.path.join(base_dir, 'data/avamec_turma_b_completo.json')
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # chrome_options.add_argument('--headless')  # Descomente para modo headless
    
    driver = None
    all_students = []
    
    # URLs dos 10 grupos da Turma B
    # Ajuste conforme necessário - você precisa descobrir os IDs corretos no Avamec
    turma_b_grupos = [
        {"grupo": "Turma B - Grupo 01", "url": "https://avamecinterativo.mec.gov.br/app/dashboard/environments/180/courses/7145/gradebook"},
        {"grupo": "Turma B - Grupo 02", "url": "https://avamecinterativo.mec.gov.br/app/dashboard/environments/180/courses/7145/gradebook?group=GRUPO_02_ID"},
        {"grupo": "Turma B - Grupo 03", "url": "https://avamecinterativo.mec.gov.br/app/dashboard/environments/180/courses/7145/gradebook?group=GRUPO_03_ID"},
        # ... Continue para os outros grupos
    ]
    
    try:
        print("=" * 80)
        print("SCRAPER COMPLETO - TODOS OS GRUPOS DA TURMA B")
        print("=" * 80)
        print()
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # Login inicial
        driver.get("https://avamecinterativo.mec.gov.br/app/dashboard/environments/180/courses/7145/gradebook")
        
        if os.path.exists(cookie_file):
            print("📂 Carregando cookies salvos...")
            with open(cookie_file, 'r') as f:
                cookies = json.load(f)
                for cookie in cookies:
                    driver.add_cookie(cookie)
            driver.refresh()
            time.sleep(3)
        else:
            print("⚠️ Faça login manualmente...")
            input("Pressione ENTER após fazer login...")
            cookies = driver.get_cookies()
            with open(cookie_file, 'w') as f:
                json.dump(cookies, f)
            print("✅ Cookies salvos!")
        
        # Aqui você precisa descobrir como navegar entre grupos
        # Opção 1: Se há um dropdown/seletor de grupo na página
        # Opção 2: Se cada grupo tem uma URL diferente
        # Opção 3: Se precisa clicar em botões para mudar de grupo
        
        print("\n" + "=" * 80)
        print("⚠️ MODO INTERATIVO - NAVEGAÇÃO MANUAL")
        print("=" * 80)
        print()
        print("O scraper vai extrair dados de cada grupo quando você pressionar ENTER.")
        print("Navegue manualmente para cada grupo da Turma B no navegador.")
        print()
        
        for i in range(1, 11):  # 10 grupos
            grupo_nome = f"Turma B - Grupo {i:02d}"
            
            print(f"\n{'='*80}")
            print(f"📋 GRUPO {i}/10: {grupo_nome}")
            print(f"{'='*80}")
            print(f"\n👉 Navegue para o {grupo_nome} no navegador")
            input("Pressione ENTER quando estiver pronto para extrair dados deste grupo...")
            
            # Aguardar página carregar
            time.sleep(2)
            
            print(f"📊 Extraindo dados do {grupo_nome}...")
            
            try:
                wait = WebDriverWait(driver, 10)
                rows = wait.until(EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "table tbody tr")
                ))
                
                print(f"   Encontradas {len(rows)} linhas")
                
                grupo_students = []
                for idx, row in enumerate(rows):
                    try:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) < 2:
                            continue
                        
                        student_name = cells[0].text.strip()
                        situacao = cells[-1].text.strip()
                        
                        if student_name:
                            grupo_students.append({
                                'nome': student_name,
                                'grupo': grupo_nome,
                                'situacao_parcial': situacao,
                                'data_extracao': datetime.now().isoformat()
                            })
                    except Exception as e:
                        continue
                
                all_students.extend(grupo_students)
                print(f"   ✅ {len(grupo_students)} alunos extraídos")
                
            except Exception as e:
                print(f"   ❌ Erro ao extrair dados: {e}")
                opcao = input("   Continuar para próximo grupo? (s/n): ")
                if opcao.lower() != 's':
                    break
        
        # Salvar dados
        if all_students:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'data_extracao': datetime.now().isoformat(),
                    'turma': 'Turma B',
                    'total_grupos': len(set([a['grupo'] for a in all_students])),
                    'total_alunos': len(all_students),
                    'alunos': all_students
                }, f, indent=2, ensure_ascii=False)
            
            print("\n" + "=" * 80)
            print("✅ EXTRAÇÃO COMPLETA!")
            print("=" * 80)
            print(f"📁 Dados salvos em: {output_file}")
            print(f"📊 Total de grupos processados: {len(set([a['grupo'] for a in all_students]))}")
            print(f"📊 Total de alunos: {len(all_students)}")
            print()
            
            # Estatísticas por grupo
            grupos_count = {}
            for aluno in all_students:
                grupo = aluno['grupo']
                grupos_count[grupo] = grupos_count.get(grupo, 0) + 1
            
            print("Alunos por grupo:")
            for grupo in sorted(grupos_count.keys()):
                print(f"  - {grupo}: {grupos_count[grupo]} alunos")
        else:
            print("\n⚠️ Nenhum dado foi extraído.")
        
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
    scrape_all_turma_b()
