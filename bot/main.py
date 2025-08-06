import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import TELEGRAM_BOT_TOKEN
from .handlers import (
    start_command, habit_command, stats_command, dashboard_command,
    rating_command, weekly_command, habits_command,
    complete_habit_callback, rating_callback, show_progress_callback
)

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)



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
    
    # Registra handlers de callbacks (botões inline)
    application.add_handler(CallbackQueryHandler(complete_habit_callback, pattern="^complete_habit_"))
    application.add_handler(CallbackQueryHandler(rating_callback, pattern="^rate_"))
    application.add_handler(CallbackQueryHandler(show_progress_callback, pattern="^show_progress$"))
    
    # Inicia o bot
    logger.info("Bot iniciado!")
    application.run_polling()

if __name__ == "__main__":
    main() 