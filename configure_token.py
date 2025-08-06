#!/usr/bin/env python3
"""
Script para configurar o token do bot automaticamente
"""

import os

def configure_token():
    """Configura o token do bot no arquivo .env"""
    
    token = "8347035109:AAEKMroTl4jrT-dZRnBF1vEb6i5ZkXMmuME"
    
    # Conteúdo do arquivo .env
    env_content = f"""# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN={token}

# Database Configuration
# Para desenvolvimento local (SQLite):
DATABASE_URL=sqlite:///./habit_bot.db
# Para produção (PostgreSQL Railway):
# DATABASE_URL=postgresql://username:password@host:port/database_name

# Optional: Logging Level
LOG_LEVEL=INFO
"""
    
    # Escreve o arquivo .env
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Token configurado com sucesso!")
    print(f"📋 Token: {token[:20]}...")
    print("📁 Arquivo .env criado/atualizado")

if __name__ == "__main__":
    configure_token() 