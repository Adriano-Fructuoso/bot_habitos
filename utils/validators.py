"""
Validações centralizadas para o HabitBot
"""

import re
from typing import Any

from app_types import (
    MAX_HABIT_NAME_LENGTH,
    MAX_XP_REWARD,
    MIN_XP_REWARD,
)


class ValidationError(Exception):
    """Erro de validação"""
    pass


def validate_habit_name(name: str) -> str:
    """Valida nome do hábito"""
    if not name or not name.strip():
        raise ValidationError("Nome do hábito não pode estar vazio")

    name = name.strip()
    if len(name) > MAX_HABIT_NAME_LENGTH:
        raise ValidationError(f"Nome muito longo (máx {MAX_HABIT_NAME_LENGTH} caracteres)")

    if len(name) < 2:
        raise ValidationError("Nome muito curto (mín 2 caracteres)")

    return name


def validate_xp_reward(xp: int) -> int:
    """Valida XP do hábito"""
    if not isinstance(xp, int):
        raise ValidationError("XP deve ser um número inteiro")

    if xp < MIN_XP_REWARD:
        raise ValidationError(f"XP mínimo é {MIN_XP_REWARD}")

    if xp > MAX_XP_REWARD:
        raise ValidationError(f"XP máximo é {MAX_XP_REWARD}")

    return xp


def validate_time_format(time_str: str) -> str:
    """Valida formato de hora HH:MM"""
    if not re.match(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$', time_str):
        raise ValidationError("Formato de hora inválido. Use HH:MM (ex: 08:30)")

    return time_str


def validate_days_format(days_str: str) -> str:
    """Valida formato de dias da semana"""
    if not re.match(r'^[1-7](,[1-7])*$', days_str):
        raise ValidationError("Formato de dias inválido. Use 1,2,3,4,5 (1=segunda, 7=domingo)")

    days = [int(d) for d in days_str.split(',')]
    if len(set(days)) != len(days):
        raise ValidationError("Dias duplicados não são permitidos")

    return days_str


def validate_habit_id(habit_id: Any) -> int:
    """Valida ID do hábito"""
    try:
        habit_id = int(habit_id)
        if habit_id <= 0:
            raise ValidationError("ID do hábito deve ser positivo")
        return habit_id
    except (ValueError, TypeError):
        raise ValidationError("ID do hábito deve ser um número inteiro")


def validate_user_id(user_id: Any) -> int:
    """Valida ID do usuário"""
    try:
        user_id = int(user_id)
        if user_id <= 0:
            raise ValidationError("ID do usuário deve ser positivo")
        return user_id
    except (ValueError, TypeError):
        raise ValidationError("ID do usuário deve ser um número inteiro")


def validate_callback_data(callback_data: str) -> dict:
    """Valida e parseia callback_data versionado"""
    if not callback_data:
        raise ValidationError("Callback data não pode estar vazio")

    parts = callback_data.split(':')
    if len(parts) < 3:
        raise ValidationError("Callback data inválido")

    version, action, habit_id = parts[0], parts[1], parts[2]
    extra = parts[3] if len(parts) > 3 else ""

    if version != "v1":
        raise ValidationError("Versão de callback não suportada")

    try:
        habit_id = validate_habit_id(habit_id)
    except ValidationError:
        raise ValidationError("ID do hábito inválido no callback")

    return {
        "version": version,
        "action": action,
        "habit_id": habit_id,
        "extra": extra
    }


def sanitize_text(text: str, max_length: int = 1000) -> str:
    """Sanitiza texto removendo caracteres perigosos"""
    if not text:
        return ""

    # Remove caracteres de controle
    text = re.sub(r'[\x00-\x1f\x7f]', '', text)

    # Limita tamanho
    if len(text) > max_length:
        text = text[:max_length]

    return text.strip()
