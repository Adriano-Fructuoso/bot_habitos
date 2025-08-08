#!/usr/bin/env python3
"""
Teste para verificar backup e scheduler
"""

import os
import sys

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_backup_script_exists():
    """Testa se o script de backup existe"""
    assert os.path.exists("scripts/backup.sh")
    assert os.access("scripts/backup.sh", os.X_OK)
    print("✅ Script de backup existe e é executável")

def test_backup_script_content():
    """Testa conteúdo do script de backup"""
    with open("scripts/backup.sh") as f:
        content = f.read()

    # Verificar elementos essenciais
    assert "sqlite:" in content
    assert "postgresql" in content
    assert "pg_dump" in content
    assert "cp" in content
    assert "DATABASE_URL" in content

    print("✅ Script de backup tem conteúdo correto")

def test_scheduler_import():
    """Testa se o scheduler pode ser importado"""
    from utils.scheduler import (
        backup_now,
        cleanup_old_data,
        get_scheduler_status,
        health_check,
        init_scheduler,
        scheduler,
        stop_scheduler,
    )

    assert scheduler is not None
    assert callable(backup_now)
    assert callable(cleanup_old_data)
    assert callable(health_check)
    assert callable(init_scheduler)
    assert callable(stop_scheduler)
    assert callable(get_scheduler_status)

    print("✅ Módulo scheduler importado corretamente")

def test_scheduler_status():
    """Testa função de status do scheduler"""
    from utils.scheduler import get_scheduler_status

    status = get_scheduler_status()

    assert "running" in status
    assert "jobs_count" in status
    assert "jobs" in status
    assert isinstance(status["running"], bool)
    assert isinstance(status["jobs_count"], int)
    assert isinstance(status["jobs"], list)

    print("✅ Status do scheduler funcionando")

def test_backup_command():
    """Testa comando /backup"""
    from bot.backup import backup_command

    assert callable(backup_command)
    print("✅ Comando /backup registrado")

def test_docker_compose_backup_volume():
    """Testa se o volume de backup está configurado"""
    with open("docker-compose.yml") as f:
        content = f.read()

    assert "./backups:/app/backups" in content
    print("✅ Volume de backup configurado no docker-compose")

def test_requirements_apscheduler():
    """Testa se APScheduler está no requirements"""
    with open("requirements.txt") as f:
        content = f.read()

    assert "apscheduler" in content
    print("✅ APScheduler no requirements.txt")

def test_backup_directory():
    """Testa se diretório de backup pode ser criado"""
    backup_dir = "./backups"

    # Criar diretório se não existir
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    assert os.path.exists(backup_dir)
    assert os.path.isdir(backup_dir)
    print("✅ Diretório de backup pode ser criado")

def test_environment_variables():
    """Testa variáveis de ambiente para backup"""
    from config import DATABASE_URL

    # Verificar se DATABASE_URL está configurado
    assert DATABASE_URL is not None
    assert len(DATABASE_URL) > 0

    # Verificar se é um tipo suportado
    assert DATABASE_URL.startswith(("sqlite://", "postgresql"))

    print("✅ Variáveis de ambiente para backup configuradas")

if __name__ == "__main__":
    print("🧪 Testando backup e scheduler...")

    test_backup_script_exists()
    test_backup_script_content()
    test_scheduler_import()
    test_scheduler_status()
    test_backup_command()
    test_docker_compose_backup_volume()
    test_requirements_apscheduler()
    test_backup_directory()
    test_environment_variables()

    print("🎉 Todos os testes de backup e scheduler passaram!")
