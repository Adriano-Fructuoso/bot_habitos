"""
Comando para backup manual
"""

from functools import partial

from utils.branding import get_info_message_with_branding
from utils.scheduler import backup_now

from .handlers import safe_handler


async def _backup_command(update, context):
    """Handler para o comando /backup"""
    await update.message.reply_text(
        get_info_message_with_branding("Iniciando backup manual..."),
        parse_mode="Markdown"
    )

    # Executar backup em background
    await backup_now()

    await update.message.reply_text(
        get_info_message_with_branding("Backup manual concluído!"),
        parse_mode="Markdown"
    )

# Wrapper com safe_handler
backup_command = partial(safe_handler, _backup_command)
