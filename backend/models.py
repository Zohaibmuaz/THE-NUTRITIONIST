from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(String, default=True)
    date_joined = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    daily_logs = relationship("DailyLog", back_populates="user")

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Personal information
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)  # in kg
    height = Column(Float, nullable=False)  # in cm
    gender = Column(String, nullable=False)  # "male", "female", "other"
    activity_level = Column(String, nullable=False)  # "sedentary", "lightly_active", "moderately_active", "very_active", "extremely_active"
    fitness_goal = Column(String, nullable=False)  # "lose_weight", "maintain_weight", "gain_weight"
    
    # Calculated goals
    daily_calorie_goal = Column(Float, nullable=False)
    daily_protein_goal = Column(Float, nullable=False)  # in grams
    daily_carb_goal = Column(Float, nullable=False)  # in grams
    daily_fat_goal = Column(Float, nullable=False)  # in grams
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="profile")

class DailyLog(Base):
    __tablename__ = "daily_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="daily_logs")
    meal_entries = relationship("MealEntry", back_populates="daily_log")

class MealEntry(Base):
    __tablename__ = "meal_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(Integer, ForeignKey("daily_logs.id"), nullable=False)
    
    # Meal information
    name = Column(String, nullable=False)  # Description of the meal
    calories = Column(Float, nullable=False, default=0)
    protein = Column(Float, nullable=False, default=0)  # in grams
    carbohydrates = Column(Float, nullable=False, default=0)  # in grams
    fats = Column(Float, nullable=False, default=0)  # in grams
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    daily_log = relationship("DailyLog", back_populates="meal_entries")
