from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Gamification fields
    total_xp_earned = Column(Integer, default=0)
    current_level = Column(Integer, default=1)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    days_since_start = Column(Integer, default=0)
    daily_goal = Column(Integer, default=3)
    mood_rating = Column(Float, default=5.0)
    energy_rating = Column(Float, default=5.0)
    craving_level = Column(Integer, default=0)
    quit_smoking_date = Column(DateTime)
    quit_weed_date = Column(DateTime)
    coffee_limit = Column(Integer, default=3)
    
    # Relationships
    habits = relationship("Habit", back_populates="user")
    daily_logs = relationship("DailyLog", back_populates="user")
    badges = relationship("Badge", back_populates="user")
    streaks = relationship("Streak", back_populates="user")
    daily_ratings = relationship("DailyRating", back_populates="user")
    achievements = relationship("Achievement", back_populates="user")

class Habit(Base):
    __tablename__ = 'habits'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50))
    difficulty = Column(String(20), default='medium')
    xp_reward = Column(Integer, default=10)
    streak_bonus = Column(Integer, default=5)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_today = Column(Boolean, default=False)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    total_completions = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="habits")
    daily_logs = relationship("DailyLog", back_populates="habit")

class DailyLog(Base):
    __tablename__ = 'daily_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    habit_id = Column(Integer, ForeignKey('habits.id'), nullable=False)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    xp_earned = Column(Integer, default=0)
    streak_bonus = Column(Integer, default=0)
    notes = Column(Text)
    mood_rating = Column(Float)
    energy_rating = Column(Float)
    craving_level = Column(Integer)
    date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="daily_logs")
    habit = relationship("Habit", back_populates="daily_logs")

class Badge(Base):
    __tablename__ = 'badges'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    icon = Column(String(50))
    category = Column(String(50))
    earned_at = Column(DateTime, default=datetime.utcnow)
    is_rare = Column(Boolean, default=False)
    xp_bonus = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="badges")

class Streak(Base):
    __tablename__ = 'streaks'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    habit_id = Column(Integer, ForeignKey('habits.id'))
    streak_type = Column(String(50), nullable=False)  # 'daily', 'weekly', 'monthly'
    current_count = Column(Integer, default=0)
    longest_count = Column(Integer, default=0)
    start_date = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="streaks")

class DailyRating(Base):
    __tablename__ = 'daily_ratings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    mood_rating = Column(Float, nullable=False)
    energy_rating = Column(Float, nullable=False)
    craving_level = Column(Integer, default=0)
    notes = Column(Text)
    goals_met = Column(Integer, default=0)
    total_goals = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="daily_ratings")

class Achievement(Base):
    __tablename__ = 'achievements'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(50))
    earned_at = Column(DateTime, default=datetime.utcnow)
    xp_reward = Column(Integer, default=0)
    is_hidden = Column(Boolean, default=False)
    progress = Column(Float, default=0.0)
    target = Column(Float, default=1.0)
    
    # Relationships
    user = relationship("User", back_populates="achievements") 