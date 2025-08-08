"""
Handlers para callbacks inline
"""

from functools import partial
from telegram import Update
from telegram.ext import ContextTypes
from db.session import get_db
from models.models import User, Habit, DailyLog, DailyRating
from utils.gamification import (
    calculate_xp_earned,
    update_user_progress,
    get_user_stats,
    get_daily_progress,
    get_motivational_message,
)
from utils.branding import add_branding, get_success_message_with_branding
from utils.idempotency import is_duplicate_callback
from utils.keyboards import (
    create_habit_edit_keyboard,
    create_reminder_config_keyboard,
    create_days_of_week_keyboard,
    create_habits_table_keyboard,
    create_main_menu_keyboard,
    create_navigation_keyboard,
    create_progress_keyboard,
)
from utils.validators import validate_callback_data
from app_types import CallbackAction
from .base import safe_handler


async def _complete_habit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para completar um hábito"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Parse callback data
        callback_data = validate_callback_data(query.data)
        habit_id = callback_data["habit_id"]
        user_id = query.from_user.id
        
        db = next(get_db())
        
        try:
            # ✅ ADICIONAR IDEMPOTÊNCIA
            if is_duplicate_callback(query.id, db):
                await query.edit_message_text("Comando já processado")
                return
            
            # Busca usuário e hábito
            db_user = db.query(User).filter(User.telegram_user_id == user_id).first()
            if not db_user:
                await query.edit_message_text("❌ Usuário não encontrado.")
                return
            
            habit = db.query(Habit).filter(
                Habit.id == habit_id,
                Habit.user_id == db_user.id,
                Habit.is_active == True
            ).first()
            
            if not habit:
                await query.edit_message_text("❌ Hábito não encontrado.")
                return
            
            # Verifica se já foi completado hoje
            from datetime import date
            today = date.today()
            
            existing_log = db.query(DailyLog).filter(
                DailyLog.user_id == db_user.id,
                DailyLog.habit_id == habit_id,
                DailyLog.completed_at >= today
            ).first()
            
            if existing_log:
                await query.edit_message_text("✅ Este hábito já foi completado hoje!")
                return
            
            # Registra conclusão
            xp_earned = calculate_xp_earned(habit.xp_reward, habit.current_streak)
            
            log = DailyLog(
                user_id=db_user.id,
                habit_id=habit_id,
                xp_earned=xp_earned
            )
            db.add(log)
            
            # Atualiza progresso do usuário
            update_user_progress(db, db_user.id, habit_id, xp_earned)
            
            # Atualiza streak do hábito
            habit.current_streak += 1
            habit.total_completions += 1
            if habit.current_streak > habit.longest_streak:
                habit.longest_streak = habit.current_streak
            
            db.commit()
            
            # Mensagem de sucesso
            success_message = f"""
✅ *Hábito Completado!*

🎯 **{habit.name}**
⭐ +{xp_earned} XP ganho
🔥 Streak: {habit.current_streak} dias
📊 Total: {habit.total_completions} vezes

{get_motivational_message('habit_completed')}
"""
            
            await query.edit_message_text(
                add_branding(success_message),
                parse_mode="Markdown"
            )
            
        finally:
            db.close()
    
    except Exception as e:
        await query.edit_message_text(f"❌ Erro: {str(e)}")


async def _rating_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para avaliar o dia"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Parse callback data
        callback_data = validate_callback_data(query.data)
        rating_value = int(callback_data["extra"])
        user_id = query.from_user.id
        
        db = next(get_db())
        
        try:
            # Busca usuário
            db_user = db.query(User).filter(User.telegram_user_id == user_id).first()
            if not db_user:
                await query.edit_message_text("❌ Usuário não encontrado.")
                return
            
            # Verifica se já avaliou hoje
            from datetime import date
            today = date.today()
            
            existing_rating = db.query(DailyRating).filter(
                DailyRating.user_id == db_user.id,
                DailyRating.rating_date == today
            ).first()
            
            if existing_rating:
                existing_rating.rating = rating_value
                message = "⭐ Avaliação atualizada!"
            else:
                rating = DailyRating(
                    user_id=db_user.id,
                    rating=rating_value
                )
                db.add(rating)
                message = "⭐ Avaliação registrada!"
            
            db.commit()
            
            # Emojis para cada rating
            emojis = {1: "😞", 2: "😐", 3: "😊", 4: "🤩"}
            emoji = emojis.get(rating_value, "⭐")
            
            await query.edit_message_text(f"{emoji} {message}")
            
        finally:
            db.close()
    
    except Exception as e:
        await query.edit_message_text(f"❌ Erro: {str(e)}")


