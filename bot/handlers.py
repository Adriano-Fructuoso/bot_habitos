from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from db.session import get_db
from models.models import User, Habit, DailyLog, Badge, Streak, DailyRating, Achievement
from utils.gamification import (
    calculate_xp_earned, update_user_progress, update_habit_streak,
    check_and_award_badges, get_user_stats, get_daily_goal_progress,
    get_motivational_message, create_daily_rating, get_weekly_summary,
    create_default_habits, check_client_conquest
)
from config import DEFAULT_HABITS, BADGES, ACHIEVEMENTS
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /start"""
    db = next(get_db())
    
    try:
        user = update.effective_user
        telegram_id = user.id
        
        # Verifica se o usuário já existe
        existing_user = db.query(User).filter(User.telegram_id == telegram_id).first()
        
        if not existing_user:
            # Cria novo usuário
            new_user = User(
                telegram_id=telegram_id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
            db.add(new_user)
            db.commit()
            
            # Cria hábitos padrão
            created_habits = create_default_habits(db, telegram_id)
            
            welcome_message = f"""
🎉 *Bem-vindo ao seu Bot de Gamificação!* 🎉

Olá {user.first_name}! Você acabou de embarcar em uma jornada incrível de transformação pessoal.

*O que você pode fazer:*
• 📊 Ver seu progresso com `/stats`
• 🎯 Completar hábitos com `/habit`
• 📈 Ver dashboard com `/dashboard`
• ⭐ Avaliar seu dia com `/rating`
• 📅 Ver resumo semanal com `/weekly`
• 📝 Ver seus hábitos com `/habits`

*Hábitos criados automaticamente:*
"""
            for habit in created_habits:
                welcome_message += f"• {habit.name}\n"
            
            welcome_message += f"\n{get_motivational_message('start')}"
            
        else:
            welcome_message = f"""
🌟 *Bem-vindo de volta, {user.first_name}!* 🌟

Que bom ter você aqui novamente! Vamos continuar sua jornada de transformação?

*Comandos disponíveis:*
• 📊 `/stats` - Ver suas estatísticas
• 🎯 `/habit` - Completar hábitos
• 📈 `/dashboard` - Dashboard completo
• ⭐ `/rating` - Avaliar seu dia
• 📅 `/weekly` - Resumo semanal
• 📝 `/habits` - Ver seus hábitos

