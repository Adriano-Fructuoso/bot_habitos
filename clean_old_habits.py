#!/usr/bin/env python3
"""
Script para remover hábitos antigos indesejados
"""

from db.session import get_db
from models.models import Habit

def clean_old_habits():
    """Remove hábitos antigos que não queremos mais"""
    
    db = next(get_db())
    
    try:
        # Lista de hábitos para remover
        habits_to_remove = [
            "Não Fumar",
            "Não Usar Maconha", 
            "Limitar Café",
            "Beber Água",
            "Bom Sono"
        ]
        
        print("🧹 Removendo hábitos antigos...")
        
        total_removed = 0
        
        for habit_name in habits_to_remove:
            habits = db.query(Habit).filter(Habit.name == habit_name).all()
            for habit in habits:
                print(f"🗑️ Removendo: {habit.name} (ID: {habit.id})")
                db.delete(habit)
                total_removed += 1
        
        if total_removed > 0:
            db.commit()
            print(f"\n🎉 {total_removed} hábitos antigos removidos!")
        else:
            print("\n✅ Nenhum hábito antigo encontrado!")
        
        # Mostra hábitos restantes
        remaining_habits = db.query(Habit).filter(Habit.is_active == True).all()
        print(f"\n📋 Hábitos ativos restantes ({len(remaining_habits)}):")
        for habit in remaining_habits:
            print(f"• {habit.name} (ID: {habit.id}) - {habit.time_minutes}min • {habit.xp_reward}XP")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clean_old_habits()
