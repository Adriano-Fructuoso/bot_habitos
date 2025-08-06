from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.models import User, Habit, DailyLog, Badge

class GamificationSystem:
    """Sistema de gamificação para o bot de hábitos"""
    
    # Configurações de XP e níveis
    XP_PER_HABIT = 10
    XP_PER_STREAK_DAY = 5
    XP_MULTIPLIER_AFTER_7_DAYS = 1.5
    
    # Configuração de níveis (XP necessário para cada nível)
    LEVEL_XP_REQUIREMENTS = {
        1: 0,
        2: 50,
        3: 150,
        4: 300,
        5: 500,
        6: 750,
        7: 1050,
        8: 1400,
        9: 1800,
        10: 2250
    }
    
    # Badges disponíveis
    AVAILABLE_BADGES = {
        "first_habit": {
            "name": "Primeiro Passo",
            "description": "Completou seu primeiro hábito",
            "icon": "🎯",
            "condition": lambda user: len(user.daily_logs) >= 1
        },
        "streak_3": {
            "name": "Consistente",
            "description": "Manteve streak por 3 dias",
            "icon": "🔥",
            "condition": lambda user: user.streak_days >= 3
        },
        "streak_7": {
            "name": "Semana Perfeita",
            "description": "Manteve streak por 7 dias",
            "icon": "⭐",
            "condition": lambda user: user.streak_days >= 7
        },
        "level_5": {
            "name": "Veterano",
            "description": "Atingiu o nível 5",
            "icon": "🏆",
            "condition": lambda user: user.level >= 5
        },
        "xp_1000": {
            "name": "Mestre dos Hábitos",
            "description": "Acumulou 1000 XP",
            "icon": "👑",
            "condition": lambda user: user.xp >= 1000
        }
    }
    
    @staticmethod
    def calculate_xp_earned(streak_days: int) -> int:
        """Calcula XP ganho baseado no streak atual"""
        base_xp = GamificationSystem.XP_PER_HABIT
        streak_bonus = streak_days * GamificationSystem.XP_PER_STREAK_DAY
        
        # Multiplicador após 7 dias de streak
        if streak_days >= 7:
            total_xp = (base_xp + streak_bonus) * GamificationSystem.XP_MULTIPLIER_AFTER_7_DAYS
        else:
            total_xp = base_xp + streak_bonus
            
        return int(total_xp)
    
    @staticmethod
    def calculate_level(xp: int) -> int:
        """Calcula o nível baseado no XP total"""
        for level, required_xp in sorted(GamificationSystem.LEVEL_XP_REQUIREMENTS.items(), reverse=True):
            if xp >= required_xp:
                return level
        return 1
    
    @staticmethod
    def update_user_progress(db: Session, user: User, xp_earned: int) -> dict:
        """Atualiza o progresso do usuário e retorna informações da atualização"""
        old_level = user.level
        old_xp = user.xp
        
        # Atualiza XP e nível
        user.xp += xp_earned
        user.level = GamificationSystem.calculate_level(user.xp)
        
        # Atualiza streak
        user.streak_days += 1
        
        # Salva no banco
        db.commit()
        
        # Verifica se subiu de nível
        level_up = user.level > old_level
        
        return {
            "xp_earned": xp_earned,
            "total_xp": user.xp,
            "level": user.level,
            "level_up": level_up,
            "streak_days": user.streak_days
        }
    
    @staticmethod
    def check_and_award_badges(db: Session, user: User) -> list:
        """Verifica e concede badges ao usuário"""
        earned_badges = []
        
        for badge_id, badge_info in GamificationSystem.AVAILABLE_BADGES.items():
            # Verifica se o usuário já tem essa badge
            existing_badge = db.query(Badge).filter(
                Badge.user_id == user.id,
                Badge.name == badge_info["name"]
            ).first()
            
            if not existing_badge and badge_info["condition"](user):
                # Concede a badge
                new_badge = Badge(
                    user_id=user.id,
                    name=badge_info["name"],
                    description=badge_info["description"],
                    icon=badge_info["icon"]
                )
                db.add(new_badge)
                earned_badges.append(badge_info)
        
        if earned_badges:
            db.commit()
            
        return earned_badges
    
    @staticmethod
    def reset_streak_if_needed(db: Session, user: User) -> bool:
        """Reseta o streak se o usuário não completou hábitos hoje"""
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        # Verifica se há logs de hoje
        today_logs = db.query(DailyLog).filter(
            DailyLog.user_id == user.id,
            DailyLog.completed_at >= today_start,
            DailyLog.completed_at <= today_end
        ).count()
        
        if today_logs == 0 and user.streak_days > 0:
            user.streak_days = 0
            db.commit()
            return True
            
        return False
    
    @staticmethod
    def get_user_stats(user: User) -> dict:
        """Retorna estatísticas do usuário"""
        return {
            "xp": user.xp,
            "level": user.level,
            "streak_days": user.streak_days,
            "total_habits_completed": len(user.daily_logs),
            "badges_count": len(user.badges),
            "next_level_xp": GamificationSystem.get_next_level_xp(user.level)
        }
    
    @staticmethod
    def get_next_level_xp(current_level: int) -> int:
        """Retorna XP necessário para o próximo nível"""
        next_level = current_level + 1
        return GamificationSystem.LEVEL_XP_REQUIREMENTS.get(next_level, 0) 