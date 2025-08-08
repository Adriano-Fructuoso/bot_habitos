"""
Handlers para conversas estruturadas (criação de hábitos)
"""

import re
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from db.session import get_db
from models.models import User, Habit
from utils.repository import HabitRepository
from utils.branding import add_branding
from utils.keyboards import create_main_menu_keyboard
from .base import safe_handler

# Estados da conversa
(
    CHOOSING_ACTION,
    ENTERING_HABIT_NAME,
    ENTERING_DAYS_OF_WEEK,
    ENTERING_TIME_INVESTED,
    ENTERING_HABIT_DESCRIPTION,
    ENTERING_XP_REWARD,
    ENTERING_CATEGORY,
    CONFIRMING_HABIT,
    HABIT_CREATED
) = range(9)


@safe_handler
async def start_habit_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia o processo de criação de hábito"""
    user = update.effective_user
    
    # Verifica se está em conversa ativa do menu
    if context.user_data.get("conversation_active") and context.user_data.get("conversation_type") == "habit_creation":
        # Se já está em conversa, processa o texto como nome do hábito
        if update.message and update.message.text:
            return await handle_habit_name(update, context)
    
    # Verifica se é comando ou texto
    if update.message.text.startswith('/'):
        # Se for comando, inicia direto
        await update.message.reply_text(
            add_branding("""
📝 *Criando Novo Hábito*

Vamos criar seu hábito passo a passo!

**Digite o nome do hábito:**
Exemplo: "Beber água", "Exercício físico", "Ler 20 páginas"
"""),
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        return ENTERING_HABIT_NAME
    else:
        # Se for texto livre, pergunta se quer criar hábito
        keyboard = [
            ["✅ Sim, criar hábito"],
            ["❌ Não, cancelar"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            add_branding("""
🤔 *Você quer criar um novo hábito?*

