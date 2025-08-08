"""
Utilitários para branding e formatação de mensagens
"""

from config import BRAND, FOOTER, OPCODES_SITE_URL


def add_branding(message: str, include_footer: bool = True) -> str:
    """
    Adiciona branding à mensagem.

    Args:
        message: Mensagem original
        include_footer: Se deve incluir o rodapé

    Returns:
        Mensagem com branding
    """
    if not include_footer:
        return message

    return message + FOOTER

def get_welcome_message() -> str:
    """
    Retorna mensagem de boas-vindas com branding.

    Returns:
        Mensagem de boas-vindas formatada
    """
    return f"""🎉 **Bem-vindo ao {BRAND}!**

Transforme seus hábitos em conquistas com gamificação inteligente!

**✨ O que você pode fazer:**
• 📝 Criar e gerenciar hábitos
• 🎯 Completar tarefas diárias
• 🔥 Manter streaks e ganhar XP
• 🏆 Desbloquear badges e conquistas
• 📊 Acompanhar seu progresso

**🚀 Comece agora:**
Use /habit para ver seus hábitos ou criar novos!

**💡 Dica:** Complete hábitos regularmente para ganhar XP e subir de nível.

{FOOTER}"""

def get_help_message() -> str:
    """
    Retorna mensagem de ajuda com branding.

    Returns:
        Mensagem de ajuda formatada
    """
    return f"""📚 **Ajuda - {BRAND}**

**🎮 Comandos disponíveis:**

**📝 Gerenciar Hábitos:**
• `/start` - Iniciar o bot
• `/habit` - Ver/criar hábitos
• `/habits` - Listar todos os hábitos

**📊 Progresso:**
• `/stats` - Suas estatísticas
• `/dashboard` - Dashboard completo
• `/weekly` - Resumo semanal

**⭐ Avaliações:**
• `/rating` - Avaliar seu dia

**🔧 Sistema:**
• `/health` - Status do sistema

**🎯 Como funciona:**

**XP e Níveis:**
• Complete hábitos para ganhar XP
• Suba de nível a cada 100 XP
• Streaks dão bônus de XP

**🔥 Streaks:**
• Mantenha consistência diária
• Streaks maiores = mais XP
• Quebre o ciclo e recomece!

**🏆 Conquistas:**
• Desbloqueie badges especiais
• Alcance marcos importantes
• Complete desafios ocultos

**🔒 Privacidade:**
• Seus dados são privados
• Não compartilhamos informações
• Você controla seus dados

**🌐 Saiba mais:**
Visite: {OPCODES_SITE_URL}

{FOOTER}"""

def get_motivational_message_with_branding(message_type: str) -> str:
    """
    Retorna mensagem motivacional com branding.

    Args:
        message_type: Tipo de mensagem

    Returns:
        Mensagem motivacional formatada
    """
    from config import MOTIVATIONAL_MESSAGES

    messages = MOTIVATIONAL_MESSAGES.get(message_type, ["💪 Continue assim!"])
    base_message = messages[0] if messages else "💪 Continue assim!"

    return add_branding(base_message, include_footer=True)

def get_error_message_with_branding(error_type: str = "general") -> str:
    """
    Retorna mensagem de erro com branding.

    Args:
        error_type: Tipo de erro

    Returns:
        Mensagem de erro formatada
    """
    error_messages = {
        "general": "❌ Ocorreu um erro. Tente novamente em alguns instantes.",
        "rate_limit": "⏳ Aguarde um momento antes de tentar novamente.",
        "invalid_input": "⚠️ Entrada inválida. Verifique e tente novamente.",
        "not_found": "🔍 Item não encontrado. Verifique se existe.",
        "permission": "🚫 Você não tem permissão para esta ação.",
    }

    message = error_messages.get(error_type, error_messages["general"])
    return add_branding(message, include_footer=True)

def get_success_message_with_branding(message: str) -> str:
    """
    Retorna mensagem de sucesso com branding.

    Args:
        message: Mensagem base

    Returns:
        Mensagem de sucesso formatada
    """
    return add_branding(f"✅ {message}", include_footer=True)

def get_info_message_with_branding(message: str) -> str:
    """
    Retorna mensagem informativa com branding.

    Args:
        message: Mensagem base

    Returns:
        Mensagem informativa formatada
    """
    return add_branding(f"ℹ️ {message}", include_footer=True)
