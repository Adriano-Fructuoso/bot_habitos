# 🚀 Guia de Deploy - Habit Bot

## 📋 Pré-requisitos

- Docker e Docker Compose instalados
- Token do bot do Telegram
- Acesso à internet

## 🔧 Configuração Inicial

### 1. Configurar variáveis de ambiente

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite com suas credenciais
nano .env
```

**Variáveis obrigatórias:**
```env
TELEGRAM_BOT_TOKEN=seu_token_aqui
APP_ENV=production
APP_VERSION=1.0.0
```

**Variáveis opcionais:**
```env
LOG_LEVEL=INFO
LOG_JSON=true
OPCODES_SITE_URL=https://opcodes.com.br
```

### 2. Construir e iniciar

```bash
# Construir imagem
make build

# Iniciar serviços
make up

# Verificar status
make status
```

## 🐳 Comandos Docker

### Comandos básicos
```bash
make help          # Ver todos os comandos
make build         # Construir imagem
make up            # Iniciar serviços
make down          # Parar serviços
make restart       # Reiniciar bot
make logs          # Ver logs do bot
make logs-db       # Ver logs do banco
```

### Desenvolvimento
```bash
make dev           # Rodar localmente (sem Docker)
make shell         # Abrir shell no container
make test          # Executar testes
make test-docker   # Executar testes no container
```

### Banco de dados
```bash
make migrate       # Executar migrações
make migrate-create MESSAGE="descrição"  # Criar nova migração
make backup        # Fazer backup
make restore FILE=backup.sql  # Restaurar backup
```

### Manutenção
```bash
make clean         # Limpar containers e volumes
./scripts/backup.sh  # Backup manual
```

## 📊 Monitoramento

### Health Check
O bot responde ao comando `/health` com:
- Status do banco de dados
- Latência de conexão
- Versão da migração
- Uptime do sistema
- Versão do Python

### Logs
```bash
# Logs em tempo real
make logs

# Logs do banco
make logs-db

# Logs específicos
docker-compose logs -f habit-bot | grep ERROR
```

## 🔄 Migrações

### Criar nova migração
```bash
# Após alterar os models
make migrate-create MESSAGE="adicionar campo novo"
```

### Executar migrações
```bash
# Aplicar todas as migrações pendentes
make migrate
```

### Verificar status
```bash
# No container
docker-compose exec habit-bot alembic current
docker-compose exec habit-bot alembic history
```

## 💾 Backup e Restore

### Backup automático
```bash
# Backup com timestamp
make backup

# Backup com nome específico
./scripts/backup.sh meu_backup
```

### Restore
```bash
# Restaurar backup
make restore FILE=backup_20241201_143022.sql
```

### Backup manual
```bash
# Backup direto do PostgreSQL
docker-compose exec db pg_dump -U habit_user habit_db > backup.sql

# Restore direto
docker-compose exec -T db psql -U habit_user habit_db < backup.sql
```

## 🛠️ Troubleshooting

### Bot não inicia
```bash
# Verificar logs
make logs

# Verificar configuração
docker-compose exec habit-bot python -c "from config import *; print('Config OK')"

# Verificar banco
docker-compose exec db psql -U habit_user -d habit_db -c "SELECT 1"
```

### Migrações falham
```bash
# Verificar status
docker-compose exec habit-bot alembic current

# Forçar upgrade
docker-compose exec habit-bot alembic upgrade head --sql

# Reset completo (CUIDADO!)
docker-compose down -v
docker-compose up -d db
docker-compose exec habit-bot alembic upgrade head
```

### Problemas de conectividade
```bash
# Verificar se o banco está rodando
docker-compose ps

# Verificar health check
docker-compose exec db pg_isready -U habit_user -d habit_db

# Reiniciar serviços
make restart
```

## 🔒 Segurança

### Variáveis sensíveis
- Nunca commite o arquivo `.env`
- Use secrets management em produção
- Rotacione tokens regularmente

### Backup
- Configure backups automáticos
- Teste restores regularmente
- Mantenha múltiplas cópias

### Logs
- Configure rotação de logs
- Monitore logs de erro
- Use LOG_JSON=true em produção

## 📈 Produção

### Recomendações
- Use volumes persistentes
- Configure monitoring
- Implemente alertas
- Use reverse proxy se necessário

### Escalabilidade
- Configure connection pooling
- Monitore uso de recursos
- Implemente rate limiting
- Use cache quando apropriado

## 🆘 Suporte

Para problemas:
1. Verifique os logs: `make logs`
2. Teste conectividade: `/health`
3. Verifique configuração: `.env`
4. Consulte este guia
5. Abra uma issue no repositório
