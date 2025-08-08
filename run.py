#!/usr/bin/env python3
"""
Script de inicialização do Habit Bot
"""

import os
import sys

from config import SENTRY_DSN, APP_ENV

# Configuração centralizada de logging
from utils.logging_config import setup_logging, get_logger

# Configura logging
setup_logging()

# Configurar Sentry se DSN estiver disponível
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=0.0,  # Desabilita tracing para reduzir custos
        environment=APP_ENV,
        integrations=[
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            )
        ]
    )
    logger = get_logger("habit-bot")
    logger.info(f"Sentry configurado para ambiente: {APP_ENV}")

logger = get_logger("habit-bot")
logger.info(f"Starting bot (env={APP_ENV})")

# Adiciona o diretório atual ao path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import TELEGRAM_BOT_TOKEN


def main():
    """Função principal de inicialização"""
    try:
        # Valida configurações
        if not TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN não configurado")

        # Importa e executa o bot
        from bot.main import main as run_bot
        from utils.cache import start_cache_cleanup

        logger.info("Bot initialized, starting polling...")
        
        # Inicia limpeza automática do cache
        start_cache_cleanup()
        
        run_bot()

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"❌ Erro de configuração: {e}")
        print("📝 Verifique se o arquivo .env está configurado corretamente")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)
    finally:
        logger.info("Bot stopped")


if __name__ == "__main__":
    main()
