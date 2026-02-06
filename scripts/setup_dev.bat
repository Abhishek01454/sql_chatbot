@echo off
REM CORE AI Chatbot - Development Environment Setup Script (Windows)
REM This script automates the setup of the development environment on Windows

setlocal enabledelayedexpansion

echo ==========================================
echo CORE AI Chatbot - Development Setup
echo ==========================================
echo.

REM Check Python installation
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.11 or higher from https://www.python.org/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [SUCCESS] Python %PYTHON_VERSION% installed
echo.

REM Check Node.js installation
echo [INFO] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js 18 or higher from https://nodejs.org/
    pause
    exit /b 1
)

for /f "tokens=1" %%i in ('node --version') do set NODE_VERSION=%%i
echo [SUCCESS] Node.js %NODE_VERSION% installed
echo.

REM Check Docker installation (optional)
echo [INFO] Checking Docker installation...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=3" %%i in ('docker --version') do set DOCKER_VERSION=%%i
    echo [SUCCESS] Docker %DOCKER_VERSION% installed
) else (
    echo [WARNING] Docker not found (optional but recommended)
)
echo.

REM Ask to continue
set /p CONTINUE="Continue with setup? (y/n): "
if /i not "%CONTINUE%"=="y" (
    echo Setup cancelled
    exit /b 0
)
echo.

REM Setup Backend
echo ==========================================
echo Setting up Backend
echo ==========================================
echo.

cd backend

REM Create virtual environment
echo [INFO] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo [SUCCESS] Virtual environment created
) else (
    echo [SUCCESS] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo [SUCCESS] Pip upgraded
echo.

REM Install dependencies
echo [INFO] Installing Python dependencies...
echo This may take a few minutes...
pip install -r requirements-enterprise.txt --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [SUCCESS] Dependencies installed
echo.

REM Setup environment file
if not exist ".env" (
    echo [INFO] Creating .env file from template...
    copy .env.example .env >nul
    echo [WARNING] Please update .env with your configuration
    echo [WARNING] Especially add your MISTRAL_API_KEY
) else (
    echo [SUCCESS] .env file already exists
)
echo.

REM Create logs directory
if not exist "logs" (
    mkdir logs
    echo [SUCCESS] Logs directory created
)

cd ..

REM Setup Frontend
echo ==========================================
echo Setting up Frontend
echo ==========================================
echo.

cd frontend

REM Install dependencies
echo [INFO] Installing Node.js dependencies...
echo This may take a few minutes...
call npm install --silent
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [SUCCESS] Dependencies installed
echo.

cd ..

REM Setup Database
set /p INIT_DB="Initialize database now? (y/n): "
if /i "%INIT_DB%"=="y" (
    echo.
    echo ==========================================
    echo Setting up Database
    echo ==========================================
    echo.
    cd backend
    call venv\Scripts\activate.bat
    python ..\scripts\init_db.py
    cd ..
) else (
    echo [INFO] Database initialization skipped
    echo [INFO] Run 'python scripts\init_db.py' when ready
)
echo.

REM Final instructions
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo [SUCCESS] Development environment is ready!
echo.
echo Next steps:
echo   1. Update backend\.env with your MISTRAL_API_KEY
echo.
echo   2. Start backend (in new terminal):
echo      cd backend
echo      venv\Scripts\activate
echo      uvicorn app.main:app --reload
echo.
echo   3. Start frontend (in new terminal):
echo      cd frontend
echo      npm run dev
echo.
echo Or use Docker:
echo   docker-compose up -d
echo.
echo Access the application:
echo   - Frontend: http://localhost:3000
echo   - Backend:  http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo.
echo ==========================================

pause
