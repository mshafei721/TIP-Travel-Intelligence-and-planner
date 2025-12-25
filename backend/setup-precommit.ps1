# ==============================================
# Pre-commit Setup Script (PowerShell)
# ==============================================
# This script sets up pre-commit hooks for the TIP backend
# Run this script from the backend directory

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "  TIP Backend - Pre-commit Hooks Setup" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python installation
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1 | Out-String
    Write-Host "  [OK] Found: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "  [ERROR] Python not found! Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Step 2: Upgrade pip
Write-Host ""
Write-Host "[2/5] Upgrading pip..." -ForegroundColor Yellow
try {
    python -m pip install --upgrade pip --quiet
    Write-Host "  [OK] pip upgraded successfully" -ForegroundColor Green
}
catch {
    Write-Host "  [WARNING] pip upgrade had issues, continuing anyway..." -ForegroundColor Yellow
}

# Step 3: Install requirements
Write-Host ""
Write-Host "[3/5] Installing Python dependencies..." -ForegroundColor Yellow
Write-Host "  This may take a few minutes..." -ForegroundColor Gray
try {
    pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Dependencies installed successfully" -ForegroundColor Green
    }
    else {
        Write-Host "  [ERROR] Failed to install dependencies" -ForegroundColor Red
        Write-Host "  Please check the error messages above" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "  [ERROR] Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Step 4: Install pre-commit hooks
Write-Host ""
Write-Host "[4/5] Installing pre-commit hooks..." -ForegroundColor Yellow

# First, check if git is initialized
if (-not (Test-Path ..\.git)) {
    Write-Host "  [ERROR] Not in a git repository!" -ForegroundColor Red
    Write-Host "  Please run this script from the backend directory of a git repository" -ForegroundColor Red
    exit 1
}

try {
    pre-commit install
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Pre-commit hooks installed successfully" -ForegroundColor Green
    }
    else {
        Write-Host "  [ERROR] Failed to install pre-commit hooks" -ForegroundColor Red
        Write-Host "  Error code: $LASTEXITCODE" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "  [ERROR] Failed to install pre-commit hooks: $_" -ForegroundColor Red
    exit 1
}

# Step 5: Run pre-commit on all files (optional verification)
Write-Host ""
Write-Host "[5/5] Running pre-commit on all files (verification)..." -ForegroundColor Yellow
Write-Host "  Note: This may take several minutes on first run..." -ForegroundColor Gray
Write-Host ""

try {
    pre-commit run --all-files
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "  [OK] All pre-commit checks passed!" -ForegroundColor Green
    }
    else {
        Write-Host ""
        Write-Host "  [WARNING] Some checks failed or files were modified" -ForegroundColor Yellow
        Write-Host "  This is normal - files have been auto-fixed where possible" -ForegroundColor Yellow
        Write-Host "  Review the changes and commit them" -ForegroundColor Yellow
    }
}
catch {
    Write-Host ""
    Write-Host "  [WARNING] Pre-commit run had issues: $_" -ForegroundColor Yellow
}

# Success message
Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pre-commit hooks are now active and will run automatically on 'git commit'" -ForegroundColor White
Write-Host ""
Write-Host "Manual commands:" -ForegroundColor Yellow
Write-Host "  pre-commit run --all-files    Run hooks on all files" -ForegroundColor Gray
Write-Host "  pre-commit run                Run hooks on staged files" -ForegroundColor Gray
Write-Host "  git commit --no-verify        Skip hooks (not recommended)" -ForegroundColor Gray
Write-Host ""
Write-Host "Configuration files:" -ForegroundColor Yellow
Write-Host "  pyproject.toml                Black, Ruff, Mypy, Pytest settings" -ForegroundColor Gray
Write-Host "  .pre-commit-config.yaml       Pre-commit hook definitions" -ForegroundColor Gray
Write-Host ""
Write-Host "For detailed documentation, see PRE-COMMIT-GUIDE.md" -ForegroundColor Cyan
Write-Host ""
