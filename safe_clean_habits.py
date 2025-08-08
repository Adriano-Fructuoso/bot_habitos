#!/usr/bin/env python3
"""
Script seguro para remover hábitos antigos e seus logs relacionados
"""

from db.session import get_db
from models.models import Habit, DailyLog

def safe_clean_habits():
    """Remove hábitos antigos de forma segura, incluindo logs relacionados"""
    
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
        
        print("🧹 Removendo hábitos antigos de forma segura...")
        
        total_removed = 0
        
        for habit_name in habits_to_remove:
            habits = db.query(Habit).filter(Habit.name == habit_name).all()
            for habit in habits:
                print(f"🗑️ Removendo: {habit.name} (ID: {habit.id})")
                
                # Remove logs relacionados primeiro
                logs = db.query(DailyLog).filter(DailyLog.habit_id == habit.id).all()
                for log in logs:
                    print(f"   📝 Removendo log ID {log.id}")
                    db.delete(log)
                
                # Remove o hábito
                db.delete(habit)
                total_removed += 1
        
        if total_removed > 0:
            db.commit()
            print(f"\n🎉 {total_removed} hábitos antigos removidos com segurança!")
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
    safe_clean_habits()
