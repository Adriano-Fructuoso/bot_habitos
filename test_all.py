#!/usr/bin/env python3
"""
Teste final para verificar toda a implementação
"""

import os
import sys

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_all_implementations():
    """Testa todas as implementações das etapas"""
    print("🧪 Testando todas as implementações...")

    # Etapa 1: Logging e Error Handling
    try:
        from config import APP_ENV, LOG_JSON, LOG_LEVEL
        assert isinstance(LOG_JSON, bool)
        assert LOG_LEVEL in ["DEBUG", "INFO", "WARNING", "ERROR"]
        assert APP_ENV in ["development", "production"]
        print("✅ Etapa 1: Logging e Error Handling")
    except Exception as e:
        print(f"❌ Etapa 1 falhou: {e}")
        return False

    # Etapa 2: Idempotência
    try:
        from utils.idempotency import cleanup_old_callbacks, is_duplicate_callback
        assert callable(is_duplicate_callback)
        assert callable(cleanup_old_callbacks)
        print("✅ Etapa 2: Idempotência")
    except Exception as e:
        print(f"❌ Etapa 2 falhou: {e}")
        return False

    # Etapa 3: Health Check
    try:
        from bot.health import START_TS, health_command
        assert callable(health_command)
        assert START_TS > 0
        print("✅ Etapa 3: Health Check")
    except Exception as e:
        print(f"❌ Etapa 3 falhou: {e}")
        return False

    # Etapa 4: Rate Limiting
    try:
        from utils.rate_limit import get_rate_limit_info, rate_limited
        assert callable(rate_limited)
        assert callable(get_rate_limit_info)
        print("✅ Etapa 4: Rate Limiting")
    except Exception as e:
        print(f"❌ Etapa 4 falhou: {e}")
        return False

    # Etapa 6: Sanitização
    try:
        from utils.sanitize import clamp_len, escape_md, validate_habit_id
        assert callable(clamp_len)
        assert callable(escape_md)
        assert callable(validate_habit_id)
        print("✅ Etapa 6: Sanitização")
    except Exception as e:
        print(f"❌ Etapa 6 falhou: {e}")
        return False

    # Etapa 7: Docker
    try:
        assert os.path.exists("Dockerfile")
        assert os.path.exists("docker-compose.yml")
        assert os.path.exists("Makefile")
        assert os.path.exists("requirements.txt")
        assert os.path.exists("scripts/backup.sh")
        assert os.path.exists("scripts/dev-up.sh")
        assert os.path.exists("scripts/prod-deploy.sh")
        print("✅ Etapa 7: Docker e Scripts")
    except Exception as e:
        print(f"❌ Etapa 7 falhou: {e}")
        return False

    # Etapa 8: Observabilidade
    try:
        from utils.observability import get_health_metrics, get_metrics
        assert callable(get_metrics)
        assert callable(get_health_metrics)
        print("✅ Etapa 8: Observabilidade")
    except Exception as e:
        print(f"❌ Etapa 8 falhou: {e}")
        return False

    # Etapa 10: Branding OP Codes
    try:
        from config import BRAND, FOOTER
        assert BRAND == "OP Codes · HabitBot"
        assert "OP Codes" in FOOTER
        print("✅ Etapa 10: Branding OP Codes")
    except Exception as e:
        print(f"❌ Etapa 10 falhou: {e}")
        return False

    # Etapa 11: Comando /help
    try:
        from bot.help import HELP_TEXT, help_cmd
        assert callable(help_cmd)
        assert "HabitBot" in HELP_TEXT
        print("✅ Etapa 11: Comando /help")
    except Exception as e:
        print(f"❌ Etapa 11 falhou: {e}")
        return False

    # Etapa 12: Backup Script
    try:
        from bot.backup import backup_command
        from utils.scheduler import backup_now, scheduler
        assert scheduler is not None
        assert callable(backup_now)
        assert callable(backup_command)
        print("✅ Etapa 12: Backup Script")
    except Exception as e:
        print(f"❌ Etapa 12 falhou: {e}")
        return False

    return True

def test_docker_files():
    """Testa arquivos Docker"""
    print("\n🐳 Testando arquivos Docker...")

    # Dockerfile
    with open("Dockerfile") as f:
        content = f.read()
        assert "FROM python:3.11-slim" in content
        assert "CMD alembic upgrade head && python run.py" in content
    print("✅ Dockerfile")

    # docker-compose.yml
    with open("docker-compose.yml") as f:
        content = f.read()
        assert "postgres:15-alpine" in content
        assert "habit-bot:" in content
    print("✅ docker-compose.yml")

    # Makefile
    with open("Makefile") as f:
        content = f.read()
        assert "build:" in content
        assert "up:" in content
        assert "test:" in content
    print("✅ Makefile")

def test_scripts():
    """Testa scripts"""
    print("\n📜 Testando scripts...")

    # Verificar se são executáveis
    assert os.access("scripts/backup.sh", os.X_OK)
    assert os.access("scripts/dev-up.sh", os.X_OK)
    assert os.access("scripts/prod-deploy.sh", os.X_OK)
    print("✅ Scripts executáveis")

def test_requirements():
    """Testa requirements.txt"""
    print("\n📦 Testando requirements.txt...")

    with open("requirements.txt") as f:
        content = f.read()
        assert "python-telegram-bot" in content
        assert "sqlalchemy" in content
        assert "alembic" in content
        assert "pytest" in content
        assert "black" in content
    print("✅ requirements.txt")

if __name__ == "__main__":
    print("🎯 TESTE FINAL - Todas as Implementações")
    print("=" * 50)

    success = True

    try:
        success &= test_all_implementations()
        test_docker_files()
        test_scripts()
        test_requirements()
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        success = False

    print("\n" + "=" * 50)
    if success:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("\n📋 Resumo das implementações:")
        print("✅ Etapa 1: Logging e Error Handling")
        print("✅ Etapa 2: Idempotência de Callbacks")
        print("✅ Etapa 3: Health Check (/health)")
        print("✅ Etapa 4: Rate Limiting")
        print("✅ Etapa 6: Sanitização de Input")
        print("✅ Etapa 7: Docker + Scripts")
        print("✅ Etapa 8: Observabilidade")
        print("✅ Etapa 10: Branding OP Codes")
        print("✅ Etapa 11: Comando /help")
        print("✅ Etapa 12: Backup Script")
        print("\n🚀 Próximos passos:")
        print("1. make build")
        print("2. make up")
        print("3. make logs")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("Verifique os erros acima.")
