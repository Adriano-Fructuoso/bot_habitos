"""
Handlers para comandos CRUD (Create, Read, Update, Delete)
"""

from functools import partial
from telegram import Update
from telegram.ext import ContextTypes
from db.session import get_db
from models.models import User, Habit, Reminder
from utils.repository import HabitRepository, ReminderRepository
from utils.branding import add_branding, get_success_message_with_branding
from utils.keyboards import (
    create_habit_edit_keyboard,
    create_reminder_config_keyboard,
    create_days_of_week_keyboard,
)
from app_types import CallbackAction
from .base import track_command, safe_handler


@track_command("addhabits")
async def _add_habit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /addhabits"""
    user = update.effective_user
    telegram_user_id = user.id
    
    # Verifica se há argumentos
    if not context.args:
        message = """
📝 *Criar Novo Hábito*

Digite o nome do hábito após o comando:

`/addhabits Beber água`

Ou use o formato completo:
`/addhabits Nome do hábito XP descrição`

Exemplo:
`/addhabits Exercício 15 Mover-se 30 minutos por dia`
"""
        await update.message.reply_text(add_branding(message), parse_mode="Markdown")
        return
    
    db = next(get_db())
    
    try:
        # Parse dos argumentos
        args = context.args
        name = args[0]
        xp_reward = 10  # padrão
        description = None
        
        if len(args) >= 2:
            try:
                xp_reward = int(args[1])
            except ValueError:
                description = args[1]
        
        if len(args) >= 3:
            description = " ".join(args[2:])
        
        # Cria hábito
        habit = HabitRepository.create_habit(
            db=db,
            user_id=telegram_user_id,
            name=name,
            xp_reward=xp_reward,
            description=description
        )
        
        success_message = get_success_message_with_branding(
            f"Hábito '{habit.name}' criado com sucesso! (+{habit.xp_reward} XP)"
        )
        
        await update.message.reply_text(success_message, parse_mode="Markdown")
    
    except Exception as e:
        error_message = f"❌ Erro ao criar hábito: {str(e)}"
        await update.message.reply_text(error_message)
    finally:
        db.close()


@track_command("edit_habit")
async def _edit_habit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /edit_habit"""
    user = update.effective_user
    telegram_user_id = user.id
    
    db = next(get_db())
    
    try:
        # Busca hábitos do usuário
        habits = HabitRepository.get_habits(db, telegram_user_id, active_only=True)
        
        if not habits:
            message = """
📝 *Nenhum hábito encontrado*

Use /add_habit para criar seu primeiro hábito!
"""
            await update.message.reply_text(add_branding(message), parse_mode="Markdown")
            return
        
        message = """
✏️ *Editar Hábito*

Escolha um hábito para editar:
"""
        
        from utils.keyboards import create_habit_list_keyboard
        
        keyboard = create_habit_list_keyboard(
            [{"id": h.id, "name": h.name, "xp_reward": h.xp_reward} for h in habits],
            CallbackAction.EDIT_HABIT
        )
        
        await update.message.reply_text(
            add_branding(message),
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    
    finally:
        db.close()


@track_command("delete_habit")
async def _delete_habit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /delete_habit"""
    user = update.effective_user
    telegram_user_id = user.id
    
    db = next(get_db())
    
    try:
        # Busca hábitos do usuário
        habits = HabitRepository.get_habits(db, telegram_user_id, active_only=True)
        
        if not habits:
            message = """
📝 *Nenhum hábito encontrado*

Use /add_habit para criar seu primeiro hábito!
"""
            await update.message.reply_text(add_branding(message), parse_mode="Markdown")
            return
        
        message = """
🗑️ *Deletar Hábito*

Escolha um hábito para deletar:
"""
        
        from utils.keyboards import create_habit_list_keyboard
        
        keyboard = create_habit_list_keyboard(
            [{"id": h.id, "name": h.name, "xp_reward": h.xp_reward} for h in habits],
            CallbackAction.DELETE_HABIT
        )
        
        await update.message.reply_text(
            add_branding(message),
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    
    finally:
        db.close()


@track_command("set_reminder")
async def _set_reminder_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /set_reminder"""
    user = update.effective_user
    telegram_user_id = user.id
    
    db = next(get_db())
    
    try:
        # Busca hábitos do usuário
        habits = HabitRepository.get_habits(db, telegram_user_id, active_only=True)
        
        if not habits:
            message = """
📝 *Nenhum hábito encontrado*

Use /add_habit para criar seu primeiro hábito!
"""
            await update.message.reply_text(add_branding(message), parse_mode="Markdown")
            return
        
        message = """
⏰ *Configurar Lembrete*

Escolha um hábito para configurar lembretes:
"""
        
        from utils.keyboards import create_habit_list_keyboard
        
        keyboard = create_habit_list_keyboard(
            [{"id": h.id, "name": h.name, "xp_reward": h.xp_reward} for h in habits],
            CallbackAction.SET_REMINDER
        )
        
        await update.message.reply_text(
            add_branding(message),
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    
    finally:
        db.close()


# Exporta os comandos CRUD diretamente (já decorados com @track_command)
add_habit_command = _add_habit_command
edit_habit_command = _edit_habit_command
delete_habit_command = _delete_habit_command
set_reminder_command = _set_reminder_command
