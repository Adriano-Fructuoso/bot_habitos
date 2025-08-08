"""
Utilitários para observabilidade e métricas
"""

import logging
import time
from datetime import datetime
from functools import wraps
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Métricas básicas em memória (em produção, usar Prometheus/DataDog)
_metrics = {
    "commands_executed": 0,
    "errors_total": 0,
    "db_queries": 0,
    "db_latency_ms": [],
    "active_users": 0,
    "habits_completed": 0,
}

def increment_metric(metric_name: str, value: int = 1):
    """Incrementa uma métrica"""
    if metric_name in _metrics:
        if isinstance(_metrics[metric_name], list):
            _metrics[metric_name].append(value)
        else:
            _metrics[metric_name] += value
    else:
        _metrics[metric_name] = value

def get_metrics() -> dict[str, Any]:
    """Retorna todas as métricas"""
    metrics = _metrics.copy()

    # Calcular médias para latências
    if metrics["db_latency_ms"]:
        metrics["db_latency_avg_ms"] = sum(metrics["db_latency_ms"]) / len(metrics["db_latency_ms"])
        metrics["db_latency_max_ms"] = max(metrics["db_latency_ms"])
        metrics["db_latency_min_ms"] = min(metrics["db_latency_ms"])
    else:
        metrics["db_latency_avg_ms"] = 0
        metrics["db_latency_max_ms"] = 0
        metrics["db_latency_min_ms"] = 0

    return metrics

def log_metric(metric_name: str, value: Any = 1, tags: Optional[dict[str, str]] = None):
    """Loga uma métrica estruturada"""
    log_data = {
        "metric": metric_name,
        "value": value,
        "timestamp": datetime.now().isoformat(),
    }

    if tags:
        log_data["tags"] = tags

    logger.info(f"METRIC: {log_data}")

def track_db_query(func):
    """Decorator para rastrear queries do banco"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            latency_ms = (time.time() - start_time) * 1000
            increment_metric("db_queries")
            increment_metric("db_latency_ms", latency_ms)
            log_metric("db_query_success", latency_ms, {"function": func.__name__})
            return result
        except Exception as e:
            increment_metric("errors_total")
            log_metric("db_query_error", 0, {
                "function": func.__name__,
                "error": str(e)
            })
            raise
    return wrapper

def track_command(command_name: str):
    """Decorator para rastrear comandos executados"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                increment_metric("commands_executed")
                log_metric("command_executed", execution_time, {
                    "command": command_name,
                    "status": "success"
                })
                return result
            except Exception as e:
                increment_metric("errors_total")
                log_metric("command_error", 0, {
                    "command": command_name,
                    "error": str(e),
                    "status": "error"
                })
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                increment_metric("commands_executed")
                log_metric("command_executed", execution_time, {
                    "command": command_name,
                    "status": "success"
                })
                return result
            except Exception as e:
                increment_metric("errors_total")
                log_metric("command_error", 0, {
                    "command": command_name,
                    "error": str(e),
                    "status": "error"
                })
                raise
        
        # Retorna o wrapper apropriado baseado no tipo da função
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    return decorator

def log_event(level: str, message: str, **kwargs):
    """Loga um evento estruturado"""
    log_data = {
        "level": level,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        **kwargs
    }
    
    if level.upper() == "ERROR":
        logger.error(f"EVENT: {log_data}")
    elif level.upper() == "WARNING":
        logger.warning(f"EVENT: {log_data}")
    else:
        logger.info(f"EVENT: {log_data}")


def log_user_activity(user_id: int, action: str, details: Optional[dict[str, Any]] = None):
    """Loga atividade do usuário"""
    log_data = {
        "user_id": user_id,
        "action": action,
        "timestamp": datetime.now().isoformat(),
    }

    if details:
        log_data["details"] = details

    logger.info(f"USER_ACTIVITY: {log_data}")

def log_habit_completion(user_id: int, habit_id: int, habit_name: str, xp_earned: int):
    """Loga conclusão de hábito"""
    increment_metric("habits_completed")
    log_user_activity(user_id, "habit_completed", {
        "habit_id": habit_id,
        "habit_name": habit_name,
        "xp_earned": xp_earned
    })

def log_error(error: Exception, context: Optional[dict[str, Any]] = None):
    """Loga erro com contexto"""
    increment_metric("errors_total")

    error_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": datetime.now().isoformat(),
    }

    if context:
        error_data["context"] = context

    logger.error(f"ERROR: {error_data}")

def get_health_metrics() -> dict[str, Any]:
    """Retorna métricas para health check"""
    return {
        "uptime_seconds": int(time.time() - _metrics.get("start_time", time.time())),
        "commands_executed": _metrics.get("commands_executed", 0),
        "errors_total": _metrics.get("errors_total", 0),
        "active_users": _metrics.get("active_users", 0),
        "habits_completed": _metrics.get("habits_completed", 0),
        "db_queries": _metrics.get("db_queries", 0),
    }

# Inicializar tempo de início
_metrics["start_time"] = time.time()
