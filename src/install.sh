#!/bin/bash

# Script de instalação para o Comparador de Emails
# Google Meet - Streamlit App

echo "🚀 Instalando Comparador de Emails - Google Meet"
echo "================================================"

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.8+ primeiro."
    exit 1
fi

echo "✅ Python 3 encontrado: $(python3 --version)"

# Verificar se pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado. Instale pip primeiro."
    exit 1
fi

echo "✅ pip3 encontrado: $(pip3 --version)"

# Criar ambiente virtual (opcional)
read -p "🤔 Deseja criar um ambiente virtual? (y/n): " create_venv
if [[ $create_venv == "y" || $create_venv == "Y" ]]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Ambiente virtual criado e ativado"
fi

# Instalar dependências
echo "📦 Instalando dependências..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependências instaladas com sucesso"
else
    echo "❌ Erro ao instalar dependências"
    exit 1
fi

# Executar testes
echo "🧪 Executando testes..."
python3 test_app.py

if [ $? -eq 0 ]; then
    echo "✅ Testes passaram com sucesso"
else
    echo "❌ Alguns testes falharam"
    exit 1
fi

echo ""
echo "🎉 Instalação concluída com sucesso!"
echo ""
echo "📋 Para executar a aplicação:"
echo "   python3 run_app.py"
echo "   ou"
echo "   streamlit run compara_emails.py"
echo ""
echo "🌐 Acesse: http://localhost:8501"
echo ""
echo "📁 Arquivos de exemplo disponíveis:"
echo "   - exemplo_participantes.csv"
echo "   - exemplo_convidados.csv"
echo "   - exemplo_grupos_tematicos.csv"
echo "   - exemplo_ata_google_meet.txt"
echo ""
echo "📖 Para mais informações, consulte o README.md"


