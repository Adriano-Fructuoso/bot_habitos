#!/bin/bash

# Script para iniciar o bot garantindo que apenas uma instância esteja rodando

echo "🤖 Iniciando HabitBot..."

# Função para parar todas as instâncias do bot
stop_bot() {
    echo "🛑 Parando instâncias anteriores..."
    pkill -f "python3 run.py" 2>/dev/null
    sleep 2
    
    # Verifica se ainda há processos rodando
    if pgrep -f "python3 run.py" > /dev/null; then
        echo "⚠️  Ainda há processos rodando, forçando parada..."
        pkill -9 -f "python3 run.py" 2>/dev/null
        sleep 1
    fi
}

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

# Parar instâncias anteriores
stop_bot

# Verificar se parou completamente
if check_bot; then
    echo "❌ Não foi possível parar todas as instâncias"
    exit 1
fi

echo "🚀 Iniciando nova instância do bot..."

# Iniciar o bot em background com nohup
nohup python3 run.py > bot.log 2>&1 &

# Aguardar mais tempo para o bot inicializar
sleep 8

# Verificar se iniciou corretamente
if check_bot; then
    echo "✅ Bot iniciado com sucesso!"
    echo "📋 Logs disponíveis em: bot.log"
    echo "📊 Para monitorar logs: tail -f bot.log"
    echo "🛑 Para parar o bot: ./stop_bot.sh"
    
    # Mostrar últimas linhas do log
    echo ""
    echo "📋 Últimas linhas do log:"
    tail -5 bot.log
else
    echo "❌ Falha ao iniciar o bot"
    echo "📋 Verifique os logs em: bot.log"
    echo ""
    echo "📋 Últimas linhas do log:"
    tail -10 bot.log
    exit 1
fi
