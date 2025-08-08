#!/bin/bash

# Script de backup universal (SQLite + PostgreSQL)
# Uso: ./scripts/backup.sh [nome_do_backup]

set -euo pipefail

# Configurações
STAMP=$(date +"%Y%m%d-%H%M%S")
OUT_DIR=${BACKUP_DIR:-/app/backups}
BACKUP_NAME="${1:-habit_${STAMP}}"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 Iniciando backup do banco de dados...${NC}"

# Criar diretório de backup
mkdir -p "$OUT_DIR"

# Detectar tipo de banco e fazer backup
if [[ "$DATABASE_URL" == sqlite:* ]]; then
    # Backup SQLite
    DB_PATH="${DATABASE_URL#sqlite:///}"
    
    # Se o caminho for relativo, converter para absoluto
    if [[ ! "$DB_PATH" = /* ]]; then
        DB_PATH="$(pwd)/$DB_PATH"
    fi
    
    BACKUP_FILE="$OUT_DIR/${BACKUP_NAME}.db"
    cp "$DB_PATH" "$BACKUP_FILE"
    
    if [ -f "$BACKUP_FILE" ] && [ -s "$BACKUP_FILE" ]; then
        BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        echo -e "${GREEN}✅ SQLite backup -> $BACKUP_FILE (${BACKUP_SIZE})${NC}"
    else
        echo -e "${RED}❌ Erro no backup SQLite${NC}"
        exit 1
    fi
    
elif [[ "$DATABASE_URL" == postgresql* ]]; then
    # Backup PostgreSQL
    BACKUP_FILE="$OUT_DIR/${BACKUP_NAME}.sql"
    
    # Verificar se pg_dump está disponível
    if ! command -v pg_dump &> /dev/null; then
        echo -e "${RED}❌ pg_dump não encontrado. Instale postgresql-client.${NC}"
        exit 1
    fi
    
    pg_dump "$DATABASE_URL" > "$BACKUP_FILE"
    
    if [ -f "$BACKUP_FILE" ] && [ -s "$BACKUP_FILE" ]; then
        BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        echo -e "${GREEN}✅ Postgres backup -> $BACKUP_FILE (${BACKUP_SIZE})${NC}"
    else
        echo -e "${RED}❌ Erro no backup PostgreSQL${NC}"
        exit 1
    fi
    
else
    echo -e "${RED}❌ Tipo de banco não suportado: $DATABASE_URL${NC}"
    exit 1
fi

# Limpar backups antigos (manter apenas os últimos 7 dias)
echo -e "${YELLOW}🧹 Limpando backups antigos...${NC}"
find "$OUT_DIR" -name "habit_*.db" -mtime +7 -delete 2>/dev/null || true
find "$OUT_DIR" -name "habit_*.sql" -mtime +7 -delete 2>/dev/null || true

# Listar backups recentes
echo -e "${BLUE}📋 Backups recentes:${NC}"
ls -laht "$OUT_DIR"/habit_* 2>/dev/null | head -6 || echo "Nenhum backup encontrado."

echo -e "${GREEN}🎉 Backup concluído com sucesso!${NC}"
