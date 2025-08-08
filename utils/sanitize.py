import logging
import re

logger = logging.getLogger(__name__)


def clamp_len(s: str, max_len: int = 256) -> str:
    """
    Limita o tamanho de uma string.

    Args:
        s: String de entrada
        max_len: Tamanho máximo permitido

    Returns:
        String truncada se necessário
    """
    if not s:
        return s

    if len(s) <= max_len:
        return s

    logger.warning(f"String truncada: {len(s)} > {max_len} caracteres")
    return s[:max_len]


# Regex para escapar caracteres especiais do MarkdownV2
_TELEGRAM_ESCAPE = re.compile(r"([_*[\]()~`>#+\-=|{}.!])")


def escape_md(s: str) -> str:
    """
    Escapa caracteres especiais do MarkdownV2 do Telegram.

    Args:
        s: String de entrada

    Returns:
        String com caracteres escapados
    """
    if not s:
        return s

    return _TELEGRAM_ESCAPE.sub(r"\\\1", s)


def is_int(s: str) -> bool:
    """
    Verifica se uma string representa um número inteiro.

    Args:
        s: String de entrada

    Returns:
        True se for um número inteiro válido
    """
    if not s:
        return False

    return s.isdigit()


def sanitize_username(username: str) -> str:
    """
    Sanitiza um username do Telegram.

    Args:
        username: Username de entrada

    Returns:
        Username sanitizado
    """
    if not username:
        return ""

    # Remove caracteres inválidos e limita tamanho
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "", username)
    return clamp_len(sanitized, 32)


def sanitize_habit_name(name: str) -> str:
    """
    Sanitiza o nome de um hábito.

    Args:
        name: Nome do hábito

    Returns:
        Nome sanitizado
    """
    if not name:
        return "Hábito sem nome"

    # Remove caracteres de controle e limita tamanho
    sanitized = re.sub(r"[\x00-\x1f\x7f]", "", name)
    return clamp_len(sanitized.strip(), 100)


def validate_habit_id(habit_id: str) -> bool:
    """
    Valida se um ID de hábito é válido.

    Args:
        habit_id: ID do hábito como string

    Returns:
        True se for um ID válido
    """
    if not habit_id:
        return False

    # Deve ser um número inteiro positivo
    if not is_int(habit_id):
        return False

    # Deve estar em um range razoável
    try:
        id_num = int(habit_id)
        return 1 <= id_num <= 999999
    except ValueError:
        return False


def sanitize_message_text(text: str, max_len: int = 4096) -> str:
    """
    Sanitiza texto de mensagem para o Telegram.

    Args:
        text: Texto de entrada
        max_len: Tamanho máximo (padrão Telegram: 4096)

    Returns:
        Texto sanitizado
    """
    if not text:
        return ""

    # Remove caracteres de controle
    sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Limita tamanho
    return clamp_len(sanitized, max_len)
