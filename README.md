# Habit Bot - Bot Telegram Gamificado

Um bot Telegram para gamificação de hábitos com persistência PostgreSQL, focado em uso individual mas estruturado para expansão.

## 🎯 Features do MVP

- ✅ Comando `/start` para cadastrar usuário
- ✅ Comando `/habit` para registrar conclusão de hábitos
- ✅ Sistema de XP e gamificação
- ✅ Persistência em PostgreSQL via Railway
- ✅ Feedback imediato via mensagens Telegram
- ✅ Estrutura modular para fácil expansão

## 🛠️ Stack Tecnológica

- **Python 3.10+**
- **python-telegram-bot 20.7** - API do Telegram
- **SQLAlchemy 2.0** - ORM para banco de dados
- **SQLite** - Banco de dados local (desenvolvimento)
- **PostgreSQL** - Banco de dados (Railway - produção)
- **python-dotenv** - Gerenciamento de variáveis de ambiente

## 🚀 Como Rodar Localmente

### 1. Clone e Configure o Ambiente

```bash
# Clone o repositório
git clone https://github.com/Adriano-Fructuoso/bot_habitos.git
cd bot_habitos

# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# No Windows:
venv\Scripts\activate
# No macOS/Linux:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

### 2. Configure as Variáveis de Ambiente

```bash
# Copie o arquivo de exemplo
cp env.example .env

# Edite o arquivo .env com suas credenciais
nano .env
```

**Variáveis obrigatórias:**
- `TELEGRAM_BOT_TOKEN` - Token do seu bot Telegram (obtenha em @BotFather)
- `DATABASE_URL` - String de conexão (SQLite local por padrão)

### 3. Configure o Banco de Dados

```bash
# Configure o banco SQLite local
python setup_local.py
```

### 4. Execute o Bot

```bash
python run.py
```

## 🚀 Deploy no Railway

### 1. Prepare o Projeto

```bash
# Certifique-se de que todos os arquivos estão commitados
git add .
git commit -m "Preparando para deploy"
git push origin main
```

### 2. Configure no Railway

1. Acesse [railway.app](https://railway.app)
2. Conecte seu repositório GitHub
3. Adicione um serviço PostgreSQL
4. Configure as variáveis de ambiente:
   - `TELEGRAM_BOT_TOKEN`
   - `DATABASE_URL` (copie da conexão PostgreSQL do Railway)

### 3. Deploy Automático

O Railway detectará automaticamente que é um projeto Python e fará o deploy.

## 📁 Estrutura do Projeto

```
bot_habitos/
├── bot/
│   ├── main.py          # Inicialização do bot
│   └── handlers.py      # Comandos do bot (/start, /habit)
├── models/
│   └── models.py        # Modelos SQLAlchemy (User, Habit)
├── db/
│   └── session.py       # Configuração da sessão do banco
├── utils/
│   └── gamification.py  # Sistema de XP e badges
├── requirements.txt     # Dependências Python
├── env.example         # Exemplo de variáveis de ambiente
└── README.md           # Este arquivo
```

## 🤖 Comandos do Bot

- `/start` - Cadastra o usuário no sistema
- `/habit` - Registra conclusão de um hábito e concede XP
- `/stats` - Mostra estatísticas do usuário

## 🔧 Comandos Úteis

```bash
# Instalar dependências
pip install -r requirements.txt

# Testar estrutura do projeto
python test_setup.py

# Criar tabelas no banco
python -c "from db.session import engine; from models.models import Base; Base.metadata.create_all(engine)"

# Rodar o bot
python run.py

# Verificar logs
tail -f bot.log
```

## 📝 Variáveis de Ambiente

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `TELEGRAM_BOT_TOKEN` | Token do bot Telegram | `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz` |
| `DATABASE_URL` | String de conexão | `sqlite:///./habit_bot.db` (local) |
| `LOG_LEVEL` | Nível de log (opcional) | `INFO` |

## 🎮 Sistema de Gamificação

- **XP por hábito**: 10 pontos base
- **Streaks**: Bônus por dias consecutivos
- **Badges**: Conquistas por marcos específicos
- **Níveis**: Progressão baseada em XP total

## 🔄 Próximos Passos

- [ ] Sistema de badges
- [ ] Relatórios semanais/mensais
- [ ] Múltiplos hábitos por usuário
- [ ] Lembretes automáticos
- [ ] Dashboard web (opcional)

## 📞 Suporte

Para dúvidas ou problemas:
- Abra uma issue no GitHub
- Entre em contato via Telegram

---

**Desenvolvido com ❤️ para gamificação de hábitos**
