import pandas as pd
import json
import os
import re
import unicodedata
from difflib import SequenceMatcher

def normalize_name(name):
    if not isinstance(name, str):
        return ""
    # Normalize unicode characters to ascii (remove accents)
    nfkd_form = unicodedata.normalize('NFKD', name)
    name = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    # Remove extra spaces and uppercasing
    return re.sub(r'\s+', ' ', name.strip().upper())

def is_ignored(name):
    """Check if name indicates cancellation or transfer."""
    ignored_keywords = ['CANCELADA', 'CANCELADO', 'TRANSFERIDO', 'TRANSFERIDA', 'DESISTENTE', 'DESISTIU']
    name_upper = name.upper()
    for keyword in ignored_keywords:
        if keyword in name_upper:
            return True
    return False

def get_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, 'data', 'grades_consolidados.csv')
    json_path = os.path.join(base_dir, 'data', 'avamec_turma_b_completo.json')
    output_path = os.path.join(base_dir, 'relatorio_ortografia_nomes.txt')

    print(f"--- Processando Relatório de Ortografia... ---")

    if not os.path.exists(csv_path) or not os.path.exists(json_path):
        print("Erro: Arquivos de dados não encontrados.")
        return

    # 1. Load Data
    # Spreadsheet
    df = pd.read_csv(csv_path, header=0)
    name_col = df.columns[1] # Assumed based on prev inspection
    
    # Find Group Col
    group_col = None
    for col in df.columns:
        if df[col].astype(str).str.contains('Turma [AB]', regex=True, na=False).any():
            group_col = col
            break
            
    sheet_data = {} # Normalized Name -> {Original Name, Group}
    
    for _, row in df.iterrows():
        turma_info = str(row[group_col])
        if 'Turma B' in turma_info:
            raw_name = str(row[name_col])
            
            if is_ignored(raw_name) or raw_name.lower() in ['nan', 'none', '']:
                continue
                
            norm = normalize_name(raw_name)
            # Extract just the Group part simpler (e.g. "Turma B - Grupo 01")
            group_match = re.search(r'(Turma B - Grupo \d+)', turma_info)
            group_name = group_match.group(1) if group_match else turma_info
            
            sheet_data[norm] = {'name': raw_name, 'group': group_name, 'source': 'Planilha'}

    # Avamec
    with open(json_path, 'r', encoding='utf-8') as f:
        avamec_content = json.load(f)
    
    avamec_data = {} # Normalized Name -> {Original Name, Group}
    for student in avamec_content.get('alunos', []):
        raw_name = student.get('nome')
        group_name = student.get('grupo')
        if raw_name:
            norm = normalize_name(raw_name)
            avamec_data[norm] = {'name': raw_name, 'group': group_name, 'source': 'Avamec'}

    # 2. Compare
    sheet_norms = set(sheet_data.keys())
    avamec_norms = set(avamec_data.keys())
    
    exact_matches = sheet_norms.intersection(avamec_norms)
    
    missing_in_avamec = sheet_norms - exact_matches
    missing_in_sheet = avamec_norms - exact_matches
    
    # 3. Fuzzy Matching Analysis to find "Orthographic Differences"
    # We look for pairs between (missing_in_avamec) and (missing_in_sheet) that are similar
    
    matches = []
    
    # Threshold for "probable typo"
    THRESHOLD = 0.68
    
    processed_avamec = set()
    
    with open(output_path, 'w', encoding='utf-8') as Report:
        Report.write("--- Relatório de Divergências Ortográficas (Turma B) ---\n")
        Report.write("Foco: Erros de digitação e diferenças de escrita.\n")
        Report.write("Ignorados: Cancelados, Transferidos, Desistentes.\n\n")
        
        Report.write("================================================================================\n")
        Report.write("PROVÁVEIS ERROS DE DIGITAÇÃO (Alta Similaridade)\n")
        Report.write("================================================================================\n")
        
        found_matches = False
        
        # Sort for consistent output
        sorted_sheet_missing = sorted(list(missing_in_avamec))
        
        for sheet_n in sorted_sheet_missing:
            best_match = None
            best_score = 0
            
            for avamec_n in missing_in_sheet:
                score = get_similarity(sheet_n, avamec_n)
                if score > best_score:
                    best_score = score
                    best_match = avamec_n
            
            if best_score > THRESHOLD:
                found_matches = True
                s_info = sheet_data[sheet_n]
                a_info = avamec_data[best_match]
                
                Report.write(f"PLANILHA: {s_info['name']:<40} | Grupo: {s_info['group']}\n")
                Report.write(f"AVAMEC:   {a_info['name']:<40} | Grupo: {a_info['group']}\n")
                Report.write(f"Diferença: {100*(1-best_score):.1f}% | (Similaridade: {best_score:.3f})\n")
                Report.write("-" * 80 + "\n")
                
                processed_avamec.add(best_match)
            else:
                # No good match found
                pass

        if not found_matches:
            Report.write("Nenhuma correspondência ortográfica óbvia encontrada acima de 60% de similaridade.\n")

        Report.write("\n\n")
        Report.write("================================================================================\n")
        Report.write("SEM CORRESPONDÊNCIA ENCONTRADA (Verificar manualmente)\n")
        Report.write("================================================================================\n")
        
        Report.write("\n>>> Na Planilha (Ativos) sem par no Avamec:\n")
        cnt = 0
        for sheet_n in sorted_sheet_missing:
            # Check if we already printed this as a fuzzy match? 
            # Ideally we only print orphans here. 
            # Re-running the best match check is inefficient but safe for this scale.
            
            best_score = 0
            for avamec_n in missing_in_sheet:
                score = get_similarity(sheet_n, avamec_n)
                if score > best_score:
                    best_score = score
            
            if best_score <= THRESHOLD:
                s_info = sheet_data[sheet_n]
                Report.write(f" - {s_info['name']} ({s_info['group']})\n")
                cnt += 1
        if cnt == 0: Report.write(" (Nenhum)\n")

        Report.write("\n>>> No Avamec sem par na Planilha:\n")
        cnt = 0
        for avamec_n in sorted(list(missing_in_sheet)):
            if avamec_n not in processed_avamec:
                a_info = avamec_data[avamec_n]
                Report.write(f" - {a_info['name']} ({a_info['group']})\n")
                cnt += 1
        if cnt == 0: Report.write(" (Nenhum)\n")
        
    print(f"Relatório gerado em: {output_path}")

if __name__ == "__main__":
    main()
