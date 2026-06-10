# 🗄️ Configuração PostgreSQL - Habit Bot

## ✅ Status: Configurado com Sucesso

O bot foi configurado para usar PostgreSQL em produção com todas as funcionalidades implementadas.

## 🔧 Configuração Realizada

### 1. **PostgreSQL Instalado e Configurado**
```bash
# Instalação via Homebrew
brew install postgresql@15
brew services start postgresql@15

# Configuração do PATH
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 2. **Usuário e Banco Criados**
```bash
# Usuário (já existia)
createuser -s habit_user

# Banco de dados (já existia)
createdb habit_db -O habit_user

# Senha configurada
psql -U habit_user -d habit_db -c "ALTER USER habit_user WITH PASSWORD 'habit_pass';"
```

### 3. **Dependências Instaladas**
```bash
# psycopg2 para conexão PostgreSQL
pip install psycopg2-binary
```

### 4. **Variáveis de Ambiente (.env)**
```env
# Configurações de Produção
APP_ENV=production
LOG_LEVEL=INFO
DATABASE_URL=postgresql+psycopg2://habit_user:habit_pass@localhost:5432/habit_db
TELEGRAM_BOT_TOKEN=SEU_TOKEN_AQUI
```

### 5. **Migrations Executadas**
```bash
# Alembic configurado para PostgreSQL
alembic upgrade head
```

## 📊 Estrutura do Banco

### Tabelas Criadas:
- ✅ `users` - Dados dos usuários
- ✅ `habits` - Hábitos dos usuários
- ✅ `daily_logs` - Logs de hábitos completados
- ✅ `badges` - Conquistas dos usuários
- ✅ `streaks` - Sequências de hábitos
- ✅ `daily_ratings` - Avaliações diárias
- ✅ `achievements` - Conquistas especiais
- ✅ `alembic_version` - Controle de migrations

### Constraints Implementadas:
- ✅ `telegram_user_id` - Índice único
- ✅ `daily_logs` - Unique(user_id, habit_id, date)
- ✅ `streaks` - Unique(user_id, habit_id)
- ✅ `daily_ratings` - Unique(user_id, date)

## 🧪 Testes Realizados

- ✅ `python test_setup.py` - Todos os imports funcionando
- ✅ `python test_database.py` - Conexão PostgreSQL estabelecida
- ✅ `python test_bot.py` - Bot configurado corretamente
- ✅ `alembic upgrade head` - Migrations executadas
- ✅ Verificação das tabelas no PostgreSQL

## 🚀 Como Executar

### Ambiente de Desenvolvimento (SQLite)
```bash
# Usar .env.example ou configurar SQLite
DATABASE_URL=sqlite:///./habit_bot.db
python run.py
```

### Ambiente de Produção (PostgreSQL)
```bash
# Usar .env com configurações PostgreSQL
APP_ENV=production
DATABASE_URL=postgresql+psycopg2://habit_user:habit_pass@localhost:5432/habit_db
python run.py
```

## 📱 Comandos do Bot

- `/start` - Cadastra usuário e cria hábitos padrão
- `/habit` - Lista hábitos para completar
- `/stats` - Mostra estatísticas do usuário
- `/dashboard` - Dashboard completo
- `/rating` - Avaliação diária
- `/weekly` - Resumo semanal
- `/habits` - Lista todos os hábitos

## 🔄 Próximos Passos

1. **Testar o bot**: `python run.py`
2. **Testar comandos no Telegram**
3. **Configurar Railway para deploy**
4. **Configurar webhook para produção**

## 💡 Benefícios do PostgreSQL

- **Confiabilidade**: ACID compliance
- **Performance**: Otimizado para consultas complexas
- **Escalabilidade**: Suporte a múltiplos usuários
- **Backup**: Sistema robusto de backup
- **Concorrência**: Múltiplas conexões simultâneas

---

**Status**: ✅ **CONCLUÍDO** - PostgreSQL configurado e funcionando!
