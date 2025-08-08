#!/usr/bin/env python3
"""
Script para testar se o bot está configurado corretamente
"""

import os
import sys

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv


def main():
    """Função principal para testar o bot"""
    print("🤖 Testando configuração do bot...")

    # Carrega variáveis de ambiente
    load_dotenv()

    # Verifica se TELEGRAM_BOT_TOKEN está configurado
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN não configurado!")
        print("📝 Configure a variável TELEGRAM_BOT_TOKEN no arquivo .env")
        print("💡 Obtenha o token em: https://t.me/botfather")
        return False

    print(f"✅ TELEGRAM_BOT_TOKEN configurado: {token[:20]}...")

    # Verifica se o token tem formato válido
    if not token.count(":") == 1:
        print("❌ Formato do token inválido!")
        print("💡 O token deve ter o formato: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
        return False

    try:
        # Testa se consegue importar o bot
        from bot.main import main

        print("✅ Módulos do bot importados com sucesso")

        # Testa conexão com banco
        from db.session import test_connection

        if test_connection():
            print("✅ Banco de dados funcionando")
        else:
            print("❌ Problema com banco de dados")
            return False

        print("\n🎉 Bot configurado corretamente!")
        print("\n📋 Para executar o bot:")
        print("   python run.py")
        print("\n📱 Para testar no Telegram:")
        print("   1. Procure seu bot no Telegram")
        print("   2. Envie /start")
        print("   3. Teste os comandos /habit, /stats e /health")

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
