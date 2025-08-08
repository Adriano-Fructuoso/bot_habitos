#!/usr/bin/env python3
"""
Teste para verificar branding OP Codes
"""

import os
import sys

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_branding_import():
    """Testa se o módulo de branding pode ser importado"""
    from utils.branding import (
        add_branding,
        get_error_message_with_branding,
        get_help_message,
        get_info_message_with_branding,
        get_motivational_message_with_branding,
        get_success_message_with_branding,
        get_welcome_message,
    )

    assert callable(add_branding)
    assert callable(get_welcome_message)
    assert callable(get_help_message)
    assert callable(get_motivational_message_with_branding)
    assert callable(get_error_message_with_branding)
    assert callable(get_success_message_with_branding)
    assert callable(get_info_message_with_branding)

    print("✅ Módulo de branding importado corretamente")

def test_brand_config():
    """Testa configuração de branding"""
    from config import BRAND, FOOTER, OPCODES_SITE_URL

    assert BRAND == "OP Codes · HabitBot"
    assert "OP Codes" in FOOTER
    assert "HabitBot" in FOOTER
    assert OPCODES_SITE_URL == "https://opcodes.com.br"

    print("✅ Configuração de branding correta")

def test_add_branding():
    """Testa função add_branding"""
    from utils.branding import add_branding

    # Teste com footer
    message = "Teste de mensagem"
    branded = add_branding(message, include_footer=True)
    assert "OP Codes" in branded
    assert "HabitBot" in branded

    # Teste sem footer
    branded_no_footer = add_branding(message, include_footer=False)
    assert branded_no_footer == message

    print("✅ Função add_branding funcionando")

def test_welcome_message():
    """Testa mensagem de boas-vindas"""
    from utils.branding import get_welcome_message

    message = get_welcome_message()

    # Verificar elementos essenciais
    assert "OP Codes" in message
    assert "HabitBot" in message
    assert "Bem-vindo" in message
    assert "hábitos" in message
    assert "XP" in message
    assert "/habit" in message

    print("✅ Mensagem de boas-vindas correta")

def test_help_message():
    """Testa mensagem de ajuda simplificada"""
    from bot.help import _help

    # Verificar que a função existe
    assert callable(_help)
    print("✅ Função _help carregada corretamente")

def test_error_messages():
    """Testa mensagens de erro"""
    from utils.branding import get_error_message_with_branding

    # Teste erro geral
    general_error = get_error_message_with_branding("general")
    assert "❌" in general_error
    assert "OP Codes" in general_error

    # Teste rate limit
    rate_limit_error = get_error_message_with_branding("rate_limit")
    assert "⏳" in rate_limit_error
    assert "OP Codes" in rate_limit_error

    # Teste entrada inválida
    invalid_error = get_error_message_with_branding("invalid_input")
    assert "⚠️" in invalid_error
    assert "OP Codes" in invalid_error

    print("✅ Mensagens de erro funcionando")

def test_success_messages():
    """Testa mensagens de sucesso"""
    from utils.branding import get_success_message_with_branding

    message = get_success_message_with_branding("Operação realizada com sucesso!")

    assert "✅" in message
    assert "OP Codes" in message
    assert "Operação realizada com sucesso!" in message

    print("✅ Mensagens de sucesso funcionando")

def test_info_messages():
    """Testa mensagens informativas"""
    from utils.branding import get_info_message_with_branding

    message = get_info_message_with_branding("Informação importante")

    assert "ℹ️" in message
    assert "OP Codes" in message
    assert "Informação importante" in message

    print("✅ Mensagens informativas funcionando")

def test_motivational_messages():
    """Testa mensagens motivacionais"""
    from utils.branding import get_motivational_message_with_branding

    message = get_motivational_message_with_branding("start")

    assert "OP Codes" in message
    assert "HabitBot" in message

    print("✅ Mensagens motivacionais funcionando")

def test_help_command():
    """Testa comando /help"""
    from bot.help import help_cmd

    assert callable(help_cmd)
    print("✅ Comando /help registrado")

if __name__ == "__main__":
    print("🧪 Testando branding OP Codes...")

    test_branding_import()
    test_brand_config()
    test_add_branding()
    test_welcome_message()
    test_help_message()
    test_error_messages()
    test_success_messages()
    test_info_messages()
    test_motivational_messages()
    test_help_command()

    print("🎉 Todos os testes de branding passaram!")
