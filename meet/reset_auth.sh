#!/bin/bash
# Script para resetar autenticação Google (deleta token.json)

cd "$(dirname "$0")"

if [ -f "token.json" ]; then
    echo "🗑️  Deletando token.json..."
    rm token.json
    echo "✅ Token deletado com sucesso!"
    echo ""
    echo "Agora execute o dashboard novamente:"
    echo "  streamlit run dashboard.py"
    echo ""
    echo "Você será solicitado a autenticar novamente com todos os scopes necessários."
else
    echo "ℹ️  token.json não encontrado. Nada a fazer."
fi

