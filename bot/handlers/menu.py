"""
Handler para o menu principal e navegação
"""

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from db.session import get_db
from models.models import User
from utils.branding import add_branding
from utils.keyboards import (
    create_main_menu_keyboard,
    create_habit_form_keyboard,
    create_habit_list_keyboard,
    create_habits_table_keyboard,
    create_habit_edit_list_keyboard,
    create_rating_keyboard,
    create_progress_keyboard,
    create_help_keyboard,
    create_navigation_keyboard
)
from utils.gamification import get_or_create_user, get_daily_goal_progress
from .base import track_command


@track_command("menu")
async def _menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /menu - mostra menu principal"""
    user = update.effective_user
    telegram_user_id = user.id
    
    db = next(get_db())
    
    try:
        # Obtém ou cria usuário
        db_user = get_or_create_user(
            db,
            telegram_user_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        
        # Busca progresso diário
        progress = get_daily_goal_progress(db, db_user.id)
        
        message = f"""
🎯 *Menu Principal - HabitBot*

Olá, {user.first_name}! 👋

**📊 Seu Progresso Hoje:**
• ✅ {progress['completed']}/{progress['goal']} hábitos completados
• 📈 {progress['progress']:.1f}% da meta diária
• 🏆 Nível {db_user.current_level}
• 💎 {db_user.total_xp_earned:,} XP total

**Escolha uma opção:**
"""
        
        keyboard = create_main_menu_keyboard()
        
        await update.message.reply_text(
            add_branding(message),
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    
    finally:
        db.close()


async def _menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para callbacks do menu principal"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    if callback_data == "menu_main":
        # Volta ao menu principal
        await _show_main_menu(query, context)
    
    elif callback_data == "menu_create_habit":
        # Inicia ConversationHandler para criação de hábito
        await _start_habit_creation_from_menu(query, context)
    
    elif callback_data == "menu_edit_habits":
        # Mostra lista de hábitos para editar
        await _show_edit_habits_list(query, context)
    
    elif callback_data == "menu_complete_today":
        # Mostra hábitos para completar hoje
        await _show_habits_table(query, context)
    
    elif callback_data == "menu_show_stats":
        # Mostra opções de progresso
        await _show_progress_options(query, context)
    
    elif callback_data == "menu_weekly_summary":
        # Mostra resumo semanal
        await _show_weekly_summary(query, context)
    
    elif callback_data == "menu_rate_day":
        # Mostra avaliação diária
        await _show_rating_form(query, context)
    
    elif callback_data == "menu_reminders":
        # Mostra opções de lembretes
        await _show_reminders_menu(query, context)
    
    elif callback_data == "menu_help":
        # Mostra menu de ajuda
        await _show_help_menu(query, context)
    
    else:
        # Callback não reconhecido
        await query.edit_message_text("❌ Opção não reconhecida. Use /menu para voltar ao menu principal.")


async def _show_main_menu(query, context):
    """Mostra o menu principal"""
    user = query.from_user
    
    message = f"""
🎯 *Menu Principal - HabitBot*

Olá, {user.first_name}! 👋

**Escolha uma opção:**
"""
    
    keyboard = create_main_menu_keyboard()
    
    await query.edit_message_text(
        add_branding(message),
        parse_mode="Markdown",
        reply_markup=keyboard
    )


async def _start_habit_creation_from_menu(query, context):
    """Inicia ConversationHandler para criação de hábito a partir do menu"""
    message = """
📝 *Criar Novo Hábito*

Vamos criar seu hábito passo a passo!

**Digite o nome do hábito:**
Exemplo: "Beber água", "Exercício físico", "Ler 20 páginas"

