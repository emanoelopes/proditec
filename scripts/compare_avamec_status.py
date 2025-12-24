#!/usr/bin/env python3
"""
Compara status do Avamec entre duas datas
Identifica alunos que mudaram de Reprovado para Aprovado
"""

import json
import os
from datetime import datetime

def compare_avamec_status():
    base_dir = os.getcwd()
    current_file = os.path.join(base_dir, 'data/avamec_status_situacao.json')
    backup_dir = os.path.join(base_dir, 'data/backups')
    
    if not os.path.exists(current_file):
        print("❌ Arquivo atual não encontrado:", current_file)
        print("Execute: python3 scripts/scrape_avamec_status.py")
        return
    
    # Procurar backup mais recente
    if not os.path.exists(backup_dir):
        print("⚠️ Diretório de backups não existe.")
        print("📝 Crie um backup primeiro:")
        print(f"   mkdir -p {backup_dir}")
        print(f"   cp {current_file} {backup_dir}/avamec_status_$(date +%Y%m%d).json")
        return
    
    backups = sorted([f for f in os.listdir(backup_dir) if f.startswith('avamec_status_') and f.endswith('.json')])
    
    if len(backups) == 0:
        print("⚠️ Nenhum backup encontrado.")
        print("📝 Crie um backup antes de executar novamente:")
        print(f"   cp {current_file} {backup_dir}/avamec_status_$(date +%Y%m%d).json")
        return
    
    previous_file = os.path.join(backup_dir, backups[-1])
    
    print("=" * 80)
    print("COMPARAÇÃO DE STATUS DO AVAMEC")
    print("=" * 80)
    print(f"📅 Arquivo anterior: {backups[-1]}")
    print(f"📅 Arquivo atual: avamec_status_situacao.json")
    print()
    
    try:
        # Carregar dados
        with open(previous_file, 'r', encoding='utf-8') as f:
            data_prev = json.load(f)
        
        with open(current_file, 'r', encoding='utf-8') as f:
            data_curr = json.load(f)
        
        alunos_prev = {}
        alunos_curr = {}
        
        for a in data_prev.get('alunos', []):
            nome = a['nome'].strip().upper()
            try:
                nota = float(a['situacao_parcial'])
                status = "APROVADO" if nota >= 7 else "REPROVADO"
                alunos_prev[nome] = {'nota': nota, 'status': status}
            except (ValueError, TypeError):
                alunos_prev[nome] = {'nota': 0, 'status': 'INDEFINIDO'}
        
        for a in data_curr.get('alunos', []):
            nome = a['nome'].strip().upper()
            try:
                nota = float(a['situacao_parcial'])
                status = "APROVADO" if nota >= 7 else "REPROVADO"
                alunos_curr[nome] = {'nota': nota, 'status': status}
            except (ValueError, TypeError):
                alunos_curr[nome] = {'nota': 0, 'status': 'INDEFINIDO'}
        
        # Encontrar mudanças
        mudancas_aprovado = []
        mudancas_reprovado = []
        melhoria_nota = []
        novos_alunos = []
        
        for nome, dados_atual in alunos_curr.items():
            if nome in alunos_prev:
                dados_anterior = alunos_prev[nome]
                
                # Reprovado → Aprovado
                if dados_anterior['status'] == 'REPROVADO' and dados_atual['status'] == 'APROVADO':
                    mudancas_aprovado.append({
                        'nome': nome,
                        'nota_anterior': dados_anterior['nota'],
                        'nota_atual': dados_atual['nota'],
                        'diferenca': dados_atual['nota'] - dados_anterior['nota']
                    })
                # Aprovado → Reprovado
                elif dados_anterior['status'] == 'APROVADO' and dados_atual['status'] == 'REPROVADO':
                    mudancas_reprovado.append({
                        'nome': nome,
                        'nota_anterior': dados_anterior['nota'],
                        'nota_atual': dados_atual['nota'],
                        'diferenca': dados_atual['nota'] - dados_anterior['nota']
                    })
                # Melhoria de nota (ainda reprovado ou já aprovado)
                elif dados_atual['nota'] > dados_anterior['nota'] + 0.5:
                    melhoria_nota.append({
                        'nome': nome,
                        'nota_anterior': dados_anterior['nota'],
                        'nota_atual': dados_atual['nota'],
                        'diferenca': dados_atual['nota'] - dados_anterior['nota'],
                        'status': dados_atual['status']
                    })
            else:
                novos_alunos.append({
                    'nome': nome, 
                    'nota': dados_atual['nota'],
                    'status': dados_atual['status']
                })
        
        
        # Relatório
        print(f"📊 Total de alunos anteriormente: {len(alunos_prev)}")
        print(f"📊 Total de alunos atualmente: {len(alunos_curr)}")
        print()
        
        if mudancas_aprovado:
            print("=" * 80)
            print(f"✅ APROVAÇÕES - REPROVADO → APROVADO ({len(mudancas_aprovado)} aluno(s))")
            print("=" * 80)
            for i, m in enumerate(mudancas_aprovado, 1):
                print(f"\n{i}. {m['nome'].title()}")
                print(f"   Nota anterior: {m['nota_anterior']:.1f} (Reprovado)")
                print(f"   Nota atual: {m['nota_atual']:.1f} (Aprovado)")
                print(f"   Melhoria: +{m['diferenca']:.1f} pontos")
        else:
            print("ℹ️  Nenhuma aprovação nova (nota < 7 → nota >= 7) desde o último backup.")
        
        print()
        
        if mudancas_reprovado:
            print("=" * 80)
            print(f"⚠️ REPROVAÇÕES - APROVADO → REPROVADO ({len(mudancas_reprovado)} aluno(s))")
            print("=" * 80)
            for i, m in enumerate(mudancas_reprovado, 1):
                print(f"\n{i}. {m['nome'].title()}")
                print(f"   Nota anterior: {m['nota_anterior']:.1f} (Aprovado)")
                print(f"   Nota atual: {m['nota_atual']:.1f} (Reprovado)")
                print(f"   Queda: {m['diferenca']:.1f} pontos")
            print()
        
        if melhoria_nota:
            print("=" * 80)
            print(f"📈 MELHORIA DE NOTAS ({len(melhoria_nota)} aluno(s))")
            print("=" * 80)
            for i, m in enumerate(melhoria_nota, 1):
                print(f"\n{i}. {m['nome'].title()}")
                print(f"   Nota anterior: {m['nota_anterior']:.1f}")
                print(f"   Nota atual: {m['nota_atual']:.1f}")
                print(f"   Melhoria: +{m['diferenca']:.1f} pontos ({m['status']})")
            print()
        
        if novos_alunos:
            print("=" * 80)
            print(f"🆕 NOVOS ALUNOS ({len(novos_alunos)})")
            print("=" * 80)
            for i, a in enumerate(novos_alunos, 1):
                print(f"{i}. {a['nome'].title()} - Nota: {a['nota']:.1f} ({a['status']})")
            print()
        
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    compare_avamec_status()
