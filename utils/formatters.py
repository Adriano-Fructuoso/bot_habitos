"""
Utilitários para formatação de dados (tabelas, listas, etc.)
"""

from typing import List, Dict, Any


def create_table(data: List[Dict[str, Any]], headers: List[str] = None) -> str:
    """
    Cria uma tabela formatada em Markdown
    
    Args:
        data: Lista de dicionários com os dados
        headers: Lista de cabeçalhos (opcional)
    
    Returns:
        String formatada em Markdown
    """
    if not data:
        return "📋 *Nenhum dado disponível*"
    
    # Se não foram fornecidos headers, usa as chaves do primeiro item
    if not headers:
        headers = list(data[0].keys())
    
    # Cria o cabeçalho
    table = "| " + " | ".join(str(h) for h in headers) + " |\n"
    table += "|" + "|".join("---" for _ in headers) + "|\n"
    
    # Adiciona as linhas
    for row in data:
        table += "| " + " | ".join(str(row.get(h, "")) for h in headers) + " |\n"
    
    return table


def create_habits_table(habits: List[Dict[str, Any]]) -> str:
    """
    Cria uma tabela específica para hábitos
    
    Args:
        habits: Lista de hábitos
    
    Returns:
        String formatada em Markdown
    """
    if not habits:
        return "📋 *Nenhum hábito encontrado*"
    
    # Formata os dados dos hábitos
    table_data = []
    for habit in habits:
        status = "✅" if habit.get('completed_today') else "⏳"
        streak = f"🔥 {habit.get('current_streak', 0)}"
        
        table_data.append({
            "Status": status,
            "Hábito": habit.get('name', ''),
            "XP": f"💎 {habit.get('xp_reward', 0)}",
            "Streak": streak,
            "Categoria": habit.get('category', '').title()
        })
    
    return create_table(table_data)


def create_progress_table(progress_data: Dict[str, Any]) -> str:
    """
    Cria uma tabela de progresso diário
    
    Args:
        progress_data: Dados de progresso
    
    Returns:
        String formatada em Markdown
    """
    if not progress_data:
        return "📊 *Nenhum dado de progresso disponível*"
    
    # Cria linhas de progresso
    rows = []
    
    # Progresso geral
    completed = progress_data.get('completed', 0)
    goal = progress_data.get('goal', 0)
    percentage = progress_data.get('progress', 0)
    
    rows.append({
        "📊 Progresso": f"{completed}/{goal}",
        "📈 Porcentagem": f"{percentage:.1f}%",
        "🎯 Status": "✅ Meta atingida!" if completed >= goal else "⏳ Em andamento"
    })
    
    # Hábitos completados hoje
    completed_habits = progress_data.get('completed_habits', [])
    if completed_habits:
        rows.append({
            "✅ Completados": f"{len(completed_habits)} hábitos",
            "📝 Lista": ", ".join(completed_habits[:3]) + ("..." if len(completed_habits) > 3 else ""),
            "🎉": "Parabéns!"
        })
    
    return create_table(rows)


def create_stats_table(stats: Dict[str, Any]) -> str:
    """
    Cria uma tabela de estatísticas do usuário
    
    Args:
        stats: Dados de estatísticas
    
    Returns:
        String formatada em Markdown
    """
    if not stats:
        return "📈 *Nenhuma estatística disponível*"
    
    rows = [
        {
            "🏆 Nível": f"Nível {stats.get('current_level', 1)}",
            "💎 XP Total": f"{stats.get('total_xp_earned', 0):,} XP",
            "📊 XP Hoje": f"{stats.get('xp_earned_today', 0)} XP"
        },
        {
            "🔥 Streak Atual": f"{stats.get('current_streak', 0)} dias",
            "🏅 Melhor Streak": f"{stats.get('longest_streak', 0)} dias",
            "📅 Dias Ativo": f"{stats.get('days_since_start', 0)} dias"
        },
        {
            "📈 Taxa Sucesso": f"{stats.get('success_rate', 0):.1f}%",
            "🎯 Meta Diária": f"{stats.get('daily_goal', 3)} hábitos",
            "⭐ Avaliação": f"{stats.get('average_rating', 0):.1f}/10"
        }
    ]
    
    return create_table(rows)


