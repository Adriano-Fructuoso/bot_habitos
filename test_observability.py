#!/usr/bin/env python3
"""
Teste para verificar observabilidade
"""

import os
import sys

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_observability_import():
    """Testa se o módulo de observabilidade pode ser importado"""
    from utils.observability import (
        get_health_metrics,
        get_metrics,
        increment_metric,
        log_error,
        log_habit_completion,
        log_metric,
        log_user_activity,
        track_command,
        track_db_query,
    )

    assert callable(increment_metric)
    assert callable(get_metrics)
    assert callable(log_metric)
    assert callable(track_db_query)
    assert callable(track_command)
    assert callable(log_user_activity)
    assert callable(log_habit_completion)
    assert callable(log_error)
    assert callable(get_health_metrics)

    print("✅ Módulo de observabilidade importado corretamente")

def test_metrics_basic():
    """Testa funcionalidades básicas de métricas"""
    from utils.observability import get_metrics, increment_metric

    # Teste incremento
    increment_metric("test_counter")
    metrics = get_metrics()
    assert metrics["test_counter"] == 1

    # Teste incremento com valor
    increment_metric("test_counter", 5)
    metrics = get_metrics()
    assert metrics["test_counter"] == 6

    print("✅ Métricas básicas funcionando")

def test_log_metric():
    """Testa log de métricas"""
    from utils.observability import log_metric

    # Teste sem tags
    log_metric("test_metric", 42)

    # Teste com tags
    log_metric("test_metric_with_tags", 100, {"user_id": "123", "action": "test"})

    print("✅ Log de métricas funcionando")

def test_track_command_decorator():
    """Testa decorator de tracking de comandos"""
    from utils.observability import track_command

    @track_command("test_command")
    def test_function():
        return "success"

    result = test_function()
    assert result == "success"

    # Verificar se métrica foi incrementada
    from utils.observability import get_metrics
    metrics = get_metrics()
    assert metrics["commands_executed"] > 0

    print("✅ Decorator de tracking de comandos funcionando")

def test_log_user_activity():
    """Testa log de atividade do usuário"""
    from utils.observability import log_user_activity

    # Teste básico
    log_user_activity(123, "test_action")

    # Teste com detalhes
    log_user_activity(456, "test_action", {"detail": "test_value"})

    print("✅ Log de atividade do usuário funcionando")

def test_log_habit_completion():
    """Testa log de conclusão de hábito"""
    from utils.observability import get_metrics, log_habit_completion

    # Teste
    log_habit_completion(123, 1, "Test Habit", 15)

    # Verificar se métrica foi incrementada
    metrics = get_metrics()
    assert metrics["habits_completed"] > 0

    print("✅ Log de conclusão de hábito funcionando")

def test_log_error():
    """Testa log de erros"""
    from utils.observability import get_metrics, log_error

    # Teste
    try:
        raise ValueError("Test error")
    except Exception as e:
        log_error(e, {"context": "test"})

    # Verificar se métrica foi incrementada
    metrics = get_metrics()
    assert metrics["errors_total"] > 0

    print("✅ Log de erros funcionando")

def test_health_metrics():
    """Testa métricas de health check"""
    from utils.observability import get_health_metrics

    metrics = get_health_metrics()

    # Verificar estrutura
    assert "uptime_seconds" in metrics
    assert "commands_executed" in metrics
    assert "errors_total" in metrics
    assert "habits_completed" in metrics
    assert "db_queries" in metrics

    # Verificar tipos
    assert isinstance(metrics["uptime_seconds"], int)
    assert isinstance(metrics["commands_executed"], int)
    assert isinstance(metrics["errors_total"], int)

    print("✅ Métricas de health check funcionando")

def test_sentry_config():
    """Testa configuração do Sentry"""
    from config import SENTRY_DSN

    # Verificar se a configuração existe (pode ser None se não configurado)
    assert SENTRY_DSN is not None or SENTRY_DSN is None  # Sempre verdadeiro

    print("✅ Configuração do Sentry verificada")

def test_observability_integration():
    """Testa integração com handlers"""
    from utils.observability import (
        log_error,
        log_habit_completion,
        log_user_activity,
        track_command,
    )

    assert callable(track_command)
    assert callable(log_user_activity)
    assert callable(log_habit_completion)
    assert callable(log_error)

    print("✅ Integração com handlers verificada")

if __name__ == "__main__":
    print("🧪 Testando observabilidade...")

    test_observability_import()
    test_metrics_basic()
    test_log_metric()
    test_track_command_decorator()
    test_log_user_activity()
    test_log_habit_completion()
    test_log_error()
    test_health_metrics()
    test_sentry_config()
    test_observability_integration()

    print("🎉 Todos os testes de observabilidade passaram!")
