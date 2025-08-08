#!/usr/bin/env python3
"""
Teste para verificar sanitização de input
"""

import os
import sys

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_clamp_len():
    """Testa limitação de tamanho de string"""
    from utils.sanitize import clamp_len

    # Teste string normal
    result = clamp_len("teste", 10)
    assert result == "teste"
    print("✅ String normal mantida")

    # Teste string truncada
    result = clamp_len("teste muito longo", 5)
    assert result == "teste"
    assert len(result) == 5
    print("✅ String truncada corretamente")

    # Teste string vazia
    result = clamp_len("", 10)
    assert result == ""
    print("✅ String vazia mantida")


def test_escape_md():
    """Testa escape de Markdown"""
    from utils.sanitize import escape_md

    # Teste caracteres especiais
    result = escape_md("texto com *asterisco* e _underline_")
    assert "\\*" in result
    assert "\\_" in result
    print("✅ Caracteres especiais escapados")

    # Teste texto normal
    result = escape_md("texto normal")
    assert result == "texto normal"
    print("✅ Texto normal mantido")

    # Teste string vazia
    result = escape_md("")
    assert result == ""
    print("✅ String vazia mantida")


def test_is_int():
    """Testa validação de inteiros"""
    from utils.sanitize import is_int

    # Teste números válidos
    assert is_int("123") == True
    assert is_int("0") == True
    print("✅ Números válidos reconhecidos")

    # Teste números inválidos
    assert is_int("abc") == False
    assert is_int("12.34") == False
    assert is_int("") == False
    assert is_int(None) == False
    print("✅ Números inválidos rejeitados")


def test_sanitize_username():
    """Testa sanitização de username"""
    from utils.sanitize import sanitize_username

    # Teste username válido
    result = sanitize_username("user123")
    assert result == "user123"
    print("✅ Username válido mantido")

    # Teste username com caracteres especiais
    result = sanitize_username("user@123!")
    assert result == "user123"
    print("✅ Caracteres especiais removidos")

    # Teste username muito longo
    long_username = "a" * 50
    result = sanitize_username(long_username)
    assert len(result) <= 32
    print("✅ Username longo truncado")


def test_validate_habit_id():
    """Testa validação de ID de hábito"""
    from utils.sanitize import validate_habit_id

    # Teste IDs válidos
    assert validate_habit_id("1") == True
    assert validate_habit_id("123") == True
    assert validate_habit_id("999999") == True
    print("✅ IDs válidos aceitos")

    # Teste IDs inválidos
    assert validate_habit_id("0") == False
    assert validate_habit_id("abc") == False
    assert validate_habit_id("1000000") == False
    assert validate_habit_id("") == False
    print("✅ IDs inválidos rejeitados")


def test_sanitize_habit_name():
    """Testa sanitização de nome de hábito"""
    from utils.sanitize import sanitize_habit_name

    # Teste nome válido
    result = sanitize_habit_name("Exercício")
    assert result == "Exercício"
    print("✅ Nome válido mantido")

    # Teste nome com caracteres de controle
    result = sanitize_habit_name("Exercício\x00\x01")
    assert "\x00" not in result
    assert "\x01" not in result
    print("✅ Caracteres de controle removidos")

    # Teste nome vazio
    result = sanitize_habit_name("")
    assert result == "Hábito sem nome"
    print("✅ Nome vazio substituído")


def test_sanitize_import():
    """Testa se a sanitização pode ser importada nos handlers"""
    from bot.handlers import clamp_len, escape_md, is_int

    assert clamp_len is not None
    assert escape_md is not None
    assert is_int is not None
    print("✅ Funções de sanitização importadas corretamente")


if __name__ == "__main__":
    print("🧪 Testando sanitização de input...")

    test_clamp_len()
    test_escape_md()
    test_is_int()
    test_sanitize_username()
    test_validate_habit_id()
    test_sanitize_habit_name()
    test_sanitize_import()

    print("🎉 Todos os testes de sanitização passaram!")
