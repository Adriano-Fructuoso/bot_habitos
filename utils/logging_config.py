"""
Configuração centralizada de logging para o Habit Bot
"""

import logging
import logging.handlers
import os
import sys
from typing import Optional

from config import APP_ENV, LOG_LEVEL, LOG_JSON


def setup_logging(
    level: Optional[str] = None,
    log_to_file: bool = False,
    log_file: str = "habit_bot.log",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Configura o sistema de logging centralizado.
    
    Args:
        level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Se deve logar para arquivo
        log_file: Nome do arquivo de log
        max_bytes: Tamanho máximo do arquivo de log
        backup_count: Número de backups a manter
    """
    # Usa o nível do config se não especificado
    if level is None:
        level = LOG_LEVEL.upper()
    
    # Configura o nível de logging
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Remove handlers existentes para evitar duplicação
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configura formato baseado no ambiente
    if LOG_JSON:
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}'
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(numeric_level)
    
    # Adiciona handler do console
    root_logger.addHandler(console_handler)
    
    # Handler para arquivo (se solicitado)
    if log_to_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(numeric_level)
        root_logger.addHandler(file_handler)
    
    # Configura nível do logger raiz
    root_logger.setLevel(numeric_level)
    
    # Configura loggers específicos
    loggers_to_configure = [
        "telegram",
        "httpx",
        "urllib3",
        "sqlalchemy.engine",
        "apscheduler",
    ]
    
    for logger_name in loggers_to_configure:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.WARNING)
        logger.propagate = False
    
    # Logger principal do bot
    bot_logger = logging.getLogger("habit-bot")
    bot_logger.setLevel(numeric_level)
    
    # Log da configuração
    bot_logger.info(f"Logging configurado - Nível: {level}, JSON: {LOG_JSON}, Ambiente: {APP_ENV}")


def get_logger(name: str) -> logging.Logger:
    """
    Obtém um logger configurado para o módulo especificado.
    
    Args:
        name: Nome do módulo (geralmente __name__)
        
    Returns:
        Logger configurado
    """
    return logging.getLogger(name)


def log_function_call(logger: logging.Logger, func_name: str, **kwargs):
    """
    Loga a chamada de uma função com seus parâmetros.
    
    Args:
        logger: Logger a ser usado
        func_name: Nome da função
        **kwargs: Parâmetros da função
    """
    if logger.isEnabledFor(logging.DEBUG):
        params = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
        logger.debug(f"Chamando {func_name}({params})")


def log_function_result(logger: logging.Logger, func_name: str, result=None, error=None):
    """
    Loga o resultado de uma função.
    
    Args:
        logger: Logger a ser usado
        func_name: Nome da função
        result: Resultado da função
        error: Erro ocorrido (se houver)
    """
    if error:
        logger.error(f"Erro em {func_name}: {error}")
    elif logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Resultado de {func_name}: {result}")


# Configuração automática quando o módulo é importado
if not logging.getLogger().handlers:
    setup_logging()
