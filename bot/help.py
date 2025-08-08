"""
Comando /help simplificado
"""

from telegram import Update
from telegram.ext import ContextTypes

from utils.branding import add_branding
from .handlers.base import track_command


@track_command("help")
async def _help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /help"""

    help_text = """
🤖 *Comandos Disponíveis*

*Hábitos:*
• /start - Iniciar bot e criar hábitos padrão
• /habit - Ver e completar hábitos do dia
• /habits - Listar todos os seus hábitos
• /add_habit - Criar novo hábito customizado
• /edit_habit - Editar hábitos existentes
• /delete_habit - Deletar hábitos

*Lembretes:*
• /set_reminder - Configurar lembretes para hábitos

*Progresso:*
• /stats - Ver suas estatísticas
• /dashboard - Dashboard completo
• /rating - Avaliar seu dia
• /weekly - Resumo semanal

*Sistema:*
• /health - Status do bot
• /help - Esta mensagem
• /backup - Backup dos dados

*Como usar:*
1. Use /start para começar
2. /add_habit para criar hábitos customizados
3. /set_reminder para configurar lembretes
4. /habit diariamente para marcar como completo
5. /stats para acompanhar seu progresso

*Precisa de ajuda?* Entre em contato com o desenvolvedor.
"""

    branded_help = add_branding(help_text)
    await update.message.reply_text(branded_help, parse_mode="Markdown")


# Exporta o comando
help_cmd = _help
