#!/usr/bin/env python3
"""
Teste para verificar se os arquivos Docker estão corretos
"""

import os
import sys

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_dockerfile_exists():
    """Testa se o Dockerfile existe"""
    assert os.path.exists("Dockerfile"), "Dockerfile não encontrado"
    print("✅ Dockerfile existe")


def test_docker_compose_exists():
    """Testa se o docker-compose.yml existe"""
    assert os.path.exists("docker-compose.yml"), "docker-compose.yml não encontrado"
    print("✅ docker-compose.yml existe")


def test_requirements_exists():
    """Testa se o requirements.txt existe"""
    assert os.path.exists("requirements.txt"), "requirements.txt não encontrado"
    print("✅ requirements.txt existe")


def test_env_example_exists():
    """Testa se o .env.example existe"""
    assert os.path.exists(".env.example"), ".env.example não encontrado"
    print("✅ .env.example existe")


def test_makefile_exists():
    """Testa se o Makefile existe"""
    assert os.path.exists("Makefile"), "Makefile não encontrado"
    print("✅ Makefile existe")


def test_backup_script_exists():
    """Testa se o script de backup existe"""
    assert os.path.exists("scripts/backup.sh"), "scripts/backup.sh não encontrado"
    print("✅ Script de backup existe")


def test_dockerfile_content():
    """Testa conteúdo básico do Dockerfile"""
    with open("Dockerfile") as f:
        content = f.read()
        assert "FROM python:3.11-slim" in content
        assert "WORKDIR /app" in content
        assert "COPY requirements.txt" in content
        assert "CMD alembic upgrade head && python run.py" in content
    print("✅ Dockerfile tem conteúdo correto")


def test_docker_compose_content():
    """Testa conteúdo básico do docker-compose.yml"""
    with open("docker-compose.yml") as f:
        content = f.read()
        assert "postgres:15-alpine" in content
        assert "habit-bot:" in content
        assert "DATABASE_URL=postgresql+psycopg2://" in content
    print("✅ docker-compose.yml tem conteúdo correto")


def test_requirements_content():
    """Testa se requirements.txt tem dependências essenciais"""
    with open("requirements.txt") as f:
        content = f.read()
        assert "python-telegram-bot" in content
        assert "sqlalchemy" in content
        assert "alembic" in content
        assert "psycopg2-binary" in content
    print("✅ requirements.txt tem dependências corretas")


def test_env_example_content():
    """Testa se .env.example tem variáveis essenciais"""
    with open(".env.example") as f:
        content = f.read()
        assert "TELEGRAM_BOT_TOKEN" in content
        assert "DATABASE_URL" in content
        assert "APP_ENV" in content
        assert "LOG_LEVEL" in content
    print("✅ .env.example tem variáveis corretas")


def test_makefile_commands():
    """Testa se Makefile tem comandos essenciais"""
    with open("Makefile") as f:
        content = f.read()
        assert "up:" in content
        assert "down:" in content
        assert "build:" in content
        assert "test:" in content
    print("✅ Makefile tem comandos essenciais")


if __name__ == "__main__":
    print("🧪 Testando arquivos Docker...")

    test_dockerfile_exists()
    test_docker_compose_exists()
    test_requirements_exists()
    test_env_example_exists()
    test_makefile_exists()
    test_backup_script_exists()

    test_dockerfile_content()
    test_docker_compose_content()
    test_requirements_content()
    test_env_example_content()
    test_makefile_commands()

    print("🎉 Todos os testes Docker passaram!")
    print("\n📋 Para usar:")
    print("1. Configure .env com suas credenciais")
    print("2. Execute: make build")
    print("3. Execute: make up")
    print("4. Execute: make logs")
