import os
from dotenv import load_dotenv

load_dotenv()

# Configurações do Bot
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Configurações do Banco de Dados
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///habit_bot.db')

# Configurações de Gamificação
DEFAULT_HABITS = {
    'exercise': {
        'name': 'Exercício Físico',
        'description': 'Praticar atividade física por pelo menos 30 minutos',
        'category': 'saude',
        'difficulty': 'medium',
        'xp_reward': 15,
        'streak_bonus': 5
    },
    'meditation': {
        'name': 'Meditação',
        'description': 'Meditar por 10-15 minutos',
        'category': 'mental',
        'difficulty': 'easy',
        'xp_reward': 10,
        'streak_bonus': 3
    },
    'reading': {
        'name': 'Leitura',
        'description': 'Ler por pelo menos 20 minutos',
        'category': 'desenvolvimento',
        'difficulty': 'easy',
        'xp_reward': 12,
        'streak_bonus': 4
    },
    'water': {
        'name': 'Beber Água',
        'description': 'Beber 2L de água por dia',
        'category': 'saude',
        'difficulty': 'easy',
        'xp_reward': 8,
        'streak_bonus': 2
    },
    'sleep': {
        'name': 'Bom Sono',
        'description': 'Dormir 7-8 horas por noite',
        'category': 'saude',
        'difficulty': 'medium',
        'xp_reward': 20,
        'streak_bonus': 8
    },
    'no_smoking': {
        'name': 'Não Fumar',
        'description': 'Evitar cigarros por 24 horas',
        'category': 'saude',
        'difficulty': 'hard',
        'xp_reward': 25,
        'streak_bonus': 10
    },
    'no_weed': {
        'name': 'Não Usar Maconha',
        'description': 'Evitar maconha por 24 horas',
        'category': 'saude',
        'difficulty': 'hard',
        'xp_reward': 25,
        'streak_bonus': 10
    },
    'coffee_limit': {
        'name': 'Limitar Café',
        'description': 'Beber no máximo 3 xícaras de café por dia',
        'category': 'saude',
        'difficulty': 'medium',
        'xp_reward': 12,
        'streak_bonus': 4
    }
}

BADGES = {
    'first_habit': {
        'name': 'Primeiro Passo',
        'description': 'Completou seu primeiro hábito',
        'icon': '🎯',
        'category': 'inicio',
        'is_rare': False,
        'xp_bonus': 50
    },
    'week_streak': {
        'name': 'Semana Perfeita',
        'description': 'Manteve streak por 7 dias',
        'icon': '🔥',
        'category': 'streak',
        'is_rare': False,
        'xp_bonus': 100
    },
    'month_streak': {
        'name': 'Mestre da Consistência',
        'description': 'Manteve streak por 30 dias',
        'icon': '👑',
        'category': 'streak',
        'is_rare': True,
        'xp_bonus': 500
    },
    'level_5': {
        'name': 'Aprendiz',
        'description': 'Alcançou o nível 5',
        'icon': '⭐',
        'category': 'nivel',
        'is_rare': False,
        'xp_bonus': 200
    },
    'level_10': {
        'name': 'Veterano',
        'description': 'Alcançou o nível 10',
        'icon': '🌟',
        'category': 'nivel',
        'is_rare': False,
        'xp_bonus': 500
    },
    'level_20': {
        'name': 'Mestre',
        'description': 'Alcançou o nível 20',
        'icon': '💎',
        'category': 'nivel',
        'is_rare': True,
        'xp_bonus': 1000
    },
    'perfect_day': {
        'name': 'Dia Perfeito',
        'description': 'Completou todos os hábitos do dia',
        'icon': '✨',
        'category': 'perfeicao',
        'is_rare': False,
        'xp_bonus': 150
    },
    'no_smoking_week': {
        'name': 'Respirando Melhor',
        'description': 'Ficou 7 dias sem fumar',
        'icon': '🌿',
        'category': 'saude',
        'is_rare': True,
        'xp_bonus': 300
    },
    'no_weed_week': {
        'name': 'Mente Clara',
        'description': 'Ficou 7 dias sem usar maconha',
        'icon': '🧠',
        'category': 'saude',
        'is_rare': True,
        'xp_bonus': 300
    }
}

