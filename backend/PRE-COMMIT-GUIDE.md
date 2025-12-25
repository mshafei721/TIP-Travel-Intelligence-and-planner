# Pre-commit Hooks Guide

This guide explains the linting, testing, and pre-commit hooks setup for the TIP backend.

## Overview

Pre-commit hooks automatically run quality checks before each commit, ensuring code quality and consistency across the project.

## Tools & Configuration

### Installed Tools

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **Ruff** | Fast Python linter | `pyproject.toml` → `[tool.ruff]` |
| **Black** | Code formatter | `pyproject.toml` → `[tool.black]` |
| **Mypy** | Static type checker | `pyproject.toml` → `[tool.mypy]` |
| **Pytest** | Testing framework | `pyproject.toml` → `[tool.pytest.ini_options]` |
| **Coverage** | Test coverage | `pyproject.toml` → `[tool.coverage]` |
| **pre-commit** | Hook manager | `.pre-commit-config.yaml` |

### Configuration Files

- **`pyproject.toml`** - Central configuration for all Python tools
- **`.pre-commit-config.yaml`** - Pre-commit hooks configuration
- **`pytest.ini`** - Legacy pytest configuration (use pyproject.toml instead)

## Quick Start

### 1. Installation (First Time Setup)

**Windows (PowerShell):**
```powershell
cd backend
.\setup-precommit.ps1
```

**Linux/Mac:**
```bash
cd backend
chmod +x setup-precommit.sh
./setup-precommit.sh
```

This script will:
1. Check Python installation
2. Upgrade pip
3. Install all dependencies from `requirements.txt`
4. Install pre-commit hooks
5. Run hooks on all files (first-time check)

### 2. Manual Installation

If you prefer manual setup:

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# (Optional) Run on all files
pre-commit run --all-files
```

## Usage

### Automatic (Recommended)

Once installed, hooks run automatically on `git commit`:

```bash
git add .
git commit -m "Your commit message"
# ↓ Pre-commit hooks run automatically
# ↓ Commit succeeds only if all checks pass
```

### Manual Commands

Run hooks manually without committing:

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run

# Run specific hook
pre-commit run ruff
pre-commit run black
pre-commit run mypy
pre-commit run pytest
```

### Run Individual Tools

You can also run tools directly:

```bash
# Ruff (linting)
ruff check .
ruff check --fix .  # Auto-fix issues

# Black (formatting)
black .
black --check .  # Check without modifying

# Mypy (type checking)
mypy app/

# Pytest (testing)
pytest
pytest -v  # Verbose
pytest --cov=app --cov-report=html  # With coverage report
pytest -m unit  # Run only unit tests
pytest -m "not slow"  # Skip slow tests
```

## What Gets Checked

### 1. General File Checks
- ✓ Trailing whitespace removed
- ✓ Files end with newline
- ✓ YAML/JSON/TOML syntax validated
- ✓ No large files (>1MB)
- ✓ No merge conflicts
- ✓ No private keys detected
- ✓ Consistent line endings (LF)

### 2. Ruff Linting
- ✓ PEP 8 style errors (E, W)
- ✓ Pyflakes (F) - unused imports, variables
- ✓ Import sorting (I)
- ✓ PEP 8 naming (N)
- ✓ Modern Python syntax (UP)
- ✓ Common bugs (B)
- ✓ Comprehension improvements (C4)
- ✓ Datetime timezone issues (DTZ)
- ✓ Debugger statements (T10)
- ✓ Error message best practices (EM)
- ✓ Logging format (G)
- ✓ Pytest style (PT)
- ✓ Return statement simplifications (RET)
- ✓ Code simplifications (SIM)
- ✓ Unused arguments (ARG)
- ✓ Use pathlib (PTH)
- ✓ Pylint rules (PL)
- ✓ Exception handling (TRY)

Auto-fixes simple issues automatically.

### 3. Black Formatting
- ✓ Consistent code style
- ✓ Line length: 100 characters
- ✓ Automatic formatting (no debates!)

### 4. Mypy Type Checking
- ✓ Type hints validated
- ✓ Function signatures checked
- ✓ No untyped definitions
- ✓ Redundant casts detected
- ✓ Strict equality checks

Note: Tests are excluded from strict type checking.

### 5. Pytest Testing
- ✓ Full test suite runs
- ✓ 80% minimum coverage required
- ✓ Coverage report generated

## Skipping Hooks (Not Recommended)

If absolutely necessary, skip hooks with:

```bash
git commit --no-verify -m "Emergency fix"
```

⚠️ **Warning:** Use sparingly. Skipping hooks bypasses quality checks.

## Troubleshooting

### Issue: Hooks fail on first run

**Solution:** This is normal. Hooks may auto-fix files. Review changes and commit again:

```bash
git add .
git commit -m "Apply pre-commit fixes"
```

### Issue: Mypy errors about missing type stubs

**Solution:** Install type stubs for the library:

```bash
pip install types-<library-name>
```

Or add to `pyproject.toml` → `[[tool.mypy.overrides]]` to ignore:

```toml
[[tool.mypy.overrides]]
module = ["library_name.*"]
ignore_missing_imports = true
```

### Issue: Tests fail on commit

**Solution:** Fix the failing tests or mark them as slow/skip:

```python
import pytest

@pytest.mark.slow
def test_expensive_operation():
    pass
```

Then run without slow tests:
```bash
pytest -m "not slow"
```

### Issue: Pre-commit hooks are slow

**Solution:** For faster commits, you can:

1. **Run only on changed files** (default behavior)
2. **Skip pytest temporarily** (edit `.pre-commit-config.yaml`, remove pytest hook)
3. **Run tests in parallel** (add `-n auto` to pytest args if you install `pytest-xdist`)

### Issue: Black and Ruff conflict

**Solution:** Configurations are aligned. If issues persist:

```bash
# Run black first, then ruff
black .
ruff check --fix .
```

## Updating Hooks

Update to latest versions:

```bash
pre-commit autoupdate
```

## CI/CD Integration

These same checks should run in your CI/CD pipeline:

```yaml
# .github/workflows/ci.yml
- name: Run pre-commit
  run: pre-commit run --all-files
```

## Best Practices

1. **Commit often** - Small commits are easier to review
2. **Fix issues immediately** - Don't bypass hooks habitually
3. **Review auto-fixes** - Black/Ruff changes should be reviewed
4. **Keep coverage high** - Maintain 80%+ test coverage
5. **Add type hints** - Mypy catches type errors early
6. **Run tests before push** - Ensure tests pass locally

## Coverage Reports

After running pytest, view the HTML coverage report:

```bash
# Generate report
pytest --cov=app --cov-report=html

# Open report (Windows)
start htmlcov/index.html

# Open report (Linux/Mac)
open htmlcov/index.html
```

## Configuration Customization

### Change Line Length

Edit `pyproject.toml`:

```toml
[tool.black]
line-length = 88  # Change from 100

[tool.ruff]
line-length = 88  # Keep in sync with Black
```

### Change Coverage Threshold

Edit `pyproject.toml`:

```toml
[tool.pytest.ini_options]
addopts = [
    "--cov-fail-under=90",  # Change from 80
]
```

### Disable Specific Ruff Rules

Edit `pyproject.toml`:

```toml
[tool.ruff.lint]
ignore = [
    "E501",  # Add more rules here
]
```

## Resources

- [Pre-commit Documentation](https://pre-commit.com/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Black Documentation](https://black.readthedocs.io/)
- [Mypy Documentation](https://mypy.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)

## Support

For issues or questions:
1. Check this guide
2. Review tool documentation
3. Ask the team
4. File an issue in the project repository
