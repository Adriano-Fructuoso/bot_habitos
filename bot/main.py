from telegram.ext import Application, CallbackQueryHandler, CommandHandler

from config import TELEGRAM_BOT_TOKEN
from utils.scheduler import init_scheduler, stop_scheduler
from utils.cache import start_cache_cleanup
from utils.logging_config import get_logger

from .backup import backup_command
from .handlers import (
    add_habit_command,
    complete_habit_callback,
    dashboard_command,
    delete_habit_callback,
    delete_habit_command,
    edit_habit_callback,
    edit_habit_command,
    habit_command,
    habits_command,
    rating_callback,
    rating_command,
    set_reminder_callback,
    set_reminder_command,
    show_progress_callback,
    start_command,
    stats_command,
    weekly_command,
)
from .health import health_command
from .help import help_cmd

logger = get_logger(__name__)


def main():
    """Função principal para inicializar e executar o bot"""

    # Verifica se o token está configurado
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN não configurado!")
        return

    # Cria a aplicação
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Registra handlers de comandos
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("habit", habit_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("dashboard", dashboard_command))
    application.add_handler(CommandHandler("rating", rating_command))
    application.add_handler(CommandHandler("weekly", weekly_command))
    application.add_handler(CommandHandler("habits", habits_command))
    application.add_handler(CommandHandler("health", health_command))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("backup", backup_command))

    # Novos comandos CRUD
    application.add_handler(CommandHandler("addhabits", add_habit_command))
    application.add_handler(CommandHandler("edithabits", edit_habit_command))
    application.add_handler(CommandHandler("delete_habit", delete_habit_command))
    application.add_handler(CommandHandler("set_reminder", set_reminder_command))

    # Registra handlers de callbacks (botões inline)
    application.add_handler(
        CallbackQueryHandler(complete_habit_callback, pattern="^complete_habit_")
    )
    application.add_handler(CallbackQueryHandler(rating_callback, pattern="^rate_"))
    application.add_handler(
        CallbackQueryHandler(show_progress_callback, pattern="^show_progress$")
    )

    # Novos callbacks CRUD
    application.add_handler(
        CallbackQueryHandler(edit_habit_callback, pattern="^edit_habit_")
    )
    application.add_handler(
        CallbackQueryHandler(delete_habit_callback, pattern="^delete_habit_")
    )
    application.add_handler(
        CallbackQueryHandler(set_reminder_callback, pattern="^set_reminder_")
    )

    # Inicializa scheduler
    init_scheduler(application)
    
    # Inicia limpeza automática do cache
    start_cache_cleanup()

    # Inicia o bot
    logger.info("Bot iniciado!")

    try:
        logger.info("Iniciando polling...")
        application.run_polling(timeout=30, read_timeout=30, write_timeout=30, connect_timeout=30, pool_timeout=30)
    except KeyboardInterrupt:
        logger.info("Bot parando...")
    except Exception as e:
        logger.error(f"Erro no polling: {e}")
    finally:
        stop_scheduler()
        logger.info("Bot parado!")


if __name__ == "__main__":
    main()
