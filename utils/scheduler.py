"""
Scheduler para tarefas automáticas
"""

import asyncio
from asyncio import create_subprocess_shell

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app_types import CALLBACK_VERSION
from config import APP_ENV
from utils.logging_config import get_logger

logger = get_logger(__name__)

# Scheduler global
scheduler = AsyncIOScheduler()


def create_job_id(reminder_id: int) -> str:
    """Cria job_id único para lembretes"""
    return f"reminder_{CALLBACK_VERSION}_{reminder_id}"


async def send_habit_reminder(user_id: int, habit_id: int, habit_name: str):
    """Envia lembrete de hábito para o usuário"""
    try:
        logger.info(f"Enviando lembrete para usuário {user_id}, hábito {habit_id}")

        # Importa aqui para evitar circular imports
        from bot.main import application

        message = f"""
⏰ *Lembrete de Hábito*

🎯 *{habit_name}*

Hora de completar seu hábito!

Use /habit para marcar como completo.
"""

        await application.bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode="Markdown"
        )

        logger.info(f"Lembrete enviado com sucesso para usuário {user_id}")

    except Exception as e:
        logger.error(f"Erro ao enviar lembrete para usuário {user_id}: {e}")


def schedule_habit_reminder(reminder_id: int, user_id: int, habit_id: int, habit_name: str, time: str, days: str):
    """Agenda um lembrete de hábito com job_id idempotente"""
    try:
        # Parse time (HH:MM)
        hour, minute = map(int, time.split(':'))

        # Parse days (1,2,3,4,5 -> [1,2,3,4,5])
        day_list = [int(d) for d in days.split(',')]

        # Cria job_id único e idempotente
        job_id = create_job_id(reminder_id)

        # Remove job existente se houver
        try:
            scheduler.remove_job(job_id)
            logger.info(f"Job existente removido: {job_id}")
        except:
            pass

        # Adiciona novo job
        scheduler.add_job(
            lambda: asyncio.create_task(send_habit_reminder(user_id, habit_id, habit_name)),
            CronTrigger(
                day_of_week=day_list,
                hour=hour,
                minute=minute
            ),
            id=job_id,
            name=f"Lembrete {habit_name}",
            replace_existing=True
        )

        logger.info(f"Lembrete agendado: {job_id} - {habit_name} às {time} nos dias {days}")

    except Exception as e:
        logger.error(f"Erro ao agendar lembrete {reminder_id}: {e}")


def remove_habit_reminder(reminder_id: int):
    """Remove um lembrete de hábito"""
    try:
        job_id = create_job_id(reminder_id)
        scheduler.remove_job(job_id)
        logger.info(f"Lembrete removido: {job_id}")
    except Exception as e:
        logger.error(f"Erro ao remover lembrete {reminder_id}: {e}")


def load_all_reminders_on_startup():
    """Carrega todos os lembretes ativos no startup"""
    try:
        from db.session import SessionLocal
        from utils.repository import ReminderRepository

        with SessionLocal() as db:
            reminders = ReminderRepository.get_all_active_reminders(db)

            for reminder in reminders:
                try:
                    schedule_habit_reminder(
                        reminder.id,
                        reminder.user.telegram_user_id,
                        reminder.habit_id,
                        reminder.habit.name,
                        reminder.time,
                        reminder.days
                    )
                except Exception as e:
                    logger.error(f"Erro ao agendar lembrete {reminder.id}: {e}")

            logger.info(f"Carregados {len(reminders)} lembretes no startup")

    except Exception as e:
        logger.error(f"Erro ao carregar lembretes no startup: {e}")


async def backup_now():
    """Executa backup manual"""
    try:
        logger.info("🔄 Iniciando backup automático...")

        # Executar script de backup
        process = await create_subprocess_shell(
            "bash scripts/backup.sh",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            logger.info("✅ Backup automático concluído com sucesso")
            if stdout:
                logger.info(f"Backup output: {stdout.decode()}")
        else:
            logger.error(f"❌ Erro no backup automático: {stderr.decode()}")

    except Exception as e:
        logger.error(f"❌ Erro ao executar backup: {e}")

async def cleanup_old_data():
    """Limpa dados antigos (callbacks processados)"""
    try:
        logger.info("🧹 Iniciando limpeza de dados antigos...")

        from db.session import get_db
        from utils.idempotency import cleanup_old_callbacks

        db = next(get_db())
        try:
            cleanup_old_callbacks(minutes=60, db=db)  # Limpar callbacks de 1 hora atrás
            logger.info("✅ Limpeza de dados antigos concluída")
        finally:
            db.close()

    except Exception as e:
        logger.error(f"❌ Erro na limpeza de dados: {e}")

async def health_check():
    """Verificação de saúde periódica"""
    try:
        logger.info("🏥 Executando health check periódico...")

        from sqlalchemy import text

        from db.session import SessionLocal

        with SessionLocal() as session:
            result = session.execute(text("SELECT 1"))
            result.fetchone()

        logger.info("✅ Health check periódico: OK")

    except Exception as e:
        logger.error(f"❌ Health check periódico falhou: {e}")

def init_scheduler(app):
    """Inicializa o scheduler com as tarefas"""

    if APP_ENV == "development":
        logger.info("🔧 Modo desenvolvimento: scheduler desabilitado")
        return

    try:
        # Backup diário às 2h da manhã
        scheduler.add_job(
            lambda: app.create_task(backup_now()),
            CronTrigger(hour=2, minute=0),
            id='daily_backup',
            name='Backup Diário',
            replace_existing=True
        )

        # Limpeza de dados a cada 6 horas
        scheduler.add_job(
            lambda: app.create_task(cleanup_old_data()),
            CronTrigger(hour='*/6'),
            id='cleanup_data',
            name='Limpeza de Dados',
            replace_existing=True
        )

        # Health check a cada hora
        scheduler.add_job(
            lambda: app.create_task(health_check()),
            CronTrigger(minute=0),
            id='health_check',
            name='Health Check',
            replace_existing=True
        )

        # Iniciar scheduler
        scheduler.start()
        logger.info("🚀 Scheduler iniciado com sucesso")

        # Carregar lembretes existentes
        load_all_reminders_on_startup()

        # Log das tarefas agendadas
        for job in scheduler.get_jobs():
            logger.info(f"📅 Tarefa agendada: {job.name} - {job.next_run_time}")

    except Exception as e:
        logger.error(f"❌ Erro ao inicializar scheduler: {e}")

def stop_scheduler():
    """Para o scheduler"""
    try:
        if scheduler.running:
            scheduler.shutdown()
            logger.info("🛑 Scheduler parado")
    except Exception as e:
        logger.error(f"❌ Erro ao parar scheduler: {e}")

def get_scheduler_status():
    """Retorna status do scheduler"""
    return {
        "running": scheduler.running,
        "jobs_count": len(scheduler.get_jobs()),
        "jobs": [
            {
                "id": job.id,
                "name": job.name,
                "next_run": str(job.next_run_time) if job.next_run_time else None
            }
            for job in scheduler.get_jobs()
        ]
    }
