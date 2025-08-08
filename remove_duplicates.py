#!/usr/bin/env python3
"""
Script para remover hábitos duplicados
"""

from db.session import get_db
from models.models import Habit
from sqlalchemy import func

def remove_duplicate_habits():
    """Remove hábitos duplicados mantendo apenas um de cada nome"""
    
    db = next(get_db())
    
    try:
        # Busca hábitos agrupados por nome
        duplicate_names = db.query(
            Habit.name,
            func.count(Habit.id).label('count')
        ).group_by(Habit.name).having(func.count(Habit.id) > 1).all()
        
        print(f"🔍 Encontrados {len(duplicate_names)} nomes duplicados:")
        
        total_removed = 0
        
        for name, count in duplicate_names:
            print(f"📋 '{name}' - {count} ocorrências")
            
            # Busca todos os hábitos com este nome
            habits = db.query(Habit).filter(Habit.name == name).order_by(Habit.created_at).all()
            
            # Mantém o primeiro (mais antigo) e remove os outros
            for habit in habits[1:]:
                print(f"   🗑️ Removendo hábito ID {habit.id} (criado em {habit.created_at})")
                db.delete(habit)
                total_removed += 1
        
        if total_removed > 0:
            db.commit()
            print(f"\n🎉 {total_removed} hábitos duplicados removidos!")
        else:
            print("\n✅ Nenhum hábito duplicado encontrado!")
        
        # Mostra hábitos restantes
        remaining_habits = db.query(Habit).filter(Habit.is_active == True).all()
        print(f"\n📋 Hábitos ativos restantes ({len(remaining_habits)}):")
        for habit in remaining_habits:
            print(f"• {habit.name} (ID: {habit.id})")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    remove_duplicate_habits()
