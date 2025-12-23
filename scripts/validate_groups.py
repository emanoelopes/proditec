#!/usr/bin/env python3
"""
Valida a qualidade dos dados de todos os grupos
Identifica anomalias e inconsistências
"""

import pandas as pd
import sys

def validate_all_groups():
    csv_path = 'data/grades_consolidados.csv'
    
    try:
        df = pd.read_csv(csv_path, header=0)
    except Exception as e:
        print(f"Erro ao ler CSV: {e}")
        return
    
    # Encontrar coluna de grupo
    group_col = None
    for col in df.columns:
        if df[col].astype(str).str.contains('Turma [AB]', regex=True, na=False).any():
            group_col = col
            break
    
    if not group_col:
        print("Coluna de grupo não encontrada!")
        return
    
    # Extrair info de turma/grupo
    df['Turma_Grupo'] = df[group_col].astype(str).str.extract(r'(Turma [AB] - Grupo \d+)', expand=False)
    
    print("=" * 80)
    print("VALIDAÇÃO DE QUALIDADE DOS DADOS - TODOS OS GRUPOS")
    print("=" * 80)
    print()
    
    grupos = sorted([g for g in df['Turma_Grupo'].unique() if pd.notna(g)])
    
    issues_found = []
    
    for grupo in grupos:
        df_grupo = df[df['Turma_Grupo'] == grupo]
        qtd_alunos = len(df_grupo)
        
        # Verificar primeira coluna (deve ser números sequenciais)
        first_col_values = df_grupo.iloc[:, 0].astype(str).str.strip()
        
        # Contar quantos são números válidos
        numeric_count = 0
        non_numeric = []
        
        for idx, val in enumerate(first_col_values):
            try:
                int(val)
                numeric_count += 1
            except ValueError:
                non_numeric.append((idx, val))
        
        # Verificar segunda coluna (nomes)
        second_col_values = df_grupo.iloc[:, 1].astype(str).str.strip()
        empty_names = sum(1 for name in second_col_values if not name or len(name) < 3 or name == 'nan')
        
        # Status
        status = "✅ OK"
        details = []
        
        if numeric_count != qtd_alunos:
            status = "⚠️ ATENÇÃO"
            details.append(f"Apenas {numeric_count}/{qtd_alunos} com ID numérico válido")
            issues_found.append({
                'grupo': grupo,
                'issue': 'IDs não numéricos',
                'detalhes': non_numeric
            })
        
        if empty_names > 0:
            status = "⚠️ ATENÇÃO"
            details.append(f"{empty_names} nomes vazios/inválidos")
            issues_found.append({
                'grupo': grupo,
                'issue': 'Nomes vazios',
                'quantidade': empty_names
            })
        
        # Verificar se quantidade está dentro do esperado (15-35 alunos)
        if qtd_alunos < 15:
            status = "⚠️ POUCOS ALUNOS"
            details.append(f"Apenas {qtd_alunos} alunos (esperado 15-35)")
        elif qtd_alunos > 35:
            status = "⚠️ MUITOS ALUNOS"
            details.append(f"{qtd_alunos} alunos (esperado 15-35)")
            issues_found.append({
                'grupo': grupo,
                'issue': 'Quantidade anormal',
                'quantidade': qtd_alunos
            })
        
        print(f"{status} {grupo}: {qtd_alunos} alunos")
        if details:
            for detail in details:
                print(f"   - {detail}")
    
    print()
    print("=" * 80)
    print("RESUMO DE PROBLEMAS ENCONTRADOS")
    print("=" * 80)
    print()
    
    if not issues_found:
        print("✅ Nenhum problema encontrado! Todos os grupos estão consistentes.")
    else:
        print(f"⚠️ {len(issues_found)} problema(s) detectado(s):\n")
        for i, issue in enumerate(issues_found, 1):
            print(f"{i}. Grupo: {issue['grupo']}")
            print(f"   Tipo: {issue['issue']}")
            if 'detalhes' in issue:
                print(f"   Detalhes: {issue['detalhes'][:3]}")  # Primeiros 3
            if 'quantidade' in issue:
                print(f"   Quantidade: {issue['quantidade']}")
            print()
    
    # Estatísticas gerais
    print("=" * 80)
    print("ESTATÍSTICAS GERAIS")
    print("=" * 80)
    print(f"Total de grupos: {len(grupos)}")
    print(f"Total de alunos: {len(df[df['Turma_Grupo'].notna()])}")
    print(f"Média de alunos por grupo: {len(df[df['Turma_Grupo'].notna()]) / len(grupos):.1f}")
    print()

if __name__ == "__main__":
    validate_all_groups()
