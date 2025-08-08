import os
import platform
import time
from functools import partial

from sqlalchemy import text

from db.session import SessionLocal
from utils.observability import get_health_metrics

from .handlers import safe_handler

# Timestamp de início do bot
START_TS = time.time()


async def _health_command(update, context):
    """Handler para o comando /health - verificação de saúde do sistema"""

    # Verificar conexão com banco de dados
    db_ok = False
    db_latency = 0

    try:
        start_time = time.time()
        with SessionLocal() as session:
            result = session.execute(text("SELECT 1"))
            result.fetchone()  # Executar a query
        db_latency = round((time.time() - start_time) * 1000, 2)  # ms
        db_ok = True
    except Exception as e:
        db_ok = False
        db_error = str(e)

    # Verificar versão do Alembic
    migration_ok = False
    migration_version = "unknown"

    try:
        with SessionLocal() as session:
            result = session.execute(
                text("SELECT version_num FROM alembic_version LIMIT 1")
            )
            row = result.fetchone()
            if row:
                migration_version = row[0]
                migration_ok = True
    except Exception:
        migration_ok = False

    # Obter métricas de observabilidade
    metrics = get_health_metrics()

    # Calcular uptime
    uptime_seconds = int(time.time() - START_TS)
    uptime_formatted = f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m {uptime_seconds % 60}s"

    # Status geral
    overall_status = "✅" if db_ok and migration_ok else "❌"

    # Montar mensagem
    msg = f"""
{overall_status} **Health Check**

**Database:**
• Status: {'✅ OK' if db_ok else '❌ FAIL'}
• Latency: {db_latency}ms
• Migration: {migration_version if migration_ok else '❌ FAIL'}

**System:**
• Uptime: {uptime_formatted}
• Python: {platform.python_version()}
• Environment: {os.getenv('APP_ENV', 'dev')}
• Version: {os.getenv('APP_VERSION', 'local')}

**Metrics:**
• Commands: {metrics['commands_executed']}
• Errors: {metrics['errors_total']}
• Habits: {metrics['habits_completed']}
• DB Queries: {metrics['db_queries']}

**Status:** {'🟢 Healthy' if db_ok and migration_ok else '🔴 Unhealthy'}
"""

    if not db_ok:
        msg += f"\n**DB Error:** {db_error}"

    await update.message.reply_text(msg, parse_mode="Markdown")


# Wrapper com safe_handler
health_command = partial(safe_handler, _health_command)
