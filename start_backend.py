#!/usr/bin/env python3
"""
Startup script for the Calorie Tracker backend
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    # Change to backend directory
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    print("🚀 Starting Calorie Tracker Backend...")
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Check if virtual environment exists
    venv_path = backend_dir / "venv"
    if not venv_path.exists():
        print("⚠️  Virtual environment not found. Creating one...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created")
    
    # Determine the correct activation script
    if os.name == 'nt':  # Windows
        activate_script = venv_path / "Scripts" / "activate.bat"
        pip_path = venv_path / "Scripts" / "pip.exe"
        python_path = venv_path / "Scripts" / "python.exe"
    else:  # Unix/Linux/MacOS
        activate_script = venv_path / "bin" / "activate"
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    # Check if requirements are installed
    try:
        subprocess.run([str(pip_path), "show", "fastapi"], check=True, capture_output=True)
        print("✅ Dependencies already installed")
    except subprocess.CalledProcessError:
        print("📦 Installing dependencies...")
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed")
    
    # Check for .env file
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("⚠️  .env file not found!")
        print("📝 Please create a .env file based on env_example.txt")
        print("🔑 Don't forget to add your Gemini API key!")
        return
    
    # Start the server
    print("🌐 Starting FastAPI server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.run([str(python_path), "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