Digite o nome de um hábito existente para completá-lo, ou escolha criar um novo:
"""),
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return CHOOSING_ACTION


@safe_handler
async def handle_action_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa a escolha do usuário"""
    text = update.message.text
    
    if "criar hábito" in text.lower():
        await update.message.reply_text(
            add_branding("""
📝 *Criando Novo Hábito*

**Digite o nome do hábito:**
Exemplo: "Beber água", "Exercício físico", "Ler 20 páginas"
"""),
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        return ENTERING_HABIT_NAME
    else:
        await update.message.reply_text(
            "❌ Criação cancelada. Use /menu para voltar ao menu principal.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END


@safe_handler
async def handle_habit_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa o nome do hábito"""
    habit_name = update.message.text.strip()
    
    if len(habit_name) < 2:
        await update.message.reply_text(
            "❌ Nome muito curto. Digite um nome com pelo menos 2 caracteres."
        )
        return ENTERING_HABIT_NAME
    
    # Salva o nome no contexto
    context.user_data['habit_name'] = habit_name
    
    # Mostra opções de dias da semana
    keyboard = [
        ["📅 Segunda a Sexta", "📅 Segunda a Domingo"],
        ["📅 Apenas Finais de Semana", "📅 Todos os dias"],
        ["📅 Personalizado", "❌ Cancelar"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        add_branding(f"""
📅 *Dias de Repetição*

**Em quais dias você quer fazer "{habit_name}"?**

• 📅 Segunda a Sexta - Dias úteis
• 📅 Segunda a Domingo - Todos os dias
• 📅 Apenas Finais de Semana - Sábado e Domingo
• 📅 Todos os dias - Diariamente
• 📅 Personalizado - Escolher dias específicos
"""),
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    return ENTERING_DAYS_OF_WEEK


@safe_handler
async def handle_days_of_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa os dias da semana"""
    choice = update.message.text.strip()
    
    if "cancelar" in choice.lower():
        await update.message.reply_text(
            "❌ Criação cancelada. Use /menu para voltar ao menu principal.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    # Verifica se está processando escolha personalizada
    if context.user_data.get('temp_days_choice') == 'personalizado':
        # Processa a escolha personalizada
        selected_days = []
        
        # Mapeia nomes dos dias para números
        day_map = {
            "segunda": 1, "terça": 2, "quarta": 3, "quinta": 4,
            "sexta": 5, "sábado": 6, "domingo": 7
        }
        
        for day_name, day_num in day_map.items():
            if day_name in choice.lower():
                selected_days.append(day_num)
        
        if selected_days:
            days_of_week = ",".join(map(str, sorted(selected_days)))
            context.user_data['days_of_week'] = days_of_week
            # Remove flag temporária
            context.user_data.pop('temp_days_choice', None)
        else:
            # Se não selecionou nenhum dia, volta a pedir
            await update.message.reply_text(
                add_branding("""
❌ *Nenhum dia selecionado*

Por favor, escolha pelo menos um dia da semana.
"""),
                parse_mode="Markdown"
            )
            return ENTERING_DAYS_OF_WEEK
    else:
        # Processa escolhas padrão
        days_map = {
            "segunda a sexta": "1,2,3,4,5",  # Segunda=1, Terça=2, etc.
            "segunda a domingo": "1,2,3,4,5,6,7",
            "apenas finais de semana": "6,7",  # Sábado=6, Domingo=7
            "todos os dias": "1,2,3,4,5,6,7"
        }
        
        days_of_week = "1,2,3,4,5,6,7"  # padrão: todos os dias
        for key, value in days_map.items():
            if key in choice.lower():
                days_of_week = value
                break
        
        # Se for personalizado, pede para escolher
        if "personalizado" in choice.lower():
            keyboard = [
                ["✅ Segunda", "✅ Terça", "✅ Quarta"],
                ["✅ Quinta", "✅ Sexta", "✅ Sábado"],
                ["✅ Domingo", "❌ Cancelar"]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            
            await update.message.reply_text(
                add_branding("""
📅 *Escolha os dias específicos:*

Clique nos dias que você quer fazer o hábito.
Depois clique em "Confirmar" ou "Cancelar".
"""),
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            # Salva temporariamente a escolha
            context.user_data['temp_days_choice'] = 'personalizado'
            return ENTERING_DAYS_OF_WEEK
        
        context.user_data['days_of_week'] = days_of_week
    
    # Mostra opções de tempo investido
    keyboard = [
        ["⏱️ 15 minutos", "⏱️ 30 minutos"],
        ["⏱️ 45 minutos", "⏱️ 1 hora"],
        ["⏱️ 1.5 horas", "⏱️ 2 horas"],
        ["⏱️ Personalizado", "❌ Cancelar"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        add_branding(f"""
⏱️ *Tempo Investido*

**Quanto tempo você vai investir em "{context.user_data['habit_name']}"?**

• ⏱️ 15 minutos - Hábito rápido
• ⏱️ 30 minutos - Hábito médio
• ⏱️ 45 minutos - Hábito moderado
• ⏱️ 1 hora - Hábito longo
• ⏱️ 1.5 horas - Hábito extenso
• ⏱️ 2 horas - Hábito muito longo
• ⏱️ Personalizado - Definir tempo específico
"""),
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    return ENTERING_TIME_INVESTED


@safe_handler
async def handle_time_invested(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa o tempo investido"""
    choice = update.message.text.strip()
    
    if "cancelar" in choice.lower():
        await update.message.reply_text(
            "❌ Criação cancelada. Use /menu para voltar ao menu principal.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    # Verifica se está processando tempo personalizado
    if context.user_data.get('temp_time_choice') == 'personalizado':
        try:
            # Tenta converter para número
            time_minutes = int(choice)
            if time_minutes > 0 and time_minutes <= 480:  # Máximo 8 horas
                context.user_data['time_minutes'] = time_minutes
                # Remove flag temporária
                context.user_data.pop('temp_time_choice', None)
            else:
                await update.message.reply_text(
                    add_branding("""
❌ *Tempo inválido*

Por favor, digite um número entre 1 e 480 minutos.
"""),
                    parse_mode="Markdown"
                )
                return ENTERING_TIME_INVESTED
        except ValueError:
            await update.message.reply_text(
                add_branding("""
❌ *Formato inválido*

Por favor, digite apenas números (exemplo: 30, 45, 90).
"""),
                parse_mode="Markdown"
            )
            return ENTERING_TIME_INVESTED
    else:
        # Processa escolhas padrão
        time_map = {
            "15 minutos": 15,
            "30 minutos": 30,
            "45 minutos": 45,
            "1 hora": 60,
            "1.5 horas": 90,
            "2 horas": 120
        }
        
        time_minutes = 30  # padrão: 30 minutos
        for key, value in time_map.items():
            if key in choice.lower():
                time_minutes = value
                break
        
        # Se for personalizado, pede para digitar
        if "personalizado" in choice.lower():
            await update.message.reply_text(
                add_branding("""
⏱️ *Tempo Personalizado*

**Digite o tempo em minutos:**
Exemplo: 20, 45, 90, 120

Ou digite "cancelar" para cancelar.
"""),
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardRemove()
            )
            context.user_data['temp_time_choice'] = 'personalizado'
            return ENTERING_TIME_INVESTED
        
        context.user_data['time_minutes'] = time_minutes
    
    # Pede descrição
    await update.message.reply_text(
        add_branding(f"""
📝 *Descrição (Opcional)*

**Digite uma descrição para "{context.user_data['habit_name']}":**
Exemplo: "Beber 2L de água por dia", "30 minutos de exercício"

Ou digite "pular" para continuar sem descrição.
"""),
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return ENTERING_HABIT_DESCRIPTION


@safe_handler
async def handle_habit_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa a descrição do hábito"""
    description = update.message.text.strip()
    
    if description.lower() in ['pular', 'skip', 'não', 'nao']:
        description = None
    
    context.user_data['habit_description'] = description
    
    await update.message.reply_text(
        add_branding(f"""
💎 *XP Reward*

**Quantos pontos XP este hábito deve dar?**
• 5 XP = Hábito fácil
• 10 XP = Hábito médio  
• 15 XP = Hábito difícil
• 20 XP = Hábito muito difícil

Digite um número de 1 a 50:
"""),
        parse_mode="Markdown"
    )
    return ENTERING_XP_REWARD


@safe_handler
async def handle_xp_reward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa o XP reward"""
    try:
        xp_reward = int(update.message.text.strip())
        if xp_reward < 1 or xp_reward > 50:
            await update.message.reply_text(
                "❌ XP deve ser entre 1 e 50. Digite novamente:"
            )
            return ENTERING_XP_REWARD
    except ValueError:
        await update.message.reply_text(
            "❌ Digite um número válido entre 1 e 50:"
        )
        return ENTERING_XP_REWARD
    
    context.user_data['xp_reward'] = xp_reward
    
    # Mostra categorias disponíveis
    keyboard = [
        ["🏃‍♂️ Saúde", "📚 Educação"],
        ["💼 Trabalho", "🏠 Casa"],
        ["💰 Finanças", "🎯 Pessoal"],
        ["❌ Cancelar"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        add_branding(f"""
📂 *Categoria*

**Escolha uma categoria para o hábito:**
• 🏃‍♂️ Saúde - Exercícios, alimentação, sono
• 📚 Educação - Leitura, estudos, cursos
• 💼 Trabalho - Produtividade, organização
• 🏠 Casa - Limpeza, organização
• 💰 Finanças - Economia, investimentos
• 🎯 Pessoal - Meditação, hobbies, relacionamentos
"""),
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    return ENTERING_CATEGORY


@safe_handler
async def handle_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa a categoria do hábito"""
    category_text = update.message.text.strip()
    
    if "cancelar" in category_text.lower():
        await update.message.reply_text(
            "❌ Criação cancelada. Use /menu para voltar ao menu principal.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    # Mapeia emoji para categoria
    category_map = {
        "🏃‍♂️": "saude",
        "📚": "educacao", 
        "💼": "trabalho",
        "🏠": "casa",
        "💰": "financas",
        "🎯": "pessoal"
    }
    
    category = "pessoal"  # padrão
    for emoji, cat in category_map.items():
        if emoji in category_text:
            category = cat
            break
    
    context.user_data['category'] = category
    
    # Mostra resumo para confirmação
    habit_name = context.user_data['habit_name']
    days_of_week = context.user_data.get('days_of_week', 'Todos os dias')
    time_minutes = context.user_data.get('time_minutes', 30)
    description = context.user_data.get('habit_description', 'Sem descrição')
    xp_reward = context.user_data['xp_reward']
    
    # Converte dias para texto legível
    days_text = {
        "1,2,3,4,5": "Segunda a Sexta",
        "1,2,3,4,5,6,7": "Todos os dias",
        "6,7": "Finais de semana"
    }.get(days_of_week, f"Dias: {days_of_week}")
    
    # Converte tempo para texto legível
    time_text = f"{time_minutes} minutos"
    if time_minutes >= 60:
        hours = time_minutes // 60
        minutes = time_minutes % 60
        time_text = f"{hours}h {minutes}min" if minutes > 0 else f"{hours}h"
    
    summary = f"""
📋 *Resumo do Hábito*

**Nome:** {habit_name}
**Dias:** {days_text}
**Tempo:** {time_text}
**Descrição:** {description}
**XP:** {xp_reward} pontos
**Categoria:** {category.title()}

**Confirma as informações?**
"""
    
    keyboard = [
        ["✅ Confirmar e criar"],
        ["❌ Cancelar e recomeçar"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        add_branding(summary),
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    return CONFIRMING_HABIT


@safe_handler
async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa a confirmação do hábito"""
    choice = update.message.text.strip()
    
    if "cancelar" in choice.lower():
        # Limpa dados e recomeça
        context.user_data.clear()
        await update.message.reply_text(
            "🔄 Vamos recomeçar! Digite /addhabits para criar um novo hábito.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    # Cria o hábito
    user = update.effective_user
    db = next(get_db())
    
    try:
        # Busca ou cria usuário
        from utils.gamification import get_or_create_user
        db_user = get_or_create_user(
            db=db,
            telegram_user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        # Cria o hábito usando o repositório
        habit = HabitRepository.create_habit(
            db=db,
            user_id=user.id,  # telegram_user_id
            name=context.user_data['habit_name'],
            description=context.user_data.get('habit_description'),
            xp_reward=context.user_data['xp_reward'],
            category=context.user_data['category'],
            days_of_week=context.user_data.get('days_of_week', '1,2,3,4,5,6,7'),
            time_minutes=context.user_data.get('time_minutes', 30)
        )
        
        # Mensagem de sucesso
        success_message = f"""
✅ *Hábito Criado com Sucesso!*

🎯 **{habit.name}**
📝 {habit.description or 'Sem descrição'}
💎 {habit.xp_reward} XP
📂 {habit.category.title()}

**Agora você pode:**
• Completar este hábito usando botões
• Digite "{habit.name}" para completar por texto
• Use /habits para ver todos os hábitos
• Use /menu para voltar ao menu principal
"""
        
        # Verifica se veio do menu
        if context.user_data.get("conversation_active") and context.user_data.get("conversation_type") == "habit_creation":
            # Se veio do menu, volta ao menu principal
            from utils.keyboards import create_main_menu_keyboard
            await update.message.reply_text(
                add_branding(success_message),
                parse_mode="Markdown",
                reply_markup=create_main_menu_keyboard()
            )
        else:
            # Se veio de comando, mostra menu normal
            await update.message.reply_text(
                add_branding(success_message),
                parse_mode="Markdown",
                reply_markup=create_main_menu_keyboard()
            )
        
        # Limpa dados da conversa
        context.user_data.clear()
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ Erro ao criar hábito: {str(e)}",
            reply_markup=ReplyKeyboardRemove()
        )
    finally:
        db.close()
    
    return ConversationHandler.END


@safe_handler
async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela a conversa"""
    await update.message.reply_text(
        "❌ Criação de hábito cancelada. Use /menu para voltar ao menu principal.",
        reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END


# Cria o ConversationHandler
habit_creation_handler = ConversationHandler(
    entry_points=[
        CommandHandler("addhabits", start_habit_creation),
        MessageHandler(filters.Regex(r"^(criar|novo|adicionar)\s+hábito"), start_habit_creation),
        # Entry point para quando vem do menu
        MessageHandler(filters.TEXT & ~filters.COMMAND, start_habit_creation),
    ],
    states={
        CHOOSING_ACTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_action_choice)
        ],
        ENTERING_HABIT_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_habit_name)
        ],
        ENTERING_DAYS_OF_WEEK: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_days_of_week)
        ],
        ENTERING_TIME_INVESTED: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_time_invested)
        ],
        ENTERING_HABIT_DESCRIPTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_habit_description)
        ],
        ENTERING_XP_REWARD: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_xp_reward)
        ],
        ENTERING_CATEGORY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_category)
        ],
        CONFIRMING_HABIT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_confirmation)
        ],
    },
    fallbacks=[
        CommandHandler("cancel", cancel_conversation),
        MessageHandler(filters.Regex(r"^(cancelar|cancel|sair)"), cancel_conversation)
    ],
    name="habit_creation",
    persistent=False
)
