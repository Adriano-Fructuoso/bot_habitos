"""
Handlers para comandos principais
"""

from functools import partial
from telegram import Update
from telegram.ext import ContextTypes
from db.session import get_db
from models.models import User, Habit, DailyLog
from utils.gamification import (
    calculate_xp_earned,
    update_user_progress,
    get_user_stats,
    get_daily_progress,
    get_weekly_summary,
    get_motivational_message,
)
from utils.branding import (
    add_branding,
    get_welcome_message,
    get_success_message_with_branding,
)
from utils.keyboards import (
    create_habit_list_keyboard,
    create_progress_keyboard,
)
from app_types import CallbackAction
from .base import track_command, safe_handler


@track_command("start")
async def _start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /start"""
    try:
        print(f"🔍 /start iniciado para usuário {update.effective_user.id}")
        
        user = update.effective_user
        telegram_user_id = user.id
        
        print(f"📝 Buscando usuário {telegram_user_id} no banco...")
        
        db = next(get_db())
        
        # Busca ou cria usuário
        db_user = db.query(User).filter(User.telegram_user_id == telegram_user_id).first()
        
        if not db_user:
            print(f"👤 Criando novo usuário {telegram_user_id}...")
            # Cria novo usuário
            db_user = User(
                telegram_user_id=telegram_user_id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            print(f"✅ Usuário criado com ID {db_user.id}")
            
            # Cria hábitos padrão
            default_habits = [
                ("Leitura", 12, "Leia pelo menos 20 minutos para expandir conhecimentos"),
                ("Exercício físico", 15, "Mova-se pelo menos 30 minutos por dia"),
                ("Meditação", 10, "Respire fundo e relaxe por 10-15 minutos"),
                ("Banho de água gelada", 20, "Tome um banho de água gelada para aumentar energia e resistência"),
            ]
            
            for name, xp, desc in default_habits:
                habit = Habit(
                    user_id=db_user.id,
                    name=name,
                    xp_reward=xp,
                    description=desc,
                    category="personal"
                )
                db.add(habit)
            
            db.commit()
            
            print("📝 Enviando mensagem de boas-vindas...")
            welcome_message = get_welcome_message()
            await update.message.reply_text(welcome_message, parse_mode="Markdown")
            print("✅ Mensagem de boas-vindas enviada")
            
        else:
            print(f"👤 Usuário {telegram_user_id} já existe (ID: {db_user.id})")
            # Usuário já existe - mostra menu principal
            from utils.keyboards import create_main_menu_keyboard
            from utils.gamification import get_daily_goal_progress
            
            print("📊 Buscando progresso diário...")
            # Busca progresso diário
            progress = get_daily_goal_progress(db, db_user.id)
            print(f"✅ Progresso: {progress}")
            
            message = f"""
🎉 *Bem-vindo de volta, {user.first_name}!*

**📊 Seu Progresso Hoje:**
• ✅ {progress['completed']}/{progress['goal']} hábitos completados
• 📈 {progress['progress']:.1f}% da meta diária
• 🏆 Nível {db_user.current_level}
• 💎 {db_user.total_xp_earned:,} XP total

