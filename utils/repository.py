"""
Repositório para operações de CRUD de hábitos e lembretes
"""

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from models.models import Habit, Reminder, User
from utils.validators import (
    ValidationError,
    validate_habit_id,
    validate_habit_name,
    validate_user_id,
    validate_xp_reward,
)
from utils.cache import (
    cache,
    get_user_habits_cache_key,
    get_user_stats_cache_key,
    get_daily_progress_cache_key,
    invalidate_user_cache,
)

logger = logging.getLogger(__name__)


class RepositoryError(Exception):
    """Erro do repositório"""
    pass


class HabitNotFoundError(RepositoryError):
    """Hábito não encontrado"""
    pass


class UserNotFoundError(RepositoryError):
    """Usuário não encontrado"""
    pass


class HabitRepository:
    """Repositório para operações de hábitos"""

    @staticmethod
    def create_habit(
        db: Session,
        user_id: int,
        name: str,
        xp_reward: int = 10,
        description: str = None,
        category: str = "personal"
    ) -> Habit:
        """Cria um novo hábito"""
        try:
            # Validações
            user_id = validate_user_id(user_id)
            name = validate_habit_name(name)
            xp_reward = validate_xp_reward(xp_reward)

            # Verifica se usuário existe
            user = db.query(User).filter(User.telegram_user_id == user_id).first()
            if not user:
                raise UserNotFoundError(f"Usuário {user_id} não encontrado")

            # Verifica limite de hábitos
            existing_habits = db.query(Habit).filter(
                Habit.user_id == user.id,
                Habit.is_active == True
            ).count()

            if existing_habits >= 20:
                raise RepositoryError("Limite máximo de 20 hábitos atingido")

            # Cria hábito
            habit = Habit(
                user_id=user.id,
                name=name,
                xp_reward=xp_reward,
                description=description,
                category=category,
                is_active=True
            )

            db.add(habit)
            db.commit()
            db.refresh(habit)
            
            # Invalida cache do usuário
            invalidate_user_cache(user_id)
            
            logger.info(f"Hábito criado: {habit.id} - {name} para usuário {user_id}")
            return habit

        except ValidationError as e:
            db.rollback()
            raise RepositoryError(f"Erro de validação: {e}")
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao criar hábito: {e}")
            raise RepositoryError(f"Erro interno: {e}")

    @staticmethod
    def get_habits(db: Session, user_id: int, active_only: bool = True) -> list[Habit]:
        """Busca hábitos do usuário"""
        try:
            user_id = validate_user_id(user_id)
            
            # Tenta buscar do cache primeiro
            cache_key = get_user_habits_cache_key(user_id, active_only)
            cached_habits = cache.get(cache_key)
            if cached_habits is not None:
                return cached_habits
            
            user = db.query(User).filter(User.telegram_user_id == user_id).first()
            if not user:
                raise UserNotFoundError(f"Usuário {user_id} não encontrado")
            
            query = db.query(Habit).filter(Habit.user_id == user.id)
            if active_only:
                query = query.filter(Habit.is_active == True)
            
            habits = query.order_by(Habit.created_at.desc()).all()
            
            # Cacheia resultado por 5 minutos
            cache.set(cache_key, habits, 300)
            
            return habits
            
        except ValidationError as e:
            raise RepositoryError(f"Erro de validação: {e}")
        except Exception as e:
            logger.error(f"Erro ao buscar hábitos: {e}")
            raise RepositoryError(f"Erro interno: {e}")

    @staticmethod
    def get_habit(db: Session, habit_id: int, user_id: int) -> Optional[Habit]:
        """Busca um hábito específico"""
        try:
            habit_id = validate_habit_id(habit_id)
            user_id = validate_user_id(user_id)

            user = db.query(User).filter(User.telegram_user_id == user_id).first()
            if not user:
                raise UserNotFoundError(f"Usuário {user_id} não encontrado")

            habit = db.query(Habit).filter(
                Habit.id == habit_id,
                Habit.user_id == user.id
            ).first()

            if not habit:
                raise HabitNotFoundError(f"Hábito {habit_id} não encontrado")

            return habit

        except ValidationError as e:
            raise RepositoryError(f"Erro de validação: {e}")
        except Exception as e:
            logger.error(f"Erro ao buscar hábito: {e}")
            raise RepositoryError(f"Erro interno: {e}")

    @staticmethod
    def update_habit(
        db: Session,
        habit_id: int,
        user_id: int,
        **kwargs
    ) -> Optional[Habit]:
        """Atualiza um hábito"""
        try:
            habit = HabitRepository.get_habit(db, habit_id, user_id)

            # Validações específicas
            if 'name' in kwargs:
                kwargs['name'] = validate_habit_name(kwargs['name'])
            if 'xp_reward' in kwargs:
                kwargs['xp_reward'] = validate_xp_reward(kwargs['xp_reward'])

            # Atualiza campos
            for key, value in kwargs.items():
                if hasattr(habit, key):
                    setattr(habit, key, value)

            habit.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(habit)

            logger.info(f"Hábito atualizado: {habit_id}")
            return habit

        except ValidationError as e:
            db.rollback()
            raise RepositoryError(f"Erro de validação: {e}")
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao atualizar hábito: {e}")
            raise RepositoryError(f"Erro interno: {e}")

    @staticmethod
    def delete_habit(db: Session, habit_id: int, user_id: int) -> bool:
        """Deleta um hábito (soft delete)"""
        try:
            habit = HabitRepository.get_habit(db, habit_id, user_id)

            habit.is_active = False
            habit.updated_at = datetime.utcnow()
            db.commit()

            logger.info(f"Hábito deletado: {habit_id}")
            return True

        except ValidationError as e:
            db.rollback()
            raise RepositoryError(f"Erro de validação: {e}")
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao deletar hábito: {e}")
            raise RepositoryError(f"Erro interno: {e}")

    @staticmethod
    def toggle_habit(db: Session, habit_id: int, user_id: int) -> Optional[Habit]:
        """Ativa/desativa um hábito"""
        try:
            habit = HabitRepository.get_habit(db, habit_id, user_id)

            habit.is_active = not habit.is_active
            habit.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(habit)

            status = "ativado" if habit.is_active else "desativado"
            logger.info(f"Hábito {status}: {habit_id}")
            return habit

        except ValidationError as e:
            db.rollback()
            raise RepositoryError(f"Erro de validação: {e}")
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao alternar hábito: {e}")
            raise RepositoryError(f"Erro interno: {e}")


