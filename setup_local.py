#!/usr/bin/env python3
"""
Script para configurar o ambiente local com SQLite
"""

import sys
import os

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Função principal para setup local"""
    print("🏠 Configurando ambiente local com SQLite...")
    
    try:
        # Importa módulos necessários
        from db.session import engine, init_db
        from models.models import Base
        
        print("✅ Módulos importados com sucesso")
        
        # Cria as tabelas
        print("📊 Criando tabelas no banco SQLite...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas com sucesso!")
        
        # Testa conexão
        print("🔍 Testando conexão...")
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Conexão com SQLite estabelecida!")
        
        print("\n🎉 Ambiente local configurado com sucesso!")
        print("\n📋 Próximos passos:")
        print("1. Configure o TELEGRAM_BOT_TOKEN no arquivo .env")
        print("2. Execute: python run.py")
        print("\n💡 O banco SQLite será criado em: habit_bot.db")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        print("💡 Certifique-se de que as dependências estão instaladas:")
        print("   pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 