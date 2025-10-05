@echo off
REM Launcher script for PDF Splitter Pro (Windows)

echo ===================================
echo   PDF Splitter Pro Launcher
echo ===================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%

REM Check if virtual environment exists
if not exist "venv\" (
    echo.
    echo Creating virtual environment...
    python -m venv venv
    
    if errorlevel 1 (
        echo Error: Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import kivy" >nul 2>&1
if errorlevel 1 goto install_deps

python -c "import PyPDF2" >nul 2>&1
if errorlevel 1 goto install_deps

goto run_app

:install_deps
echo.
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo Error: Failed to install dependencies.
    pause
    exit /b 1
)

:run_app
echo.
echo Starting PDF Splitter Pro...
echo.

REM Run the application
python main.py

REM Deactivate virtual environment on exit
call deactivate

pause
