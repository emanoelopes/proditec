#!/usr/bin/env python3
"""
Cria tabela comparativa:
- Nome do Cursista
- Status Final (Planilhas Google Sheets)
- Situação Parcial (Avamec)
"""

import pandas as pd
import json
import os

def create_comparison_table():
    base_dir = os.getcwd()
    
    # Arquivos
    grades_file = os.path.join(base_dir, 'data/grades_consolidados.csv')
    
    # Tentar arquivo completo primeiro, depois o parcial
    avamec_file = os.path.join(base_dir, 'data/avamec_completo.json')
    if not os.path.exists(avamec_file):
        avamec_file = os.path.join(base_dir, 'data/avamec_status_situacao.json')
    
    
    print("=" * 100)
    print("TABELA COMPARATIVA: STATUS FINAL (PLANILHAS) vs SITUAÇÃO PARCIAL (AVAMEC)")
    print("=" * 100)
    print()
    
    # Carregar dados das planilhas
    if not os.path.exists(grades_file):
        print(f"❌ Arquivo não encontrado: {grades_file}")
        return
    
    df_grades = pd.read_csv(grades_file, header=0)
    
    # Dados já vêm filtrados (sem cancelados/desistentes) da consolidação
    
    # Carregar dados do Avamec
    avamec_data = {}
    if os.path.exists(avamec_file):
        with open(avamec_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for aluno in data.get('alunos', []):
                nome_key = aluno['nome'].strip().upper()
                avamec_data[nome_key] = aluno['situacao_parcial']
    else:
        print(f"⚠️ Dados do Avamec não encontrados: {avamec_file}")
        print("Execute: python3 scripts/scrape_avamec_status.py")
        print()
    
    # Colunas
    name_col = df_grades.columns[1]  # Segunda coluna = nome
    status_col = 'Extra_Col_61'  # Coluna BJ = Status Final
    
    # Encontrar coluna de grupo
    group_col = None
    for col in df_grades.columns:
        if df_grades[col].astype(str).str.contains('Turma [AB]', regex=True, na=False).any():
            group_col = col
            break
    
    # Criar tabela comparativa
    comparacao = []
    
    for _, row in df_grades.iterrows():
        nome = str(row[name_col]).strip()
        nome_upper = nome.upper()
        status_final = str(row[status_col]).strip() if status_col in df_grades.columns else 'N/A'
        grupo = str(row[group_col]) if group_col else 'N/A'
        
        # Buscar no Avamec
        situacao_avamec = avamec_data.get(nome_upper, '—')
        
        # Determinar status da nota
        if situacao_avamec == '—':
            status_nota = '⏳ Aguardando lançamento'
        else:
            try:
                nota = float(situacao_avamec)
                if nota == 0:
                    status_nota = '⚠️ Zero lançado'
                else:
                    status_nota = '✅ Lançada'
            except (ValueError, TypeError):
                status_nota = '❓ Verificar'
        
        comparacao.append({
            'Nome': nome,
            'Grupo': grupo,
            'Status Final (Planilhas)': status_final,
            'Situação Parcial (Avamec)': situacao_avamec,
            'Status da Nota': status_nota
        })
    
    # Criar DataFrame
    df_comp = pd.DataFrame(comparacao)
    
    # Ordenar
    df_comp = df_comp.sort_values(['Grupo', 'Nome'])
    
    
    # Estatísticas
    total = len(df_comp)
    com_avamec = len([x for x in df_comp['Situação Parcial (Avamec)'] if x != '—'])
    aguardando = len([x for x in df_comp['Status da Nota'] if 'Aguardando' in x])
    
    print(f"📊 Total de cursistas: {total}")
    print(f"📊 Com dados do Avamec: {com_avamec}")
    print(f"📊 Sem dados do Avamec: {total - com_avamec}")
    print(f"⏳ Aguardando lançamento: {aguardando}")
    print()
    
    # Mostrar tabela
    print("=" * 115)
    print(f"{'Nome':<40} {'Grupo':<22} {'Status Final':<15} {'Situação':<10} {'Status da Nota':<25}")
    print("=" * 115)
    
    for _, row in df_comp.iterrows():
        nome = row['Nome'][:38]
        grupo = str(row['Grupo'])[:20]
        status = row['Status Final (Planilhas)'][:13]
        avamec = str(row['Situação Parcial (Avamec)'])[:8]
        status_nota = row['Status da Nota'][:23]
        
        print(f"{nome:<40} {grupo:<22} {status:<15} {avamec:<10} {status_nota:<25}")
    
    print("=" * 115)
    print()
    
    # Salvar em CSV para análise
    output_file = os.path.join(base_dir, 'data/comparacao_status.csv')
    df_comp.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"✅ Tabela salva em: {output_file}")
    print()
    
    # Análise de divergências (se houver dados Avamec)
    if com_avamec > 0:
        print("=" * 100)
        print("ANÁLISE DE DIVERGÊNCIAS")
        print("=" * 100)
        
        divergencias = []
        for _, row in df_comp.iterrows():
            status_planilha = row['Status Final (Planilhas)'].upper()
            situacao_avamec = str(row['Situação Parcial (Avamec)'])
            
            if situacao_avamec != '—':
                try:
                    nota_avamec = float(situacao_avamec)
                    status_avamec = 'APROVADO' if nota_avamec >= 7 else 'REPROVADO'
                    
                    if status_planilha != status_avamec:
                        divergencias.append({
                            'nome': row['Nome'],
                            'grupo': row['Grupo'],
                            'planilha': status_planilha,
                            'avamec': f"{situacao_avamec} ({status_avamec})"
                        })
                except (ValueError, TypeError):
                    pass
        
        if divergencias:
            print(f"\n⚠️ {len(divergencias)} divergência(s) encontrada(s):\n")
            for i, d in enumerate(divergencias, 1):
                print(f"{i}. {d['nome']}")
                print(f"   Grupo: {d['grupo']}")
                print(f"   Planilha: {d['planilha']}")
                print(f"   Avamec: {d['avamec']}")
                print()
        else:
            print("\n✅ Nenhuma divergência encontrada!")
            print("   Status Final das planilhas está consistente com Situação Parcial do Avamec.")
            print()
        
        print("=" * 100)

if __name__ == "__main__":
    create_comparison_table()
