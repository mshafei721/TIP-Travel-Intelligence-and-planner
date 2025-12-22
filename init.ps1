# TIP - Travel Intelligence & Planner
# Project Initialization Script for Windows PowerShell
#
# This script sets up the development environment for TIP

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TIP - Travel Intelligence & Planner" -ForegroundColor Cyan
Write-Host "Initialization Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check for required tools
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check Node.js
try {
    $nodeVersion = node --version
    Write-Host "[OK] Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Node.js not found. Please install from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Check Python
try {
    $pythonVersion = python --version
    Write-Host "[OK] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found. Please install from https://www.python.org/" -ForegroundColor Red
    exit 1
}

# Check Git
try {
    $gitVersion = git --version
    Write-Host "[OK] Git found: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Git not found. Please install from https://git-scm.com/" -ForegroundColor Red
    exit 1
}

# Check Docker (optional)
try {
    $dockerVersion = docker --version
    Write-Host "[OK] Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Docker not found. Some features may not work." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Setting up project..." -ForegroundColor Yellow

# Create .env template if it doesn't exist
if (!(Test-Path ".env")) {
    Write-Host "Creating .env template..." -ForegroundColor Yellow
    @"
# TIP Environment Configuration

# Database (Supabase)
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# Redis
REDIS_URL=redis://localhost:6379

# External APIs
WEATHER_API_KEY=your_weather_api_key
CURRENCY_API_KEY=your_currency_api_key
FLIGHT_API_KEY=your_flight_api_key
VISA_API_KEY=your_visa_api_key
MAPBOX_API_KEY=your_mapbox_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key

# LLM APIs
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# App Settings
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
ENVIRONMENT=development
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "[OK] .env template created" -ForegroundColor Green
} else {
    Write-Host "[SKIP] .env already exists" -ForegroundColor Gray
}

# Install frontend dependencies
if (Test-Path "frontend/package.json") {
    Write-Host ""
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location -Path "frontend"
    npm install
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Frontend dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Failed to install frontend dependencies" -ForegroundColor Red
    }
    Set-Location -Path ".."
} else {
    Write-Host "[SKIP] frontend/package.json not found. Skipping frontend setup." -ForegroundColor Gray
}

# Install backend dependencies
if (Test-Path "backend/requirements.txt") {
    Write-Host ""
    Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
    Set-Location -Path "backend"

    # Create virtual environment if it doesn't exist
    if (!(Test-Path "venv")) {
        Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
        python -m venv venv
    }

    # Activate virtual environment and install dependencies
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Backend dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Failed to install backend dependencies" -ForegroundColor Red
    }

    deactivate
    Set-Location -Path ".."
} else {
    Write-Host "[SKIP] backend/requirements.txt not found. Skipping backend setup." -ForegroundColor Gray
}

# Start Redis with Docker (if available)
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host ""
    Write-Host "Checking Redis..." -ForegroundColor Yellow

    # Check if Redis container is already running
    $redisRunning = docker ps --filter "name=tip-redis" --format "{{.Names}}"

    if ($redisRunning -eq "tip-redis") {
        Write-Host "[OK] Redis container already running" -ForegroundColor Green
    } else {
        Write-Host "Starting Redis container..." -ForegroundColor Yellow
        docker run -d --name tip-redis -p 6379:6379 redis:alpine
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Redis container started" -ForegroundColor Green
        } else {
            Write-Host "[ERROR] Failed to start Redis container" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Initialization Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Configure your .env file with API keys" -ForegroundColor White
Write-Host "2. To start frontend: cd frontend && npm run dev" -ForegroundColor White
Write-Host "3. To start backend: cd backend && .\venv\Scripts\Activate.ps1 && uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "4. To start Celery worker: cd backend && .\venv\Scripts\Activate.ps1 && celery -A app.tasks.celery worker --loglevel=info" -ForegroundColor White
Write-Host ""
Write-Host "For more information, see README.md" -ForegroundColor Gray