async def _show_progress_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para mostrar progresso detalhado"""
    print(f"🔍 Progresso callback iniciado: {update.callback_query.data}")
    
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    callback_data = query.data
    
    print(f"📝 Callback data: {callback_data}")
    
    db = next(get_db())
    
    try:
        # Busca usuário
        db_user = db.query(User).filter(User.telegram_user_id == user_id).first()
        if not db_user:
            await query.edit_message_text("❌ Usuário não encontrado.")
            return
        
        # Busca estatísticas
        from utils.gamification import get_user_stats
        stats = get_user_stats(db, db_user.id)
        
        # Busca progresso diário
        from utils.gamification import get_daily_progress
        progress = get_daily_progress(db, db_user.id)
        
        # Determina o tipo de progresso baseado no callback
        if callback_data == "show_progress":
            # Mostra menu de opções
            message = f"""
📊 *Progresso Detalhado*

🎯 **Hoje**:
• Completados: {progress['completed']}/{progress['goal']}
• Taxa: {progress['progress']:.1f}%

🏆 **Geral**:
• Nível: {stats['current_level']}
• XP Total: {stats['total_xp_earned']:,}
• Streak: {stats['current_streak']} dias
• Melhor Streak: {stats['longest_streak']} dias

📅 **Histórico**:
• Dias desde início: {stats['days_since_start']}
• Total de hábitos: {stats['total_habits']}

Escolha o que você quer visualizar:
"""
            keyboard = create_progress_keyboard()
        
        elif callback_data == "progress_today":
            # Mostra progresso de hoje
            message = f"""
📊 *Progresso de Hoje*

🎯 **Status Atual**:
• Completados: {progress['completed']}/{progress['goal']}
• Taxa: {progress['progress']:.1f}%
• XP ganho hoje: {progress.get('xp_earned', 0)}

📋 **Hábitos para hoje**:
{chr(10).join([f"• {habit['name']} ({habit['xp_reward']} XP)" for habit in progress.get('habits', [])])}

🔥 **Motivação**:
{progress.get('motivation', 'Continue assim! Você está no caminho certo!')}
"""
            keyboard = create_navigation_keyboard()
        
        elif callback_data == "progress_week":
            # Mostra progresso da semana
            from utils.gamification import get_weekly_summary
            weekly = get_weekly_summary(db, db_user.id)
            
            if weekly:
                success_rate = (weekly['total_completed'] / len(weekly['week_logs']) * 100) if weekly['week_logs'] else 0
                message = f"""
📅 *Progresso da Semana*

📊 **Esta semana**:
• Hábitos completados: {weekly['total_completed']}
• Dias ativos: {weekly['active_days']}/7
• Taxa de sucesso: {success_rate:.1f}%
• XP ganho: {weekly['total_xp_earned']}

⭐ **Avaliações médias**:
• Humor: {weekly['avg_mood']}/10
• Energia: {weekly['avg_energy']}/10
"""
            else:
                message = "📅 *Progresso da Semana*\n\nNenhum dado disponível para esta semana."
            
            keyboard = create_navigation_keyboard()
        
        elif callback_data == "progress_month":
            # Mostra progresso do mês
            message = f"""
📈 *Progresso do Mês*

🏆 **Resumo mensal**:
• Nível atual: {stats['current_level']}
• XP total: {stats['total_xp_earned']:,}
• Streak atual: {stats['current_streak']} dias
• Melhor streak: {stats['longest_streak']} dias

📊 **Estatísticas**:
• Total de hábitos: {stats['total_habits']}
• Dias desde início: {stats['days_since_start']}
• Hábitos ativos: {stats['active_habits']}
"""
            keyboard = create_navigation_keyboard()
        
        elif callback_data.startswith("help_"):
            # Callbacks de ajuda
            help_type = callback_data.replace("help_", "")
            
            if help_type == "how_it_works":
                message = """
