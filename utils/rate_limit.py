import logging
import time
from collections import defaultdict

logger = logging.getLogger(__name__)

# Memória em cache; em produção você pode migrar para Redis
_LAST = defaultdict(float)


def rate_limited(key: str, window_s: int) -> bool:
    """
    Verifica se uma ação está dentro do limite de taxa.

    Args:
        key: Chave única para identificar a ação (ex: "start:123456")
        window_s: Janela de tempo em segundos

    Returns:
        True se estiver limitado (muito recente), False se permitido
    """
    now = time.time()
    last_time = _LAST.get(key, 0)

    if now - last_time < window_s:
        logger.warning(f"Rate limit atingido para {key} (janela: {window_s}s)")
        return True

    _LAST[key] = now
    return False


def get_rate_limit_info(key: str) -> dict:
    """
    Retorna informações sobre o rate limit de uma chave.
    """
    now = time.time()
    last_time = _LAST.get(key, 0)
    time_since_last = now - last_time

    return {
        "key": key,
        "last_request": last_time,
        "time_since_last": time_since_last,
        "is_limited": time_since_last < 1,  # Assumindo janela de 1s para info
    }


def clear_rate_limit(key: str = None):
    """
    Limpa o cache de rate limit.

    Args:
        key: Chave específica para limpar, ou None para limpar tudo
    """
    if key:
        _LAST.pop(key, None)
        logger.info(f"Rate limit limpo para {key}")
    else:
        _LAST.clear()
        logger.info("Rate limit cache limpo completamente")
