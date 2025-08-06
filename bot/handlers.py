import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from db.session import get_db
from models.models import User, Habit, DailyLog
from utils.gamification import GamificationSystem

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /start"""
    try:
        # Obtém informações do usuário
        user_info = update.effective_user
        telegram_id = user_info.id
        username = user_info.username
        first_name = user_info.first_name
        last_name = user_info.last_name
        
        # Obtém sessão do banco
        db = next(get_db())
        
        # Verifica se o usuário já existe
        existing_user = db.query(User).filter(User.telegram_id == telegram_id).first()
        
        if existing_user:
            # Usuário já cadastrado
            stats = GamificationSystem.get_user_stats(existing_user)
            message = (
                f"👋 Olá {first_name}! Você já está cadastrado!\n\n"
                f"📊 Suas estatísticas:\n"
                f"• Nível: {stats['level']}\n"
                f"• XP: {stats['xp']}\n"
                f"• Streak: {stats['streak_days']} dias\n"
                f"• Hábitos completados: {stats['total_habits_completed']}\n"
                f"• Badges: {stats['badges_count']}\n\n"
                f"Use /habit para registrar um hábito completado!"
            )
        else:
            # Cria novo usuário
            new_user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                xp=0,
                level=1,
                streak_days=0
            )
            db.add(new_user)
            db.commit()
            
            # Cria um hábito padrão
            default_habit = Habit(
                user_id=new_user.id,
                name="Hábito Diário",
                description="Seu primeiro hábito para começar a jornada!",
                xp_reward=10
            )
            db.add(default_habit)
            db.commit()
            
            message = (
                f"🎉 Bem-vindo ao Habit Bot, {first_name}!\n\n"
                f"✅ Você foi cadastrado com sucesso!\n"
                f"📝 Um hábito padrão foi criado para você.\n\n"
                f"Use /habit para registrar quando completar um hábito e ganhar XP!\n\n"
                f"🎮 Sistema de gamificação:\n"
                f"• Cada hábito = {GamificationSystem.XP_PER_HABIT} XP base\n"
                f"• Streak diário = bônus de XP\n"
                f"• Suba de nível acumulando XP\n"
                f"• Desbloqueie badges especiais!"
            )
        
        await update.message.reply_text(message)
        
    except Exception as e:
        logger.error(f"Erro no comando start: {e}")
        await update.message.reply_text("❌ Ocorreu um erro. Tente novamente mais tarde.")
    finally:
        db.close()

async def habit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /habit"""
    try:
        # Obtém informações do usuário
        user_info = update.effective_user
        telegram_id = user_info.id
        
        # Obtém sessão do banco
        db = next(get_db())
        
        # Busca o usuário
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        
        if not user:
            await update.message.reply_text(
                "❌ Você precisa se cadastrar primeiro! Use /start para começar."
            )
            return
        
        # Verifica se o usuário já completou um hábito hoje
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        today_logs = db.query(DailyLog).filter(
            DailyLog.user_id == user.id,
            DailyLog.completed_at >= today_start,
            DailyLog.completed_at <= today_end
        ).count()
        
        if today_logs > 0:
            await update.message.reply_text(
                "✅ Você já registrou um hábito hoje! Volte amanhã para continuar seu streak!"
            )
            return
        
        # Busca o hábito padrão do usuário (ou o primeiro ativo)
        habit = db.query(Habit).filter(
            Habit.user_id == user.id,
            Habit.is_active == True
        ).first()
        
        if not habit:
            # Cria um hábito padrão se não existir
            habit = Habit(
                user_id=user.id,
                name="Hábito Diário",
                description="Seu hábito diário",
                xp_reward=10
            )
            db.add(habit)
            db.commit()
        
        # Calcula XP ganho
        xp_earned = GamificationSystem.calculate_xp_earned(user.streak_days)
        
        # Cria o log do hábito completado
        daily_log = DailyLog(
            user_id=user.id,
            habit_id=habit.id,
            xp_earned=xp_earned
        )
        db.add(daily_log)
        db.commit()
        
        # Atualiza progresso do usuário
        progress = GamificationSystem.update_user_progress(db, user, xp_earned)
        
        # Verifica badges
        earned_badges = GamificationSystem.check_and_award_badges(db, user)
        
        # Monta mensagem de resposta
        message = f"🎉 Parabéns! Você completou: {habit.name}\n\n"
        message += f"💎 XP ganho: +{progress['xp_earned']}\n"
        message += f"📊 XP total: {progress['total_xp']}\n"
        message += f"🏆 Nível: {progress['level']}\n"
        message += f"🔥 Streak: {progress['streak_days']} dias\n\n"
        
        if progress['level_up']:
            message += f"🎊 PARABÉNS! Você subiu para o nível {progress['level']}!\n\n"
        
        if earned_badges:
            message += "🏅 Novas badges conquistadas:\n"
            for badge in earned_badges:
                message += f"• {badge['icon']} {badge['name']}: {badge['description']}\n"
            message += "\n"
        
        # Próximo nível
        next_level_xp = GamificationSystem.get_next_level_xp(progress['level'])
        if next_level_xp > 0:
            xp_needed = next_level_xp - progress['total_xp']
            message += f"📈 Próximo nível: {xp_needed} XP restantes\n\n"
        
        message += "💪 Continue assim! Use /habit amanhã para manter seu streak!"
        
        await update.message.reply_text(message)
        
    except Exception as e:
        logger.error(f"Erro no comando habit: {e}")
        await update.message.reply_text("❌ Ocorreu um erro. Tente novamente mais tarde.")
    finally:
        db.close()

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /stats (opcional)"""
    try:
        user_info = update.effective_user
        telegram_id = user_info.id
        
        db = next(get_db())
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        
        if not user:
            await update.message.reply_text("❌ Use /start para se cadastrar primeiro!")
            return
        
        stats = GamificationSystem.get_user_stats(user)
        
        message = (
            f"📊 Suas estatísticas:\n\n"
            f"🏆 Nível: {stats['level']}\n"
            f"💎 XP: {stats['xp']}\n"
            f"🔥 Streak atual: {stats['streak_days']} dias\n"
            f"✅ Hábitos completados: {stats['total_habits_completed']}\n"
            f"🏅 Badges: {stats['badges_count']}\n\n"
        )
        
        if stats['next_level_xp'] > 0:
            xp_needed = stats['next_level_xp'] - stats['xp']
            message += f"📈 Próximo nível: {xp_needed} XP restantes"
        
        await update.message.reply_text(message)
        
    except Exception as e:
        logger.error(f"Erro no comando stats: {e}")
        await update.message.reply_text("❌ Ocorreu um erro. Tente novamente mais tarde.")
    finally:
        db.close() 