🎯 *Como Funciona*

O HabitBot é seu assistente pessoal para criar e manter hábitos saudáveis!

**📝 Criar Hábitos:**
• Defina nome, descrição e categoria
• Escolha dificuldade e XP
• Configure dias da semana
• Defina tempo estimado

**✅ Completar Hábitos:**
• Marque hábitos como completados
• Ganhe XP e aumente streaks
• Veja seu progresso em tempo real

**🏆 Sistema de Gamificação:**
• Ganhe XP por completar hábitos
• Mantenha streaks para bônus
• Suba de nível e desbloqueie conquistas
• Receba mensagens motivacionais
"""
            elif help_type == "commands":
                message = """
📝 *Comandos Disponíveis*

**Comandos principais:**
• `/start` - Inicia o bot
• `/menu` - Menu principal
• `/habit` - Criar hábito rápido
• `/stats` - Ver estatísticas
• `/rating` - Avaliar dia
• `/weekly` - Resumo semanal
• `/help` - Esta ajuda

**Comandos de hábitos:**
• `/habits` - Listar hábitos
• `/edithabits` - Editar hábitos
• `/delete_habit` - Deletar hábito

**Comandos de sistema:**
• `/health` - Status do bot
• `/backup` - Backup dos dados
"""
            elif help_type == "achievements":
                message = """
🏆 *Conquistas*

**Conquistas disponíveis:**

🔥 **Streaks:**
• 7 dias seguidos
• 30 dias seguidos
• 100 dias seguidos

📊 **Progresso:**
• Primeiro hábito
• 10 hábitos completados
• 100 hábitos completados

⭐ **Especiais:**
• Semana perfeita
• Mês perfeito
• Nível máximo
"""
            elif help_type == "streaks":
                message = """
🔥 *Sistema de Streaks*

**Como funcionam:**
• Complete hábitos consecutivamente
• Mantenha o streak ativo
• Ganhe bônus de XP
• Quebre recordes pessoais

**Bônus de Streak:**
• 3+ dias: +10% XP
• 7+ dias: +25% XP
• 30+ dias: +50% XP
• 100+ dias: +100% XP

**Dicas:**
• Não quebre o streak!
• Complete pelo menos 1 hábito por dia
• Use lembretes para não esquecer
"""
            elif help_type == "settings":
                message = """
⚙️ *Configurações*

**Configurações disponíveis:**

⏰ **Lembretes:**
• Configure horários
• Escolha dias da semana
• Ative/desative notificações

📊 **Notificações:**
• Progresso diário
• Streaks quebrados
• Conquistas desbloqueadas

🎯 **Metas:**
• Defina metas diárias
• Ajuste dificuldade
• Personalize XP
"""
            elif help_type == "faq":
                message = """
❓ *Perguntas Frequentes*

**Q: Como criar um hábito?**
A: Use "Criar Hábito" no menu ou `/habit`

**Q: Como completar hábitos?**
A: Use "Hábitos" no menu e marque como completado

**Q: Como ver meu progresso?**
A: Use "Ver Progresso" no menu

**Q: Como configurar lembretes?**
A: Use "Lembretes" no menu

**Q: Como resetar meu progresso?**
A: Entre em contato com o suporte
"""
            else:
                message = "❓ *Ajuda*\n\nEscolha uma opção para obter ajuda."
            
            keyboard = create_navigation_keyboard()
        
        else:
            # Fallback para outros callbacks
            message = "📊 *Progresso*\n\nEscolha uma opção para visualizar seu progresso."
            keyboard = create_progress_keyboard()
        
        print(f"📤 Enviando mensagem de progresso: {callback_data}")
        
        await query.edit_message_text(
            add_branding(message),
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        print(f"✅ Mensagem de progresso enviada com sucesso!")
    
    finally:
        db.close()


async def _edit_habit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para editar um hábito específico"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Parse callback data
        callback_data = validate_callback_data(query.data)
        habit_id = callback_data["habit_id"]
        user_id = query.from_user.id
        
        db = next(get_db())
        
        try:
            # Busca hábito
            from utils.repository import HabitRepository
            habit = HabitRepository.get_habit(db, habit_id, user_id)
            
            if not habit:
                await query.edit_message_text("❌ Hábito não encontrado.")
                return
            
            message = f"""
