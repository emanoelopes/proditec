#!/usr/bin/env python3
"""
Relatório de Notas Faltantes - Turma B Grupo 01
Gera um relatório em texto mostrando quais notas estão faltando.
"""

import pandas as pd
import sys
from datetime import datetime

def gerar_relatorio():
    csv_path = 'data/grades_consolidados.csv'
    
    # Carregar dados
    df = pd.read_csv(csv_path, header=0)
    
    # Filtrar Turma B - Grupo 01
    # Encontrar coluna com info de turma
    group_col = None
    for col in df.columns:
        if df[col].astype(str).str.contains('Turma B - Grupo 01', regex=False, na=False).any():
            group_col = col
            break
    
    if not group_col:
        print("ERRO: Não foi possível encontrar a coluna com informação de grupo.")
        return
    
    # Filtrar apenas Turma B - Grupo 01
    df_grupo1 = df[df[group_col].astype(str).str.contains('Turma B - Grupo 01', regex=False, na=False)]
    
    # A coluna 1 (index 1) geralmente contém o nome completo
    # Vamos pegar a segunda coluna como nome
    name_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
    
    # Encontrar colunas de Sala
    sala_cols = [c for c in df.columns if 'Sala' in c and c != 'Sala']
    
    
    print("=" * 80)
    print(f"NOTAS FALTANTES - TURMA B GRUPO 01")
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 80)
    print(f"\nTotal de alunos: {len(df_grupo1)}\n")
    
    # Para cada aluno, listar as salas sem nota
    for idx, row in df_grupo1.iterrows():
        nome = row[name_col] if name_col else f"Aluno {idx}"
        
        # Encontrar salas sem nota (apenas vazias, zero é nota válida)
        salas_faltantes = []
        for sala in sala_cols:
            valor = str(row[sala]).strip()
            # Apenas células vazias ou null são consideradas faltantes
            if valor in ['', 'nan', 'NaN'] or pd.isna(row[sala]):
                salas_faltantes.append(sala)
        
        # Só exibir se tiver notas faltantes
        if salas_faltantes:
            print(f"📝 {nome}")
            print(f"   Faltam: {', '.join(salas_faltantes)}")
            print()
    
    print("=" * 80)

if __name__ == "__main__":
    gerar_relatorio()
