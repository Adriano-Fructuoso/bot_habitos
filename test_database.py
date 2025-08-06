#!/usr/bin/env python3
"""
Script para testar a conexão com o banco de dados PostgreSQL
"""

import sys
import os

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

def main():
    """Função principal para testar o banco de dados"""
    print("🗄️ Testando conexão com banco de dados...")
    
    # Carrega variáveis de ambiente
    load_dotenv()
    
    # Verifica se DATABASE_URL está configurada
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL não configurada!")
        print("📝 Configure a variável DATABASE_URL no arquivo .env")
        print("💡 Exemplo: DATABASE_URL=postgresql://user:pass@host:port/db")
        return False
    
    print(f"📋 DATABASE_URL configurada: {database_url[:20]}...")
    
    try:
        # Importa e testa a conexão
        from db.session import test_connection, init_db
        
        # Testa conexão
        if test_connection():
            print("\n📊 Inicializando tabelas...")
            init_db()
            print("✅ Tabelas criadas com sucesso!")
            
            print("\n🎉 Banco de dados configurado e funcionando!")
            return True
        else:
            print("❌ Falha na conexão com o banco de dados")
            return False
            
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