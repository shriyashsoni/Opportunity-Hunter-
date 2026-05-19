@echo off
title Opportunity Hunter AI Agent Runner
color 0B

echo ============================================================
echo           STARTING OPPORTUNITY HUNTER AI AGENT          
echo ============================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to your system PATH.
    echo Please install Python from https://python.org and try again.
    echo.
    pause
    exit /b
)

:: Run the agent
echo [INFO] Executing AI Agent sweep...
python main.py

echo.
echo ============================================================
echo           EXECUTION COMPLETED SUCCESSFULLY          
echo ============================================================
echo.
pause