**Escolha uma opção:**
"""
            
            print("🎯 Criando menu principal...")
            keyboard = create_main_menu_keyboard()
            
            print("📤 Enviando menu principal...")
            await update.message.reply_text(
                add_branding(message),
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            print("✅ Menu principal enviado com sucesso!")
    
    except Exception as e:
        print(f"❌ Erro no comando /start: {e}")
        print(f"❌ Tipo de erro: {type(e).__name__}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        db.rollback()
        raise e
    finally:
        db.close()
        print("🔒 Conexão com banco fechada")


@track_command("habit")
async def _habit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /habit"""
    user = update.effective_user
    telegram_user_id = user.id
    
    db = next(get_db())
    
    try:
        db_user = db.query(User).filter(User.telegram_user_id == telegram_user_id).first()
        if not db_user:
            await update.message.reply_text("❌ Usuário não encontrado. Use /start primeiro.")
            return
        
        # Busca hábitos ativos
        habits = db.query(Habit).filter(
            Habit.user_id == db_user.id,
            Habit.is_active == True
        ).all()
        
        if not habits:
            message = """
📝 *Nenhum hábito encontrado*

Use /add_habit para criar seu primeiro hábito!
"""
            await update.message.reply_text(add_branding(message), parse_mode="Markdown")
            return
        
        # Busca progresso diário
        progress = get_daily_progress(db, db_user.id)
        
        # Monta mensagem
        message = f"""
🎯 *Seus Hábitos de Hoje*

📊 Progresso: {progress['completed']}/{progress['goal']} ({progress['progress']:.1f}%)

"""
        
        # Adiciona hábitos
        for habit in habits:
            completed = any(log.habit_id == habit.id for log in progress['logs'])
            status = "✅" if completed else "⭕"
            message += f"{status} {habit.name} (+{habit.xp_reward} XP)\n"
        
        # Adiciona teclado
        keyboard = create_habit_list_keyboard(
            [{"id": h.id, "name": h.name, "xp_reward": h.xp_reward} for h in habits],
            CallbackAction.COMPLETE_HABIT,
            show_status=False
        )
        
        await update.message.reply_text(
            add_branding(message),
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
        # Verifica se completou todos os hábitos
        if progress['completed'] == progress['goal'] and progress['goal'] > 0:
            perfect_message = f"""
✨ *DIA PERFEITO!* ✨
Você completou todos os seus hábitos hoje!
{get_motivational_message('streak_milestone')}
"""
            await update.message.reply_text(add_branding(perfect_message), parse_mode="Markdown")
    
    finally:
        db.close()


@track_command("stats")
async def _stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /stats"""
    user = update.effective_user
    telegram_user_id = user.id
    
    db = next(get_db())
    
    try:
        db_user = db.query(User).filter(User.telegram_user_id == telegram_user_id).first()
        if not db_user:
            await update.message.reply_text("❌ Usuário não encontrado. Use /start primeiro.")
            return
        
        stats = get_user_stats(db, db_user.id)
        
        message = f"""
📊 *Suas Estatísticas*

🏆 Nível: {stats['current_level']}
⭐ XP Total: {stats['total_xp_earned']:,}
🔥 Streak Atual: {stats['current_streak']} dias
🏅 Melhor Streak: {stats['longest_streak']} dias
📅 Dias desde o início: {stats['days_since_start']}
✅ Hábitos completados hoje: {stats['habits_completed_today']}
📝 Total de hábitos: {stats['total_habits']}
"""
        
        keyboard = create_progress_keyboard()
        
        await update.message.reply_text(
            add_branding(message),
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    
    finally:
        db.close()


@track_command("dashboard")
async def _dashboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /dashboard"""
    user = update.effective_user
    telegram_user_id = user.id
    
    db = next(get_db())
    
    try:
        db_user = db.query(User).filter(User.telegram_user_id == telegram_user_id).first()
        if not db_user:
            await update.message.reply_text("❌ Usuário não encontrado. Use /start primeiro.")
            return
        
        stats = get_user_stats(db, db_user.id)
        progress = get_daily_progress(db, db_user.id)
        
        message = f"""
🎛️ *Dashboard Completo*

👤 **Usuário**: {user.first_name}
🏆 **Nível**: {stats['current_level']}
⭐ **XP Total**: {stats['total_xp_earned']:,}
🔥 **Streak Atual**: {stats['current_streak']} dias
🏅 **Melhor Streak**: {stats['longest_streak']} dias

📊 **Hoje**:
• Progresso: {progress['completed']}/{progress['goal']} ({progress['progress']:.1f}%)
• Hábitos completados: {stats['habits_completed_today']}
• Total de hábitos: {stats['total_habits']}

📅 **Histórico**:
• Dias desde o início: {stats['days_since_start']}
• Hábitos ativos: {stats['total_habits']}
"""
        
        await update.message.reply_text(add_branding(message), parse_mode="Markdown")
    
    finally:
        db.close()


@track_command("rating")
async def _rating_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /rating"""
    user = update.effective_user
    telegram_user_id = user.id
    
    db = next(get_db())
    
    try:
        db_user = db.query(User).filter(User.telegram_user_id == telegram_user_id).first()
        if not db_user:
            await update.message.reply_text("❌ Usuário não encontrado. Use /start primeiro.")
            return
        
        message = """
⭐ *Como você avalia seu dia hoje?*

Clique em uma opção abaixo:
"""
        
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        from app_types import CallbackAction, CALLBACK_VERSION
        
        keyboard = [
            [
                InlineKeyboardButton("😞 Ruim", callback_data=f"{CALLBACK_VERSION}:{CallbackAction.RATE_DAY.value}:0:1"),
                InlineKeyboardButton("😐 Regular", callback_data=f"{CALLBACK_VERSION}:{CallbackAction.RATE_DAY.value}:0:2"),
            ],
            [
                InlineKeyboardButton("😊 Bom", callback_data=f"{CALLBACK_VERSION}:{CallbackAction.RATE_DAY.value}:0:3"),
                InlineKeyboardButton("🤩 Excelente", callback_data=f"{CALLBACK_VERSION}:{CallbackAction.RATE_DAY.value}:0:4"),
            ]
        ]
        
        await update.message.reply_text(
            add_branding(message),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    
    finally:
        db.close()


@track_command("weekly")
async def _weekly_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /weekly"""
    user = update.effective_user
    telegram_user_id = user.id
    
    db = next(get_db())
    
    try:
        db_user = db.query(User).filter(User.telegram_user_id == telegram_user_id).first()
        if not db_user:
            await update.message.reply_text("❌ Usuário não encontrado. Use /start primeiro.")
            return
        
        weekly = get_weekly_summary(db, db_user.id)
        
        if not weekly:
            await update.message.reply_text("❌ Erro ao buscar resumo semanal.")
            return
        
        # Calcula taxa de sucesso
        total_habits_week = len(weekly['week_logs'])
        success_rate = (weekly['total_completed'] / total_habits_week * 100) if total_habits_week > 0 else 0
        
        message = f"""
📅 *Resumo Semanal*

📊 **Esta semana**:
• Hábitos completados: {weekly['total_completed']}
• Dias ativos: {weekly['active_days']}/7
• Taxa de sucesso: {success_rate:.1f}%
• XP ganho: {weekly['total_xp_earned']}

🔥 **Streaks**:
• Streak atual: {weekly['user'].current_streak} dias
• Melhor streak: {weekly['user'].longest_streak} dias

⭐ **Avaliações médias**:
• Humor: {weekly['avg_mood']}/10
• Energia: {weekly['avg_energy']}/10
"""
        
        await update.message.reply_text(add_branding(message), parse_mode="Markdown")
    
    finally:
        db.close()


@track_command("habits")
async def _habits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /habits"""
    user = update.effective_user
    telegram_user_id = user.id
    
    db = next(get_db())
    
    try:
        db_user = db.query(User).filter(User.telegram_user_id == telegram_user_id).first()
        if not db_user:
            await update.message.reply_text("❌ Usuário não encontrado. Use /start primeiro.")
            return
        
        habits = db.query(Habit).filter(
            Habit.user_id == db_user.id,
            Habit.is_active == True
        ).order_by(Habit.created_at.desc()).all()
        
        if not habits:
            message = """
📝 *Nenhum hábito encontrado*

Use /add_habit para criar seu primeiro hábito!
"""
            await update.message.reply_text(add_branding(message), parse_mode="Markdown")
            return
        
        message = f"""
📝 *Seus Hábitos* ({len(habits)} total)

"""
        
        for habit in habits:
            status = "✅" if habit.is_active else "❌"
            message += f"{status} **{habit.name}** (+{habit.xp_reward} XP)\n"
            if habit.description:
                message += f"   _{habit.description}_\n"
            message += f"   Streak: {habit.current_streak} dias | Total: {habit.total_completions}\n\n"
        
        keyboard = create_habit_list_keyboard(
            [{"id": h.id, "name": h.name, "xp_reward": h.xp_reward, "is_active": h.is_active} for h in habits],
            CallbackAction.EDIT_HABIT
        )
        
        await update.message.reply_text(
            add_branding(message),
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    
    finally:
        db.close()


# Exporta os comandos diretamente (já decorados com @track_command)
start_command = _start_command
habit_command = _habit_command
stats_command = _stats_command
dashboard_command = _dashboard_command
rating_command = _rating_command
weekly_command = _weekly_command
habits_command = _habits_command
