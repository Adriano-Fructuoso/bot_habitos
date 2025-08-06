import os
import logging
from telegram.ext import Application, CommandHandler
from dotenv import load_dotenv
from .handlers import start_command, habit_command, stats_command
from db.session import init_db
from telegram import Update

# Carrega variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update, context):
    """Handler para erros do bot"""
    logger.error(f"Erro no bot: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Ocorreu um erro inesperado. Tente novamente mais tarde."
        )

def main():
    """Função principal para inicializar o bot"""
    try:
        # Obtém o token do bot
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN não configurado nas variáveis de ambiente")
        
        # Inicializa o banco de dados
        logger.info("Inicializando banco de dados...")
        init_db()
        logger.info("Banco de dados inicializado com sucesso!")
        
        # Cria a aplicação do bot
        application = Application.builder().token(token).build()
        
        # Adiciona handlers para os comandos
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("habit", habit_command))
        application.add_handler(CommandHandler("stats", stats_command))
        
        # Adiciona handler de erro
        application.add_error_handler(error_handler)
        
        # Log de inicialização
        logger.info("Bot iniciado com sucesso!")
        logger.info("Comandos disponíveis: /start, /habit, /stats")
        
        # Inicia o bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Erro ao inicializar o bot: {e}")
        raise

if __name__ == "__main__":
    main() 