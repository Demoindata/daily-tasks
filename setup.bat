@echo off
chcp 65001 >nul
title Daily Task Reminder - Setup

cd /d "%~dp0"

echo ============================================
echo   Daily Task Reminder - Setup
echo ============================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [Error] Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

:menu
echo What would you like to do?
echo.
echo  1  Launch the task reminder now
echo  2  Install auto-start (weekdays at 09:00)
echo  3  Remove auto-start schedule
echo  4  Check schedule status
echo  5  Exit
echo.

set /p choice=Enter your choice (1-5):

if "%choice%"=="1" (
    echo.
    echo Starting Daily Task Reminder...
    start "" python "%~dp0daily_tasks.py"
    goto :eof
)

if "%choice%"=="2" (
    echo.
    echo Installing scheduled task...
    python "%~dp0daily_tasks.py" --setup
    if %errorlevel% equ 0 (
        echo.
        echo Success! The reminder will show up every weekday at 09:00.
    ) else (
        echo.
        echo Setup failed. Try running this script as Administrator.
    )
    echo.
    pause
    goto menu
)

if "%choice%"=="3" (
    echo.
    python "%~dp0daily_tasks.py" --remove
    echo.
    pause
    goto menu
)

if "%choice%"=="4" (
    echo.
    python "%~dp0daily_tasks.py" --status
    echo.
    pause
    goto menu
)

if "%choice%"=="5" exit /b 0

echo Invalid choice.
echo.
pause
goto menu
