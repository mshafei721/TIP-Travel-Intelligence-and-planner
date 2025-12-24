# ==============================================
# TIP - Docker Management Script (PowerShell)
# ==============================================

param(
    [Parameter(Position=0)]
    [ValidateSet("up", "down", "restart", "logs", "ps", "build", "clean", "test")]
    [string]$Command = "up",

    [Parameter(Position=1)]
    [string]$Service = ""
)

$ErrorActionPreference = "Stop"

function Write-Header {
    param([string]$Message)
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Blue
}

# Check if Docker is running
function Test-Docker {
    try {
        docker info | Out-Null
        return $true
    } catch {
        Write-Error "Docker is not running. Please start Docker Desktop."
        exit 1
    }
}

# Main script
Write-Header "TIP Docker Manager"

Test-Docker

switch ($Command) {
    "up" {
        Write-Info "Starting Docker services..."
        docker-compose up -d
        Write-Success "Services started successfully"
        Write-Info "Access:"
        Write-Host "  - Backend API: http://localhost:8000"
        Write-Host "  - API Docs: http://localhost:8000/docs"
        Write-Host "  - Flower UI: http://localhost:5555"
        Write-Host "`nView logs: .\docker.ps1 logs"
    }

    "down" {
        Write-Info "Stopping Docker services..."
        docker-compose down
        Write-Success "Services stopped successfully"
    }

    "restart" {
        Write-Info "Restarting Docker services..."
        if ($Service) {
            docker-compose restart $Service
            Write-Success "Service '$Service' restarted"
        } else {
            docker-compose restart
            Write-Success "All services restarted"
        }
    }

    "logs" {
        if ($Service) {
            Write-Info "Viewing logs for $Service..."
            docker-compose logs -f $Service
        } else {
            Write-Info "Viewing logs for all services..."
            docker-compose logs -f
        }
    }

    "ps" {
        Write-Info "Service status:"
        docker-compose ps
    }

    "build" {
        Write-Info "Building Docker images..."
        docker-compose build --no-cache
        Write-Success "Images built successfully"
    }

    "clean" {
        Write-Info "Cleaning up Docker resources..."
        docker-compose down -v
        docker system prune -f
        Write-Success "Cleanup complete"
    }

    "test" {
        Write-Info "Testing Docker setup..."

        # Start services
        docker-compose up -d
        Start-Sleep -Seconds 5

        # Test Backend API
        Write-Info "Testing Backend API..."
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Success "Backend API is healthy"
            }
        } catch {
            Write-Error "Backend API health check failed"
        }

        # Test Flower UI
        Write-Info "Testing Flower UI..."
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:5555" -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Success "Flower UI is accessible"
            }
        } catch {
            Write-Error "Flower UI is not accessible"
        }

        # Test Celery worker
        Write-Info "Testing Celery worker..."
        docker-compose exec -T celery-worker celery -A app.core.celery_app inspect ping

        Write-Success "Docker setup test complete"
    }

    default {
        Write-Error "Unknown command: $Command"
        Write-Info "Available commands: up, down, restart, logs, ps, build, clean, test"
    }
}

Write-Host ""
