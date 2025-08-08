#!/usr/bin/env python3
"""
Versão alternativa do bot usando webhook
"""

import asyncio
import logging
from bot.main import create_application
from config import TELEGRAM_BOT_TOKEN

# Configura logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

async def main():
    """Função principal usando webhook"""
    
    # Cria a aplicação
    application = create_application()
    
    # URL do webhook (você precisará de um servidor público)
    webhook_url = "https://seu-dominio.com/webhook"
    
    try:
        logger.info("Configurando webhook...")
        
        # Remove webhook existente
        await application.bot.delete_webhook()
        
        # Configura novo webhook
        await application.bot.set_webhook(url=webhook_url)
        
        logger.info(f"Webhook configurado: {webhook_url}")
        logger.info("Bot pronto para receber updates via webhook!")
        
        # Mantém o bot rodando
        await asyncio.Event().wait()
        
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
    finally:
        await application.bot.delete_webhook()
        logger.info("Webhook removido")

if __name__ == "__main__":
    asyncio.run(main())
