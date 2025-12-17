#!/usr/bin/env pwsh
Set-StrictMode -Version Latest

Write-Host "=== RAG Document QA - Full Setup ===" -ForegroundColor Green
Write-Host ""

# Create and activate venv
Write-Host "1. Setting up Python virtual environment..." -ForegroundColor Cyan
python -m venv venv
& .\venv\Scripts\Activate.ps1

# Install backend dependencies
Write-Host "2. Installing backend dependencies..." -ForegroundColor Cyan
pip install --upgrade pip
pip install -r requirements.txt

# Install frontend dependencies
Write-Host "3. Installing frontend dependencies..." -ForegroundColor Cyan
Push-Location frontend
npm install
Write-Host "4. Building frontend..." -ForegroundColor Cyan
npm run build
Pop-Location

# Create .env if not exists
if (-not (Test-Path .env)) {
  Write-Host "5. Creating .env file from .env.example..." -ForegroundColor Cyan
  Copy-Item .env.example .env
  Write-Host "   ??  Update .env with your OPENAI_API_KEY" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\Activate.ps1"
Write-Host "  uvicorn src.api:app --host 0.0.0.0 --port 8000"
Write-Host ""
Write-Host "Then open: http://localhost:8000" -ForegroundColor Green
