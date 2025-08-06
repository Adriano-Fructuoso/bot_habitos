import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class Config:
    """Configurações centralizadas do projeto"""
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Gamification Settings
    XP_PER_HABIT = 10
    XP_PER_STREAK_DAY = 5
    XP_MULTIPLIER_AFTER_7_DAYS = 1.5
    
    # Level XP Requirements
    LEVEL_XP_REQUIREMENTS = {
        1: 0,
        2: 50,
        3: 150,
        4: 300,
        5: 500,
        6: 750,
        7: 1050,
        8: 1400,
        9: 1800,
        10: 2250
    }
    
    @classmethod
    def validate(cls):
        """Valida se todas as configurações obrigatórias estão presentes"""
        required_vars = ['TELEGRAM_BOT_TOKEN', 'DATABASE_URL']
        missing_vars = []
        
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Variáveis de ambiente obrigatórias não configuradas: {', '.join(missing_vars)}")
        
        return True 