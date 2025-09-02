import google.generativeai as genai
import os
import json
import re
from typing import Dict, Any
from sqlalchemy.orm import Session
from datetime import date
from .models import DailyLog, MealEntry
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def calculate_bmr(weight: float, height: float, age: int, gender: str) -> float:
    """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation"""
    if gender.lower() == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:  # female or other
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    return bmr

def calculate_tdee(bmr: float, activity_level: str) -> float:
    """Calculate Total Daily Energy Expenditure based on activity level"""
    activity_multipliers = {
        "sedentary": 1.2,
        "lightly_active": 1.375,
        "moderately_active": 1.55,
        "very_active": 1.725,
        "extremely_active": 1.9
    }
    
    multiplier = activity_multipliers.get(activity_level.lower(), 1.2)
    return bmr * multiplier

def analyze_meal_with_ai(meal_description: str) -> Dict[str, float]:
    """Analyze meal description using Gemini AI to extract nutritional information"""
    prompt = f"""
    You are a nutrition expert. Analyze the following meal description and provide ACCURATE nutritional information.

    The meal description might be in English, Hindi, Urdu, or Roman Urdu. Understand the food items regardless of language.

    Meal description: "{meal_description}"

    Provide nutritional information in this EXACT JSON format (no additional text, no markdown):
    {{
        "calories": [number],
        "protein": [number in grams],
        "carbohydrates": [number in grams],
        "fats": [number in grams]
    }}

    IMPORTANT ACCURACY GUIDELINES:
    - 1 medium banana = ~105 calories, 1.3g protein, 27g carbs, 0.4g fat
    - 4 bananas = ~420 calories, 5.2g protein, 108g carbs, 1.6g fat
    - 1 cup daal (lentils) = ~230 calories, 18g protein, 40g carbs, 0.8g fat
    - 1 roti (chapati) = ~120 calories, 3g protein, 20g carbs, 2g fat
    - 1 medium apple = ~95 calories, 0.5g protein, 25g carbs, 0.3g fat
    - 1 medium peach = ~60 calories, 1g protein, 15g carbs, 0.4g fat
    - 1 cup rice = ~200 calories, 4g protein, 45g carbs, 0.5g fat
    - 1 egg = ~70 calories, 6g protein, 0.6g carbs, 5g fat
    - 1 slice bread = ~80 calories, 3g protein, 15g carbs, 1g fat
    
    Use REALISTIC serving sizes and ACCURATE nutritional values. Do not overestimate calories.
    Return ONLY the JSON object, no explanations.
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up the response to extract JSON
        # Remove any markdown formatting or extra text
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)
        response_text = re.sub(r'^.*?\{', '{', response_text)  # Remove text before first {
        response_text = re.sub(r'\}.*?$', '}', response_text)  # Remove text after last }
        
        # Parse JSON
        nutritional_data = json.loads(response_text)
        
        # Validate and ensure all required fields are present with reasonable values
        result = {
            "calories": max(0, float(nutritional_data.get("calories", 0))),
            "protein": max(0, float(nutritional_data.get("protein", 0))),
            "carbohydrates": max(0, float(nutritional_data.get("carbohydrates", 0))),
            "fats": max(0, float(nutritional_data.get("fats", 0)))
        }
        
        print(f"AI Analysis for '{meal_description}': {result}")
        return result
        
    except Exception as e:
        print(f"Error analyzing meal with AI: {e}")
        print(f"Response was: {response_text if 'response_text' in locals() else 'No response'}")
        
        # Fallback: Try to provide accurate estimates based on common foods
        meal_lower = meal_description.lower()
        
        # Count quantities and estimate accordingly
        if 'banana' in meal_lower or 'bananas' in meal_lower:
            # Count bananas (rough estimate)
            banana_count = 1
            if any(word in meal_lower for word in ['2', 'two', '3', 'three', '4', 'four', '5', 'five']):
                if '2' in meal_lower or 'two' in meal_lower:
                    banana_count = 2
                elif '3' in meal_lower or 'three' in meal_lower:
                    banana_count = 3
                elif '4' in meal_lower or 'four' in meal_lower:
                    banana_count = 4
                elif '5' in meal_lower or 'five' in meal_lower:
                    banana_count = 5
            return {
                "calories": banana_count * 105,
                "protein": banana_count * 1.3,
                "carbohydrates": banana_count * 27,
                "fats": banana_count * 0.4
            }
        elif any(word in meal_lower for word in ['daal', 'dal', 'lentil']):
            if 'roti' in meal_lower or 'bread' in meal_lower:
                # Daal + roti combination
                return {"calories": 350, "protein": 21, "carbohydrates": 60, "fats": 2.8}
            else:
                # Just daal
                return {"calories": 230, "protein": 18, "carbohydrates": 40, "fats": 0.8}
        elif any(word in meal_lower for word in ['apple', 'peach', 'fruit']):
            return {"calories": 95, "protein": 0.5, "carbohydrates": 25, "fats": 0.3}
        elif any(word in meal_lower for word in ['rice', 'chawal']):
            return {"calories": 200, "protein": 4, "carbohydrates": 45, "fats": 0.5}
        else:
            return {"calories": 150, "protein": 6, "carbohydrates": 25, "fats": 3}

def get_ai_nutrition_advice(question: str, user_profile=None) -> str:
    """Get nutrition advice from Gemini AI with user context"""
    if user_profile:
        system_prompt = f"""
        You are a professional nutritionist and dietitian providing personalized advice.
        
        User Profile:
        - Age: {user_profile.age} years
        - Weight: {user_profile.weight} kg
        - Height: {user_profile.height} cm
        - Gender: {user_profile.gender}
        - Activity Level: {user_profile.activity_level}
        - Fitness Goal: {user_profile.fitness_goal}
        - Daily Calorie Goal: {user_profile.daily_calorie_goal:.0f} calories
        - Daily Protein Goal: {user_profile.daily_protein_goal:.0f}g
        - Daily Carb Goal: {user_profile.daily_carb_goal:.0f}g
        - Daily Fat Goal: {user_profile.daily_fat_goal:.0f}g
        
        Format your response in MARKDOWN with:
        - Use **bold** for important points and headings
        - Use bullet points with - for lists
        - Use proper paragraphs with line breaks
        - No double commas or formatting errors
        - Clean, professional structure
        
        Provide personalized, evidence-based advice considering this user's profile.
        Always recommend consulting with healthcare professionals for medical advice.
        Keep responses helpful and actionable with proper markdown formatting.
        """
    else:
        system_prompt = """
        You are a professional nutritionist and dietitian. Provide helpful, accurate, 
        and evidence-based advice about nutrition, diet, and healthy eating habits. 
        Always recommend consulting with healthcare professionals for medical advice.
        Keep responses concise but informative.
        """
    
    full_prompt = f"{system_prompt}\n\nUser question: {question}"
    
    try:
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        return f"I apologize, but I'm having trouble processing your question right now. Please try again later. Error: {str(e)}"

def get_daily_summary(user_id: int, target_date: date, db: Session) -> Dict[str, Any]:
    """Get daily nutritional summary for a user"""
    daily_log = db.query(DailyLog).filter(
        DailyLog.user_id == user_id,
        DailyLog.date == target_date
    ).first()
    
    if not daily_log:
        return {
            "total_calories": 0,
            "total_protein": 0,
            "total_carbohydrates": 0,
            "total_fats": 0,
            "meal_count": 0
        }
    
    meals = db.query(MealEntry).filter(MealEntry.log_id == daily_log.id).all()
    
    return {
        "total_calories": sum(meal.calories for meal in meals),
        "total_protein": sum(meal.protein for meal in meals),
        "total_carbohydrates": sum(meal.carbohydrates for meal in meals),
        "total_fats": sum(meal.fats for meal in meals),
        "meal_count": len(meals)
    }

def generate_meal_analysis_report(user_id: int, user_profile, db: Session) -> str:
    """Generate comprehensive meal analysis report"""
    from datetime import date, timedelta
    
    # Get last 30 days of data
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    # Get all meals in the last 30 days
    daily_logs = db.query(DailyLog).filter(
        DailyLog.user_id == user_id,
        DailyLog.date >= start_date,
        DailyLog.date <= end_date
    ).all()
    
    all_meals = []
    daily_totals = []
    
    for log in daily_logs:
        meals = db.query(MealEntry).filter(MealEntry.log_id == log.id).all()
        all_meals.extend(meals)
        
        daily_total = {
            "date": log.date,
            "calories": sum(meal.calories for meal in meals),
            "protein": sum(meal.protein for meal in meals),
            "carbs": sum(meal.carbohydrates for meal in meals),
            "fats": sum(meal.fats for meal in meals),
            "meal_count": len(meals)
        }
        daily_totals.append(daily_total)
    
    if not all_meals:
        return "No meal data available for analysis. Start logging your meals to get personalized insights!"
    
    # Calculate statistics
    total_calories = sum(meal.calories for meal in all_meals)
    total_protein = sum(meal.protein for meal in all_meals)
    total_carbs = sum(meal.carbohydrates for meal in all_meals)
    total_fats = sum(meal.fats for meal in all_meals)
    
    daily_calories = [day["calories"] for day in daily_totals if day["calories"] > 0]
    avg_daily_calories = sum(daily_calories) / len(daily_calories) if daily_calories else 0
    max_daily_calories = max(daily_calories) if daily_calories else 0
    min_daily_calories = min(daily_calories) if daily_calories else 0
    
    # Most common foods
    food_frequency = {}
    for meal in all_meals:
        food_words = meal.name.lower().split()
        for word in food_words:
            if len(word) > 3:  # Ignore short words
                food_frequency[word] = food_frequency.get(word, 0) + 1
    
    common_foods = sorted(food_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Generate AI report
    prompt = f"""
    Generate a comprehensive nutrition analysis report in MARKDOWN format for this user:
    
    User Profile:
    - Age: {user_profile.age} years, {user_profile.gender}
    - Weight: {user_profile.weight} kg, Height: {user_profile.height} cm
    - Activity Level: {user_profile.activity_level}
    - Fitness Goal: {user_profile.fitness_goal}
    - Daily Calorie Goal: {user_profile.daily_calorie_goal:.0f} calories
    
    Analysis Period: Last 30 days
    Total Meals Logged: {len(all_meals)}
    Days with Data: {len(daily_totals)}
    
    Nutritional Summary:
    - Total Calories: {total_calories:.0f} (Average: {avg_daily_calories:.0f}/day)
    - Total Protein: {total_protein:.0f}g (Average: {total_protein/len(daily_totals):.0f}g/day)
    - Total Carbs: {total_carbs:.0f}g (Average: {total_carbs/len(daily_totals):.0f}g/day)
    - Total Fats: {total_fats:.0f}g (Average: {total_fats/len(daily_totals):.0f}g/day)
    
    Daily Calorie Range: {min_daily_calories:.0f} - {max_daily_calories:.0f} calories
    
    Most Common Foods: {', '.join([food[0] for food in common_foods[:5]])}
    
    Format the response as proper MARKDOWN with:
    - Use **bold** for headings and important points
    - Use bullet points with - for lists
    - Use proper paragraphs with line breaks
    - No double commas or formatting errors
    - Clean, professional structure
    
    Include these sections:
    1. **Executive Summary**
    2. **Current Intake vs Goals**
    3. **Areas for Improvement**
    4. **Recommendations for {user_profile.fitness_goal}**
    5. **Foods to Avoid/Limit**
    6. **Healthy Alternatives**
    7. **Progress Assessment**
    8. **Actionable Next Steps**
    
    Make it personalized, encouraging, and practical with proper markdown formatting.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating report: {str(e)}"

