"""
THE Nutritionist™ - Streamlit Deployment
Developed by Zohaib Muaz
"""

import streamlit as st
import requests
import json
import sqlite3
import os
from datetime import datetime
import subprocess
import threading
import time
import uvicorn
from fastapi import FastAPI
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.append(str(backend_path))

def start_backend():
    """Start the FastAPI backend server"""
    try:
        os.chdir("backend")
        subprocess.Popen([
            "python", "-m", "uvicorn", "main:app", 
            "--host", "0.0.0.0", "--port", "8000"
        ])
        os.chdir("..")
        time.sleep(3)  # Give server time to start
    except Exception as e:
        st.error(f"Error starting backend: {e}")

def check_backend():
    """Check if backend is running"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        return response.status_code == 200
    except:
        return False

# Start backend if not running
if not check_backend():
    with st.spinner("Starting backend server..."):
        start_backend()

# Streamlit app configuration
st.set_page_config(
    page_title="THE Nutritionist™",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .feature-card {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .demo-button {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        text-decoration: none;
        display: inline-block;
        margin: 1rem;
        text-align: center;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🍃 THE Nutritionist™</h1>
    <h3>AI-Powered Nutrition Tracking & Health Management</h3>
    <p><strong>Developed by Zohaib Muaz</strong></p>
</div>
""", unsafe_allow_html=True)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ## 🚀 **Live Demo Available!**
    
    Experience the futuristic UI and AI-powered features of THE Nutritionist™. 
    This comprehensive health management system combines cutting-edge technology 
    with stunning visual design.
    
    ### ✨ **Key Features:**
    - 🤖 **AI-Powered Meal Analysis** - Natural language meal logging
    - 💬 **Interactive AI Nutritionist** - Personalized nutrition advice
    - 📊 **Advanced Analytics** - Beautiful charts and progress tracking
    - 🎨 **Futuristic UI/UX** - Glassmorphism effects and neon colors
    - 🌙 **Dark/Light Themes** - Smooth theme transitions
    - 📱 **Fully Responsive** - Perfect on all devices
    """)
    
    # Demo link
    if st.button("🚀 Launch Full Application", help="Open the complete app in new window"):
        st.markdown("""
        <script>
        window.open('http://localhost:3000', '_blank');
        </script>
        """, unsafe_allow_html=True)
        st.success("Click the link below to access the full application!")
        st.markdown("[🔗 **Open THE Nutritionist™**](http://localhost:3000)")

with col2:
    st.markdown("""
    <div class="feature-card">
        <h4>🛠️ Tech Stack</h4>
        <ul>
            <li><strong>Backend:</strong> FastAPI + Python</li>
            <li><strong>Frontend:</strong> HTML5 + CSS3 + JavaScript</li>
            <li><strong>Database:</strong> SQLite</li>
            <li><strong>AI:</strong> Custom nutrition algorithms</li>
            <li><strong>Design:</strong> Glassmorphism + Animations</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Instructions
st.markdown("""
---
## 📱 **How to Use:**

1. **Register/Login** - Create your account with the beautiful glass-style forms
2. **Complete Profile** - Set your fitness goals and personal information  
3. **Log Meals** - Simply describe what you ate in natural language
4. **Chat with AI** - Ask the AI nutritionist for personalized advice
5. **View Analytics** - Explore your nutrition data with stunning neon charts
6. **Switch Themes** - Toggle between dark and light modes

---
## 🎯 **Demo Highlights:**

- **Futuristic Design**: Experience glassmorphism effects and smooth animations
- **AI Integration**: See how natural language processing works for meal logging
- **Responsive Layout**: Test the mobile-friendly sidebar and navigation
- **Theme System**: Try the beautiful dark/light mode transitions
- **Interactive Charts**: Explore nutrition data with Chart.js visualizations

---
## 👨‍💻 **About the Developer:**

**Zohaib Muaz** - Full Stack Developer specializing in AI integration and modern UI/UX design.

This project showcases expertise in:
- Full-stack web development
- AI and machine learning integration  
- Modern CSS animations and effects
- Responsive design principles
- User experience optimization

---
## 🔗 **Links:**

- 📱 **Live Demo**: Launch the app using the button above
- 💻 **Source Code**: Available on GitHub
- 📄 **Documentation**: Comprehensive README included
- 💼 **Portfolio**: [Developer Portfolio]

---
*Built with ❤️ using FastAPI, JavaScript, and modern web technologies*
""")

# Footer
st.markdown("""
---
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>© 2025 THE Nutritionist™ - Developed by Zohaib Muaz</p>
    <p><em>AI-Powered Nutrition Tracking & Health Management System</em></p>
</div>
""", unsafe_allow_html=True)

# Background process to keep backend running
if not st.session_state.get("backend_started", False):
    st.session_state.backend_started = True
    if not check_backend():
        st.warning("Backend server is starting... Please wait a moment and refresh the page.")
