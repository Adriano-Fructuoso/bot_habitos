"""
Handlers base e utilitários
"""

import asyncio
import functools
from typing import Callable, Any
from telegram import Update
from telegram.ext import ContextTypes
from utils.observability import log_event, log_error
from utils.idempotency import is_duplicate_callback
from utils.rate_limit import rate_limited
from utils.branding import get_error_message_with_branding
from utils.logging_config import get_logger

logger = get_logger(__name__)


def safe_handler(func: Callable) -> Callable:
    """Wrapper universal para handlers com tratamento de erro"""
    
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
        user = update.effective_user
        user_id = user.id if user else "unknown"
        command = func.__name__
        
        try:
            # Log início do comando
            log_event("command_start", {
                "user_id": user_id,
                "command": command,
                "chat_type": update.effective_chat.type if update.effective_chat else None
            })
            
            # Executa handler
            result = await func(update, context)
            
            # Log sucesso
            log_event("command_success", {
                "user_id": user_id,
                "command": command
            })
            
            return result
            
        except Exception as e:
            # Log erro
            log_error(e, {
                "user_id": user_id,
                "command": command,
                "update": str(update)
            })
            
            # Envia mensagem de erro para o usuário
            error_message = get_error_message_with_branding("general")
            if update.message:
                await update.message.reply_text(error_message, parse_mode="Markdown")
            elif update.callback_query:
                await update.callback_query.answer("❌ Erro interno. Tente novamente.")
            
            logger.error(f"Erro no handler {command}: {e}")
            return None
    
    return wrapper


def track_command(command_name: str) -> Callable:
    """Decorator para tracking de comandos"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
            user = update.effective_user
            user_id = user.id if user else "unknown"
            
            # Rate limiting
            if rate_limited(f"{command_name}:{user_id}", 1):
                await update.message.reply_text(
                    get_error_message_with_branding("rate_limit"),
                    parse_mode="Markdown"
                )
                return
            
            # Idempotência para callbacks
            if update.callback_query:
                callback_id = update.callback_query.id
                if is_duplicate_callback(callback_id):
                    await update.callback_query.answer("Comando já processado")
                    return
            
            # Executa comando
            return await func(update, context)
        
        return wrapper
    return decorator
