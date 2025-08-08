#!/usr/bin/env python3
"""
Teste de conectividade com Telegram API
"""

import asyncio
import httpx
from config import TELEGRAM_BOT_TOKEN

async def test_telegram_connection():
    """Testa conectividade com Telegram API"""
    
    print("🔍 Testando conectividade com Telegram API...")
    
    # Teste 1: getMe
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
            )
            print(f"✅ getMe: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Bot: {data['result']['first_name']} (@{data['result']['username']})")
            else:
                print(f"   Erro: {response.text}")
    except Exception as e:
        print(f"❌ Erro no getMe: {e}")
    
    # Teste 2: getUpdates
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
            )
            print(f"✅ getUpdates: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Updates pendentes: {len(data['result'])}")
            else:
                print(f"   Erro: {response.text}")
    except Exception as e:
        print(f"❌ Erro no getUpdates: {e}")
    
    # Teste 3: deleteWebhook
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook"
            )
            print(f"✅ deleteWebhook: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no deleteWebhook: {e}")

if __name__ == "__main__":
    asyncio.run(test_telegram_connection())
