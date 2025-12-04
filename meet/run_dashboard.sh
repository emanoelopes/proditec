#!/bin/bash
# Script para executar o dashboard

cd "$(dirname "$0")"

echo "🚀 Iniciando Dashboard de Monitoramento de Salas Temáticas..."
echo ""

# Verifica se o ambiente virtual existe
if [ -d ".venv" ]; then
    echo "📦 Ativando ambiente virtual..."
    source .venv/bin/activate
fi

# Verifica se as dependências estão instaladas
if ! python -c "import streamlit" 2>/dev/null; then
    echo "⚠️  Dependências não encontradas. Instalando..."
    pip install -r requirements.txt
fi

# Executa o dashboard
echo "🌐 Iniciando Streamlit..."
streamlit run dashboard.py --server.port 8501

