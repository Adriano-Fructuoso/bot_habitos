"""
Handlers do bot organizados por funcionalidade
"""

from .base import safe_handler, track_command
from .commands import (
    start_command,
    habit_command,
    stats_command,
    dashboard_command,
    rating_command,
    weekly_command,
    habits_command,
)
from .crud import (
    add_habit_command,
    edit_habit_command,
    delete_habit_command,
    set_reminder_command,
)
from .callbacks import (
    complete_habit_callback,
    rating_callback,
    show_progress_callback,
    edit_habit_callback,
    delete_habit_callback,
    set_reminder_callback,
    # Novos handlers para tabela de hábitos
    toggle_complete_habit_callback,
    confirm_selection_callback,
    clear_selection_callback,
    edit_habit_full_callback,
)
from .menu import (
    menu_command,
    menu_callback,
)
from .text import (
    handle_text_message,
    handle_voice_message,
)
from .conversation import (
    habit_creation_handler,
)

__all__ = [
    # Base
    "safe_handler",
    "track_command",
    # Commands
    "start_command",
    "habit_command",
    "stats_command",
    "dashboard_command",
    "rating_command",
    "weekly_command",
    "habits_command",
    "add_habit_command",
    "edit_habit_command",
    "delete_habit_command",
    "set_reminder_command",
    # Callbacks
    "complete_habit_callback",
    "rating_callback",
    "show_progress_callback",
    "edit_habit_callback",
    "delete_habit_callback",
    "set_reminder_callback",
    # Menu
    "menu_command",
    "menu_callback",
    # Text handlers
    "handle_text_message",
    "handle_voice_message",
    # Conversation handlers
    "habit_creation_handler",
]
