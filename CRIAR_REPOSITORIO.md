# 📋 Como Criar o Repositório no GitHub

## 🎯 Objetivo
Criar um repositório privado no GitHub chamado `bot_habitos` e fazer o push do código.

## 📝 Passos para Criar o Repositório

### 1. Acesse o GitHub
- Vá para: https://github.com/new
- Ou clique em "New repository" no seu perfil

### 2. Configure o Repositório
- **Repository name**: `bot_habitos`
- **Description**: `Bot Telegram gamificado para hábitos`
- **Visibility**: ✅ **Private** (importante!)
- **NÃO** marque "Add a README file" (já temos um)
- **NÃO** marque "Add .gitignore" (já temos um)
- **NÃO** marque "Choose a license" (opcional)

### 3. Crie o Repositório
- Clique em "Create repository"

## 🚀 Após Criar o Repositório

### Opção 1: Usar o Script Automático
```bash
./setup_github.sh
```

### Opção 2: Comandos Manuais
```bash
# Verificar se o remote está configurado
git remote -v

# Fazer push para o GitHub
git push -u origin main
```

## ✅ Verificação

Após o push, você deve ver:
- ✅ Repositório criado em: https://github.com/adrianofructuoso/bot_habitos
- ✅ Todos os arquivos do projeto no GitHub
- ✅ Commit inicial com a mensagem "🎉 Initial commit: Bot Telegram gamificado para hábitos"

## 🔗 Links Úteis

- **Repositório**: https://github.com/adrianofructuoso/bot_habitos
- **Railway**: https://railway.app
- **BotFather**: https://t.me/botfather

## 📋 Próximos Passos

1. ✅ Criar repositório no GitHub
2. ✅ Fazer push do código
3. 🔄 Configurar Railway
4. 🔄 Configurar bot no Telegram
5. 🔄 Fazer deploy

---

**💡 Dica**: Se você não conseguir fazer o push, verifique se está autenticado no GitHub via terminal ou use um token de acesso pessoal. 