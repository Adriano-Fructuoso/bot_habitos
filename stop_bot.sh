#!/bin/bash

# Script para parar o bot

echo "🛑 Parando HabitBot..."

# Função para verificar se o bot está rodando
check_bot() {
    if pgrep -f "python3 run.py" > /dev/null; then
        echo "✅ Bot está rodando (PID: $(pgrep -f 'python3 run.py'))"
        return 0
    else
        echo "❌ Bot não está rodando"
        return 1
    fi
}

# Verificar se o bot está rodando
if ! check_bot; then
    echo "ℹ️  Bot já não está rodando"
    exit 0
fi

# Parar o bot
echo "🔄 Parando processos..."
pkill -f "python3 run.py" 2>/dev/null
sleep 2

# Verificar se ainda há processos rodando
if pgrep -f "python3 run.py" > /dev/null; then
    echo "⚠️  Ainda há processos rodando, forçando parada..."
    pkill -9 -f "python3 run.py" 2>/dev/null
    sleep 1
fi

# Verificar se parou
if check_bot; then
    echo "❌ Não foi possível parar o bot"
    exit 1
else
    echo "✅ Bot parado com sucesso!"
fi
