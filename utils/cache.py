"""
Sistema de cache para melhorar performance
"""

import time
from typing import Any, Optional, Dict, List
from functools import wraps
from datetime import datetime, timedelta
from utils.logging_config import get_logger

logger = get_logger(__name__)


class Cache:
    """Cache simples em memória com TTL"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Busca valor no cache"""
        if key not in self._cache:
            self._stats["misses"] += 1
            return None
        
        item = self._cache[key]
        
        # Verifica se expirou
        if time.time() > item["expires_at"]:
            del self._cache[key]
            self._stats["misses"] += 1
            return None
        
        self._stats["hits"] += 1
        return item["value"]
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Define valor no cache com TTL"""
        self._cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl_seconds,
            "created_at": time.time()
        }
        self._stats["sets"] += 1
    
    def delete(self, key: str) -> None:
        """Remove valor do cache"""
        if key in self._cache:
            del self._cache[key]
            self._stats["deletes"] += 1
    
    def clear(self) -> None:
        """Limpa todo o cache"""
        self._cache.clear()
        logger.info("Cache limpo")
    
    def cleanup_expired(self) -> int:
        """Remove itens expirados e retorna quantidade removida"""
        now = time.time()
        expired_keys = [
            key for key, item in self._cache.items()
            if now > item["expires_at"]
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.info(f"Removidos {len(expired_keys)} itens expirados do cache")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self._stats,
            "total_requests": total_requests,
            "hit_rate": hit_rate,
            "current_size": len(self._cache),
            "keys": list(self._cache.keys())
        }


# Cache global
cache = Cache()


def cached(ttl_seconds: int = 300, key_prefix: str = ""):
    """Decorator para cachear resultados de funções"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gera chave única baseada na função e argumentos
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Tenta buscar do cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Executa função e cacheia resultado
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl_seconds)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(pattern: str) -> int:
    """Invalida cache baseado em padrão de chave"""
    keys_to_delete = [key for key in cache._cache.keys() if pattern in key]
    
    for key in keys_to_delete:
        cache.delete(key)
    
    if keys_to_delete:
        logger.info(f"Invalidados {len(keys_to_delete)} itens do cache com padrão '{pattern}'")
    
    return len(keys_to_delete)


# Funções específicas para cache de hábitos
def get_user_habits_cache_key(user_id: int, active_only: bool = True) -> str:
    """Gera chave de cache para hábitos do usuário"""
    return f"user_habits:{user_id}:{'active' if active_only else 'all'}"


def get_user_stats_cache_key(user_id: int) -> str:
    """Gera chave de cache para estatísticas do usuário"""
    return f"user_stats:{user_id}"


def get_daily_progress_cache_key(user_id: int) -> str:
    """Gera chave de cache para progresso diário"""
    today = datetime.now().strftime("%Y-%m-%d")
    return f"daily_progress:{user_id}:{today}"


def invalidate_user_cache(user_id: int) -> None:
    """Invalida todo cache relacionado ao usuário"""
    patterns = [
        f"user_habits:{user_id}",
        f"user_stats:{user_id}",
        f"daily_progress:{user_id}"
    ]
    
    for pattern in patterns:
        invalidate_cache(pattern)


# Limpeza automática a cada 5 minutos
def start_cache_cleanup():
    """Inicia limpeza automática do cache"""
    import threading
    import time
    
    def cleanup_loop():
        while True:
            try:
                cache.cleanup_expired()
                time.sleep(300)  # 5 minutos
            except Exception as e:
                logger.error(f"Erro na limpeza do cache: {e}")
                time.sleep(60)  # 1 minuto em caso de erro
    
    cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
    cleanup_thread.start()
    logger.info("Limpeza automática do cache iniciada")

