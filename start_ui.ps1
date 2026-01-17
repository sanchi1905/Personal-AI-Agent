# Personal AI Agent - Phase 5 Desktop UI Launcher
# Run both backend and frontend

Write-Host "🚀 Starting Personal AI Agent - Phase 5 Desktop UI" -ForegroundColor Cyan
Write-Host "=" -ForegroundColor Cyan

# Check if Node.js is installed
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js is not installed. Please install Node.js 18+ first." -ForegroundColor Red
    exit 1
}

# Check if Python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python is not installed. Please install Python 3.9+ first." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📦 Installing UI dependencies..." -ForegroundColor Yellow
Set-Location ui
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install UI dependencies" -ForegroundColor Red
    exit 1
}
Set-Location ..

Write-Host "✅ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Start backend in background
Write-Host "🔧 Starting backend API server on port 8000..." -ForegroundColor Yellow
$backend = Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "src.api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000" -PassThru -NoNewWindow

Start-Sleep -Seconds 3

# Check if backend started
if ($backend.HasExited) {
    Write-Host "❌ Backend failed to start" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Backend API running on http://localhost:8000" -ForegroundColor Green
Write-Host ""

# Start frontend
Write-Host "🎨 Starting frontend UI server on port 3000..." -ForegroundColor Yellow
Set-Location ui
Write-Host ""
Write-Host "=" -ForegroundColor Cyan
Write-Host "🌐 Desktop UI will open at: http://localhost:3000" -ForegroundColor Green
Write-Host "🔌 Backend API running at: http://localhost:8000" -ForegroundColor Green
Write-Host "=" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop both servers" -ForegroundColor Yellow
Write-Host ""

# Start frontend (this will block)
npm run dev

# Cleanup when frontend stops
Write-Host ""
Write-Host "🛑 Stopping backend server..." -ForegroundColor Yellow
Stop-Process -Id $backend.Id -Force
Write-Host "✅ All servers stopped" -ForegroundColor Green
