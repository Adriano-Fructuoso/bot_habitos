from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.models import User, Habit, DailyLog, Badge, Streak, DailyRating, Achievement
from config import (
    DEFAULT_HABITS, BADGES, ACHIEVEMENTS, MOTIVATIONAL_MESSAGES,
    XP_PER_LEVEL, STREAK_MULTIPLIER, PERFECT_DAY_BONUS, WEEKLY_BONUS, MONTHLY_BONUS
)
import random

def calculate_xp_earned(base_xp, streak_days, difficulty_multiplier=1.0):
    """Calcula XP ganho com base no XP base, streak e dificuldade"""
    streak_bonus = min(streak_days * 2, 20)  # Máximo de 20 XP de bônus por streak
    total_xp = int((base_xp + streak_bonus) * difficulty_multiplier)
    return total_xp

def calculate_level(total_xp):
    """Calcula o nível atual baseado no XP total"""
    level = 1
    xp_needed = XP_PER_LEVEL
    
    while total_xp >= xp_needed:
        total_xp -= xp_needed
        level += 1
        xp_needed = int(xp_needed * 1.2)  # Aumenta 20% a cada nível
    
    return level

def update_user_progress(db: Session, user_id: int, habit_id: int, xp_earned: int):
    """Atualiza o progresso do usuário após completar um hábito"""
    user = db.query(User).filter(User.telegram_id == user_id).first()
    if not user:
        return None
    
    # Atualiza XP e nível
    old_level = user.current_level
    user.total_xp_earned += xp_earned
    user.current_level = calculate_level(user.total_xp_earned)
    
    # Atualiza streak
    user.current_streak += 1
    if user.current_streak > user.longest_streak:
        user.longest_streak = user.current_streak
    
    # Verifica se subiu de nível
    level_up = user.current_level > old_level
    
    db.commit()
    
    return {
        'user': user,
        'level_up': level_up,
        'old_level': old_level,
        'new_level': user.current_level,
        'xp_earned': xp_earned
    }

def update_habit_streak(db: Session, user_id: int, habit_id: int):
    """Atualiza o streak de um hábito específico"""
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == user_id
    ).first()
    
    if not habit:
        return None
    
    habit.current_streak += 1
    habit.total_completions += 1
    
    if habit.current_streak > habit.longest_streak:
        habit.longest_streak = habit.current_streak
    
    db.commit()
    return habit

def check_and_award_badges(db: Session, user_id: int):
    """Verifica e concede badges baseado no progresso do usuário"""
    user = db.query(User).filter(User.telegram_id == user_id).first()
    if not user:
        return []
    
    awarded_badges = []
    
    # Verifica badges existentes
    existing_badges = {badge.name: badge for badge in user.badges}
    
    # Badge: Primeiro hábito
    if 'Primeiro Passo' not in existing_badges and user.total_xp_earned > 0:
        badge_data = BADGES['first_habit']
        badge = Badge(
            user_id=user.id,
            name=badge_data['name'],
            description=badge_data['description'],
            icon=badge_data['icon'],
            category=badge_data['category'],
            is_rare=badge_data['is_rare'],
            xp_bonus=badge_data['xp_bonus']
        )
        db.add(badge)
        awarded_badges.append(badge)
    
    # Badge: Streak de 7 dias
    if 'Semana Perfeita' not in existing_badges and user.current_streak >= 7:
        badge_data = BADGES['week_streak']
        badge = Badge(
            user_id=user.id,
            name=badge_data['name'],
            description=badge_data['description'],
            icon=badge_data['icon'],
            category=badge_data['category'],
            is_rare=badge_data['is_rare'],
            xp_bonus=badge_data['xp_bonus']
        )
        db.add(badge)
        awarded_badges.append(badge)
    
    # Badge: Streak de 30 dias
    if 'Mestre da Consistência' not in existing_badges and user.current_streak >= 30:
        badge_data = BADGES['month_streak']
        badge = Badge(
            user_id=user.id,
            name=badge_data['name'],
            description=badge_data['description'],
            icon=badge_data['icon'],
            category=badge_data['category'],
            is_rare=badge_data['is_rare'],
            xp_bonus=badge_data['xp_bonus']
        )
        db.add(badge)
        awarded_badges.append(badge)
    
    # Badges de nível
    level_badges = {
        5: 'Aprendiz',
        10: 'Veterano',
        20: 'Mestre'
    }
    
    for level, badge_name in level_badges.items():
        if badge_name not in existing_badges and user.current_level >= level:
            badge_key = f'level_{level}'
            badge_data = BADGES[badge_key]
            badge = Badge(
                user_id=user.id,
                name=badge_data['name'],
                description=badge_data['description'],
                icon=badge_data['icon'],
                category=badge_data['category'],
                is_rare=badge_data['is_rare'],
                xp_bonus=badge_data['xp_bonus']
            )
            db.add(badge)
            awarded_badges.append(badge)
    
    # Badge: Dia perfeito
    if 'Dia Perfeito' not in existing_badges:
        today_logs = db.query(DailyLog).filter(
            DailyLog.user_id == user.id,
            DailyLog.date >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        ).all()
        
        if today_logs and all(log.completed for log in today_logs):
            badge_data = BADGES['perfect_day']
            badge = Badge(
                user_id=user.id,
                name=badge_data['name'],
                description=badge_data['description'],
                icon=badge_data['icon'],
                category=badge_data['category'],
                is_rare=badge_data['is_rare'],
                xp_bonus=badge_data['xp_bonus']
            )
            db.add(badge)
            awarded_badges.append(badge)
    
    db.commit()
    return awarded_badges

