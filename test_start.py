#!/usr/bin/env python3
"""
Teste simples para identificar problema no comando /start
"""

import asyncio
import sys
import os

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import TELEGRAM_BOT_TOKEN
from db.session import get_db
from models.models import User
from utils.gamification import get_daily_goal_progress
from utils.keyboards import create_main_menu_keyboard
from utils.branding import add_branding

async def test_start_command():
    """Testa as funções usadas no comando /start"""
    
    print("🔍 Testando comando /start...")
    
    # Teste 1: Verificar token
    print(f"✅ Token configurado: {TELEGRAM_BOT_TOKEN[:10]}...")
    
    # Teste 2: Verificar conexão com banco
    try:
        db = next(get_db())
        print("✅ Conexão com banco OK")
        
        # Teste 3: Buscar usuário
        test_user_id = 123456789  # ID de teste
        user = db.query(User).filter(User.telegram_user_id == test_user_id).first()
        print(f"✅ Busca de usuário OK (usuário encontrado: {user is not None})")
        
        # Teste 4: Testar get_daily_goal_progress
        if user:
            try:
                progress = get_daily_goal_progress(db, user.id)
                print(f"✅ get_daily_goal_progress OK: {progress}")
            except Exception as e:
                print(f"❌ Erro em get_daily_goal_progress: {e}")
        else:
            print("⚠️ Usuário não encontrado, pulando teste de progresso")
        
        # Teste 5: Testar create_main_menu_keyboard
        try:
            keyboard = create_main_menu_keyboard()
            print("✅ create_main_menu_keyboard OK")
        except Exception as e:
            print(f"❌ Erro em create_main_menu_keyboard: {e}")
        
        # Teste 6: Testar add_branding
        try:
            test_message = "Teste de mensagem"
            branded = add_branding(test_message)
            print("✅ add_branding OK")
        except Exception as e:
            print(f"❌ Erro em add_branding: {e}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro na conexão com banco: {e}")
        return False
    
    print("✅ Todos os testes passaram!")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_start_command())
    if success:
        print("\n🎉 Comando /start deve funcionar corretamente!")
    else:
        print("\n❌ Há problemas no comando /start!")
