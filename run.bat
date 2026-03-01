@echo off
REM Chatbot Performance Metrics Analyzer - Windows Launcher
REM This script will automatically setup and run the application

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║  Chatbot Performance Metrics Analyzer                  ║
echo ║  Starting application...                               ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Get the directory where this script is located
setlocal enabledelayedexpansion
set SCRIPT_DIR=%~dp0

REM Change to the script directory
cd /d "%SCRIPT_DIR%"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

REM Check if venv folder exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo.
echo Installing dependencies (this may take a minute)...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo.
    echo ❌ Failed to install dependencies
    echo Attempting to continue anyway...
)

REM Run Streamlit
echo.
echo ✅ Starting app...
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo The app will open in your browser at:
echo   http://localhost:8501
echo.
echo Press Ctrl+C to stop the server (and close this window)
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

streamlit run app.py

pause
