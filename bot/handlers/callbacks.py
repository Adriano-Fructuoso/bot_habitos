"""
Handlers para callbacks inline
"""

from functools import partial
from telegram import Update
from telegram.ext import ContextTypes
from db.session import get_db
from models.models import User, Habit, DailyLog, DailyRating
from utils.gamification import (
    calculate_xp_earned,
    update_user_progress,
    get_user_stats,
    get_daily_progress,
    get_motivational_message,
)
from utils.branding import add_branding, get_success_message_with_branding
from utils.idempotency import is_duplicate_callback
from utils.keyboards import (
    create_habit_edit_keyboard,
    create_delete_confirmation_keyboard,
    create_reminder_config_keyboard,
    create_time_keyboard,
    create_days_keyboard,
)
from utils.validators import validate_callback_data
from app_types import CallbackAction
from .base import safe_handler


async def _complete_habit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para completar um hábito"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Parse callback data
        callback_data = validate_callback_data(query.data)
        habit_id = callback_data["habit_id"]
        user_id = query.from_user.id
        
        db = next(get_db())
        
        try:
            # ✅ ADICIONAR IDEMPOTÊNCIA
            if is_duplicate_callback(query.id, db):
                await query.edit_message_text("Comando já processado")
                return
            
            # Busca usuário e hábito
            db_user = db.query(User).filter(User.telegram_user_id == user_id).first()
            if not db_user:
                await query.edit_message_text("❌ Usuário não encontrado.")
                return
            
            habit = db.query(Habit).filter(
                Habit.id == habit_id,
                Habit.user_id == db_user.id,
                Habit.is_active == True
            ).first()
            
            if not habit:
                await query.edit_message_text("❌ Hábito não encontrado.")
                return
            
            # Verifica se já foi completado hoje
            from datetime import date
            today = date.today()
            
            existing_log = db.query(DailyLog).filter(
                DailyLog.user_id == db_user.id,
                DailyLog.habit_id == habit_id,
                DailyLog.completed_at >= today
            ).first()
            
            if existing_log:
                await query.edit_message_text("✅ Este hábito já foi completado hoje!")
                return
            
            # Registra conclusão
            xp_earned = calculate_xp_earned(habit.xp_reward, habit.current_streak)
            
            log = DailyLog(
                user_id=db_user.id,
                habit_id=habit_id,
                xp_earned=xp_earned
            )
            db.add(log)
            
            # Atualiza progresso do usuário
            update_user_progress(db, db_user.id, habit_id, xp_earned)
            
            # Atualiza streak do hábito
            habit.current_streak += 1
            habit.total_completions += 1
            if habit.current_streak > habit.longest_streak:
                habit.longest_streak = habit.current_streak
            
            db.commit()
            
            # Mensagem de sucesso
            success_message = f"""
✅ *Hábito Completado!*

🎯 **{habit.name}**
⭐ +{xp_earned} XP ganho
🔥 Streak: {habit.current_streak} dias
📊 Total: {habit.total_completions} vezes

{get_motivational_message('habit_completed')}
"""
            
            await query.edit_message_text(
                add_branding(success_message),
                parse_mode="Markdown"
            )
            
        finally:
            db.close()
    
    except Exception as e:
        await query.edit_message_text(f"❌ Erro: {str(e)}")


async def _rating_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para avaliar o dia"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Parse callback data
        callback_data = validate_callback_data(query.data)
        rating_value = int(callback_data["extra"])
        user_id = query.from_user.id
        
        db = next(get_db())
        
        try:
            # Busca usuário
            db_user = db.query(User).filter(User.telegram_user_id == user_id).first()
            if not db_user:
                await query.edit_message_text("❌ Usuário não encontrado.")
                return
            
            # Verifica se já avaliou hoje
            from datetime import date
            today = date.today()
            
            existing_rating = db.query(DailyRating).filter(
                DailyRating.user_id == db_user.id,
                DailyRating.rating_date == today
            ).first()
            
            if existing_rating:
                existing_rating.rating = rating_value
                message = "⭐ Avaliação atualizada!"
            else:
                rating = DailyRating(
                    user_id=db_user.id,
                    rating=rating_value
                )
                db.add(rating)
                message = "⭐ Avaliação registrada!"
            
            db.commit()
            
            # Emojis para cada rating
            emojis = {1: "😞", 2: "😐", 3: "😊", 4: "🤩"}
            emoji = emojis.get(rating_value, "⭐")
            
            await query.edit_message_text(f"{emoji} {message}")
            
        finally:
            db.close()
    
    except Exception as e:
        await query.edit_message_text(f"❌ Erro: {str(e)}")


