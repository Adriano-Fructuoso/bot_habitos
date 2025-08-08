#!/usr/bin/env python3
"""
Teste para verificar idempotência de callbacks
"""

import os
import sys
from datetime import datetime

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_idempotency_functions():
    """Testa funções de idempotência"""
    from db.session import get_db
    from utils.idempotency import cleanup_old_callbacks, is_duplicate_callback

    db = next(get_db())

    try:
        # Teste 1: Callback novo deve retornar False
        callback_id = f"test_callback_{datetime.now().timestamp()}"
        result = is_duplicate_callback(callback_id, db)
        assert (
            result == False
        ), f"Callback novo deveria retornar False, mas retornou {result}"
        print("✅ Callback novo processado corretamente")

        # Teste 2: Mesmo callback deve retornar True (duplicado)
        result = is_duplicate_callback(callback_id, db)
        assert (
            result == True
        ), f"Callback duplicado deveria retornar True, mas retornou {result}"
        print("✅ Callback duplicado detectado corretamente")

        # Teste 3: Callback diferente deve retornar False
        callback_id_2 = f"test_callback_2_{datetime.now().timestamp()}"
        result = is_duplicate_callback(callback_id_2, db)
        assert (
            result == False
        ), f"Callback diferente deveria retornar False, mas retornou {result}"
        print("✅ Callback diferente processado corretamente")

        # Teste 4: Limpeza de callbacks antigos
        cleanup_old_callbacks(minutes=1, db=db)  # Remove callbacks de mais de 1 minuto
        print("✅ Limpeza de callbacks antigos executada")

    finally:
        db.close()


def test_processed_callback_model():
    """Testa modelo ProcessedCallback"""
    from db.session import get_db
    from models.models import ProcessedCallback

    db = next(get_db())

    try:
        # Verificar se o modelo pode ser importado
        assert ProcessedCallback is not None
        print("✅ Modelo ProcessedCallback importado corretamente")

        # Verificar se a tabela existe
        result = db.query(ProcessedCallback).count()
        print(f"✅ Tabela processed_callbacks existe com {result} registros")

    finally:
        db.close()


if __name__ == "__main__":
    print("🧪 Testando idempotência de callbacks...")

    test_processed_callback_model()
    test_idempotency_functions()

    print("🎉 Todos os testes de idempotência passaram!")