ACHIEVEMENTS = {
    'habit_master': {
        'name': 'Mestre dos Hábitos',
        'description': 'Completou 100 hábitos no total',
        'category': 'progresso',
        'xp_reward': 1000,
        'is_hidden': False,
        'target': 100
    },
    'streak_legend': {
        'name': 'Lenda da Consistência',
        'description': 'Manteve streak por 100 dias',
        'category': 'streak',
        'xp_reward': 2000,
        'is_hidden': False,
        'target': 100
    },
    'early_bird': {
        'name': 'Madrugador',
        'description': 'Completou hábitos antes das 8h por 7 dias',
        'category': 'tempo',
        'xp_reward': 500,
        'is_hidden': True,
        'target': 7
    },
    'night_owl': {
        'name': 'Coruja Noturna',
        'description': 'Completou hábitos após 22h por 7 dias',
        'category': 'tempo',
        'xp_reward': 500,
        'is_hidden': True,
        'target': 7
    },
    'social_butterfly': {
        'name': 'Borboleta Social',
        'description': 'Completou hábitos em 7 locais diferentes',
        'category': 'variedade',
        'xp_reward': 300,
        'is_hidden': True,
        'target': 7
    }
}

MOTIVATIONAL_MESSAGES = {
    'start': [
        "🚀 Vamos começar essa jornada incrível!",
        "💪 Você tem o poder de transformar sua vida!",
        "🌟 Cada pequeno passo conta para grandes mudanças!",
        "🎯 Foco, determinação e sucesso!"
    ],
    'habit_completed': [
        "🎉 Parabéns! Você está cada vez mais forte!",
        "🔥 Incrível! Continue assim!",
        "⭐ Você está construindo um futuro melhor!",
        "💎 Cada conquista te aproxima dos seus objetivos!"
    ],
    'streak_milestone': [
        "🔥 Streak em chamas! Você está no fogo!",
        "⚡ Impressione! Sua consistência é inspiradora!",
        "🏆 Você está se tornando uma máquina de hábitos!",
        "🚀 Nada pode te parar agora!"
    ],
    'level_up': [
        "🌟 Nível up! Você está evoluindo!",
        "🎊 Parabéns! Você subiu de nível!",
        "💫 Cada nível é uma nova conquista!",
        "🏅 Você está se superando a cada dia!"
    ],
    'badge_earned': [
        "🏆 Nova conquista desbloqueada!",
        "🎖️ Você merece essa medalha!",
        "💎 Uma conquista rara! Você é especial!",
        "👑 Você está se tornando um mestre!"
    ],
    'encouragement': [
        "💪 Você é mais forte do que pensa!",
        "🌟 Acredite no seu potencial!",
        "🔥 Cada dia é uma nova oportunidade!",
        "🎯 Foque no progresso, não na perfeição!"
    ],
    'setback': [
        "💙 Não se preocupe, amanhã é um novo dia!",
        "🔄 Recomeçar faz parte do processo!",
        "🌟 Você aprendeu algo valioso hoje!",
        "💪 A jornada tem altos e baixos, continue firme!"
    ]
}

# Configurações de XP e Níveis
XP_PER_LEVEL = 100
STREAK_MULTIPLIER = 1.5
PERFECT_DAY_BONUS = 50
WEEKLY_BONUS = 200
MONTHLY_BONUS = 1000

# Configurações de Tempo
DAILY_RESET_HOUR = 0  # Meia-noite
WEEKLY_RESET_DAY = 0  # Domingo (0 = segunda-feira)
MONTHLY_RESET_DAY = 1  # Primeiro dia do mês 