*Digite o nome do hábito:*
"""
    
    # Marca que está em conversa de criação
    context.user_data["conversation_active"] = True
    context.user_data["conversation_type"] = "habit_creation"
    
    await query.edit_message_text(
        add_branding(message),
        parse_mode="Markdown"
    )


async def _show_habits_list(query, context, action):
    """Mostra lista de hábitos para uma ação específica"""
    user = query.from_user
    telegram_user_id = user.id
    
    db = next(get_db())
    
    try:
        # Busca usuário primeiro
        from models.models import Habit, User
        db_user = db.query(User).filter(User.telegram_user_id == telegram_user_id).first()
        if not db_user:
            await query.edit_message_text("❌ Usuário não encontrado.")
            return
        
        # Busca hábitos do usuário
        habits = db.query(Habit).filter(
            Habit.user_id == db_user.id,
            Habit.is_active == True
        ).all()
        
        if not habits:
            message = """
📝 *Nenhum hábito encontrado*

Use "Criar Hábito" para adicionar seu primeiro hábito!
"""
            keyboard = create_navigation_keyboard()
            await query.edit_message_text(
                add_branding(message),
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            return
        
        # Converte para formato esperado pelo keyboard
        habits_data = [
            {
                "id": h.id,
                "name": h.name,
                "xp_reward": h.xp_reward,
                "is_active": h.is_active
            }
            for h in habits
        ]
        
        if action == "edit":
            message = "✏️ *Editar Hábitos*\n\nEscolha um hábito para editar:"
            from app_types import CallbackAction
            keyboard = create_habit_list_keyboard(habits_data, CallbackAction.EDIT_HABIT)
        else:  # complete
            message = "✅ *Completar Hábitos*\n\nEscolha um hábito para marcar como completo:"
            from app_types import CallbackAction
            keyboard = create_habit_list_keyboard(habits_data, CallbackAction.COMPLETE_HABIT)
        
        await query.edit_message_text(
            add_branding(message),
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    
    finally:
        db.close()


async def _show_habits_table(query, context):
    """Mostra tabela de hábitos para completar hoje"""
    user = query.from_user
    telegram_user_id = user.id
    
    db = next(get_db())
    
    try:
        # Busca usuário primeiro
        from models.models import Habit, User
        db_user = db.query(User).filter(User.telegram_user_id == telegram_user_id).first()
        if not db_user:
            await query.edit_message_text("❌ Usuário não encontrado.")
            return
        
        # Busca hábitos do usuário
        habits = db.query(Habit).filter(
            Habit.user_id == db_user.id,
            Habit.is_active == True
        ).all()
        
        if not habits:
            message = """
📝 *Nenhum hábito encontrado*

Use "Criar Hábito" para adicionar seu primeiro hábito!
"""
            keyboard = create_navigation_keyboard()
            await query.edit_message_text(
                add_branding(message),
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            return
        
        # Converte para formato esperado pelo keyboard
        habits_data = [
            {
                "id": h.id,
                "name": h.name,
                "xp_reward": h.xp_reward,
                "time_minutes": h.time_minutes,
                "is_active": h.is_active
            }
            for h in habits
        ]
        
        # Pega hábitos selecionados do contexto
        selected_habits = context.user_data.get('selected_habits', [])
        
        message = """
📋 *Hábitos*

Toque nos hábitos que você completou hoje:
• ⭕ = Não completado
• ✅ = Completado

"""
        
        keyboard = create_habits_table_keyboard(habits_data, selected_habits)
        
        await query.edit_message_text(
            add_branding(message),
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    
    finally:
        db.close()


async def _show_edit_habits_list(query, context):
    """Mostra lista de hábitos para edição completa"""
    user = query.from_user
    telegram_user_id = user.id
    
    db = next(get_db())
    
    try:
        # Busca usuário primeiro
        from models.models import Habit, User
        db_user = db.query(User).filter(User.telegram_user_id == telegram_user_id).first()
        if not db_user:
            await query.edit_message_text("❌ Usuário não encontrado.")
            return
        
        # Busca hábitos do usuário
        habits = db.query(Habit).filter(
            Habit.user_id == db_user.id
        ).all()
        
        if not habits:
            message = """
📝 *Nenhum hábito encontrado*

