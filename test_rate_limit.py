#!/usr/bin/env python3
"""
Teste para verificar rate limiting
"""

import os
import sys
import time

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_rate_limit_functions():
    """Testa funções de rate limiting"""
    from utils.rate_limit import clear_rate_limit, get_rate_limit_info, rate_limited

    # Limpar cache antes dos testes
    clear_rate_limit()

    # Teste 1: Primeira chamada deve retornar False (permitido)
    key = "test:123"
    result = rate_limited(key, 1)
    assert (
        result == False
    ), f"Primeira chamada deveria retornar False, mas retornou {result}"
    print("✅ Primeira chamada permitida")

    # Teste 2: Segunda chamada imediata deve retornar True (limitado)
    result = rate_limited(key, 1)
    assert (
        result == True
    ), f"Segunda chamada deveria retornar True, mas retornou {result}"
    print("✅ Segunda chamada limitada")

    # Teste 3: Após 1 segundo deve ser permitido novamente
    time.sleep(1.1)  # Aguardar mais que a janela
    result = rate_limited(key, 1)
    assert result == False, f"Após 1s deveria retornar False, mas retornou {result}"
    print("✅ Após janela de tempo, permitido novamente")

    # Teste 4: Informações do rate limit
    info = get_rate_limit_info(key)
    assert info["key"] == key
    assert "last_request" in info
    assert "time_since_last" in info
    print("✅ Informações do rate limit funcionando")

    # Teste 5: Limpeza de cache
    clear_rate_limit(key)
    info = get_rate_limit_info(key)
    assert info["last_request"] == 0, "Cache deveria ter sido limpo"
    print("✅ Limpeza de cache funcionando")


def test_rate_limit_different_keys():
    """Testa rate limiting com chaves diferentes"""
    from utils.rate_limit import clear_rate_limit, rate_limited

    # Limpar cache
    clear_rate_limit()

    # Teste com chaves diferentes
    key1 = "start:123"
    key2 = "habit:123"

    # Ambas devem ser permitidas
    result1 = rate_limited(key1, 1)
    result2 = rate_limited(key2, 1)

    assert result1 == False, f"Chave {key1} deveria ser permitida"
    assert result2 == False, f"Chave {key2} deveria ser permitida"
    print("✅ Chaves diferentes são independentes")


def test_rate_limit_import():
    """Testa se o rate limiting pode ser importado nos handlers"""
    from bot.handlers import rate_limited

    assert rate_limited is not None
    assert callable(rate_limited)
    print("✅ Rate limiting importado corretamente nos handlers")


if __name__ == "__main__":
    print("🧪 Testando rate limiting...")

    test_rate_limit_functions()
    test_rate_limit_different_keys()
    test_rate_limit_import()

    print("🎉 Todos os testes de rate limiting passaram!")