{get_motivational_message('encouragement')}
"""
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erro no comando start: {e}")
        await update.message.reply_text("❌ Ocorreu um erro. Tente novamente.")
    finally:
        db.close()

async def habit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /habit - mostra lista de hábitos para completar"""
    db = next(get_db())
    
    try:
        user = update.effective_user
        telegram_id = user.id
        
        # Busca usuário
        db_user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not db_user:
            await update.message.reply_text("❌ Usuário não encontrado. Use /start primeiro.")
            return
        
        # Busca hábitos ativos
        habits = db.query(Habit).filter(
            Habit.user_id == db_user.id,
            Habit.is_active == True
        ).all()
        
        if not habits:
            await update.message.reply_text("❌ Nenhum hábito encontrado. Use /start para criar hábitos padrão.")
            return
        
        # Verifica quais hábitos já foram completados hoje
        today = datetime.now().date()
        today_logs = db.query(DailyLog).filter(
            DailyLog.user_id == db_user.id,
            DailyLog.date >= datetime.combine(today, datetime.min.time())
        ).all()
        
        completed_today = {log.habit_id for log in today_logs if log.completed}
        
        # Cria botões para cada hábito
        keyboard = []
        for habit in habits:
            status = "✅" if habit.id in completed_today else "⭕"
            button_text = f"{status} {habit.name} (+{habit.xp_reward} XP)"
            keyboard.append([InlineKeyboardButton(
                button_text, 
                callback_data=f"complete_habit_{habit.id}"
            )])
        
        # Adiciona botão para ver progresso
        keyboard.append([InlineKeyboardButton("📊 Ver Progresso", callback_data="show_progress")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        progress = get_daily_goal_progress(db, telegram_id)
        progress_text = f"\n📈 *Progresso de Hoje:* {progress['completed']}/{progress['goal']} ({progress['progress']:.1f}%)"
        
        message = f"""
🎯 *Seus Hábitos de Hoje*

Escolha um hábito para marcar como completo:
{progress_text}

*Como funciona:*
• ⭕ = Não completado hoje
• ✅ = Já completado hoje
• XP = Pontos de experiência ganhos
"""
        
        await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Erro no comando habit: {e}")
        await update.message.reply_text("❌ Ocorreu um erro. Tente novamente.")
    finally:
        db.close()

async def complete_habit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para completar um hábito"""
    db = next(get_db())
    
    try:
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        telegram_id = user.id
        
        # Extrai ID do hábito do callback_data
        habit_id = int(query.data.split('_')[2])
        
        # Busca usuário e hábito
        db_user = db.query(User).filter(User.telegram_id == telegram_id).first()
        habit = db.query(Habit).filter(Habit.id == habit_id).first()
        
        if not db_user or not habit:
            await query.edit_message_text("❌ Erro: usuário ou hábito não encontrado.")
            return
        
        # Verifica se já foi completado hoje
        today = datetime.now().date()
        existing_log = db.query(DailyLog).filter(
            DailyLog.user_id == db_user.id,
            DailyLog.habit_id == habit_id,
            DailyLog.date >= datetime.combine(today, datetime.min.time())
        ).first()
        
        if existing_log and existing_log.completed:
            await query.edit_message_text("✅ Este hábito já foi completado hoje!")
            return
        
        # Calcula XP
        xp_earned = calculate_xp_earned(habit.xp_reward, habit.current_streak)
        
        # Cria ou atualiza log
        if existing_log:
            existing_log.completed = True
            existing_log.completed_at = datetime.now()
            existing_log.xp_earned = xp_earned
        else:
            new_log = DailyLog(
                user_id=db_user.id,
                habit_id=habit_id,
                completed=True,
                completed_at=datetime.now(),
                xp_earned=xp_earned
            )
            db.add(new_log)
        
        # Atualiza progresso do usuário
        progress_update = update_user_progress(db, telegram_id, habit_id, xp_earned)
        
        # Atualiza streak do hábito
        update_habit_streak(db, telegram_id, habit_id)
        
        # Verifica badges
        awarded_badges = check_and_award_badges(db, telegram_id)
        
        # Verifica se completou todos os hábitos do dia
        perfect_day = check_client_conquest(db, telegram_id)
        
        # Monta mensagem de resposta
        message = f"""
🎉 *Hábito Completado!* 🎉

✅ **{habit.name}** foi marcado como completo!

*Ganhos:*
• 💎 +{xp_earned} XP
• 🔥 Streak: {habit.current_streak + 1} dias
• 📊 Nível: {progress_update['new_level']}

{get_motivational_message('habit_completed')}
"""
        
        # Adiciona mensagem de level up
        if progress_update['level_up']:
            message += f"\n🌟 *NÍVEL UP!* 🌟\nVocê subiu do nível {progress_update['old_level']} para o nível {progress_update['new_level']}!\n{get_motivational_message('level_up')}"
        
        # Adiciona badges conquistadas
        if awarded_badges:
            message += "\n🏆 *Novas Conquistas:*\n"
            for badge in awarded_badges:
                message += f"• {badge.icon} {badge.name} (+{badge.xp_bonus} XP)\n"
            message += get_motivational_message('badge_earned')
        
        # Adiciona mensagem de dia perfeito
        if perfect_day:
            message += f"\n✨ *DIA PERFEITO!* ✨\nVocê completou todos os seus hábitos hoje!\n{get_motivational_message('streak_milestone')}"
        
        await query.edit_message_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erro no callback complete_habit: {e}")
        await query.edit_message_text("❌ Ocorreu um erro. Tente novamente.")
    finally:
        db.close()

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /stats - mostra estatísticas do usuário"""
    db = next(get_db())
    
    try:
        user = update.effective_user
        telegram_id = user.id
        
        # Busca estatísticas
        stats = get_user_stats(db, telegram_id)
        if not stats:
            await update.message.reply_text("❌ Usuário não encontrado. Use /start primeiro.")
            return
        
        user_data = stats['user']
        
        # Cria barra de progresso para o nível
        progress_bar_length = 20
        filled_length = int((stats['level_progress'] / 100) * progress_bar_length)
        progress_bar = "█" * filled_length + "░" * (progress_bar_length - filled_length)
        
        message = f"""
📊 *Suas Estatísticas*

👤 **{user_data.first_name}**
🏆 Nível: {user_data.current_level}
💎 XP Total: {user_data.total_xp_earned:,}
📈 Progresso: {stats['level_progress']:.1f}%

{progress_bar}

*Hábitos:*
• 📝 Total: {stats['total_habits']}
• ✅ Ativos: {stats['active_habits']}
• 🎯 Completados: {stats['completed_logs']}
• 📊 Taxa de Sucesso: {stats['completion_rate']:.1f}%

*Streaks:*
• 🔥 Atual: {user_data.current_streak} dias
• 🏆 Melhor: {user_data.longest_streak} dias

*Conquistas:*
• 🏅 Badges: {stats['total_badges']}
• 💎 Raras: {stats['rare_badges']}

*Próximo Nível:*
• 🎯 XP Necessário: {stats['next_level_xp']:,}
• 📊 XP Atual: {stats['current_level_xp']:,}
"""
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erro no comando stats: {e}")
        await update.message.reply_text("❌ Ocorreu um erro. Tente novamente.")
    finally:
        db.close()

async def dashboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /dashboard - mostra dashboard completo"""
    db = next(get_db())
    
    try:
        user = update.effective_user
        telegram_id = user.id
        
        # Busca dados do usuário
        db_user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not db_user:
            await update.message.reply_text("❌ Usuário não encontrado. Use /start primeiro.")
            return
        
        # Busca hábitos
        habits = db.query(Habit).filter(
            Habit.user_id == db_user.id,
            Habit.is_active == True
        ).all()
        
        # Busca logs de hoje
        today = datetime.now().date()
        today_logs = db.query(DailyLog).filter(
            DailyLog.user_id == db_user.id,
            DailyLog.date >= datetime.combine(today, datetime.min.time())
        ).all()
        
        completed_today = {log.habit_id for log in today_logs if log.completed}
        
        # Busca progresso
        progress = get_daily_goal_progress(db, telegram_id)
        
        # Busca badges recentes
        recent_badges = db.query(Badge).filter(
            Badge.user_id == db_user.id
        ).order_by(Badge.earned_at.desc()).limit(3).all()
        
        message = f"""
📈 *Dashboard Completo*

👤 **{db_user.first_name}**
🏆 Nível {db_user.current_level} | 💎 {db_user.total_xp_earned:,} XP
🔥 Streak: {db_user.current_streak} dias

*Progresso de Hoje:*
📊 {progress['completed']}/{progress['goal']} hábitos ({progress['progress']:.1f}%)

*Seus Hábitos:*
"""
        
        for habit in habits:
            status = "✅" if habit.id in completed_today else "⭕"
            streak_text = f"🔥{habit.current_streak}" if habit.current_streak > 0 else ""
            message += f"{status} {habit.name} {streak_text}\n"
        
        if recent_badges:
            message += "\n*Conquistas Recentes:*\n"
            for badge in recent_badges:
                message += f"{badge.icon} {badge.name}\n"
        
        message += f"\n{get_motivational_message('encouragement')}"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erro no comando dashboard: {e}")
        await update.message.reply_text("❌ Ocorreu um erro. Tente novamente.")
    finally:
        db.close()

async def rating_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /rating - avaliação diária"""
    db = next(get_db())
    
    try:
        user = update.effective_user
        telegram_id = user.id
        
        # Verifica se o usuário existe
        db_user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not db_user:
            await update.message.reply_text("❌ Usuário não encontrado. Use /start primeiro.")
            return
        
        # Cria botões para avaliação
        keyboard = []
        
        # Botões para humor (1-10)
        mood_row = []
        for i in range(1, 11):
            mood_row.append(InlineKeyboardButton(
                f"{i}", 
                callback_data=f"rate_mood_{i}"
            ))
            if len(mood_row) == 5:
                keyboard.append(mood_row)
                mood_row = []
        if mood_row:
            keyboard.append(mood_row)
        
        # Botões para energia (1-10)
        energy_row = []
        for i in range(1, 11):
            energy_row.append(InlineKeyboardButton(
                f"{i}", 
                callback_data=f"rate_energy_{i}"
            ))
            if len(energy_row) == 5:
                keyboard.append(energy_row)
                energy_row = []
        if energy_row:
            keyboard.append(energy_row)
        
        # Botões para craving (0-10)
        craving_row = []
        for i in range(0, 11):
            craving_row.append(InlineKeyboardButton(
                f"{i}", 
                callback_data=f"rate_craving_{i}"
            ))
            if len(craving_row) == 5:
                keyboard.append(craving_row)
                craving_row = []
        if craving_row:
            keyboard.append(craving_row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = """
⭐ *Avaliação Diária*

Como você está se sentindo hoje?

*Humor (1-10):*
😢 1 = Muito triste
😊 10 = Muito feliz

*Energia (1-10):*
😴 1 = Muito cansado
⚡ 10 = Muito energizado

*Craving (0-10):*
😌 0 = Sem vontade
😤 10 = Vontade muito forte

Escolha suas avaliações:
"""
        
        await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Erro no comando rating: {e}")
        await update.message.reply_text("❌ Ocorreu um erro. Tente novamente.")
    finally:
        db.close()

async def rating_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para processar avaliações"""
    db = next(get_db())
    
    try:
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        telegram_id = user.id
        
        # Extrai dados do callback
        parts = query.data.split('_')
        rating_type = parts[1]
        rating_value = int(parts[2])
        
        # Busca usuário
        db_user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not db_user:
            await query.edit_message_text("❌ Usuário não encontrado.")
            return
        
        # Armazena temporariamente no contexto
        if 'rating_data' not in context.user_data:
            context.user_data['rating_data'] = {}
        
        context.user_data['rating_data'][rating_type] = rating_value
        
        # Verifica se todas as avaliações foram feitas
        rating_data = context.user_data['rating_data']
        if 'mood' in rating_data and 'energy' in rating_data and 'craving' in rating_data:
            # Cria avaliação no banco
            daily_rating = create_daily_rating(
                db, telegram_id,
                rating_data['mood'],
                rating_data['energy'],
                rating_data['craving']
            )
            
            # Limpa dados temporários
            del context.user_data['rating_data']
            
            # Monta mensagem de resposta
            mood_emoji = "😊" if rating_data['mood'] >= 7 else "😐" if rating_data['mood'] >= 4 else "😢"
            energy_emoji = "⚡" if rating_data['energy'] >= 7 else "😐" if rating_data['energy'] >= 4 else "😴"
            craving_emoji = "😌" if rating_data['craving'] <= 3 else "😐" if rating_data['craving'] <= 6 else "😤"
            
            message = f"""
⭐ *Avaliação Registrada!*

{mood_emoji} **Humor:** {rating_data['mood']}/10
{energy_emoji} **Energia:** {rating_data['energy']}/10
{craving_emoji} **Craving:** {rating_data['craving']}/10

Obrigado por compartilhar como você está se sentindo! 
Isso nos ajuda a entender melhor seu progresso.

{get_motivational_message('encouragement')}
"""
            
            await query.edit_message_text(message, parse_mode='Markdown')
        else:
            # Ainda faltam avaliações
            remaining = []
            if 'mood' not in rating_data:
                remaining.append("Humor")
            if 'energy' not in rating_data:
                remaining.append("Energia")
            if 'craving' not in rating_data:
                remaining.append("Craving")
            
            await query.edit_message_text(f"✅ Avaliação registrada! Falta: {', '.join(remaining)}")
        
    except Exception as e:
        logger.error(f"Erro no callback rating: {e}")
        await query.edit_message_text("❌ Ocorreu um erro. Tente novamente.")
    finally:
        db.close()

async def weekly_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /weekly - resumo semanal"""
    db = next(get_db())
    
    try:
        user = update.effective_user
        telegram_id = user.id
        
        # Busca resumo semanal
        weekly_summary = get_weekly_summary(db, telegram_id)
        if not weekly_summary:
            await update.message.reply_text("❌ Usuário não encontrado. Use /start primeiro.")
            return
        
        user_data = weekly_summary['user']
        
        # Calcula estatísticas adicionais
        total_habits = len(weekly_summary['week_logs'])
        completion_rate = (weekly_summary['total_completed'] / total_habits * 100) if total_habits > 0 else 0
        
        # Determina emoji baseado no humor médio
        mood_emoji = "😊" if weekly_summary['avg_mood'] >= 7 else "😐" if weekly_summary['avg_mood'] >= 4 else "😢"
        energy_emoji = "⚡" if weekly_summary['avg_energy'] >= 7 else "😐" if weekly_summary['avg_energy'] >= 4 else "😴"
        
        message = f"""
📅 *Resumo Semanal*

👤 **{user_data.first_name}**
📊 **Período:** Últimos 7 dias

*Progresso:*
• ✅ Hábitos Completados: {weekly_summary['total_completed']}
• 💎 XP Ganho: {weekly_summary['total_xp_earned']}
• 📈 Taxa de Sucesso: {completion_rate:.1f}%
• 🌟 Dias Ativos: {weekly_summary['active_days']}/7

*Avaliações Médias:*
{mood_emoji} **Humor:** {weekly_summary['avg_mood']}/10
{energy_emoji} **Energia:** {weekly_summary['avg_energy']}/10
😤 **Craving:** {weekly_summary['avg_craving']}/10

*Destaques:*
• 🔥 Streak Atual: {user_data.current_streak} dias
• 🏆 Melhor Streak: {user_data.longest_streak} dias
• 🏅 Badges: {len(user_data.badges)}

{get_motivational_message('encouragement')}
"""
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erro no comando weekly: {e}")
        await update.message.reply_text("❌ Ocorreu um erro. Tente novamente.")
    finally:
        db.close()

async def habits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /habits - lista todos os hábitos"""
    db = next(get_db())
    
    try:
        user = update.effective_user
        telegram_id = user.id
        
        # Busca usuário
        db_user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not db_user:
            await update.message.reply_text("❌ Usuário não encontrado. Use /start primeiro.")
            return
        
        # Busca todos os hábitos
        habits = db.query(Habit).filter(Habit.user_id == db_user.id).all()
        
        if not habits:
            await update.message.reply_text("❌ Nenhum hábito encontrado. Use /start para criar hábitos padrão.")
            return
        
        message = f"""
📝 *Seus Hábitos*

Total: {len(habits)} hábitos
"""
        
        # Agrupa por categoria
        categories = {}
        for habit in habits:
            category = habit.category or 'Geral'
            if category not in categories:
                categories[category] = []
            categories[category].append(habit)
        
        for category, habit_list in categories.items():
            message += f"\n*{category.title()}:*\n"
            for habit in habit_list:
                status = "✅" if habit.is_active else "❌"
                difficulty_emoji = {
                    'easy': '🟢',
                    'medium': '🟡',
                    'hard': '🔴'
                }.get(habit.difficulty, '⚪')
                
                message += f"{status} {difficulty_emoji} {habit.name}\n"
                message += f"   💎 +{habit.xp_reward} XP | 🔥 Streak: {habit.current_streak}\n"
                message += f"   📊 Total: {habit.total_completions} vezes\n\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erro no comando habits: {e}")
        await update.message.reply_text("❌ Ocorreu um erro. Tente novamente.")
    finally:
        db.close()

async def show_progress_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para mostrar progresso detalhado"""
    db = next(get_db())
    
    try:
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        telegram_id = user.id
        
        # Busca estatísticas
        stats = get_user_stats(db, telegram_id)
        if not stats:
            await query.edit_message_text("❌ Usuário não encontrado.")
            return
        
        user_data = stats['user']
        progress = get_daily_goal_progress(db, telegram_id)
        
        # Cria barra de progresso
        progress_bar_length = 15
        filled_length = int((progress['progress'] / 100) * progress_bar_length)
        progress_bar = "█" * filled_length + "░" * (progress_bar_length - filled_length)
        
        message = f"""
📊 *Progresso Detalhado*

👤 **{user_data.first_name}**
🏆 Nível {user_data.current_level} | 💎 {user_data.total_xp_earned:,} XP

*Hoje:*
{progress_bar} {progress['progress']:.1f}%
✅ {progress['completed']}/{progress['goal']} hábitos completados

*Streaks:*
🔥 Atual: {user_data.current_streak} dias
🏆 Melhor: {user_data.longest_streak} dias

*Estatísticas Gerais:*
📝 Hábitos: {stats['active_habits']}/{stats['total_habits']} ativos
🎯 Taxa de Sucesso: {stats['completion_rate']:.1f}%
🏅 Badges: {stats['total_badges']} ({stats['rare_badges']} raras)

*Próximo Nível:*
📈 {stats['current_level_xp']:,}/{stats['next_level_xp']:,} XP
"""
        
        await query.edit_message_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erro no callback show_progress: {e}")
        await query.edit_message_text("❌ Ocorreu um erro. Tente novamente.")
    finally:
        db.close() 