async def _show_progress_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para mostrar progresso detalhado"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    db = next(get_db())
    
    try:
        # Busca usuário
        db_user = db.query(User).filter(User.telegram_user_id == user_id).first()
        if not db_user:
            await query.edit_message_text("❌ Usuário não encontrado.")
            return
        
        # Busca estatísticas
        from utils.gamification import get_user_stats
        stats = get_user_stats(db_user.id, db)
        
        # Busca progresso diário
        from utils.gamification import get_daily_progress
        progress = get_daily_progress(db, db_user.id)
        
        message = f"""
📊 *Progresso Detalhado*

🎯 **Hoje**:
• Completados: {progress['completed']}/{progress['goal']}
• Taxa: {progress['progress']:.1f}%

🏆 **Geral**:
• Nível: {stats['current_level']}
• XP Total: {stats['total_xp_earned']:,}
• Streak: {stats['current_streak']} dias
• Melhor Streak: {stats['longest_streak']} dias

📅 **Histórico**:
• Dias desde início: {stats['days_since_start']}
• Total de hábitos: {stats['total_habits']}
"""
        
        await query.edit_message_text(
            add_branding(message),
            parse_mode="Markdown"
        )
    
    finally:
        db.close()


async def _edit_habit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para editar um hábito específico"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Parse callback data
        callback_data = validate_callback_data(query.data)
        habit_id = callback_data["habit_id"]
        user_id = query.from_user.id
        
        db = next(get_db())
        
        try:
            # Busca hábito
            from utils.repository import HabitRepository
            habit = HabitRepository.get_habit(db, habit_id, user_id)
            
            if not habit:
                await query.edit_message_text("❌ Hábito não encontrado.")
                return
            
            message = f"""
✏️ *Editar Hábito*

🎯 **{habit.name}**
⭐ XP: {habit.xp_reward}
🔥 Streak: {habit.current_streak} dias
📊 Total: {habit.total_completions} vezes

Escolha uma opção:
"""
            
            keyboard = create_habit_edit_keyboard(habit_id, habit.is_active)
            
            await query.edit_message_text(
                add_branding(message),
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        finally:
            db.close()
    
    except Exception as e:
        await query.edit_message_text(f"❌ Erro: {str(e)}")


async def _delete_habit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para deletar um hábito específico"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Parse callback data
        callback_data = validate_callback_data(query.data)
        habit_id = callback_data["habit_id"]
        user_id = query.from_user.id
        
        db = next(get_db())
        
        try:
            # Busca hábito
            from utils.repository import HabitRepository
            habit = HabitRepository.get_habit(db, habit_id, user_id)
            
            if not habit:
                await query.edit_message_text("❌ Hábito não encontrado.")
                return
            
            message = f"""
🗑️ *Confirmar Exclusão*

Tem certeza que deseja deletar o hábito:

**{habit.name}**?

Esta ação não pode ser desfeita.
"""
            
            keyboard = create_delete_confirmation_keyboard(habit_id)
            
            await query.edit_message_text(
                add_branding(message),
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        finally:
            db.close()
    
    except Exception as e:
        await query.edit_message_text(f"❌ Erro: {str(e)}")


async def _set_reminder_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para configurar lembrete"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Parse callback data
        callback_data = validate_callback_data(query.data)
        habit_id = callback_data["habit_id"]
        user_id = query.from_user.id
        
        db = next(get_db())
        
        try:
            # Busca hábito
            from utils.repository import HabitRepository
            habit = HabitRepository.get_habit(db, habit_id, user_id)
            
            if not habit:
                await query.edit_message_text("❌ Hábito não encontrado.")
                return
            
            # Verifica se já tem lembrete
            from utils.repository import ReminderRepository
            existing_reminder = ReminderRepository.get_reminder(db, user_id, habit_id)
            
            message = f"""
⏰ *Configurar Lembrete*

🎯 **{habit.name}**

Escolha uma opção:
"""
            
            keyboard = create_reminder_config_keyboard(habit_id, existing_reminder is not None)
            
            await query.edit_message_text(
                add_branding(message),
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        finally:
            db.close()
    
    except Exception as e:
        await query.edit_message_text(f"❌ Erro: {str(e)}")


# Wrappers para os callbacks
complete_habit_callback = safe_handler(_complete_habit_callback)
rating_callback = safe_handler(_rating_callback)
show_progress_callback = safe_handler(_show_progress_callback)
edit_habit_callback = safe_handler(_edit_habit_callback)
delete_habit_callback = safe_handler(_delete_habit_callback)
set_reminder_callback = safe_handler(_set_reminder_callback)
