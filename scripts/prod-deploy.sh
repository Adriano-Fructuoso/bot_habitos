#!/bin/bash

# Script de deploy em produção
# Uso: ./scripts/prod-deploy.sh [tag]

set -e

# Configurações
TAG=${1:-latest}
COMPOSE_FILE="docker-compose.yml"
BACKUP_BEFORE_DEPLOY=true

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Iniciando deploy em produção...${NC}"
echo -e "${BLUE}📋 Tag: ${TAG}${NC}"

# Verificar se .env existe
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Arquivo .env não encontrado!${NC}"
    echo -e "${YELLOW}📝 Copie .env.example para .env e configure as variáveis.${NC}"
    exit 1
fi

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker não está rodando!${NC}"
    exit 1
fi

# Backup antes do deploy (se habilitado)
if [ "$BACKUP_BEFORE_DEPLOY" = true ]; then
    echo -e "${YELLOW}💾 Fazendo backup antes do deploy...${NC}"
    if docker compose ps | grep -q "db.*Up"; then
        ./scripts/backup.sh "pre_deploy_$(date +%Y%m%d_%H%M%S)"
    else
        echo -e "${YELLOW}⚠️  Banco não está rodando, pulando backup.${NC}"
    fi
fi

# Parar serviços existentes
echo -e "${BLUE}🛑 Parando serviços existentes...${NC}"
docker compose down || true

# Limpar imagens antigas (opcional)
echo -e "${BLUE}🧹 Limpando imagens antigas...${NC}"
docker image prune -f || true

# Construir nova imagem
echo -e "${BLUE}🔨 Construindo nova imagem...${NC}"
docker compose build --no-cache

# Iniciar serviços
echo -e "${BLUE}🚀 Iniciando serviços...${NC}"
docker compose up -d

# Aguardar banco estar pronto
echo -e "${BLUE}⏳ Aguardando banco estar pronto...${NC}"
sleep 10

# Verificar se banco está respondendo
for i in {1..30}; do
    if docker compose exec db pg_isready -U habit_user -d habit_db > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Banco de dados pronto!${NC}"
        break
    fi
    echo -e "${YELLOW}⏳ Aguardando banco... (${i}/30)${NC}"
    sleep 2
done

# Executar migrações
echo -e "${BLUE}🔄 Executando migrações...${NC}"
docker compose run --rm habit-bot alembic upgrade head

# Verificar se bot está rodando
echo -e "${BLUE}🔍 Verificando se bot está rodando...${NC}"
sleep 5

if docker compose ps | grep -q "habit-bot.*Up"; then
    echo -e "${GREEN}✅ Bot iniciado com sucesso!${NC}"
else
    echo -e "${RED}❌ Bot não conseguiu iniciar!${NC}"
    echo -e "${YELLOW}📋 Verificando logs...${NC}"
    docker compose logs habit-bot --tail=50
    exit 1
fi

# Health check
echo -e "${BLUE}🏥 Executando health check...${NC}"
sleep 10

# Mostrar status final
echo -e "${GREEN}🎉 Deploy concluído com sucesso!${NC}"
echo -e "${BLUE}📊 Status dos serviços:${NC}"
docker compose ps

echo -e "${BLUE}📋 Comandos úteis:${NC}"
echo -e "${BLUE}   make logs          # Ver logs${NC}"
echo -e "${BLUE}   make down          # Parar serviços${NC}"
echo -e "${BLUE}   ./scripts/backup.sh # Fazer backup${NC}"

# Verificar se há erros nos logs
ERROR_COUNT=$(docker compose logs habit-bot --tail=100 | grep -i error | wc -l)
if [ "$ERROR_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Encontrados ${ERROR_COUNT} erros nos logs. Verifique: make logs${NC}"
else
    echo -e "${GREEN}✅ Nenhum erro encontrado nos logs.${NC}"
fi
