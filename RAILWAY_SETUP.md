# 🚂 Configuração do Railway PostgreSQL

## 🎯 Objetivo
Configurar o banco de dados PostgreSQL no Railway para o bot de hábitos.

## 📋 Passos para Configurar Railway

### 1. Criar Conta no Railway
1. Acesse [railway.app](https://railway.app)
2. Faça login com sua conta GitHub
3. Clique em "New Project"

### 2. Conectar Repositório
1. Selecione "Deploy from GitHub repo"
2. Escolha o repositório: `Adriano-Fructuoso/bot_habitos`
3. Clique em "Deploy Now"

### 3. Adicionar PostgreSQL
1. No projeto criado, clique em "New"
2. Selecione "Database" → "PostgreSQL"
3. Aguarde a criação do banco

### 4. Obter DATABASE_URL
1. Clique no serviço PostgreSQL criado
2. Vá para a aba "Connect"
3. Copie a "Postgres Connection URL"
4. Formato: `postgresql://username:password@host:port/database_name`

### 5. Configurar Variáveis de Ambiente
1. No projeto Railway, vá para "Variables"
2. Adicione as variáveis:
   - `TELEGRAM_BOT_TOKEN` = seu_token_aqui
   - `DATABASE_URL` = postgresql://username:password@host:port/database_name

## 🧪 Teste Local

### 1. Configurar .env
```bash
# Copie o arquivo de exemplo
cp env.example .env

# Edite com suas credenciais
nano .env
```

### 2. Testar Conexão
```bash
# Com ambiente virtual ativo
python test_database.py
```

### 3. Verificar Tabelas
```bash
# Inicializar banco
python -c "from db.session import init_db; init_db()"
```

## ✅ Verificação

Após a configuração, você deve ver:
- ✅ Conexão com PostgreSQL estabelecida
- ✅ Tabelas criadas automaticamente
- ✅ Bot funcionando com persistência

## 🔗 Links Úteis

- **Railway**: https://railway.app
- **Repositório**: https://github.com/Adriano-Fructuoso/bot_habitos
- **BotFather**: https://t.me/botfather

## 📊 Estrutura das Tabelas

O banco criará automaticamente:
- `users` - Dados dos usuários
- `habits` - Hábitos dos usuários
- `daily_logs` - Logs de hábitos completados
- `badges` - Conquistas dos usuários

---

**💡 Dica**: O Railway oferece 500 horas gratuitas por mês, suficiente para um bot pessoal! 