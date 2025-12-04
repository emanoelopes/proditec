#!/usr/bin/env python3
"""
Script de teste para verificar se a aplicação funciona corretamente.
"""

import sys
import os
import pandas as pd
from datetime import datetime

def test_imports():
    """
    Testa se todas as dependências estão disponíveis.
    """
    print("🔍 Testando imports...")
    
    try:
        import pandas as pd
        print("✅ pandas importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar pandas: {e}")
        return False
    
    try:
        import streamlit as st
        print("✅ streamlit importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar streamlit: {e}")
        return False
    
    try:
        import plotly.express as px
        import plotly.graph_objects as go
        print("✅ plotly importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar plotly: {e}")
        return False
    
    return True

def test_data_processing():
    """
    Testa o processamento de dados com exemplos.
    """
    print("\n🔍 Testando processamento de dados...")
    
    try:
        # Teste com dados de exemplo
        participantes_data = {
            'nome': ['João Silva', 'Maria Santos', 'Pedro Oliveira'],
            'email': ['joao.silva@empresa.com', 'maria.santos@universidade.edu', 'pedro.oliveira@empresa.com']
        }
        
        convidados_data = {
            'email': ['joao.silva@empresa.com', 'maria.santos@universidade.edu', 'antonio.silva@empresa.com']
        }
        
        # Criar DataFrames
        participantes_df = pd.DataFrame(participantes_data)
        convidados_df = pd.DataFrame(convidados_data)
        
        print(f"✅ DataFrames criados:")
        print(f"   - Participantes: {len(participantes_df)} registros")
        print(f"   - Convidados: {len(convidados_df)} registros")
        
        # Teste de comparação
        emails_participantes = set(participantes_df['email'])
        emails_convidados = set(convidados_df['email'])
        
        emails_nao_convidados = emails_participantes - emails_convidados
        
        print(f"✅ Comparação realizada:")
        print(f"   - Emails não convidados: {len(emails_nao_convidados)}")
        print(f"   - Lista: {list(emails_nao_convidados)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no processamento de dados: {e}")
        return False

def test_file_operations():
    """
    Testa operações com arquivos.
    """
    print("\n🔍 Testando operações com arquivos...")
    
    try:
        # Verificar se os arquivos de exemplo existem
        arquivos_exemplo = [
            'exemplo_participantes.csv',
            'exemplo_convidados.csv',
            'exemplo_grupos_tematicos.csv',
            'exemplo_ata_google_meet.txt'
        ]
        
        for arquivo in arquivos_exemplo:
            if os.path.exists(arquivo):
                print(f"✅ {arquivo} encontrado")
            else:
                print(f"❌ {arquivo} não encontrado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nas operações de arquivo: {e}")
        return False

def main():
    """
    Função principal de teste.
    """
    print("🚀 Iniciando testes da aplicação Comparador de Emails")
    print("=" * 60)
    
    # Teste 1: Imports
    if not test_imports():
        print("\n❌ Teste de imports falhou. Instale as dependências:")
        print("   pip install -r requirements.txt")
        return False
    
    # Teste 2: Processamento de dados
    if not test_data_processing():
        print("\n❌ Teste de processamento de dados falhou.")
        return False
    
    # Teste 3: Operações com arquivos
    if not test_file_operations():
        print("\n❌ Teste de operações com arquivos falhou.")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Todos os testes passaram com sucesso!")
    print("\n📋 Para executar a aplicação:")
    print("   python run_app.py")
    print("   ou")
    print("   streamlit run compara_emails.py")
    print("\n🌐 Acesse: http://localhost:8501")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


