# 🤖 Como Criar e Testar o Bot no Telegram

## 📱 Passo a Passo Completo

### 1. Criar o Bot no Telegram

#### Acesse o BotFather
1. Abra o Telegram no seu celular
2. Procure por **@BotFather** na busca
3. Clique em "Start" ou envie `/start`

#### Crie um Novo Bot
1. Envie o comando: `/newbot`
2. Digite um nome para o bot (ex: "Habit Bot")
3. Digite um username (deve terminar em 'bot', ex: "meu_habit_bot")
4. O BotFather enviará uma mensagem com o **TOKEN**

#### Exemplo de Conversa:
```
Você: /newbot
BotFather: Alright, a new bot. How are we going to call it? Please choose a name for your bot.

Você: Habit Bot
BotFather: Good. Now let's choose a username for your bot. It must end in `bot`. Like this: TetrisBot or tetris_bot.

Você: meu_habit_bot
BotFather: Done! Congratulations on your new bot. You will find it at t.me/meu_habit_bot. You can now add a description, about section and profile picture for your bot, see /help for a list of commands. By the way, when you've finished creating your cool bot, ping our Bot Support if you want a better username for it. Just make sure the bot is fully operational before you do this.

Use this token to access the HTTP API:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

Keep your token secure and store it safely, it can be used by anyone to control your bot.
```

### 2. Configurar o Token Localmente

#### Copie o Token
- Copie o token que o BotFather enviou
- Exemplo: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

#### Configure o Arquivo .env
```bash
# No terminal, com ambiente virtual ativo
cp env.example .env
nano .env
```

#### Edite o arquivo .env:
```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Database Configuration
DATABASE_URL=sqlite:///./habit_bot.db

# Optional: Logging Level
LOG_LEVEL=INFO
```

### 3. Testar o Bot Localmente

#### Execute o Bot
```bash
# Com ambiente virtual ativo
python run.py
```

Você deve ver algo como:
```
🚀 Iniciando testes da estrutura do Habit Bot
✅ Config importado com sucesso
📁 Usando SQLite local: habit_bot.db
✅ Database session importado com sucesso
✅ Models importados com sucesso
✅ Gamification system importado com sucesso
✅ Bot handlers importados com sucesso
Bot iniciado com sucesso!
Comandos disponíveis: /start, /habit, /stats
```

### 4. Testar no Telegram

#### Encontre seu Bot
1. No Telegram, procure pelo username que você criou
2. Exemplo: `@meu_habit_bot`
3. Clique em "Start" ou envie `/start`

#### Teste os Comandos
1. **`/start`** - Cadastra você no sistema
2. **`/habit`** - Registra um hábito completado
3. **`/stats`** - Mostra suas estatísticas

### 5. Exemplo de Conversa

```
Você: /start
Bot: 🎉 Bem-vindo ao Habit Bot, [Seu Nome]!

✅ Você foi cadastrado com sucesso!
📝 Um hábito padrão foi criado para você.

Use /habit para registrar quando completar um hábito e ganhar XP!

🎮 Sistema de gamificação:
• Cada hábito = 10 XP base
• Streak diário = bônus de XP
• Suba de nível acumulando XP
• Desbloqueie badges especiais!

Você: /habit
Bot: 🎉 Parabéns! Você completou: Hábito Diário

💎 XP ganho: +10
📊 XP total: 10
🏆 Nível: 1
🔥 Streak: 1 dias

💪 Continue assim! Use /habit amanhã para manter seu streak!

Você: /stats
Bot: 📊 Suas estatísticas:

🏆 Nível: 1
💎 XP: 10
🔥 Streak atual: 1 dias
✅ Hábitos completados: 1
🏅 Badges: 0

📈 Próximo nível: 40 XP restantes
```

## 🔧 Solução de Problemas

### Bot não responde
1. Verifique se o bot está rodando no terminal
2. Confirme se o token está correto no .env
3. Verifique se não há erros no terminal

### Erro de conexão
1. Verifique sua conexão com a internet
2. Confirme se o bot está ativo no BotFather

### Erro de banco de dados
1. Execute: `python setup_local.py`
2. Verifique se o arquivo `habit_bot.db` foi criado

## 📱 Dicas para Uso no Celular

1. **Adicione o bot aos favoritos** para acesso rápido
2. **Use comandos de texto** em vez de botões
3. **Teste diariamente** para manter o streak
4. **Verifique estatísticas** regularmente

## 🔗 Links Úteis

- **BotFather**: https://t.me/botfather
- **Seu Bot**: t.me/[seu_username_bot]
- **Documentação**: https://core.telegram.org/bots

---

**💡 Dica**: Mantenha o terminal aberto enquanto testa o bot. Para parar o bot, pressione `Ctrl+C`. 