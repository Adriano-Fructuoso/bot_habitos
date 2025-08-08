"""
Handlers para mensagens de texto livre
"""

from telegram import Update
from telegram.ext import ContextTypes
from db.session import get_db
from models.models import User, Habit
from utils.repository import HabitRepository
from utils.branding import add_branding
from utils.keyboards import create_main_menu_keyboard
from .base import safe_handler


@safe_handler
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para mensagens de texto livre"""
    user = update.effective_user
    text = update.message.text.strip()
    
    # Ignora comandos (que começam com /)
    if text.startswith('/'):
        return
    
    # Verifica se está em uma conversa ativa
    if context.user_data.get('conversation_active'):
        # Se está em conversa de criação de hábito, deixa o ConversationHandler processar
        if context.user_data.get('conversation_type') == 'habit_creation':
            return  # Deixa o ConversationHandler processar
        # Para outros tipos de conversa, deixa o ConversationHandler processar
        return
    
    db = next(get_db())
    
    try:
        # Busca usuário
        db_user = db.query(User).filter(User.telegram_user_id == user.id).first()
        if not db_user:
            await update.message.reply_text("❌ Usuário não encontrado. Use /start para se registrar.")
            return
        
        # Processa o texto baseado no conteúdo
        response = await process_text_input(db, db_user, text, context)
        
        await update.message.reply_text(
            add_branding(response), 
            parse_mode="Markdown",
            reply_markup=create_main_menu_keyboard()
        )
        
    except Exception as e:
        error_message = f"❌ Erro ao processar mensagem: {str(e)}"
        await update.message.reply_text(error_message)
    finally:
        db.close()


async def process_text_input(db, db_user, text: str, context: ContextTypes.DEFAULT_TYPE):
    """Processa diferentes tipos de entrada de texto"""
    
    text_lower = text.lower()
    
    # Comandos de ajuda
    if any(word in text_lower for word in ['ajuda', 'help', 'como', 'o que']):
        return """
🤖 *Como usar o bot:*

**Comandos principais:**
• `/start` - Iniciar o bot
• `/menu` - Menu principal
• `/habits` - Ver meus hábitos
• `/stats` - Minhas estatísticas
• `/dashboard` - Dashboard completo

**Criar hábitos:**
• `/addhabits Nome do hábito`
• `/addhabits Nome XP descrição`

**Texto livre:**
• Digite o nome de um hábito para completá-lo
• "status" para ver progresso
• "menu" para menu principal
• "ajuda" para esta mensagem
"""
    
    # Verificar status/progresso
    if any(word in text_lower for word in ['status', 'progresso', 'como estou', 'estatísticas']):
        from utils.gamification import get_daily_goal_progress
        from utils.formatters import create_progress_table, create_summary_card
        
        progress = get_daily_goal_progress(db, db_user.id)
        
        # Adiciona dados extras para o card
        progress['current_level'] = db_user.current_level
        progress['current_streak'] = db_user.current_streak
        progress['xp_earned_today'] = sum(log.xp_earned for log in progress.get('logs', []))
        
        # Cria tabela e card
        table = create_progress_table(progress)
        card = create_summary_card(progress)
        
        return f"""
{card}

{table}

Continue assim! 💪
"""
    
    # Menu principal
    if any(word in text_lower for word in ['menu', 'opções', 'voltar']):
        return """
🎯 *Menu Principal*

Escolha uma opção nos botões abaixo ou digite:
• Nome de um hábito para completá-lo
• "status" para ver progresso
• "ajuda" para ajuda
"""
    
    # Tentar completar um hábito pelo nome
    habits = HabitRepository.get_habits(db, db_user.telegram_user_id, active_only=True)
    
    for habit in habits:
        if habit.name.lower() in text_lower or text_lower in habit.name.lower():
            # Completa o hábito
            from utils.gamification import complete_habit
            
            result = complete_habit(db, db_user.id, habit.id)
            
            if result['success']:
                return f"""
✅ *Hábito Completado!*

🎯 **{habit.name}**
💎 +{habit.xp_reward} XP
📈 Total: {result['new_total_xp']:,} XP
🏆 Nível: {result['new_level']}

{result['message']}
"""
            else:
                return f"❌ {result['message']}"
    
    # Se não encontrou nenhum hábito, oferece sugestões
    if habits:
        habit_names = [h.name for h in habits]
        suggestions = "\n".join([f"• {name}" for name in habit_names[:5]])
        
        return f"""
🤔 *Hábito não encontrado*

Você digitou: *"{text}"*

**Seus hábitos disponíveis:**
{suggestions}

**Dica:** Digite o nome exato do hábito para completá-lo!
"""
    else:
        return """
📝 *Nenhum hábito encontrado*

Você ainda não tem hábitos cadastrados.

**Para criar um hábito:**
• Use `/addhabits Nome do hábito`
• Exemplo: `/addhabits Beber água`

**Ou digite:**
• "ajuda" para mais informações
• "menu" para menu principal
"""


# Handler para mensagens de voz (se quiser adicionar no futuro)
@safe_handler
async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para mensagens de voz"""
    await update.message.reply_text(
        "🎤 Funcionalidade de voz ainda não implementada. "
        "Por favor, digite sua mensagem ou use os botões."
    )
