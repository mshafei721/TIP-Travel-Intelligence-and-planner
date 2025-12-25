# ==============================================
# Pre-commit Setup Script (PowerShell)
# ==============================================
# This script sets up pre-commit hooks for the TIP backend
# Run this script from the backend directory

Write-Host "==============================================`n" -ForegroundColor Cyan
Write-Host "  TIP Backend - Pre-commit Hooks Setup`n" -ForegroundColor Cyan
Write-Host "==============================================`n" -ForegroundColor Cyan

# Check if Python is installed
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found! Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Install/upgrade pip
Write-Host "`n[2/5] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
Write-Host "  ✓ pip upgraded" -ForegroundColor Green

# Install requirements
Write-Host "`n[3/5] Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Install pre-commit hooks
Write-Host "`n[4/5] Installing pre-commit hooks..." -ForegroundColor Yellow
pre-commit install
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Pre-commit hooks installed" -ForegroundColor Green
} else {
    Write-Host "  ✗ Failed to install pre-commit hooks" -ForegroundColor Red
    exit 1
}

# Run pre-commit on all files (optional first check)
Write-Host "`n[5/5] Running pre-commit on all files (first-time check)..." -ForegroundColor Yellow
Write-Host "  Note: This may take a few minutes on first run..." -ForegroundColor Gray
pre-commit run --all-files
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n  ✓ All pre-commit checks passed!" -ForegroundColor Green
} else {
    Write-Host "`n  ⚠ Some checks failed. Files have been auto-fixed where possible." -ForegroundColor Yellow
    Write-Host "  Review the changes and commit them." -ForegroundColor Yellow
}

Write-Host "`n==============================================`n" -ForegroundColor Cyan
Write-Host "  ✓ Setup Complete!`n" -ForegroundColor Green
Write-Host "==============================================`n" -ForegroundColor Cyan
Write-Host "Pre-commit hooks are now active. They will run automatically on 'git commit'.`n" -ForegroundColor White
Write-Host "Manual commands:" -ForegroundColor Yellow
Write-Host "  • Run on all files:     pre-commit run --all-files" -ForegroundColor Gray
Write-Host "  • Run on staged files:  pre-commit run" -ForegroundColor Gray
Write-Host "  • Skip hooks (not recommended): git commit --no-verify`n" -ForegroundColor Gray
Write-Host "Tool configurations are in:" -ForegroundColor Yellow
Write-Host "  • pyproject.toml (Black, Ruff, Mypy, Pytest, Coverage)" -ForegroundColor Gray
Write-Host "  • .pre-commit-config.yaml (Hook definitions)`n" -ForegroundColor Gray