✏️ *Editar Hábito*

🎯 **{habit.name}**
⭐ XP: {habit.xp_reward}
🔥 Streak: {habit.current_streak} dias
📊 Total: {habit.total_completions} vezes

Escolha uma opção:
"""
            
            keyboard = create_habit_edit_keyboard(habit_id, habit.is_active)
            
            await query.edit_message_text(
                add_branding(message),
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        finally:
            db.close()
    
    except Exception as e:
        await query.edit_message_text(f"❌ Erro: {str(e)}")


async def _delete_habit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para deletar um hábito específico"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Parse callback data
        callback_data = validate_callback_data(query.data)
        habit_id = callback_data["habit_id"]
        user_id = query.from_user.id
        
        db = next(get_db())
        
        try:
            # Busca hábito
            from utils.repository import HabitRepository
            habit = HabitRepository.get_habit(db, habit_id, user_id)
            
            if not habit:
                await query.edit_message_text("❌ Hábito não encontrado.")
                return
            
            message = f"""
🗑️ *Confirmar Exclusão*

Tem certeza que deseja deletar o hábito:

**{habit.name}**?

Esta ação não pode ser desfeita.
"""
            
            keyboard = create_delete_confirmation_keyboard(habit_id)
            
            await query.edit_message_text(
                add_branding(message),
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        finally:
            db.close()
    
    except Exception as e:
        await query.edit_message_text(f"❌ Erro: {str(e)}")


async def _set_reminder_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para configurar lembrete"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Parse callback data
        callback_data = validate_callback_data(query.data)
        habit_id = callback_data["habit_id"]
        user_id = query.from_user.id
        
        db = next(get_db())
        
        try:
            # Busca hábito
            from utils.repository import HabitRepository
            habit = HabitRepository.get_habit(db, habit_id, user_id)
            
            if not habit:
                await query.edit_message_text("❌ Hábito não encontrado.")
                return
            
            # Verifica se já tem lembrete
            from utils.repository import ReminderRepository
            existing_reminder = ReminderRepository.get_reminder(db, user_id, habit_id)
            
            message = f"""
⏰ *Configurar Lembrete*

🎯 **{habit.name}**

