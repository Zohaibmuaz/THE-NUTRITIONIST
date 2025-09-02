@echo off
echo 🚀 Starting Calorie Tracker Application
echo =====================================

echo.
echo 📋 Choose an option:
echo 1. Start Backend Server
echo 2. Start Frontend Server  
echo 3. Run Setup Test
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo 🌐 Starting Backend Server...
    python start_backend.py
) else if "%choice%"=="2" (
    echo.
    echo 🎨 Starting Frontend Server...
    python start_frontend.py
) else if "%choice%"=="3" (
    echo.
    echo 🧪 Running Setup Test...
    python test_setup.py
) else if "%choice%"=="4" (
    echo 👋 Goodbye!
    exit /b 0
) else (
    echo ❌ Invalid choice. Please run the script again.
    pause
    exit /b 1
)

pause
