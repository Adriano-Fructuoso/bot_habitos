"""
Helpers para construção de teclados inline
"""


from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from app_types import CALLBACK_VERSION, CallbackAction


def build_callback_data(action: CallbackAction, habit_id: int, extra: str = "") -> str:
    """Constrói callback_data versionado"""
    return f"{CALLBACK_VERSION}:{action.value}:{habit_id}:{extra}"


def create_habit_list_keyboard(habits: list[dict], action: CallbackAction,
                              show_status: bool = True) -> InlineKeyboardMarkup:
    """Cria teclado com lista de hábitos"""
    keyboard = []

    for habit in habits:
        status = "✅" if habit.get('is_active', True) else "❌"
        xp_text = f" (+{habit['xp_reward']} XP)" if show_status else ""
        button_text = f"{status} {habit['name']}{xp_text}"

        keyboard.append([
            InlineKeyboardButton(
                button_text,
                callback_data=build_callback_data(action, habit['id'])
            )
        ])

    return InlineKeyboardMarkup(keyboard)


def create_habit_edit_keyboard(habit_id: int, is_active: bool) -> InlineKeyboardMarkup:
    """Cria teclado para editar hábito"""
    keyboard = [
        [
            InlineKeyboardButton(
                "✏️ Renomear",
                callback_data=build_callback_data(CallbackAction.RENAME_HABIT, habit_id)
            )
        ],
        [
            InlineKeyboardButton(
                "🎯 Alterar XP",
                callback_data=build_callback_data(CallbackAction.CHANGE_XP, habit_id)
            )
        ],
        [
            InlineKeyboardButton(
                f"{'❌ Desativar' if is_active else '✅ Ativar'}",
                callback_data=build_callback_data(CallbackAction.TOGGLE_HABIT, habit_id)
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 Voltar",
                callback_data=build_callback_data(CallbackAction.BACK_TO_EDIT, 0)
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


def create_delete_confirmation_keyboard(habit_id: int) -> InlineKeyboardMarkup:
    """Cria teclado de confirmação de exclusão"""
    keyboard = [
        [
            InlineKeyboardButton(
                "🗑️ SIM, deletar",
                callback_data=build_callback_data(CallbackAction.CONFIRM_DELETE, habit_id)
            )
        ],
        [
            InlineKeyboardButton(
                "❌ Cancelar",
                callback_data=build_callback_data(CallbackAction.CANCEL_DELETE, 0)
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


def create_reminder_config_keyboard(habit_id: int, has_reminder: bool = False) -> InlineKeyboardMarkup:
    """Cria teclado para configurar lembrete"""
    keyboard = [
        [
            InlineKeyboardButton(
                "⏰ Configurar Horário",
                callback_data=build_callback_data(CallbackAction.REMINDER_TIME, habit_id)
            )
        ],
        [
            InlineKeyboardButton(
                "📅 Configurar Dias",
                callback_data=build_callback_data(CallbackAction.REMINDER_DAYS, habit_id)
            )
        ]
    ]

    if has_reminder:
        keyboard.append([
            InlineKeyboardButton(
                "❌ Remover Lembrete",
                callback_data=build_callback_data(CallbackAction.REMOVE_REMINDER, habit_id)
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🔙 Voltar",
            callback_data=build_callback_data(CallbackAction.BACK_TO_REMINDER, 0)
        )
    ])

    return InlineKeyboardMarkup(keyboard)


def create_time_keyboard(habit_id: int) -> InlineKeyboardMarkup:
    """Cria teclado com horários comuns"""
    common_times = [
        "06:00", "07:00", "08:00", "09:00", "12:00",
        "18:00", "19:00", "20:00", "21:00", "22:00"
    ]

    keyboard = []
    row = []

    for i, time in enumerate(common_times):
        row.append(
            InlineKeyboardButton(
                time,
                callback_data=build_callback_data(CallbackAction.REMINDER_TIME, habit_id, time)
            )
        )

        if len(row) == 2:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton(
            "✏️ Digitar horário",
            callback_data=build_callback_data(CallbackAction.REMINDER_TIME, habit_id, "custom")
        )
    ])

    return InlineKeyboardMarkup(keyboard)


def create_days_keyboard(habit_id: int) -> InlineKeyboardMarkup:
    """Cria teclado com dias da semana"""
    days_options = [
        ("Seg-Sex", "1,2,3,4,5"),
        ("Seg-Sáb", "1,2,3,4,5,6"),
        ("Todos os dias", "1,2,3,4,5,6,7"),
        ("Finais de semana", "6,7"),
        ("Segunda", "1"),
        ("Terça", "2"),
        ("Quarta", "3"),
        ("Quinta", "4"),
        ("Sexta", "5"),
        ("Sábado", "6"),
        ("Domingo", "7")
    ]

    keyboard = []
    row = []

    for i, (label, days) in enumerate(days_options):
        row.append(
            InlineKeyboardButton(
                label,
                callback_data=build_callback_data(CallbackAction.REMINDER_DAYS, habit_id, days)
            )
        )

        if len(row) == 2:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton(
            "✏️ Digitar dias",
            callback_data=build_callback_data(CallbackAction.REMINDER_DAYS, habit_id, "custom")
        )
    ])

    return InlineKeyboardMarkup(keyboard)


def create_progress_keyboard() -> InlineKeyboardMarkup:
    """Cria teclado para ver progresso"""
    keyboard = [
        [
            InlineKeyboardButton(
                "📊 Ver Progresso",
                callback_data=build_callback_data(CallbackAction.SHOW_PROGRESS, 0)
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)
