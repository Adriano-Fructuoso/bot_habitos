#!/bin/bash

# Script para criar repositório no GitHub e fazer push

echo "🚀 Configurando repositório GitHub para bot_habitos"
echo ""

# Verifica se o repositório já existe
echo "📋 Verificando se o repositório existe..."
if curl -s "https://api.github.com/repos/adrianofructuoso/bot_habitos" > /dev/null 2>&1; then
    echo "✅ Repositório já existe!"
else
    echo "❌ Repositório não encontrado."
    echo ""
    echo "📝 Para criar o repositório, siga estes passos:"
    echo "1. Acesse: https://github.com/new"
    echo "2. Nome do repositório: bot_habitos"
    echo "3. Descrição: Bot Telegram gamificado para hábitos"
    echo "4. Marque como 'Private'"
    echo "5. NÃO inicialize com README (já temos um)"
    echo "6. Clique em 'Create repository'"
    echo ""
    read -p "Pressione Enter quando o repositório estiver criado..."
fi

echo ""
echo "🔄 Fazendo push para o GitHub..."

# Tenta fazer o push
if git push -u origin main; then
    echo ""
    echo "🎉 Sucesso! Repositório criado e código enviado!"
    echo ""
    echo "📋 Próximos passos:"
    echo "1. Acesse: https://github.com/adrianofructuoso/bot_habitos"
    echo "2. Configure as variáveis de ambiente no Railway"
    echo "3. Faça o deploy!"
    echo ""
    echo "🔗 Links úteis:"
    echo "- Repositório: https://github.com/adrianofructuoso/bot_habitos"
    echo "- Railway: https://railway.app"
else
    echo ""
    echo "❌ Erro ao fazer push. Verifique:"
    echo "1. Se o repositório foi criado corretamente"
    echo "2. Se você tem permissão para fazer push"
    echo "3. Se está autenticado no GitHub"
fi 