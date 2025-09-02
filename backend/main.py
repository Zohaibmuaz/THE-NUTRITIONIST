from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import uvicorn
from dotenv import load_dotenv
import os

from .database import get_db, engine, Base
from .models import User, UserProfile, DailyLog, MealEntry
from .schemas import (
    UserCreate, UserLogin, UserResponse, ProfileCreate, ProfileResponse,
    MealLogCreate, MealLogResponse, DailyLogResponse, AIQuestion, AIResponse
)
from .auth import create_access_token, verify_token, get_password_hash, verify_password
from .services import (
    calculate_bmr, calculate_tdee, get_daily_summary,
    analyze_meal_with_ai, get_ai_nutrition_advice
)

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Calorie & Diet Tracker API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Authentication endpoints
@app.post("/api/auth/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(db_user.id)})
    
    return UserResponse(
        id=db_user.id,
        email=db_user.email,
        full_name=db_user.full_name,
        access_token=access_token
    )

@app.post("/api/auth/login", response_model=UserResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        access_token=access_token
    )

# Profile endpoints
@app.get("/api/profile", response_model=ProfileResponse)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user profile"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return profile

@app.put("/api/profile", response_model=ProfileResponse)
def create_or_update_profile(
    profile_data: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update user profile"""
    # Calculate BMR and TDEE
    bmr = calculate_bmr(
        profile_data.weight,
        profile_data.height,
        profile_data.age,
        profile_data.gender
    )
    tdee = calculate_tdee(bmr, profile_data.activity_level)
    
    # Adjust TDEE based on fitness goal
    if profile_data.fitness_goal == "lose_weight":
        daily_calorie_goal = tdee - 500  # 500 calorie deficit
    elif profile_data.fitness_goal == "gain_weight":
        daily_calorie_goal = tdee + 500  # 500 calorie surplus
    else:  # maintain_weight
        daily_calorie_goal = tdee
    
    # Calculate macro goals (standard ratios)
    daily_protein_goal = (daily_calorie_goal * 0.25) / 4  # 25% protein, 4 cal/g
    daily_carb_goal = (daily_calorie_goal * 0.45) / 4    # 45% carbs, 4 cal/g
    daily_fat_goal = (daily_calorie_goal * 0.30) / 9     # 30% fat, 9 cal/g
    
    # Check if profile exists
    existing_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    if existing_profile:
        # Update existing profile
        for field, value in profile_data.dict().items():
            setattr(existing_profile, field, value)
        existing_profile.daily_calorie_goal = daily_calorie_goal
        existing_profile.daily_protein_goal = daily_protein_goal
        existing_profile.daily_carb_goal = daily_carb_goal
        existing_profile.daily_fat_goal = daily_fat_goal
        db.commit()
        db.refresh(existing_profile)
        return existing_profile
    else:
        # Create new profile
        new_profile = UserProfile(
            user_id=current_user.id,
            **profile_data.dict(),
            daily_calorie_goal=daily_calorie_goal,
            daily_protein_goal=daily_protein_goal,
            daily_carb_goal=daily_carb_goal,
            daily_fat_goal=daily_fat_goal
        )
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)
        return new_profile

# Meal logging endpoints
@app.post("/api/logs/meals", response_model=MealLogResponse)
def log_meal(
    meal_data: MealLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log a new meal for a specific date"""
    from datetime import date, datetime
    
    # Use provided date or default to today
    target_date = date.today()
    if hasattr(meal_data, 'date') and meal_data.date:
        if isinstance(meal_data.date, str):
            try:
                target_date = datetime.strptime(meal_data.date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format. Use YYYY-MM-DD"
                )
        else:
            target_date = meal_data.date
    
    daily_log = db.query(DailyLog).filter(
        DailyLog.user_id == current_user.id,
        DailyLog.date == target_date
    ).first()
    
    if not daily_log:
        daily_log = DailyLog(user_id=current_user.id, date=target_date)
        db.add(daily_log)
        db.commit()
        db.refresh(daily_log)
    
    # Analyze meal with AI
    nutritional_data = analyze_meal_with_ai(meal_data.description)
    
    # Create meal entry
    meal_entry = MealEntry(
        log_id=daily_log.id,
        name=meal_data.description,
        calories=nutritional_data.get("calories", 0),
        protein=nutritional_data.get("protein", 0),
        carbohydrates=nutritional_data.get("carbohydrates", 0),
        fats=nutritional_data.get("fats", 0)
    )
    
    db.add(meal_entry)
    db.commit()
    db.refresh(meal_entry)
    
    return meal_entry

@app.get("/api/logs/{date}", response_model=DailyLogResponse)
def get_daily_log(
    date: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all meal entries and summary for a specific date"""
    from datetime import datetime
    
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    daily_log = db.query(DailyLog).filter(
        DailyLog.user_id == current_user.id,
        DailyLog.date == target_date
    ).first()
    
    if not daily_log:
        return DailyLogResponse(
            date=target_date,
            meals=[],
            total_calories=0,
            total_protein=0,
            total_carbohydrates=0,
            total_fats=0
        )
    
    meals = db.query(MealEntry).filter(MealEntry.log_id == daily_log.id).all()
    
    # Calculate totals
    total_calories = sum(meal.calories for meal in meals)
    total_protein = sum(meal.protein for meal in meals)
    total_carbohydrates = sum(meal.carbohydrates for meal in meals)
    total_fats = sum(meal.fats for meal in meals)
    
    return DailyLogResponse(
        date=target_date,
        meals=meals,
        total_calories=total_calories,
        total_protein=total_protein,
        total_carbohydrates=total_carbohydrates,
        total_fats=total_fats
    )

@app.delete("/api/logs/meals/{meal_id}")
def delete_meal(
    meal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a meal entry"""
    # Find the meal entry
    meal = db.query(MealEntry).join(DailyLog).filter(
        MealEntry.id == meal_id,
        DailyLog.user_id == current_user.id
    ).first()
    
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found"
        )
    
    # Delete the meal
    db.delete(meal)
    db.commit()
    
    return {"message": "Meal deleted successfully"}

# AI guidance endpoint
@app.post("/api/ai/ask", response_model=AIResponse)
def ask_nutritionist(
    question_data: AIQuestion,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a question to the nutrition AI"""
    try:
        # Get user profile for personalized advice
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        response = get_ai_nutrition_advice(question_data.question, profile)
        return AIResponse(response=response)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting AI response: {str(e)}"
        )

# Meal analysis report endpoint
@app.post("/api/ai/analyze-meals", response_model=AIResponse)
def analyze_meals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate comprehensive meal analysis report"""
    try:
        # Get user profile
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found. Please complete your profile setup."
            )
        
        # Generate analysis report
        from services import generate_meal_analysis_report
        report = generate_meal_analysis_report(current_user.id, profile, db)
        return AIResponse(response=report)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating analysis report: {str(e)}"
        )

# Download comprehensive report endpoint
@app.get("/api/reports/download")
def download_comprehensive_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download comprehensive nutrition report as HTML"""
    try:
        # Get user profile
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found. Please complete your profile setup."
            )
        
        # Generate comprehensive report data
        from services import generate_comprehensive_report_html
        report_html = generate_comprehensive_report_html(current_user.id, profile, db)
        
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=report_html, media_type="text/html")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating report: {str(e)}"
        )

# Dashboard endpoint
@app.get("/api/dashboard")
def get_dashboard_data(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get dashboard data including goals and current day summary"""
    # Get user profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please complete your profile setup."
        )
    
    # Get today's summary
    from datetime import date
    today = date.today()
    today_summary = get_daily_summary(current_user.id, today, db)
    
    # Get weekly data for trends
    from datetime import timedelta
    week_ago = today - timedelta(days=7)
    weekly_data = []
    
    for i in range(7):
        check_date = week_ago + timedelta(days=i)
        daily_summary = get_daily_summary(current_user.id, check_date, db)
        weekly_data.append({
            "date": check_date.isoformat(),
            "calories": daily_summary["total_calories"],
            "protein": daily_summary["total_protein"],
            "carbs": daily_summary["total_carbohydrates"],
            "fats": daily_summary["total_fats"]
        })
    
    return {
        "goals": {
            "calories": profile.daily_calorie_goal,
            "protein": profile.daily_protein_goal,
            "carbs": profile.daily_carb_goal,
            "fats": profile.daily_fat_goal
        },
        "today": today_summary,
        "weekly_trends": weekly_data
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

