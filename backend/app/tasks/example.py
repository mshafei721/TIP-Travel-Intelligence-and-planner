"""
Example Celery tasks for testing and development

These tasks demonstrate:
- Basic task creation with @shared_task decorator
- Task parameters and return values
- Async execution
"""

from celery import shared_task

from app.core.celery_app import BaseTipTask


@shared_task(bind=True, base=BaseTipTask, name="app.tasks.example.add")
def add(self, x: int, y: int) -> int:
    """
    Example task: Add two numbers

    Args:
        x: First number
        y: Second number

    Returns:
        Sum of x and y
    """
    print(f"Adding {x} + {y}")
    return x + y


@shared_task(bind=True, base=BaseTipTask, name="app.tasks.example.multiply")
def multiply(self, x: int, y: int) -> int:
    """
    Example task: Multiply two numbers

    Args:
        x: First number
        y: Second number

    Returns:
        Product of x and y
    """
    print(f"Multiplying {x} * {y}")
    return x * y