def create_weekly_summary_table(weekly_data: Dict[str, Any]) -> str:
    """
    Cria uma tabela de resumo semanal
    
    Args:
        weekly_data: Dados semanais
    
    Returns:
        String formatada em Markdown
    """
    if not weekly_data:
        return "📅 *Nenhum dado semanal disponível*"
    
    rows = [
        {
            "📅 Semana": f"{weekly_data.get('week_start', '')} - {weekly_data.get('week_end', '')}",
            "✅ Completados": f"{weekly_data.get('total_completed', 0)} hábitos",
            "📊 Taxa Sucesso": f"{weekly_data.get('success_rate', 0):.1f}%"
        },
        {
            "💎 XP Ganho": f"{weekly_data.get('total_xp_earned', 0)} XP",
            "🔥 Streak": f"{weekly_data.get('current_streak', 0)} dias",
            "⭐ Avaliação": f"{weekly_data.get('average_rating', 0):.1f}/10"
        }
    ]
    
    # Adiciona dias da semana se disponível
    daily_stats = weekly_data.get('daily_stats', {})
    if daily_stats:
        for day, stats in daily_stats.items():
            rows.append({
                f"📆 {day}": f"{stats.get('completed', 0)}/{stats.get('total', 0)}",
                "💎 XP": f"{stats.get('xp_earned', 0)}",
                "⭐": f"{stats.get('rating', 0):.1f}/10" if stats.get('rating') else "N/A"
            })
    
    return create_table(rows)


def create_rating_table(rating_data: Dict[str, Any]) -> str:
    """
    Cria uma tabela de avaliações
    
    Args:
        rating_data: Dados de avaliação
    
    Returns:
        String formatada em Markdown
    """
    if not rating_data:
        return "⭐ *Nenhuma avaliação disponível*"
    
    rows = [
        {
            "😊 Humor": f"{rating_data.get('mood_rating', 0):.1f}/10",
            "⚡ Energia": f"{rating_data.get('energy_rating', 0):.1f}/10",
            # Removido craving - não é mais necessário
        }
    ]
    
    # Adiciona notas se disponível
    notes = rating_data.get('notes')
    if notes:
        rows.append({
            "📝 Notas": notes[:50] + "..." if len(notes) > 50 else notes,
            "📅 Data": rating_data.get('created_at', ''),
            "🕐 Hora": rating_data.get('time', '')
        })
    
    return create_table(rows)


def format_progress_bar(current: int, total: int, width: int = 10) -> str:
    """
    Cria uma barra de progresso visual
    
    Args:
        current: Valor atual
        total: Valor total
        width: Largura da barra
    
    Returns:
        String com a barra de progresso
    """
    if total == 0:
        return "▱" * width
    
    percentage = current / total
    filled = int(width * percentage)
    empty = width - filled
    
    bar = "▰" * filled + "▱" * empty
    return f"{bar} {current}/{total} ({percentage:.1%})"


def create_habit_card(habit: Dict[str, Any]) -> str:
    """
    Cria um card visual para um hábito
    
    Args:
        habit: Dados do hábito
    
    Returns:
        String formatada
    """
    name = habit.get('name', '')
    description = habit.get('description', '')
    xp_reward = habit.get('xp_reward', 0)
    category = habit.get('category', '').title()
    current_streak = habit.get('current_streak', 0)
    completed_today = habit.get('completed_today', False)
    
    status = "✅ Completado" if completed_today else "⏳ Pendente"
    
    card = f"""
🎯 **{name}**
📝 {description or 'Sem descrição'}
💎 {xp_reward} XP | 📂 {category}
🔥 Streak: {current_streak} dias
{status}
"""
    
    return card.strip()


def create_summary_card(summary_data: Dict[str, Any]) -> str:
    """
    Cria um card de resumo
    
    Args:
        summary_data: Dados do resumo
    
    Returns:
        String formatada
    """
    card = f"""
📊 **Resumo do Dia**

✅ {summary_data.get('completed', 0)}/{summary_data.get('goal', 0)} hábitos completados
📈 {summary_data.get('progress', 0):.1f}% da meta diária
💎 {summary_data.get('xp_earned_today', 0)} XP ganho hoje
🏆 Nível {summary_data.get('current_level', 1)}
🔥 Streak: {summary_data.get('current_streak', 0)} dias
"""
    
    return card.strip()