Escolha uma opção:
"""
            
            keyboard = create_reminder_config_keyboard(habit_id, existing_reminder is not None)
            
            await query.edit_message_text(
                add_branding(message),
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        finally:
            db.close()
    
    except Exception as e:
        await query.edit_message_text(f"❌ Erro: {str(e)}")


# Wrappers para os callbacks
complete_habit_callback = safe_handler(_complete_habit_callback)
rating_callback = safe_handler(_rating_callback)
show_progress_callback = safe_handler(_show_progress_callback)
edit_habit_callback = safe_handler(_edit_habit_callback)
delete_habit_callback = safe_handler(_delete_habit_callback)
set_reminder_callback = safe_handler(_set_reminder_callback)


# Novos handlers para tabela de hábitos
@safe_handler
async def toggle_complete_habit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para marcar/desmarcar hábito na tabela"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Parse callback data
        habit_id = int(query.data.split('_')[-1])
        user_id = query.from_user.id
        
        # Pega hábitos selecionados do contexto
        selected_habits = context.user_data.get('selected_habits', [])
        
        # Toggle seleção
        if habit_id in selected_habits:
            selected_habits.remove(habit_id)
        else:
            selected_habits.append(habit_id)
        
        context.user_data['selected_habits'] = selected_habits
        
        # Recarrega a tabela
        from .menu import _show_habits_table
        await _show_habits_table(query, context)
        
    except Exception as e:
        await query.edit_message_text(f"❌ Erro: {str(e)}")


@safe_handler
async def confirm_selection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para confirmar seleção de hábitos"""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = query.from_user.id
        selected_habits = context.user_data.get('selected_habits', [])
        
        if not selected_habits:
            await query.edit_message_text("❌ Nenhum hábito selecionado!")
            return
        
        db = next(get_db())
        
        try:
            # Busca usuário
            db_user = db.query(User).filter(User.telegram_user_id == user_id).first()
            if not db_user:
                await query.edit_message_text("❌ Usuário não encontrado.")
                return
            
            total_xp_earned = 0
            completed_habits = []
            
            # Completa cada hábito selecionado
            for habit_id in selected_habits:
                habit = db.query(Habit).filter(
                    Habit.id == habit_id,
                    Habit.user_id == db_user.id,
                    Habit.is_active == True
                ).first()
                
                if habit:
                    # Verifica se já foi completado hoje
                    from datetime import date
                    today = date.today()
                    
                    existing_log = db.query(DailyLog).filter(
                        DailyLog.user_id == db_user.id,
                        DailyLog.habit_id == habit_id,
                        DailyLog.completed_at >= today
                    ).first()
                    
                    if not existing_log:
                        # Registra conclusão
                        xp_earned = calculate_xp_earned(habit.xp_reward, habit.current_streak)
                        
                        log = DailyLog(
                            user_id=db_user.id,
                            habit_id=habit_id,
                            xp_earned=xp_earned
                        )
                        db.add(log)
                        
                        # Atualiza progresso do usuário
                        update_user_progress(db, db_user.id, habit_id, xp_earned)
                        
                        # Atualiza streak do hábito
                        habit.current_streak += 1
                        habit.total_completions += 1
                        if habit.current_streak > habit.longest_streak:
                            habit.longest_streak = habit.current_streak
                        
                        total_xp_earned += xp_earned
                        completed_habits.append(habit.name)
            
            db.commit()
            
            # Mensagem de sucesso
            if completed_habits:
                success_message = f"""
✅ *Hábitos Completados com Sucesso!*

**Hábitos completados:**
{chr(10).join([f"• {name}" for name in completed_habits])}

**💎 XP Ganho:** +{total_xp_earned} XP
**📊 Total XP:** {db_user.total_xp_earned:,} XP
**🏆 Nível:** {db_user.current_level}

Parabéns! Continue assim! 🚀

⏰ Menu principal em 5 segundos...
"""
                
                await query.edit_message_text(
                    add_branding(success_message),
                    parse_mode="Markdown"
                )
                
                # Limpa seleção
                context.user_data.pop('selected_habits', None)
                
                # Após 5 segundos, mostra menu principal
                import asyncio
                await asyncio.sleep(5)
                
                await query.edit_message_text(
                    add_branding("🎯 *Menu Principal*\n\nEscolha uma opção:"),
                    parse_mode="Markdown",
                    reply_markup=create_main_menu_keyboard()
                )
            else:
                await query.edit_message_text("❌ Nenhum hábito foi completado!")
                
        finally:
            db.close()
        
    except Exception as e:
        await query.edit_message_text(f"❌ Erro: {str(e)}")


@safe_handler
async def clear_selection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para limpar seleção de hábitos"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Limpa seleção
        context.user_data.pop('selected_habits', None)
        
        # Recarrega a tabela
        from .menu import _show_habits_table
        await _show_habits_table(query, context)
        
    except Exception as e:
        await query.edit_message_text(f"❌ Erro: {str(e)}")


@safe_handler
async def edit_habit_full_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para editar hábito completo"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Parse callback data
        habit_id = int(query.data.split('_')[-1])
        user_id = query.from_user.id
        
        db = next(get_db())
        
        try:
            # Busca hábito
            from utils.repository import HabitRepository
            habit = HabitRepository.get_habit(db, habit_id, user_id)
            
            if not habit:
                await query.edit_message_text("❌ Hábito não encontrado.")
                return
            
            message = f"""
✏️ *Editar Hábito*

🎯 **{habit.name}**
📝 {habit.description or 'Sem descrição'}
💎 {habit.xp_reward} XP
📂 {habit.category.title() if habit.category else 'Sem categoria'}
⏰ {habit.time_minutes} minutos
📅 Dias: {habit.days_of_week or 'Todos os dias'}

Escolha o que deseja editar:
"""
            
            keyboard = create_habit_edit_keyboard(habit_id)
            
            await query.edit_message_text(
                add_branding(message),
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        finally:
            db.close()
    
    except Exception as e:
        await query.edit_message_text(f"❌ Erro: {str(e)}")
