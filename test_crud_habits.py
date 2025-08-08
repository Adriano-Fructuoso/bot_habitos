"""
Testes para comandos CRUD de hábitos
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram import Message, Update, User
from telegram.ext import ContextTypes

from bot.handlers.crud import (
    _add_habit_command,
    _delete_habit_command,
    _edit_habit_command,
    _set_reminder_command,
)
from models.models import Habit
from models.models import User as DBUser
from utils.repository import HabitRepository, ReminderRepository


@pytest.fixture
def mock_update():
    """Mock do Update do Telegram"""
    update = MagicMock(spec=Update)
    update.effective_user = MagicMock(spec=User)
    update.effective_user.id = 123456
    update.effective_user.username = "test_user"
    update.effective_user.first_name = "Test"
    update.effective_user.last_name = "User"
    update.message = MagicMock(spec=Message)
    update.message.reply_text = AsyncMock()
    return update


@pytest.fixture
def mock_context():
    """Mock do Context"""
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}
    return context


@pytest.fixture
def mock_db():
    """Mock do banco de dados"""
    db = MagicMock()
    return db


def test_add_habit_command_start(mock_update, mock_context, mock_db):
    """Testa início do comando /add_habit"""
    with patch('bot.handlers.get_db', return_value=iter([mock_db])):
        with patch('bot.handlers.get_or_create_user') as mock_get_user:
            with patch('bot.handlers.rate_limited', return_value=False):
                mock_get_user.return_value = MagicMock(spec=DBUser)
                mock_get_user.return_value.id = 1

                # Executa comando
                import asyncio
                asyncio.run(_add_habit_command(mock_update, mock_context))

                # Verifica se iniciou wizard
                assert mock_context.user_data["wizard_state"] == "adding_habit"
                assert mock_context.user_data["wizard_step"] == "name"

                # Verifica se enviou mensagem
                mock_update.message.reply_text.assert_called_once()


def test_edit_habit_command_list(mock_update, mock_context, mock_db):
    """Testa comando /edit_habit"""
    with patch('bot.handlers.get_db', return_value=iter([mock_db])):
        with patch('bot.handlers.get_or_create_user') as mock_get_user:
            with patch('bot.handlers.rate_limited', return_value=False):
                with patch('utils.repository.HabitRepository.get_habits') as mock_get_habits:
                    mock_get_user.return_value = MagicMock(spec=DBUser)
                    mock_get_user.return_value.id = 1

                    # Mock hábitos
                    habit1 = MagicMock(spec=Habit)
                    habit1.id = 1
                    habit1.name = "Meditar"
                    habit1.xp_reward = 10
                    habit1.is_active = True

                    habit2 = MagicMock(spec=Habit)
                    habit2.id = 2
                    habit2.name = "Exercício"
                    habit2.xp_reward = 15
                    habit2.is_active = False

                    mock_get_habits.return_value = [habit1, habit2]

                    # Executa comando
                    import asyncio
                    asyncio.run(_edit_habit_command(mock_update, mock_context))

                    # Verifica se enviou mensagem com botões
                    mock_update.message.reply_text.assert_called_once()


def test_delete_habit_command_list(mock_update, mock_context, mock_db):
    """Testa comando /delete_habit"""
    with patch('bot.handlers.get_db', return_value=iter([mock_db])):
        with patch('bot.handlers.get_or_create_user') as mock_get_user:
            with patch('bot.handlers.rate_limited', return_value=False):
                with patch('utils.repository.HabitRepository.get_habits') as mock_get_habits:
                    mock_get_user.return_value = MagicMock(spec=DBUser)
                    mock_get_user.return_value.id = 1

                    # Mock hábitos
                    habit = MagicMock(spec=Habit)
                    habit.id = 1
                    habit.name = "Meditar"
                    habit.xp_reward = 10
                    habit.is_active = True

                    mock_get_habits.return_value = [habit]

                    # Executa comando
                    import asyncio
                    asyncio.run(_delete_habit_command(mock_update, mock_context))

                    # Verifica se enviou mensagem de confirmação
                    mock_update.message.reply_text.assert_called_once()


def test_set_reminder_command_list(mock_update, mock_context, mock_db):
    """Testa comando /set_reminder"""
    with patch('bot.handlers.get_db', return_value=iter([mock_db])):
        with patch('bot.handlers.get_or_create_user') as mock_get_user:
            with patch('bot.handlers.rate_limited', return_value=False):
                with patch('utils.repository.HabitRepository.get_habits') as mock_get_habits:
                    mock_get_user.return_value = MagicMock(spec=DBUser)
                    mock_get_user.return_value.id = 1

                    # Mock hábitos
                    habit = MagicMock(spec=Habit)
                    habit.id = 1
                    habit.name = "Meditar"
                    habit.xp_reward = 10
                    habit.is_active = True

                    mock_get_habits.return_value = [habit]

                    # Executa comando
                    import asyncio
                    asyncio.run(_set_reminder_command(mock_update, mock_context))

                    # Verifica se enviou mensagem
                    mock_update.message.reply_text.assert_called_once()


def test_habit_repository_create():
    """Testa criação de hábito no repositório"""
    with patch('sqlalchemy.orm.Session') as mock_session:
        mock_db = MagicMock()
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()
        
        # Mock user
        mock_user = MagicMock()
        mock_user.id = 1
        
        # Mock query chain para user
        mock_user_query = MagicMock()
        mock_user_filter = MagicMock()
        mock_user_filter.first.return_value = mock_user
        mock_user_query.filter.return_value = mock_user_filter
        
        # Mock query chain para hábitos
        mock_habit_query = MagicMock()
        mock_habit_filter = MagicMock()
        mock_habit_filter.count.return_value = 0  # 0 hábitos existentes
        mock_habit_query.filter.return_value = mock_habit_filter
        
        # Configura side_effect para retornar diferentes queries
        mock_db.query.side_effect = [mock_user_query, mock_habit_query]
        
        habit = HabitRepository.create_habit(
            mock_db, 
            user_id=1, 
            name="Test Habit", 
            xp_reward=10
        )
        
        assert habit is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()


def test_reminder_repository_create():
    """Testa criação de lembrete no repositório"""
    with patch('sqlalchemy.orm.Session') as mock_session:
        mock_db = MagicMock()
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()

        reminder = ReminderRepository.create_reminder(
            mock_db,
            user_id=1,
            habit_id=1,
            time="08:00",
            days="1,2,3,4,5"
        )

        assert reminder is not None
        mock_db.add.assert_called_once()
        # Commit é chamado 2 vezes: uma no delete_reminder e outra no create_reminder
        assert mock_db.commit.call_count == 2
        mock_db.refresh.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
