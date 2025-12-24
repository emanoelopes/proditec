#!/usr/bin/env python3
"""
Compara alterações de status entre ontem e hoje
Filtra por Turma B
"""

import pandas as pd
import sys

def compare_turma_b_changes():
    # Arquivos
    previous_file = 'data/backups/grades_yesterday_from_git.csv'
    current_file = 'data/grades_consolidados.csv'
    
    try:
        print("=" * 80)
        print("ALTERAÇÕES DE STATUS - TURMA B")
        print("=" * 80)
        print()
        
        # Carregar dados
        df_prev = pd.read_csv(previous_file, header=0)
        df_curr = pd.read_csv(current_file, header=0)
        
        # Encontrar coluna de grupo
        group_col = None
        for col in df_curr.columns:
            if df_curr[col].astype(str).str.contains('Turma [AB]', regex=True, na=False).any():
                group_col = col
                break
        
        if not group_col:
            print("❌ Coluna de grupo não encontrada")
            return
        
        # Filtrar apenas Turma B
        df_prev_b = df_prev[df_prev[group_col].astype(str).str.contains('Turma B', na=False)].copy()
        df_curr_b = df_curr[df_curr[group_col].astype(str).str.contains('Turma B', na=False)].copy()
        
        # Coluna de status (Extra_Col_61)
        status_col = 'Extra_Col_61'
        name_col = df_curr.columns[1]  # Segunda coluna = nome
        
        if status_col not in df_curr.columns:
            print(f"❌ Coluna de status '{status_col}' não encontrada")
            return
        
        print(f"📊 Turma B - Ontem: {len(df_prev_b)} alunos")
        print(f"📊 Turma B - Hoje: {len(df_curr_b)} alunos")
        print()
        
        # Criar dicionários para comparação
        prev_status = {}
        curr_status = {}
        
        for _, row in df_prev_b.iterrows():
            nome = str(row[name_col]).strip().upper()
            grupo = str(row[group_col])
            status = str(row[status_col]).strip().upper()
            prev_status[nome] = {'grupo': grupo, 'status': status}
        
        for _, row in df_curr_b.iterrows():
            nome = str(row[name_col]).strip().upper()
            grupo = str(row[group_col])
            status = str(row[status_col]).strip().upper()
            curr_status[nome] = {'grupo': grupo, 'status': status}
        
        # Encontrar mudanças
        aprovacoes = []
        reprovacoes = []
        novos = []
        
        for nome, dados_atual in curr_status.items():
            if nome in prev_status:
                status_ant = prev_status[nome]['status']
                status_now = dados_atual['status']
                
                if status_ant == 'REPROVADO' and status_now == 'APROVADO':
                    aprovacoes.append({
                        'nome': nome,
                        'grupo': dados_atual['grupo']
                    })
                elif status_ant == 'APROVADO' and status_now == 'REPROVADO':
                    reprovacoes.append({
                        'nome': nome,
                        'grupo': dados_atual['grupo']
                    })
            else:
                novos.append({
                    'nome': nome,
                    'grupo': dados_atual['grupo'],
                    'status': dados_atual['status']
                })
        
        # Resultados
        if aprovacoes:
            print("=" * 80)
            print(f"✅ APROVAÇÕES ({len(aprovacoes)} aluno(s))")
            print("=" * 80)
            for i, a in enumerate(aprovacoes, 1):
                print(f"{i}. {a['nome'].title()}")
                print(f"   Grupo: {a['grupo']}")
                print()
        else:
            print("ℹ️  Nenhuma nova aprovação na Turma B")
            print()
        
        if reprovacoes:
            print("=" * 80)
            print(f"⚠️ REPROVAÇÕES ({len(reprovacoes)} aluno(s))")
            print("=" * 80)
            for i, r in enumerate(reprovacoes, 1):
                print(f"{i}. {r['nome'].title()}")
                print(f"   Grupo: {r['grupo']}")
                print()
        
        if novos:
            print("=" * 80)
            print(f"🆕 NOVOS ALUNOS ({len(novos)})")
            print("=" * 80)
            for i, n in enumerate(novos, 1):
                print(f"{i}. {n['nome'].title()} - {n['grupo']} - {n['status']}")
            print()
        
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    compare_turma_b_changes()
