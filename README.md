# 🤖 HabitBot - Bot de Hábitos para Telegram

Bot inteligente para gerenciar hábitos com gamificação, lembretes e acompanhamento de progresso.

## 🚀 Como Rodar

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar ambiente
```bash
cp env.example .env
# Editar .env com TELEGRAM_BOT_TOKEN
```

### 3. Executar migrações
```bash
python -m alembic upgrade head
```

### 4. Rodar bot
```bash
python run.py
```

## ✅ Como Validar

### Qualidade do código
```bash
# Lint
ruff check .

# Formatação
black --check .

# Tipagem
mypy .
```

### Testes
```bash
# Todos os testes
pytest -q

# Testes específicos
pytest test_crud_habits.py -v
pytest test_repository.py -v
```

### Funcionalidade
```bash
# Rodar bot
python run.py

# Testar comandos no Telegram:
# /start - Iniciar
# /add_habit - Criar hábito
# /habit - Ver hábitos
# /set_reminder - Configurar lembrete
# /help - Ajuda
```

## 📋 Comandos Disponíveis

### Hábitos
- `/start` - Iniciar bot e criar hábitos padrão
- `/habit` - Ver e completar hábitos do dia
- `/habits` - Listar todos os seus hábitos
- `/add_habit` - Criar novo hábito customizado
- `/edit_habit` - Editar hábitos existentes
- `/delete_habit` - Deletar hábitos

### Lembretes
- `/set_reminder` - Configurar lembretes para hábitos

### Progresso
- `/stats` - Ver suas estatísticas
- `/dashboard` - Dashboard completo
- `/rating` - Avaliar seu dia
- `/weekly` - Resumo semanal

### Sistema
- `/health` - Status do bot
- `/help` - Esta mensagem
- `/backup` - Backup dos dados

## 🏗️ Arquitetura

```
habit-bot/
├── bot/           # Handlers e comandos
├── utils/         # Utilitários e serviços
├── models/        # Modelos de dados
├── db/           # Configuração do banco
├── types.py      # Tipagem e enums
└── config.py     # Configurações
```

## 🔧 Tecnologias

- **Python 3.10+**
- **python-telegram-bot** - API do Telegram
- **SQLAlchemy** - ORM
- **APScheduler** - Agendamento
- **Alembic** - Migrações
- **PostgreSQL** - Banco de dados

## 📊 Status

- ✅ CRUD completo de hábitos
- ✅ Sistema de lembretes
- ✅ Gamificação (XP, badges, streaks)
- ✅ Rate limiting e sanitização
- ✅ Logging estruturado
- ✅ Testes unitários
- ✅ Docker e deploy

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
