#!/usr/bin/env python3
"""
Script de inicialização do Habit Bot
"""

import sys
import os

# Adiciona o diretório atual ao path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config

def main():
    """Função principal de inicialização"""
    try:
        # Valida configurações
        Config.validate()
        
        # Importa e executa o bot
        from bot.main import main as run_bot
        run_bot()
        
    except ValueError as e:
        print(f"❌ Erro de configuração: {e}")
        print("📝 Verifique se o arquivo .env está configurado corretamente")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 