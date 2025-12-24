#!/usr/bin/env python3
"""
Compara dados de ontem e hoje para identificar mudanças de status
De: Reprovado -> Aprovado
"""

import pandas as pd
import os
from datetime import datetime
import sys

def compare_grade_status():
    base_dir = os.getcwd()
    current_file = os.path.join(base_dir, 'data/grades_consolidados.csv')
    backup_dir = os.path.join(base_dir, 'data/backups')
    
    # Procurar backup mais recente
    if not os.path.exists(backup_dir):
        print("⚠️ Diretório de backups não existe.")
        print("📝 Crie backups diários executando:")
        print("   cp data/grades_consolidados.csv data/backups/grades_$(date +%Y%m%d).csv")
        return
    
    # Listar backups disponíveis
    backups = sorted([f for f in os.listdir(backup_dir) if f.startswith('grades_') and f.endswith('.csv')])
    
    if len(backups) == 0:
        print("⚠️ Nenhum backup encontrado.")
        print("📝 Crie um backup executando:")
        print("   mkdir -p data/backups")
        print("   cp data/grades_consolidados.csv data/backups/grades_$(date +%Y%m%d).csv")
        return
    
    # Usar o backup mais recente
    previous_file = os.path.join(backup_dir, backups[-1])
    
    print("=" * 80)
    print("COMPARAÇÃO DE STATUS DE APROVAÇÃO")
    print("=" * 80)
    print(f"Arquivo anterior: {backups[-1]}")
    print(f"Arquivo atual: grades_consolidados.csv (hoje)")
    print()
    
    try:
        # Carregar dados
        df_prev = pd.read_csv(previous_file, header=0)
        df_curr = pd.read_csv(current_file, header=0)
        
        # Encontrar coluna de status (coluna BJ das planilhas = Extra_Col_61)
        status_col = None
        
        # Tentar encontrar Extra_Col_61 primeiro
        if 'Extra_Col_61' in df_curr.columns:
            status_col = 'Extra_Col_61'
        else:
            # Fallback: procurar por coluna com "Status" no nome
            for col in df_curr.columns:
                if 'Status' in col and 'Final' in col:
                    status_col = col
                    break
        
        if not status_col:
            print("⚠️ Coluna de Status Final (Extra_Col_61) não encontrada.")
            print("Colunas disponíveis:", df_curr.columns.tolist())
            return
        
        # Encontrar coluna de grupo
        group_col = None
        for col in df_curr.columns:
            if df_curr[col].astype(str).str.contains('Turma [AB]', regex=True, na=False).any():
                group_col = col
                break
        
        # Encontrar coluna de nome
        name_col = df_curr.columns[1] if len(df_curr.columns) > 1 else df_curr.columns[0]
        
        # Adicionar identificador único para matching
        df_prev['id'] = df_prev[name_col].astype(str).str.strip().str.upper()
        df_curr['id'] = df_curr[name_col].astype(str).str.strip().str.upper()
        
        # Encontrar estudantes com mudança de status
        changes = []
        
        for idx, curr_row in df_curr.iterrows():
            student_id = curr_row['id']
            curr_status = str(curr_row[status_col]).strip().upper()
            
            # Buscar mesmo estudante no arquivo anterior
            prev_row = df_prev[df_prev['id'] == student_id]
            
            if len(prev_row) > 0:
                prev_status = str(prev_row.iloc[0][status_col]).strip().upper()
                
                # Verificar mudança de Reprovado -> Aprovado
                if 'REPROVADO' in prev_status and 'APROVADO' in curr_status:
                    changes.append({
                        'Nome': curr_row[name_col],
                        'Grupo': curr_row[group_col] if group_col else 'N/A',
                        'Status Anterior': prev_status,
                        'Status Atual': curr_status
                    })
        
        print(f"📊 Total de estudantes analisados: {len(df_curr)}")
        print(f"✅ Mudanças encontradas: {len(changes)}")
        print()
        
        if len(changes) > 0:
            print("=" * 80)
            print("ESTUDANTES COM STATUS ALTERADO: REPROVADO → APROVADO")
            print("=" * 80)
            print()
            
            for i, change in enumerate(changes, 1):
                print(f"{i}. {change['Nome']}")
                print(f"   Grupo: {change['Grupo']}")
                print(f"   Antes: {change['Status Anterior']}")
                print(f"   Agora: {change['Status Atual']}")
                print()
        else:
            print("✅ Nenhuma mudança de Reprovado → Aprovado encontrada.")
            print()
            print("💡 Nota: Isso pode significar que:")
            print("   - Não houve recuperação aprovada entre ontem e hoje")
            print("   - O backup usado é muito antigo")
            print("   - Os dados ainda não foram atualizados hoje")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Erro ao comparar arquivos: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    compare_grade_status()