def generate_comprehensive_report_html(user_id: int, user_profile, db: Session) -> str:
    """Generate comprehensive HTML report for download"""
    from datetime import date, timedelta
    
    # Get last 30 days of data
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    # Get all meals in the last 30 days
    daily_logs = db.query(DailyLog).filter(
        DailyLog.user_id == user_id,
        DailyLog.date >= start_date,
        DailyLog.date <= end_date
    ).all()
    
    all_meals = []
    daily_totals = []
    
    for log in daily_logs:
        meals = db.query(MealEntry).filter(MealEntry.log_id == log.id).all()
        all_meals.extend(meals)
        
        daily_total = {
            "date": log.date,
            "calories": sum(meal.calories for meal in meals),
            "protein": sum(meal.protein for meal in meals),
            "carbs": sum(meal.carbohydrates for meal in meals),
            "fats": sum(meal.fats for meal in meals),
            "meal_count": len(meals)
        }
        daily_totals.append(daily_total)
    
    # Calculate statistics
    total_calories = sum(meal.calories for meal in all_meals)
    total_protein = sum(meal.protein for meal in all_meals)
    total_carbs = sum(meal.carbohydrates for meal in all_meals)
    total_fats = sum(meal.fats for meal in all_meals)
    
    daily_calories = [day["calories"] for day in daily_totals if day["calories"] > 0]
    avg_daily_calories = sum(daily_calories) / len(daily_calories) if daily_calories else 0
    max_daily_calories = max(daily_calories) if daily_calories else 0
    min_daily_calories = min(daily_calories) if daily_calories else 0
    
    # Most common foods
    food_frequency = {}
    for meal in all_meals:
        food_words = meal.name.lower().split()
        for word in food_words:
            if len(word) > 3:
                food_frequency[word] = food_frequency.get(word, 0) + 1
    
    common_foods = sorted(food_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Generate HTML report
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Comprehensive Nutrition Report - {user_profile.user.full_name}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f8f9fa;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                text-align: center;
                margin-bottom: 30px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 2.5em;
            }}
            .header p {{
                margin: 10px 0 0 0;
                font-size: 1.2em;
                opacity: 0.9;
            }}
            .section {{
                background: white;
                padding: 25px;
                margin-bottom: 25px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .section h2 {{
                color: #667eea;
                border-bottom: 3px solid #667eea;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }}
            .profile-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }}
            .profile-item {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #667eea;
            }}
            .profile-item strong {{
                color: #667eea;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            .stat-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
            }}
            .stat-card h3 {{
                margin: 0 0 10px 0;
                font-size: 2em;
            }}
            .stat-card p {{
                margin: 0;
                opacity: 0.9;
            }}
            .meal-list {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            }}
            .meal-item {{
                background: white;
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
                border-left: 4px solid #28a745;
            }}
            .food-list {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin: 20px 0;
            }}
            .food-tag {{
                background: #667eea;
                color: white;
                padding: 8px 15px;
                border-radius: 20px;
                font-size: 0.9em;
            }}
            .recommendations {{
                background: #e8f5e8;
                padding: 20px;
                border-radius: 8px;
                border-left: 4px solid #28a745;
            }}
            .warnings {{
                background: #ffe8e8;
                padding: 20px;
                border-radius: 8px;
                border-left: 4px solid #dc3545;
            }}
            .footer {{
                text-align: center;
                margin-top: 40px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 10px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🍎 Comprehensive Nutrition Report</h1>
            <p>Generated on {date.today().strftime('%B %d, %Y')}</p>
        </div>

        <div class="section">
            <h2>👤 User Profile</h2>
            <div class="profile-grid">
                <div class="profile-item">
                    <strong>Name:</strong> {user_profile.user.full_name}
                </div>
                <div class="profile-item">
                    <strong>Age:</strong> {user_profile.age} years
                </div>
                <div class="profile-item">
                    <strong>Gender:</strong> {user_profile.gender.title()}
                </div>
                <div class="profile-item">
                    <strong>Weight:</strong> {user_profile.weight} kg
                </div>
                <div class="profile-item">
                    <strong>Height:</strong> {user_profile.height} cm
                </div>
                <div class="profile-item">
                    <strong>Activity Level:</strong> {user_profile.activity_level.replace('_', ' ').title()}
                </div>
                <div class="profile-item">
                    <strong>Fitness Goal:</strong> {user_profile.fitness_goal.replace('_', ' ').title()}
                </div>
            </div>
        </div>

        <div class="section">
            <h2>📊 Daily Goals</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>{user_profile.daily_calorie_goal:.0f}</h3>
                    <p>Calories</p>
                </div>
                <div class="stat-card">
                    <h3>{user_profile.daily_protein_goal:.0f}g</h3>
                    <p>Protein</p>
                </div>
                <div class="stat-card">
                    <h3>{user_profile.daily_carb_goal:.0f}g</h3>
                    <p>Carbohydrates</p>
                </div>
                <div class="stat-card">
                    <h3>{user_profile.daily_fat_goal:.0f}g</h3>
                    <p>Fats</p>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>📈 Performance Analysis (Last 30 Days)</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>{avg_daily_calories:.0f}</h3>
                    <p>Avg Daily Calories</p>
                </div>
                <div class="stat-card">
                    <h3>{total_protein/len(daily_totals):.0f}g</h3>
                    <p>Avg Daily Protein</p>
                </div>
                <div class="stat-card">
                    <h3>{total_carbs/len(daily_totals):.0f}g</h3>
                    <p>Avg Daily Carbs</p>
                </div>
                <div class="stat-card">
                    <h3>{total_fats/len(daily_totals):.0f}g</h3>
                    <p>Avg Daily Fats</p>
                </div>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>{len(all_meals)}</h3>
                    <p>Total Meals Logged</p>
                </div>
                <div class="stat-card">
                    <h3>{len(daily_totals)}</h3>
                    <p>Days with Data</p>
                </div>
                <div class="stat-card">
                    <h3>{min_daily_calories:.0f} - {max_daily_calories:.0f}</h3>
                    <p>Calorie Range</p>
                </div>
                <div class="stat-card">
                    <h3>{((avg_daily_calories / user_profile.daily_calorie_goal) * 100):.0f}%</h3>
                    <p>Goal Achievement</p>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>🍽️ Recent Meals</h2>
            <div class="meal-list">
                {''.join([f'''
                <div class="meal-item">
                    <strong>{meal.name}</strong><br>
                    <small>{meal.calories:.0f} cal • {meal.protein:.0f}g protein • {meal.carbohydrates:.0f}g carbs • {meal.fats:.0f}g fat</small>
                </div>
                ''' for meal in all_meals[-10:]])}
            </div>
        </div>

        <div class="section">
            <h2>🥗 Most Common Foods</h2>
            <div class="food-list">
                {''.join([f'<span class="food-tag">{food[0]} ({food[1]}x)</span>' for food in common_foods[:10]])}
            </div>
        </div>

        <div class="section">
            <h2>✅ Recommendations</h2>
            <div class="recommendations">
                <h3>What's Working Well:</h3>
                <ul>
                    <li>Consistent meal logging shows commitment to tracking</li>
                    <li>Variety in food choices indicates balanced approach</li>
                    <li>Regular monitoring helps maintain awareness</li>
                </ul>
            </div>
        </div>

        <div class="section">
            <h2>⚠️ Areas for Improvement</h2>
            <div class="warnings">
                <h3>Focus Areas:</h3>
                <ul>
                    <li>Increase daily calorie intake to meet goals</li>
                    <li>Add more protein-rich foods to your diet</li>
                    <li>Consider meal timing for better nutrition distribution</li>
                    <li>Track hydration and water intake</li>
                </ul>
            </div>
        </div>

        <div class="footer">
            <p>This report was generated by your Calorie Tracker app</p>
            <p>For personalized nutrition advice, consult with a registered dietitian</p>
        </div>
    </body>
    </html>
    """
    
    return html_content

