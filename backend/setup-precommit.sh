#!/bin/bash
# ==============================================
# Pre-commit Setup Script (Bash)
# ==============================================
# This script sets up pre-commit hooks for the TIP backend
# Run this script from the backend directory

set -e  # Exit on error

echo "=============================================="
echo ""
echo "  TIP Backend - Pre-commit Hooks Setup"
echo ""
echo "=============================================="
echo ""

# Check if Python is installed
echo -e "\033[33m[1/5] Checking Python installation...\033[0m"
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo -e "\033[32m  ✓ Found: $PYTHON_VERSION\033[0m"
else
    echo -e "\033[31m  ✗ Python not found! Please install Python 3.11+\033[0m"
    exit 1
fi

# Install/upgrade pip
echo -e "\n\033[33m[2/5] Upgrading pip...\033[0m"
python -m pip install --upgrade pip
echo -e "\033[32m  ✓ pip upgraded\033[0m"

# Install requirements
echo -e "\n\033[33m[3/5] Installing Python dependencies...\033[0m"
pip install -r requirements.txt
echo -e "\033[32m  ✓ Dependencies installed\033[0m"

# Install pre-commit hooks
echo -e "\n\033[33m[4/5] Installing pre-commit hooks...\033[0m"
pre-commit install
echo -e "\033[32m  ✓ Pre-commit hooks installed\033[0m"

# Run pre-commit on all files (optional first check)
echo -e "\n\033[33m[5/5] Running pre-commit on all files (first-time check)...\033[0m"
echo -e "\033[90m  Note: This may take a few minutes on first run...\033[0m"
if pre-commit run --all-files; then
    echo -e "\n\033[32m  ✓ All pre-commit checks passed!\033[0m"
else
    echo -e "\n\033[33m  ⚠ Some checks failed. Files have been auto-fixed where possible.\033[0m"
    echo -e "\033[33m  Review the changes and commit them.\033[0m"
fi

echo -e "\n=============================================="
echo -e ""
echo -e "\033[32m  ✓ Setup Complete!\033[0m"
echo -e ""
echo -e "=============================================="
echo -e ""
echo -e "Pre-commit hooks are now active. They will run automatically on 'git commit'."
echo -e ""
echo -e "\033[33mManual commands:\033[0m"
echo -e "\033[90m  • Run on all files:     pre-commit run --all-files\033[0m"
echo -e "\033[90m  • Run on staged files:  pre-commit run\033[0m"
echo -e "\033[90m  • Skip hooks (not recommended): git commit --no-verify\033[0m"
echo -e ""
echo -e "\033[33mTool configurations are in:\033[0m"
echo -e "\033[90m  • pyproject.toml (Black, Ruff, Mypy, Pytest, Coverage)\033[0m"
echo -e "\033[90m  • .pre-commit-config.yaml (Hook definitions)\033[0m"
echo -e ""
