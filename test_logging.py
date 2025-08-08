#!/usr/bin/env python3
"""
Teste para verificar configuração de logging
"""

import os
import sys
from unittest.mock import patch

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_logging_config():
    """Testa configuração de logging"""
    from config import LOG_JSON

    assert isinstance(LOG_JSON, bool)
    print("✅ LOG_JSON configurado corretamente")


def test_log_format():
    """Testa formato de log"""
    from bot.handlers import log_event

    with patch("bot.handlers.logger") as mock_logger:
        log_event("INFO", "test message", user_id=123)

        # Verifica se o logger foi chamado
        mock_logger.info.assert_called_once()
        print("✅ Log funcionando (formato: {'JSON' if LOG_JSON else 'texto'})")


def test_safe_handler_wrapper():
    """Testa se os wrappers foram criados corretamente"""
    from bot.handlers import (
        dashboard_command,
        habit_command,
        habits_command,
        rating_command,
        start_command,
        stats_command,
        weekly_command,
    )

    # Verifica se os wrappers existem
    assert start_command is not None
    assert habit_command is not None
    assert stats_command is not None
    assert dashboard_command is not None
    assert rating_command is not None
    assert weekly_command is not None
    assert habits_command is not None

    print("✅ Wrappers de handlers criados corretamente")


if __name__ == "__main__":
    print("🧪 Testando configuração de logging...")

    test_logging_config()
    test_log_format()
    test_safe_handler_wrapper()

    print("🎉 Todos os testes de logging passaram!")
