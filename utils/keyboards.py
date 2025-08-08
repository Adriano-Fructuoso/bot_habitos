"""
Sistema de botões inline para melhorar a UX do bot
"""

from typing import List, Dict, Any, Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from app_types import CallbackAction


def create_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Cria o menu principal com botões fixos"""
    keyboard = [
        [
            InlineKeyboardButton("📝 Criar Hábito", callback_data="menu_create_habit"),
            InlineKeyboardButton("✏️ Editar Hábitos", callback_data="menu_edit_habits")
        ],
        [
            InlineKeyboardButton("📋 Hábitos", callback_data="menu_complete_today"),
            InlineKeyboardButton("📊 Ver Progresso", callback_data="menu_show_stats")
        ],
        [
            InlineKeyboardButton("📅 Resumo Semanal", callback_data="menu_weekly_summary"),
            InlineKeyboardButton("⭐ Avaliar Dia", callback_data="menu_rate_day")
        ],
        [
            InlineKeyboardButton("⏰ Lembretes", callback_data="menu_reminders"),
            InlineKeyboardButton("❓ Ajuda", callback_data="menu_help")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_habit_form_keyboard(step: str = "name") -> InlineKeyboardMarkup:
    """Cria botões para formulário de criação de hábito"""
    if step == "name":
        keyboard = [
            [InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="menu_main")],
            [InlineKeyboardButton("❌ Cancelar", callback_data="form_cancel")]
        ]
    elif step == "category":
        keyboard = [
            [
                InlineKeyboardButton("🏃 Saúde", callback_data="form_category_saude"),
                InlineKeyboardButton("🧠 Mental", callback_data="form_category_mental")
            ],
            [
                InlineKeyboardButton("📚 Desenvolvimento", callback_data="form_category_desenvolvimento"),
                InlineKeyboardButton("👤 Pessoal", callback_data="form_category_pessoal")
            ],
            [InlineKeyboardButton("🔙 Voltar", callback_data="form_back_name")],
            [InlineKeyboardButton("❌ Cancelar", callback_data="form_cancel")]
        ]
    elif step == "difficulty":
        keyboard = [
            [
                InlineKeyboardButton("🟢 Fácil", callback_data="form_difficulty_easy"),
                InlineKeyboardButton("🟡 Médio", callback_data="form_difficulty_medium")
            ],
            [InlineKeyboardButton("🔴 Difícil", callback_data="form_difficulty_hard")],
            [InlineKeyboardButton("🔙 Voltar", callback_data="form_back_category")],
            [InlineKeyboardButton("❌ Cancelar", callback_data="form_cancel")]
        ]
    elif step == "time":
        keyboard = [
            [
                InlineKeyboardButton("⏰ 5 min", callback_data="form_time_5"),
                InlineKeyboardButton("⏰ 10 min", callback_data="form_time_10"),
                InlineKeyboardButton("⏰ 15 min", callback_data="form_time_15")
            ],
            [
                InlineKeyboardButton("⏰ 30 min", callback_data="form_time_30"),
                InlineKeyboardButton("⏰ 1 hora", callback_data="form_time_60")
            ],
            [InlineKeyboardButton("🔙 Voltar", callback_data="form_back_difficulty")],
            [InlineKeyboardButton("❌ Cancelar", callback_data="form_cancel")]
        ]
    elif step == "confirm":
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirmar", callback_data="form_confirm"),
                InlineKeyboardButton("✏️ Editar", callback_data="form_edit")
            ],
            [InlineKeyboardButton("🔙 Voltar", callback_data="form_back_time")],
            [InlineKeyboardButton("❌ Cancelar", callback_data="form_cancel")]
        ]
    
    return InlineKeyboardMarkup(keyboard)


def create_habit_list_keyboard(habits: List[Dict[str, Any]], action: CallbackAction) -> InlineKeyboardMarkup:
    """Cria lista de hábitos com botões de ação"""
    keyboard = []
    
    for habit in habits:
        status = "✅" if habit.get("is_active", True) else "❌"
        button_text = f"{status} {habit['name']} (+{habit['xp_reward']} XP)"
        callback_data = f"{action.value}_{habit['id']}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
    
    # Botões de navegação
    keyboard.append([
        InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="menu_main"),
        InlineKeyboardButton("➕ Criar Novo", callback_data="menu_create_habit")
    ])
    
    return InlineKeyboardMarkup(keyboard)


def create_habits_table_keyboard(habits: List[Dict[str, Any]], selected_habits: List[int] = None) -> InlineKeyboardMarkup:
    """Cria tabela de hábitos para completar hoje"""
    if selected_habits is None:
        selected_habits = []
    
    keyboard = []
    
    # Linhas de hábitos (formato compacto)
    for habit in habits:
        is_selected = habit['id'] in selected_habits
        check_mark = "✅" if is_selected else "⭕"
        
        # Verifica se time_minutes existe e é válido
        time_min = habit.get('time_minutes')
        if time_min is None or time_min == 0:
            time_min = 30  # Valor padrão
        
        xp = habit['xp_reward']
        
        # Nome truncado para caber melhor
        name = habit['name'][:12] + "..." if len(habit['name']) > 12 else habit['name']
        
        # Botão principal com informações compactas
        main_button = f"{check_mark} {name} ({time_min}min • {xp}XP)"
        
        # Verifica se o texto não é muito longo
        if len(main_button) > 64:  # Limite do Telegram
            main_button = f"{check_mark} {name[:8]}... ({time_min}min • {xp}XP)"
        
        keyboard.append([
            InlineKeyboardButton(main_button, callback_data=f"toggle_complete_{habit['id']}")
        ])
    
    # Botões de ação
    if selected_habits:
        keyboard.append([
            InlineKeyboardButton("✅ Confirmar Seleção", callback_data="confirm_selection"),
            InlineKeyboardButton("🔄 Limpar Seleção", callback_data="clear_selection")
        ])
    
    keyboard.append([
        InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="menu_main"),
        InlineKeyboardButton("📊 Ver Progresso", callback_data="menu_show_stats")
    ])
    
    return InlineKeyboardMarkup(keyboard)


def create_habit_edit_list_keyboard(habits: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Cria lista de hábitos para edição completa"""
    keyboard = []
    
    for habit in habits:
        status = "✅" if habit.get("is_active", True) else "❌"
        streak = habit.get("current_streak", 0)
        button_text = f"{status} {habit['name']} (🔥{streak})"
        callback_data = f"edit_habit_{habit['id']}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
    
    # Botões de navegação
    keyboard.append([
        InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="menu_main"),
        InlineKeyboardButton("➕ Criar Novo", callback_data="menu_create_habit")
    ])
    
    return InlineKeyboardMarkup(keyboard)


