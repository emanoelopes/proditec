#!/usr/bin/env python3
"""
Scraper AUTOMÁTICO - Extrai situação parcial de TODAS as turmas e grupos
Navega automaticamente pelos grupos usando Selenium
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

def scrape_all_avamec():
    """Extrai situação parcial de todos os grupos (Turma A e B)"""
    
    base_dir = os.getcwd()
    cookie_file = os.path.join(base_dir, 'data/avamec_cookies.json')
    output_file = os.path.join(base_dir, 'data/avamec_completo.json')
    
    # Configurações das turmas
    turmas_config = [
        {
            'nome': 'Turma A',
            'url': 'https://avamecinterativo.mec.gov.br/app/dashboard/environments/179/gradebook',
            'grupos': 10
        },
        {
            'nome': 'Turma B',
            'url': 'https://avamecinterativo.mec.gov.br/app/dashboard/environments/180/gradebook',
            'grupos': 10
        }
    ]
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    # chrome_options.add_argument('--headless')  # Descomente para modo headless
    
    driver = None
    all_students = []
    
    try:
        print("=" * 80)
        print("SCRAPER AUTOMÁTICO - TODAS AS TURMAS E GRUPOS")
        print("=" * 80)
        print()
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        wait = WebDriverWait(driver, 20)
        
        # Login inicial com Turma A
        print("🔐 Fazendo login...")
        driver.get(turmas_config[0]['url'])
        
        if os.path.exists(cookie_file):
            print("📂 Carregando cookies salvos...")
            with open(cookie_file, 'r') as f:
                cookies = json.load(f)
                for cookie in cookies:
                    try:
                        driver.add_cookie(cookie)
                    except:
                        pass
            driver.refresh()
            time.sleep(3)
        else:
            print("⚠️ Faça login manualmente...")
            input("Pressione ENTER após fazer login...")
            cookies = driver.get_cookies()
            with open(cookie_file, 'w') as f:
                json.dump(cookies, f)
            print("✅ Cookies salvos!")
        
        # Processar cada turma
        for turma_config in turmas_config:
            turma_nome = turma_config['nome']
            turma_url = turma_config['url']
            total_grupos = turma_config['grupos']
            
            print(f"\n{'='*80}")
            print(f"📚 PROCESSANDO: {turma_nome}")
            print(f"{'='*80}\n")
            
            # Navegar para a URL base da turma
            driver.get(turma_url)
            time.sleep(3)
            
            # Processar cada grupo
            for grupo_num in range(1, total_grupos + 1):
                grupo_nome = f"{turma_nome} - Grupo {grupo_num:02d}"
                
                print(f"📋 Grupo {grupo_num}/{total_grupos}: {grupo_nome}")
                
                try:
                    # Recarregar página base se necessário
                    if grupo_num > 1:
                        driver.get(turma_url)
                        time.sleep(2)
                    
                    # PASSO 1: Clicar no grupo desejado
                    # Procurar pelo seletor de grupo (dropdown ou lista)
                    # Ajuste o seletor conforme a estrutura real da página
                    
                    # Opção A: Se for um dropdown
                    try:
                        # Tentar encontrar dropdown de grupo
                        group_selector = wait.until(EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "select[name='group'], select#group-select, .group-selector")
                        ))
                        
                        # Selecionar o grupo
                        from selenium.webdriver.support.ui import Select
                        select = Select(group_selector)
                        # Tenta selecionar por texto ou valor
                        try:
                            select.select_by_visible_text(f"Grupo {grupo_num:02d}")
                        except:
                            select.select_by_index(grupo_num)
                        
                        time.sleep(2)
                        print(f"   ✓ Grupo {grupo_num:02d} selecionado")
                    except:
                        # Opção B: Se for uma lista de links
                        try:
                            grupo_link = wait.until(EC.presence_of_element_located(
                                (By.XPATH, f"//a[contains(text(), 'Grupo {grupo_num:02d}') or contains(text(), 'Grupo 0{grupo_num}')]")
                            ))
                            grupo_link.click()
                            time.sleep(2)
                            print(f"   ✓ Grupo {grupo_num:02d} clicado")
                        except:
                            print(f"   ⚠️ Não foi possível selecionar o grupo automaticamente")
                            print(f"   👉 Navegue manualmente para {grupo_nome}")
                            input("   Pressione ENTER quando estiver pronto...")
                    
                    # PASSO 2: Clicar em "Visão Agrupada"
                    try:
                        visao_agrupada = wait.until(EC.element_to_be_clickable(
                            (By.XPATH, "//button[contains(text(), 'Visão agrupada')] | //a[contains(text(), 'Visão agrupada')] | //*[contains(@class, 'grouped-view')]")
                        ))
                        visao_agrupada.click()
                        time.sleep(2)
                        print("   ✓ Visão agrupada ativada")
                    except:
                        print("   ℹ️ Visão agrupada não encontrada (pode já estar ativa)")
                    
                    # PASSO 3: Ler a tabela
                    time.sleep(2)
                    rows = wait.until(EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "table tbody tr, .grade-table tr, .student-row")
                    ))
                    
                    print(f"   📝 Encontradas {len(rows)} linhas")
                    
                    grupo_students = []
                    for idx, row in enumerate(rows):
                        try:
                            cells = row.find_elements(By.TAG_NAME, "td")
                            if len(cells) < 2:
                                continue
                            
                            # Primeira célula = nome do aluno
                            student_name = cells[0].text.strip()
                            
                            # Última célula = situação parcial
                            situacao = cells[-1].text.strip()
                            
                            # Filtrar CANCELADOS, DESISTENTES, TRANSFERIDOS
                            if student_name and student_name not in ['Nome', 'Aluno', 'Cursista']:
                                # Ignorar se nome contém marcação de cancelamento
                                nome_upper = student_name.upper()
                                if any(x in nome_upper for x in ['CANCELAD', 'DESISTENT', 'TRANSFERIDO', 'EVASÃO']):
                                    continue  # Pular este aluno
                                
                                grupo_students.append({
                                    'nome': student_name,
                                    'turma': turma_nome,
                                    'grupo': grupo_nome,
                                    'situacao_parcial': situacao,
                                    'data_extracao': datetime.now().isoformat()
                                })
                        except Exception as e:
                            continue
                    
                    all_students.extend(grupo_students)
                    print(f"   ✅ {len(grupo_students)} alunos extraídos\n")
                    
                except Exception as e:
                    print(f"   ❌ Erro ao processar {grupo_nome}: {e}")
                    print(f"   Deseja continuar? (s/n): ", end='')
                    # Apenas alerta, continua automaticamente
                    time.sleep(1)
                    print("sim (continuando...)")
        
        # Salvar dados
        if all_students:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'data_extracao': datetime.now().isoformat(),
                    'total_turmas': len(turmas_config),
                    'total_grupos': sum(t['grupos'] for t in turmas_config),
                    'total_alunos': len(all_students),
                    'alunos': all_students
                }, f, indent=2, ensure_ascii=False)
            
            print("\n" + "=" * 80)
            print("✅ EXTRAÇÃO COMPLETA!")
            print("=" * 80)
            print(f"📁 Dados salvos em: {output_file}")
            print(f"📊 Total de alunos: {len(all_students)}")
            print()
            
            # Estatísticas por turma
            turmas_count = {}
            grupos_count = {}
            for aluno in all_students:
                turma = aluno['turma']
                grupo = aluno['grupo']
                turmas_count[turma] = turmas_count.get(turma, 0) + 1
                grupos_count[grupo] = grupos_count.get(grupo, 0) + 1
            
            print("Alunos por turma:")
            for turma in sorted(turmas_count.keys()):
                print(f"  - {turma}: {turmas_count[turma]} alunos")
            
            print("\nAlunos por grupo:")
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
    scrape_all_avamec()
