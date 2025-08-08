#!/usr/bin/env python3
"""
Teste para verificar comando /health
"""

import os
import sys
from unittest.mock import AsyncMock, patch

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_health_module_import():
    """Testa se o módulo health pode ser importado"""
    from bot.health import START_TS, health_command

    assert health_command is not None
    assert START_TS > 0
    print("✅ Módulo health importado corretamente")


def test_health_command_structure():
    """Testa estrutura do comando health"""
    from bot.health import _health_command

    # Verifica se a função existe e é assíncrona
    assert callable(_health_command)
    print("✅ Função _health_command existe e é callable")


def test_health_command_response():
    """Testa resposta do comando health"""
    from telegram import Message, Update
    from telegram.ext import ContextTypes

    from bot.health import _health_command

    # Mock do update
    mock_update = AsyncMock(spec=Update)
    mock_message = AsyncMock(spec=Message)
    mock_update.message = mock_message

    # Mock do context
    mock_context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)

    # Executar comando
    with patch("bot.health.SessionLocal") as mock_session:
        # Mock da sessão do banco
        mock_session_instance = AsyncMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.execute.return_value.fetchone.return_value = [1]

        # Mock da query de migração
        mock_session_instance.execute.return_value.fetchone.side_effect = [
            [1],  # Primeira chamada (SELECT 1)
            ["7093835ceccf"],  # Segunda chamada (alembic_version)
        ]

        # Executar
        import asyncio

        asyncio.run(_health_command(mock_update, mock_context))

        # Verificar se reply_text foi chamado
        mock_message.reply_text.assert_called_once()

        # Verificar conteúdo da resposta
        call_args = mock_message.reply_text.call_args
        message_text = call_args[0][0]

        # Verificar se contém informações essenciais
        assert "Health Check" in message_text
        assert "Database:" in message_text
        assert "System:" in message_text
        assert "Uptime:" in message_text
        assert "Python:" in message_text

        print("✅ Comando health responde corretamente")


def test_health_config():
    """Testa configuração de versão"""
    from config import APP_VERSION

    assert APP_VERSION is not None
    assert isinstance(APP_VERSION, str)
    print(f"✅ APP_VERSION configurado: {APP_VERSION}")


if __name__ == "__main__":
    print("🧪 Testando comando /health...")

    test_health_module_import()
    test_health_command_structure()
    test_health_config()
    test_health_command_response()

    print("🎉 Todos os testes de health passaram!")
