#!/usr/bin/env python3
"""
Script para corrigir hábitos com time_minutes inválidos
"""

from db.session import get_db
from models.models import Habit

def fix_habits_time_minutes():
    """Corrige hábitos que não têm time_minutes definido"""
    
    db = next(get_db())
    
    try:
        # Busca todos os hábitos
        habits = db.query(Habit).all()
        
        print(f"🔍 Encontrados {len(habits)} hábitos no banco")
        
        fixed_count = 0
        
        for habit in habits:
            print(f"📋 {habit.name} - time_minutes atual: {habit.time_minutes}")
            
            # Se time_minutes é None ou 0, define um valor padrão baseado no nome
            if habit.time_minutes is None or habit.time_minutes == 0:
                if "leitura" in habit.name.lower() or "ler" in habit.name.lower():
                    habit.time_minutes = 20
                elif "exercício" in habit.name.lower() or "exercicio" in habit.name.lower():
                    habit.time_minutes = 30
                elif "meditação" in habit.name.lower() or "meditacao" in habit.name.lower():
                    habit.time_minutes = 15
                elif "banho" in habit.name.lower() or "água gelada" in habit.name.lower():
                    habit.time_minutes = 5
                else:
                    habit.time_minutes = 30  # Valor padrão
                
                fixed_count += 1
                print(f"   ✅ Corrigido para {habit.time_minutes} minutos")
        
        if fixed_count > 0:
            db.commit()
            print(f"\n🎉 {fixed_count} hábitos corrigidos!")
        else:
            print("\n✅ Todos os hábitos já estão corretos!")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_habits_time_minutes()