def reset_streak_if_needed(db: Session, user_id: int):
    """Reseta o streak se o usuário não completou hábitos hoje"""
    user = db.query(User).filter(User.telegram_id == user_id).first()
    if not user:
        return False
    
    today = datetime.now().date()
    today_logs = db.query(DailyLog).filter(
        DailyLog.user_id == user.id,
        DailyLog.date >= datetime.combine(today, datetime.min.time())
    ).all()
    
    if not today_logs:
        user.current_streak = 0
        db.commit()
        return True
    
    return False

def get_user_stats(db: Session, user_id: int):
    """Obtém estatísticas completas do usuário"""
    user = db.query(User).filter(User.telegram_id == user_id).first()
    if not user:
        return None
    
    # Estatísticas de hábitos
    total_habits = db.query(Habit).filter(Habit.user_id == user.id).count()
    active_habits = db.query(Habit).filter(
        Habit.user_id == user.id,
        Habit.is_active == True
    ).count()
    
    # Estatísticas de logs
    total_logs = db.query(DailyLog).filter(DailyLog.user_id == user.id).count()
    completed_logs = db.query(DailyLog).filter(
        DailyLog.user_id == user.id,
        DailyLog.completed == True
    ).count()
    
    # Estatísticas de badges
    total_badges = len(user.badges)
    rare_badges = len([b for b in user.badges if b.is_rare])
    
    # Progresso para próximo nível
    current_level_xp = user.total_xp_earned
    for level in range(1, user.current_level):
        current_level_xp -= XP_PER_LEVEL * (1.2 ** (level - 1))
    
    next_level_xp = XP_PER_LEVEL * (1.2 ** (user.current_level - 1))
    level_progress = (current_level_xp / next_level_xp) * 100
    
    return {
        'user': user,
        'total_habits': total_habits,
        'active_habits': active_habits,
        'total_logs': total_logs,
        'completed_logs': completed_logs,
        'completion_rate': (completed_logs / total_logs * 100) if total_logs > 0 else 0,
        'total_badges': total_badges,
        'rare_badges': rare_badges,
        'level_progress': level_progress,
        'next_level_xp': next_level_xp,
        'current_level_xp': current_level_xp
    }

def check_perfect_week(db: Session, user_id: int):
    """Verifica se o usuário teve uma semana perfeita"""
    user = db.query(User).filter(User.telegram_id == user_id).first()
    if not user:
        return False
    
    week_ago = datetime.now() - timedelta(days=7)
    week_logs = db.query(DailyLog).filter(
        DailyLog.user_id == user.id,
        DailyLog.date >= week_ago,
        DailyLog.completed == True
    ).all()
    
    # Verifica se completou pelo menos um hábito por dia na semana
    days_with_habits = set(log.date.date() for log in week_logs)
    return len(days_with_habits) >= 7

def check_client_conquest(db: Session, user_id: int):
    """Verifica se o usuário completou todos os hábitos do dia"""
    user = db.query(User).filter(User.telegram_id == user_id).first()
    if not user:
        return False
    
    today = datetime.now().date()
    today_logs = db.query(DailyLog).filter(
        DailyLog.user_id == user.id,
        DailyLog.date >= datetime.combine(today, datetime.min.time())
    ).all()
    
    active_habits = db.query(Habit).filter(
        Habit.user_id == user.id,
        Habit.is_active == True
    ).count()
    
    completed_today = len([log for log in today_logs if log.completed])
    return completed_today >= active_habits

