#!/usr/bin/env python3
"""
Script para executar a aplicação Streamlit do Comparador de Emails.
"""

import subprocess
import sys
import os

def main():
    """
    Executa a aplicação Streamlit.
    """
    # Diretório do script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Caminho para o arquivo principal
    app_file = os.path.join(script_dir, "compara_emails.py")
    
    # Verificar se o arquivo existe
    if not os.path.exists(app_file):
        print(f"❌ Arquivo não encontrado: {app_file}")
        sys.exit(1)
    
    # Comando para executar o Streamlit
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        app_file,
        "--server.port", "8501",
        "--server.address", "localhost",
        "--browser.gatherUsageStats", "false"
    ]
    
    print("🚀 Iniciando aplicação Streamlit...")
    print(f"📁 Diretório: {script_dir}")
    print(f"📄 Arquivo: {app_file}")
    print("🌐 Acesse: http://localhost:8501")
    print("⏹️  Para parar: Ctrl+C")
    print("-" * 50)
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Aplicação encerrada pelo usuário")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar aplicação: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


