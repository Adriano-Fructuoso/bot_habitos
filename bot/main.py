from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from config import TELEGRAM_BOT_TOKEN
from utils.scheduler import init_scheduler, stop_scheduler
from utils.cache import start_cache_cleanup
from utils.logging_config import get_logger

from .backup import backup_command
from .handlers import (
    complete_habit_callback,
    dashboard_command,
    delete_habit_callback,
    delete_habit_command,
    edit_habit_callback,
    edit_habit_command,
    habit_command,
    habits_command,
    menu_callback,
    menu_command,
    rating_callback,
    rating_command,
    set_reminder_callback,
    set_reminder_command,
    show_progress_callback,
    start_command,
    stats_command,
    weekly_command,
    handle_text_message,
    handle_voice_message,
    habit_creation_handler,
    # Novos handlers para tabela de hábitos
    toggle_complete_habit_callback,
    confirm_selection_callback,
    clear_selection_callback,
    edit_habit_full_callback,
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

    # Cria a aplicação com configurações de rede
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
    application.add_handler(CommandHandler("menu", menu_command))

    # Comandos CRUD (exceto addhabits que usa ConversationHandler)
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
    application.add_handler(
        CallbackQueryHandler(show_progress_callback, pattern="^progress_")
    )
    application.add_handler(
        CallbackQueryHandler(show_progress_callback, pattern="^help_")
    )
    application.add_handler(
        CallbackQueryHandler(show_progress_callback, pattern="^quick_")
    )
    application.add_handler(
        CallbackQueryHandler(show_progress_callback, pattern="^form_")
    )
    application.add_handler(CallbackQueryHandler(menu_callback, pattern="^menu_"))

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
    
    # Novos callbacks para tabela de hábitos
    application.add_handler(
        CallbackQueryHandler(toggle_complete_habit_callback, pattern="^toggle_complete_")
    )
    application.add_handler(
        CallbackQueryHandler(confirm_selection_callback, pattern="^confirm_selection$")
    )
    application.add_handler(
        CallbackQueryHandler(clear_selection_callback, pattern="^clear_selection$")
    )
    application.add_handler(
        CallbackQueryHandler(edit_habit_full_callback, pattern="^edit_habit_")
    )

    # ConversationHandler para criação de hábitos (deve vir ANTES dos handlers de texto)
    application.add_handler(habit_creation_handler)
    
    # Handlers para mensagens de texto (deve vir DEPOIS do ConversationHandler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))

    # Inicializa scheduler
    init_scheduler(application)
    
    # Inicia limpeza automática do cache
    start_cache_cleanup()

    # Inicia o bot
    logger.info("Bot iniciado!")

    try:
        logger.info("Iniciando polling...")
        logger.info(f"Token configurado: {TELEGRAM_BOT_TOKEN[:10]}...")
        
        # Configurações simples e robustas
        application.run_polling(
            drop_pending_updates=True
        )
    except KeyboardInterrupt:
        logger.info("Bot parando...")
    except Exception as e:
        logger.error(f"Erro no polling: {e}")
        logger.error(f"Tipo de erro: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    finally:
        stop_scheduler()
        logger.info("Bot parado!")


if __name__ == "__main__":
    main()
