# Quick Start Script for PDF Summarization Application (PowerShell)

Write-Host ""
Write-Host "=============================================="
Write-Host "  PDF Summarization Application - Quick Start" -ForegroundColor Cyan
Write-Host "=============================================="
Write-Host ""

# Check if running from correct directory
if (-not (Test-Path "backend")) {
    Write-Host "ERROR: Please run this script from the root directory (summarize folder)" -ForegroundColor Red
    Write-Host "Expected: TECHM work\summarize\"
    pause
    exit 1
}

# Check for .env file
if (-not (Test-Path "backend\.env")) {
    Write-Host "WARNING: .env file not found in backend directory" -ForegroundColor Yellow
    Write-Host "Please create backend\.env with your CEREBRAS_API_KEY" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Starting backend server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; venv\Scripts\activate; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

Write-Host "Waiting for backend to start..." -ForegroundColor Gray
Start-Sleep -Seconds 3

Write-Host "Starting frontend server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host ""
Write-Host "=============================================="
Write-Host "  Servers Starting..." -ForegroundColor Green
Write-Host "=============================================="
Write-Host ""
Write-Host "Backend URL:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend URL: http://localhost:5173" -ForegroundColor Cyan
Write-Host "Health Check: http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""

Write-Host "Waiting for servers to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 5

Write-Host "Opening application in browser..." -ForegroundColor Green
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "=============================================="
Write-Host "  Application Ready!" -ForegroundColor Green
Write-Host "=============================================="
Write-Host ""
Write-Host "The application should open automatically."
Write-Host "Close the terminal windows to stop the servers."
Write-Host ""

pause