Use "Criar Hábito" para adicionar seu primeiro hábito!
"""
            keyboard = create_navigation_keyboard()
            await query.edit_message_text(
                add_branding(message),
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            return
        
        # Converte para formato esperado pelo keyboard
        habits_data = [
            {
                "id": h.id,
                "name": h.name,
                "xp_reward": h.xp_reward,
                "current_streak": h.current_streak,
                "is_active": h.is_active
            }
            for h in habits
        ]
        
        message = """
✏️ *Editar Hábitos*

Escolha um hábito para editar completamente:
"""
        
        keyboard = create_habit_edit_list_keyboard(habits_data)
        
        await query.edit_message_text(
            add_branding(message),
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    
    finally:
        db.close()


async def _show_progress_options(query, context):
    """Mostra opções de progresso"""
    message = """
📊 *Ver Progresso*

Escolha o que você quer visualizar:
"""
    
    keyboard = create_progress_keyboard()
    
    await query.edit_message_text(
        add_branding(message),
        parse_mode="Markdown",
        reply_markup=keyboard
    )


async def _show_weekly_summary(query, context):
    """Mostra resumo semanal"""
    user = query.from_user
    telegram_user_id = user.id
    
    db = next(get_db())
    
    try:
        # Busca usuário primeiro
        from models.models import User
        db_user = db.query(User).filter(User.telegram_user_id == telegram_user_id).first()
        if not db_user:
            await query.edit_message_text("❌ Usuário não encontrado.")
            return
        
        # Busca resumo semanal
        from utils.gamification import get_weekly_summary
        weekly = get_weekly_summary(db, db_user.id)
        
        if not weekly:
            message = "❌ Erro ao buscar resumo semanal."
            keyboard = create_navigation_keyboard()
            await query.edit_message_text(
                add_branding(message),
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            return
        
        # Calcula taxa de sucesso
        total_habits_week = len(weekly['week_logs'])
        success_rate = (weekly['total_completed'] / total_habits_week * 100) if total_habits_week > 0 else 0
        
        message = f"""
📅 *Resumo Semanal*

📊 **Esta semana:**
• Hábitos completados: {weekly['total_completed']}
• Dias ativos: {weekly['active_days']}/7
• Taxa de sucesso: {success_rate:.1f}%
• XP ganho: {weekly['total_xp_earned']}

🔥 **Streaks:**
• Streak atual: {weekly['user'].current_streak} dias
• Melhor streak: {weekly['user'].longest_streak} dias

⭐ **Avaliações médias:**
• Humor: {weekly['avg_mood']}/10
• Energia: {weekly['avg_energy']}/10
"""
        
        keyboard = create_navigation_keyboard()
        
        await query.edit_message_text(
            add_branding(message),
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    
    finally:
        db.close()


async def _show_rating_form(query, context):
    """Mostra formulário de avaliação diária"""
    message = """
⭐ *Avaliação Diária*

Como você está se sentindo hoje?

**Humor (1-10):**
😢 1 = Muito triste
😊 10 = Muito feliz

**Energia (1-10):**
😴 1 = Muito cansado
⚡ 10 = Muito energizado

Escolha suas avaliações:
"""
    
    keyboard = create_rating_keyboard()
    
    await query.edit_message_text(
        add_branding(message),
        parse_mode="Markdown",
        reply_markup=keyboard
    )


async def _show_reminders_menu(query, context):
    """Mostra menu de lembretes"""
    message = """
⏰ *Lembretes*

Configure lembretes para seus hábitos:

• Escolha um hábito
• Defina horário
• Configure dias da semana
• Receba notificações automáticas
"""
    
    keyboard = create_navigation_keyboard()
    
    await query.edit_message_text(
        add_branding(message),
        parse_mode="Markdown",
        reply_markup=keyboard
    )


async def _show_help_menu(query, context):
    """Mostra menu de ajuda"""
    message = """
❓ *Ajuda - HabitBot*

Escolha um tópico para saber mais:
"""
    
    keyboard = create_help_keyboard()
    
    await query.edit_message_text(
        add_branding(message),
        parse_mode="Markdown",
        reply_markup=keyboard
    )


# Exporta os handlers
menu_command = _menu_command
menu_callback = _menu_callback