def create_habit_edit_keyboard(habit_id: int) -> InlineKeyboardMarkup:
    """Cria botões para editar um hábito específico"""
    keyboard = [
        [
            InlineKeyboardButton("✏️ Renomear", callback_data=f"edit_name_{habit_id}"),
            InlineKeyboardButton("🎯 XP", callback_data=f"edit_xp_{habit_id}")
        ],
        [
            InlineKeyboardButton("📝 Descrição", callback_data=f"edit_desc_{habit_id}"),
            InlineKeyboardButton("📂 Categoria", callback_data=f"edit_category_{habit_id}")
        ],
        [
            InlineKeyboardButton("⏰ Tempo", callback_data=f"edit_time_{habit_id}"),
            InlineKeyboardButton("🔄 Dificuldade", callback_data=f"edit_difficulty_{habit_id}")
        ],
        [
            InlineKeyboardButton("📅 Dias da Semana", callback_data=f"edit_days_{habit_id}"),
            InlineKeyboardButton("✅ Ativar/Desativar", callback_data=f"edit_toggle_{habit_id}")
        ],
        [
            InlineKeyboardButton("🗑️ Deletar", callback_data=f"edit_delete_{habit_id}"),
            InlineKeyboardButton("⏰ Lembretes", callback_data=f"edit_reminder_{habit_id}")
        ],
        [InlineKeyboardButton("🔙 Voltar", callback_data="menu_edit_habits")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_reminder_config_keyboard(habit_id: int) -> InlineKeyboardMarkup:
    """Cria botões para configurar lembretes"""
    keyboard = [
        [
            InlineKeyboardButton("⏰ 08:00", callback_data=f"reminder_time_{habit_id}_08:00"),
            InlineKeyboardButton("⏰ 12:00", callback_data=f"reminder_time_{habit_id}_12:00")
        ],
        [
            InlineKeyboardButton("⏰ 18:00", callback_data=f"reminder_time_{habit_id}_18:00"),
            InlineKeyboardButton("⏰ 21:00", callback_data=f"reminder_time_{habit_id}_21:00")
        ],
        [InlineKeyboardButton("📅 Dias da Semana", callback_data=f"reminder_days_{habit_id}")],
        [InlineKeyboardButton("❌ Remover Lembrete", callback_data=f"reminder_remove_{habit_id}")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="menu_reminders")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_days_of_week_keyboard(habit_id: int, selected_days: List[int] = None) -> InlineKeyboardMarkup:
    """Cria botões para selecionar dias da semana"""
    if selected_days is None:
        selected_days = []
    
    days = [
        ("Seg", 1), ("Ter", 2), ("Qua", 3), ("Qui", 4),
        ("Sex", 5), ("Sáb", 6), ("Dom", 7)
    ]
    
    keyboard = []
    row = []
    
    for day_name, day_num in days:
        check = "✅" if day_num in selected_days else "⭕"
        button_text = f"{check} {day_name}"
        callback_data = f"reminder_day_{habit_id}_{day_num}"
        row.append(InlineKeyboardButton(button_text, callback_data=callback_data))
        
        if len(row) == 4:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    keyboard.append([
        InlineKeyboardButton("✅ Confirmar", callback_data=f"reminder_confirm_{habit_id}"),
        InlineKeyboardButton("🔙 Voltar", callback_data=f"reminder_time_{habit_id}")
    ])
    
    return InlineKeyboardMarkup(keyboard)


def create_rating_keyboard() -> InlineKeyboardMarkup:
    """Cria botões para avaliação diária"""
    keyboard = []
    
    # Humor (1-10)
    mood_row = []
    for i in range(1, 11):
        mood_row.append(InlineKeyboardButton(f"{i}", callback_data=f"rate_mood_{i}"))
        if len(mood_row) == 5:
            keyboard.append(mood_row)
            mood_row = []
    if mood_row:
        keyboard.append(mood_row)
    
    # Energia (1-10)
    energy_row = []
    for i in range(1, 11):
        energy_row.append(InlineKeyboardButton(f"{i}", callback_data=f"rate_energy_{i}"))
        if len(energy_row) == 5:
            keyboard.append(energy_row)
            energy_row = []
    if energy_row:
        keyboard.append(energy_row)
    
    # Removido craving - não é mais necessário
    
    keyboard.append([InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="menu_main")])
    
    return InlineKeyboardMarkup(keyboard)


def create_progress_keyboard() -> InlineKeyboardMarkup:
    """Cria botões para visualizar progresso"""
    keyboard = [
        [
            InlineKeyboardButton("📊 Hoje", callback_data="progress_today"),
            InlineKeyboardButton("📅 Esta Semana", callback_data="progress_week")
        ],
        [
            InlineKeyboardButton("📈 Este Mês", callback_data="progress_month"),
            InlineKeyboardButton("🏆 Conquistas", callback_data="progress_achievements")
        ],
        [
            InlineKeyboardButton("🔥 Streaks", callback_data="progress_streaks"),
            InlineKeyboardButton("📋 Todos os Hábitos", callback_data="progress_all_habits")
        ],
        [InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="menu_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_help_keyboard() -> InlineKeyboardMarkup:
    """Cria botões para ajuda"""
    keyboard = [
        [
            InlineKeyboardButton("🎯 Como Funciona", callback_data="help_how_it_works"),
            InlineKeyboardButton("📝 Comandos", callback_data="help_commands")
        ],
        [
            InlineKeyboardButton("🏆 Conquistas", callback_data="help_achievements"),
            InlineKeyboardButton("🔥 Streaks", callback_data="help_streaks")
        ],
        [
            InlineKeyboardButton("⚙️ Configurações", callback_data="help_settings"),
            InlineKeyboardButton("❓ FAQ", callback_data="help_faq")
        ],
        [InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="menu_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_navigation_keyboard() -> InlineKeyboardMarkup:
    """Cria botões de navegação padrão"""
    keyboard = [
        [
            InlineKeyboardButton("🔙 Voltar", callback_data="menu_main"),
            InlineKeyboardButton("🏠 Menu Principal", callback_data="menu_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_quick_actions_keyboard() -> InlineKeyboardMarkup:
    """Cria botões de ações rápidas"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Completar", callback_data="quick_complete"),
            InlineKeyboardButton("📊 Stats", callback_data="quick_stats")
        ],
        [
            InlineKeyboardButton("📝 Novo Hábito", callback_data="quick_new_habit"),
            InlineKeyboardButton("⏰ Lembretes", callback_data="quick_reminders")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
