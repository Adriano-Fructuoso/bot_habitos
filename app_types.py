"""
Tipos e enums para o HabitBot
"""

from typing import TypedDict, Protocol, Literal, Union, Optional
from enum import Enum
from datetime import datetime


class CallbackAction(str, Enum):
    """Ações disponíveis para callbacks"""
    COMPLETE_HABIT = "complete_habit"
    EDIT_HABIT = "edit_habit"
    DELETE_HABIT = "delete_habit"
    SET_REMINDER = "set_reminder"
    RATE_DAY = "rate_day"
    SHOW_PROGRESS = "show_progress"
    RENAME_HABIT = "rename_habit"
    CHANGE_XP = "change_xp"
    TOGGLE_HABIT = "toggle_habit"
    CONFIRM_DELETE = "confirm_delete"
    REMINDER_TIME = "reminder_time"
    REMINDER_DAYS = "reminder_days"
    REMOVE_REMINDER = "remove_reminder"
    BACK_TO_EDIT = "back_to_edit"
    BACK_TO_REMINDER = "back_to_reminder"
    CANCEL_DELETE = "cancel_delete"


class HabitDifficulty(str, Enum):
    """Dificuldade dos hábitos"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class HabitCategory(str, Enum):
    """Categorias de hábitos"""
    SAUDE = "saude"
    MENTAL = "mental"
    DESENVOLVIMENTO = "desenvolvimento"
    PERSONAL = "personal"


class CallbackData(TypedDict):
    """Estrutura de callback_data versionado"""
    version: str
    action: str
    habit_id: int
    extra: str


class HabitData(TypedDict):
    """Dados de um hábito"""
    id: int
    name: str
    xp_reward: int
    is_active: bool
    current_streak: int
    longest_streak: int
    total_completions: int
    created_at: datetime


class ReminderData(TypedDict):
    """Dados de um lembrete"""
    id: int
    habit_id: int
    time: str  # HH:MM
    timezone: str
    days: str  # "1,2,3,4,5"
    enabled: bool


class UserStats(TypedDict):
    """Estatísticas do usuário"""
    total_xp: int
    current_level: int
    current_streak: int
    longest_streak: int
    days_since_start: int
    habits_completed_today: int
    total_habits: int


class DailyProgress(TypedDict):
    """Progresso diário"""
    completed: int
    goal: int
    progress: float
    habits: list[HabitData]


class RepositoryProtocol(Protocol):
    """Protocolo para repositórios"""
    
    def get_habits(self, user_id: int, active_only: bool = True) -> list[HabitData]:
        """Busca hábitos do usuário"""
        ...
    
    def create_habit(self, user_id: int, name: str, xp_reward: int = 10) -> HabitData:
        """Cria um novo hábito"""
        ...
    
    def update_habit(self, habit_id: int, user_id: int, **kwargs) -> Optional[HabitData]:
        """Atualiza um hábito"""
        ...
    
    def delete_habit(self, habit_id: int, user_id: int) -> bool:
        """Deleta um hábito"""
        ...
    
    def toggle_habit(self, habit_id: int, user_id: int) -> Optional[HabitData]:
        """Ativa/desativa um hábito"""
        ...


class SchedulerProtocol(Protocol):
    """Protocolo para scheduler"""
    
    def schedule_reminder(self, reminder_id: int, user_id: int, habit_id: int, 
                         habit_name: str, time: str, days: str) -> None:
        """Agenda um lembrete"""
        ...
    
    def remove_reminder(self, reminder_id: int) -> None:
        """Remove um lembrete"""
        ...
    
    def load_all_reminders(self) -> None:
        """Carrega todos os lembretes no startup"""
        ...


# Constantes
CALLBACK_VERSION = "v1"
MAX_HABIT_NAME_LENGTH = 200
MIN_XP_REWARD = 1
MAX_XP_REWARD = 100
MAX_HABITS_PER_USER = 20
RATE_LIMIT_SECONDS = 1