def get_daily_goal_progress(db: Session, user_id: int):
    """Obtém o progresso das metas diárias do usuário"""
    user = db.query(User).filter(User.telegram_id == user_id).first()
    if not user:
        return None
    
    today = datetime.now().date()
    today_logs = db.query(DailyLog).filter(
        DailyLog.user_id == user.id,
        DailyLog.date >= datetime.combine(today, datetime.min.time())
    ).all()
    
    completed_today = len([log for log in today_logs if log.completed])
    goal = user.daily_goal
    
    return {
        'completed': completed_today,
        'goal': goal,
        'progress': (completed_today / goal * 100) if goal > 0 else 0,
        'remaining': max(0, goal - completed_today)
    }

def get_motivational_message(message_type: str):
    """Retorna uma mensagem motivacional aleatória"""
    messages = MOTIVATIONAL_MESSAGES.get(message_type, MOTIVATIONAL_MESSAGES['encouragement'])
    return random.choice(messages)

def create_daily_rating(db: Session, user_id: int, mood_rating: float, energy_rating: float, 
                       craving_level: int = 0, notes: str = None):
    """Cria uma avaliação diária do usuário"""
    user = db.query(User).filter(User.telegram_id == user_id).first()
    if not user:
        return None
    
    # Verifica se já existe avaliação para hoje
    today = datetime.now().date()
    existing_rating = db.query(DailyRating).filter(
        DailyRating.user_id == user.id,
        DailyRating.date >= datetime.combine(today, datetime.min.time())
    ).first()
    
    if existing_rating:
        # Atualiza avaliação existente
        existing_rating.mood_rating = mood_rating
        existing_rating.energy_rating = energy_rating
        existing_rating.craving_level = craving_level
        existing_rating.notes = notes
        db.commit()
        return existing_rating
    
    # Cria nova avaliação
    progress = get_daily_goal_progress(db, user_id)
    daily_rating = DailyRating(
        user_id=user.id,
        mood_rating=mood_rating,
        energy_rating=energy_rating,
        craving_level=craving_level,
        notes=notes,
        goals_met=progress['completed'] if progress else 0,
        total_goals=progress['goal'] if progress else 0
    )
    
    db.add(daily_rating)
    db.commit()
    return daily_rating

def get_weekly_summary(db: Session, user_id: int):
    """Gera um resumo semanal do progresso do usuário"""
    user = db.query(User).filter(User.telegram_id == user_id).first()
    if not user:
        return None
    
    week_ago = datetime.now() - timedelta(days=7)
    
    # Logs da semana
    week_logs = db.query(DailyLog).filter(
        DailyLog.user_id == user.id,
        DailyLog.date >= week_ago
    ).all()
    
    # Avaliações da semana
    week_ratings = db.query(DailyRating).filter(
        DailyRating.user_id == user.id,
        DailyRating.date >= week_ago
    ).all()
    
    # Estatísticas
    total_completed = len([log for log in week_logs if log.completed])
    total_xp_earned = sum(log.xp_earned for log in week_logs if log.completed)
    
    # Médias das avaliações
    avg_mood = sum(r.mood_rating for r in week_ratings) / len(week_ratings) if week_ratings else 0
    avg_energy = sum(r.energy_rating for r in week_ratings) / len(week_ratings) if week_ratings else 0
    avg_craving = sum(r.craving_level for r in week_ratings) / len(week_ratings) if week_ratings else 0
    
    # Dias ativos
    active_days = len(set(log.date.date() for log in week_logs if log.completed))
    
    return {
        'user': user,
        'total_completed': total_completed,
        'total_xp_earned': total_xp_earned,
        'active_days': active_days,
        'avg_mood': round(avg_mood, 1),
        'avg_energy': round(avg_energy, 1),
        'avg_craving': round(avg_craving, 1),
        'week_ratings': week_ratings,
        'week_logs': week_logs
    }

def create_default_habits(db: Session, user_id: int):
    """Cria hábitos padrão para um novo usuário"""
    user = db.query(User).filter(User.telegram_id == user_id).first()
    if not user:
        return []
    
    created_habits = []
    
    for habit_key, habit_data in DEFAULT_HABITS.items():
        # Verifica se o hábito já existe
        existing_habit = db.query(Habit).filter(
            Habit.user_id == user.id,
            Habit.name == habit_data['name']
        ).first()
        
        if not existing_habit:
            habit = Habit(
                user_id=user.id,
                name=habit_data['name'],
                description=habit_data['description'],
                category=habit_data['category'],
                difficulty=habit_data['difficulty'],
                xp_reward=habit_data['xp_reward'],
                streak_bonus=habit_data['streak_bonus']
            )
            db.add(habit)
            created_habits.append(habit)
    
    db.commit()
    return created_habits 