class ReminderRepository:
    """Repositório para operações de lembretes"""

    @staticmethod
    def create_reminder(
        db: Session,
        user_id: int,
        habit_id: int,
        time: str,  # HH:MM
        days: str,  # "1,2,3,4,5"
        timezone: str = "America/Sao_Paulo"
    ) -> Reminder:
        """Cria um novo lembrete"""
        try:
            from utils.validators import validate_days_format, validate_time_format

            # Validações
            user_id = validate_user_id(user_id)
            habit_id = validate_habit_id(habit_id)
            time = validate_time_format(time)
            days = validate_days_format(days)

            # Verifica se usuário e hábito existem
            user = db.query(User).filter(User.telegram_user_id == user_id).first()
            if not user:
                raise UserNotFoundError(f"Usuário {user_id} não encontrado")

            habit = db.query(Habit).filter(
                Habit.id == habit_id,
                Habit.user_id == user.id
            ).first()
            if not habit:
                raise HabitNotFoundError(f"Hábito {habit_id} não encontrado")

            # Remove lembrete existente para este hábito
            ReminderRepository.delete_reminder(db, user_id, habit_id)

            # Cria novo lembrete
            reminder = Reminder(
                user_id=user.id,
                habit_id=habit_id,
                time=time,
                days=days,
                timezone=timezone,
                enabled=True
            )

            db.add(reminder)
            db.commit()
            db.refresh(reminder)

            logger.info(f"Lembrete criado: {reminder.id} para hábito {habit_id}")
            return reminder

        except ValidationError as e:
            db.rollback()
            raise RepositoryError(f"Erro de validação: {e}")
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao criar lembrete: {e}")
            raise RepositoryError(f"Erro interno: {e}")

    @staticmethod
    def get_reminders(db: Session, user_id: int) -> list[Reminder]:
        """Busca lembretes do usuário"""
        try:
            user_id = validate_user_id(user_id)

            user = db.query(User).filter(User.telegram_user_id == user_id).first()
            if not user:
                raise UserNotFoundError(f"Usuário {user_id} não encontrado")

            return db.query(Reminder).filter(
                Reminder.user_id == user.id,
                Reminder.enabled == True
            ).all()

        except ValidationError as e:
            raise RepositoryError(f"Erro de validação: {e}")
        except Exception as e:
            logger.error(f"Erro ao buscar lembretes: {e}")
            raise RepositoryError(f"Erro interno: {e}")

    @staticmethod
    def get_reminder(db: Session, user_id: int, habit_id: int) -> Optional[Reminder]:
        """Busca lembrete específico"""
        try:
            user_id = validate_user_id(user_id)
            habit_id = validate_habit_id(habit_id)

            user = db.query(User).filter(User.telegram_user_id == user_id).first()
            if not user:
                raise UserNotFoundError(f"Usuário {user_id} não encontrado")

            return db.query(Reminder).filter(
                Reminder.user_id == user.id,
                Reminder.habit_id == habit_id,
                Reminder.enabled == True
            ).first()

        except ValidationError as e:
            raise RepositoryError(f"Erro de validação: {e}")
        except Exception as e:
            logger.error(f"Erro ao buscar lembrete: {e}")
            raise RepositoryError(f"Erro interno: {e}")

    @staticmethod
    def delete_reminder(db: Session, user_id: int, habit_id: int) -> bool:
        """Deleta um lembrete"""
        try:
            reminder = ReminderRepository.get_reminder(db, user_id, habit_id)
            if not reminder:
                return False

            reminder.enabled = False
            reminder.updated_at = datetime.utcnow()
            db.commit()

            logger.info(f"Lembrete deletado: {reminder.id}")
            return True

        except ValidationError as e:
            db.rollback()
            raise RepositoryError(f"Erro de validação: {e}")
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao deletar lembrete: {e}")
            raise RepositoryError(f"Erro interno: {e}")

    @staticmethod
    def get_all_active_reminders(db: Session) -> list[Reminder]:
        """Busca todos os lembretes ativos (para re-agendamento no startup)"""
        try:
            return db.query(Reminder).filter(Reminder.enabled == True).all()
        except Exception as e:
            logger.error(f"Erro ao buscar lembretes ativos: {e}")
            raise RepositoryError(f"Erro interno: {e}")
