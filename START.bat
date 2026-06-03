@echo off
REM Quick Start Script for PDF Summarization Application

echo.
echo ==============================================
echo  PDF Summarization Application - Quick Start
echo ==============================================
echo.

REM Check if running from correct directory
if not exist "backend" (
    echo ERROR: Please run this script from the root directory (summarize folder)
    echo Expected: TECHM work\summarize\
    pause
    exit /b 1
)

REM Start Backend
echo Starting backend server...
start cmd /k "cd backend && venv\Scripts\activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a moment for backend to start
timeout /t 3 /nobreak

REM Start Frontend
echo Starting frontend server...
start cmd /k "cd frontend && npm run dev"

REM Wait for servers to start
timeout /t 5 /nobreak

echo.
echo ==============================================
echo   Servers Started Successfully!
echo ==============================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo Health:   http://localhost:8000/health
echo.
echo Press ENTER to open the application...
pause

REM Open browser
start http://localhost:5173

echo.
echo Application opened in browser!
echo Close these windows to stop the servers.
pause
