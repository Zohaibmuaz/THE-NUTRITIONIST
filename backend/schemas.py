from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date, datetime

# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    access_token: str
    
    class Config:
        from_attributes = True

# Profile schemas
class ProfileCreate(BaseModel):
    age: int
    weight: float
    height: float
    gender: str
    activity_level: str
    fitness_goal: str

class ProfileResponse(BaseModel):
    id: int
    user_id: int
    age: int
    weight: float
    height: float
    gender: str
    activity_level: str
    fitness_goal: str
    daily_calorie_goal: float
    daily_protein_goal: float
    daily_carb_goal: float
    daily_fat_goal: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Meal logging schemas
class MealLogCreate(BaseModel):
    description: str
    date: Optional[str] = None

class MealLogResponse(BaseModel):
    id: int
    log_id: int
    name: str
    calories: float
    protein: float
    carbohydrates: float
    fats: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class DailyLogResponse(BaseModel):
    date: date
    meals: List[MealLogResponse]
    total_calories: float
    total_protein: float
    total_carbohydrates: float
    total_fats: float

# AI schemas
class AIQuestion(BaseModel):
    question: str

class AIResponse(BaseModel):
    response: str
