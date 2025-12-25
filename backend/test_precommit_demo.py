"""Demo file to test pre-commit hooks"""

# All issues have been auto-fixed by pre-commit hooks!
# This demonstrates:
# 1. Ruff removed unused imports
# 2. Ruff removed f-string prefix when no placeholders
# 3. Black auto-formatted spacing and style
# 4. Type annotations added for Mypy


def well_formatted_function(x: int, y: int, z: int) -> int:
    """Add three integers together."""
    return x + y + z


def test_function() -> None:
    """Print a greeting message."""
    print("Hello World")


def with_type_hints(name: str, age: int) -> str:
    """Format a person's information."""
    return f"{name} is {age} years old"
