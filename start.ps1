# Personal AI Agent - Startup Script
Write-Host "Starting Personal AI Agent..." -ForegroundColor Cyan

# Kill any existing backend processes
Write-Host "Cleaning up old processes..." -ForegroundColor Yellow
Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start backend in new window
Write-Host "Starting backend server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; Write-Host 'Backend Server Running on http://127.0.0.1:8000' -ForegroundColor Green; python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000"

# Wait for backend to start
Start-Sleep -Seconds 3

# Start frontend
Write-Host "Starting frontend..." -ForegroundColor Green
Set-Location "$PSScriptRoot\ui"
npm run dev

Write-Host "Press any key to stop all servers..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Cleanup
Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
