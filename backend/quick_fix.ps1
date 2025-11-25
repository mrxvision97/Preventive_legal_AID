# Quick Fix Script for FastAPI ModuleNotFoundError
# Run this script from the backend directory

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "VU Legal AID - Quick Fix Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "app\main.py")) {
    Write-Host "Error: Please run this script from the backend directory" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    exit 1
}

Write-Host "Step 1: Checking virtual environment..." -ForegroundColor Yellow

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 2: Activating virtual environment..." -ForegroundColor Yellow

# Activate virtual environment
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "Warning: Could not activate venv. Continuing anyway..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 3: Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "✅ pip upgraded" -ForegroundColor Green

Write-Host ""
Write-Host "Step 4: Installing dependencies..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Yellow

python -m pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to install dependencies" -ForegroundColor Red
    Write-Host "Try running manually: python -m pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Dependencies installed" -ForegroundColor Green

Write-Host ""
Write-Host "Step 5: Verifying installation..." -ForegroundColor Yellow

python -c "import fastapi; import uvicorn; print('✅ FastAPI and Uvicorn are installed!')"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Verification failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the server, run:" -ForegroundColor Yellow
Write-Host "  python -m uvicorn app.main:app --reload" -ForegroundColor Cyan
Write-Host ""
Write-Host "Or use the batch script:" -ForegroundColor Yellow
Write-Host "  .\run_server.bat" -ForegroundColor Cyan
Write-Host ""

