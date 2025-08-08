#!/bin/bash

# Script de desenvolvimento - Inicia ambiente local
# Uso: ./scripts/dev-up.sh

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Iniciando ambiente de desenvolvimento...${NC}"

# Verificar se .env existe
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Arquivo .env não encontrado. Copiando .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}📝 Configure o arquivo .env com suas credenciais antes de continuar.${NC}"
    echo -e "${YELLOW}   TELEGRAM_BOT_TOKEN=seu_token_aqui${NC}"
    exit 1
fi

# Verificar se virtualenv existe
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Criando virtualenv...${NC}"
    python3 -m venv venv
fi

# Ativar virtualenv
echo -e "${BLUE}🔧 Ativando virtualenv...${NC}"
source venv/bin/activate

# Instalar dependências
echo -e "${BLUE}📦 Instalando dependências...${NC}"
pip install -r requirements.txt

# Verificar se banco existe
if [ ! -f "data/habit.db" ]; then
    echo -e "${YELLOW}🗄️  Inicializando banco de dados...${NC}"
    mkdir -p data
    python -c "from db.session import init_db; init_db()"
fi

# Executar migrações
echo -e "${BLUE}🔄 Executando migrações...${NC}"
alembic upgrade head

# Verificar configuração
echo -e "${BLUE}🔍 Verificando configuração...${NC}"
python test_setup.py

echo -e "${GREEN}✅ Ambiente de desenvolvimento pronto!${NC}"
echo -e "${BLUE}🚀 Para iniciar o bot: python run.py${NC}"
echo -e "${BLUE}📋 Para ver logs: tail -f logs/habit-bot.log${NC}"
echo -e "${BLUE}🧪 Para executar testes: make test${NC}"
