#!/usr/bin/env python3
"""
Script de teste para verificar se a estrutura do projeto está funcionando
"""

import sys
import os

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Testa se todos os imports estão funcionando"""
    print("🧪 Testando imports...")
    
    try:
        # Testa imports básicos
        from config import TELEGRAM_BOT_TOKEN, DATABASE_URL
        print("✅ Config importado com sucesso")
        
        from db.session import engine, Base
        print("✅ Database session importado com sucesso")
        
        from models.models import User, Habit, DailyLog, Badge, Streak, DailyRating, Achievement
        print("✅ Models importados com sucesso")
        
        from utils.gamification import calculate_xp_earned, update_user_progress
        print("✅ Gamification system importado com sucesso")
        
        try:
            from bot.handlers import start_command, habit_command
            print("✅ Bot handlers importados com sucesso")
        except ImportError:
            print("⚠️ Bot handlers não podem ser importados (dependências não instaladas)")
            print("   Execute: pip install -r requirements.txt")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_config():
    """Testa configurações"""
    print("\n🔧 Testando configurações...")
    
    try:
        from config import TELEGRAM_BOT_TOKEN, DATABASE_URL
        
        # Verifica se as variáveis estão definidas (mesmo que vazias)
        if TELEGRAM_BOT_TOKEN:
            print("✅ TELEGRAM_BOT_TOKEN configurado")
        else:
            print("❌ TELEGRAM_BOT_TOKEN não encontrado")
            
        if DATABASE_URL:
            print("✅ DATABASE_URL configurado")
        else:
            print("❌ DATABASE_URL não encontrado")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        return False

def test_database_connection():
    """Testa conexão com banco de dados (se configurado)"""
    print("\n🗄️ Testando conexão com banco...")
    
    try:
        from config import DATABASE_URL
        
        if not DATABASE_URL:
            print("⚠️ DATABASE_URL não configurado - pulando teste de conexão")
            return True
            
        from db.session import engine
        
        # Testa conexão
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Conexão com banco de dados estabelecida")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão com banco: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes da estrutura do Habit Bot\n")
    
    tests = [
        test_imports,
        test_config,
        test_database_connection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Resultado dos testes: {passed}/{total} passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! A estrutura está pronta para uso.")
        print("\n📝 Próximos passos:")
        print("1. Configure o arquivo .env com suas credenciais")
        print("2. Execute: python run.py")
    else:
        print("❌ Alguns testes falharam. Verifique a configuração.")
        sys.exit(1)

if __name__ == "__main__":
    main() 