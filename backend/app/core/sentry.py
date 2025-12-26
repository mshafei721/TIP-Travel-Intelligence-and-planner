"""
Sentry Integration for TIP API

Provides error tracking, performance monitoring, and distributed tracing
for production environments.
"""

import logging
from typing import Any

from fastapi import FastAPI

logger = logging.getLogger(__name__)

# Sentry availability flag
SENTRY_AVAILABLE = False

try:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.httpx import HttpxIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.starlette import StarletteIntegration

    SENTRY_AVAILABLE = True
except ImportError:
    logger.info("Sentry SDK not installed. Error tracking disabled.")


def configure_sentry(
    dsn: str | None = None,
    environment: str = "development",
    release: str | None = None,
    traces_sample_rate: float = 0.1,
    profiles_sample_rate: float = 0.1,
    enable_tracing: bool = True,
) -> bool:
    """
    Initialize Sentry SDK for error tracking and performance monitoring.

    Args:
        dsn: Sentry DSN (Data Source Name). If None, uses SENTRY_DSN env var.
        environment: Current environment (development/staging/production)
        release: Application version/release identifier
        traces_sample_rate: Percentage of transactions to trace (0.0-1.0)
        profiles_sample_rate: Percentage of transactions to profile (0.0-1.0)
        enable_tracing: Enable performance monitoring

    Returns:
        True if Sentry was initialized successfully, False otherwise
    """
    if not SENTRY_AVAILABLE:
        logger.warning("Sentry SDK not available. Install with: pip install sentry-sdk")
        return False

    if not dsn:
        import os
        dsn = os.getenv("SENTRY_DSN")

    if not dsn:
        logger.info("Sentry DSN not configured. Error tracking disabled.")
        return False

    # Don't initialize in development unless explicitly requested
    if environment == "development" and not dsn:
        logger.info("Skipping Sentry in development environment")
        return False

    try:
        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            release=release,
            # Performance monitoring
            enable_tracing=enable_tracing,
            traces_sample_rate=traces_sample_rate,
            profiles_sample_rate=profiles_sample_rate,
            # Integrations
            integrations=[
                # FastAPI/Starlette integration
                StarletteIntegration(transaction_style="endpoint"),
                FastApiIntegration(transaction_style="endpoint"),
                # Celery integration for background tasks
                CeleryIntegration(),
                # HTTP client integration
                HttpxIntegration(),
                # Logging integration - capture logs as breadcrumbs
                LoggingIntegration(
                    level=logging.INFO,        # Capture INFO+ as breadcrumbs
                    event_level=logging.ERROR, # Capture ERROR+ as events
                ),
            ],
            # Data scrubbing
            send_default_pii=False,  # Don't send personally identifiable info
            # Additional options
            attach_stacktrace=True,
            # Before send hook for filtering
            before_send=before_send_filter,
            before_send_transaction=before_send_transaction_filter,
        )

        logger.info(
            "Sentry initialized",
            extra={
                "environment": environment,
                "traces_sample_rate": traces_sample_rate,
            }
        )
        return True

    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")
        return False


def before_send_filter(event: dict, hint: dict) -> dict | None:
    """
    Filter or modify events before sending to Sentry.

    Use this to:
    - Remove sensitive data
    - Filter out certain errors
    - Add additional context
    """
    # Filter out expected errors that shouldn't be tracked
    if "exc_info" in hint:
        exc_type, exc_value, _ = hint["exc_info"]

        # Skip 404 and 401 errors (expected behavior)
        from fastapi import HTTPException
        if isinstance(exc_value, HTTPException):
            if exc_value.status_code in (404, 401):
                return None

        # Skip validation errors (user input issues)
        from fastapi.exceptions import RequestValidationError
        if isinstance(exc_value, RequestValidationError):
            return None

    # Scrub sensitive data from request
    if "request" in event:
        request = event["request"]
        # Remove authorization header
        if "headers" in request:
            headers = request["headers"]
            if isinstance(headers, dict):
                headers.pop("authorization", None)
                headers.pop("cookie", None)
                headers.pop("x-api-key", None)

    return event


def before_send_transaction_filter(event: dict, hint: dict) -> dict | None:
    """
    Filter transactions before sending to Sentry.

    Use this to skip health check transactions and other noisy endpoints.
    """
    # Skip health check endpoints
    transaction = event.get("transaction", "")
    if any(path in transaction for path in ["/health", "/api/health", "/_health"]):
        return None

    # Skip static file requests
    if transaction.startswith("/static/"):
        return None

    return event


def set_user_context(user_id: str, email: str | None = None) -> None:
    """Set the current user context for error tracking."""
    if not SENTRY_AVAILABLE:
        return

    sentry_sdk.set_user({
        "id": user_id,
        "email": email,
    })


def clear_user_context() -> None:
    """Clear the current user context."""
    if not SENTRY_AVAILABLE:
        return

    sentry_sdk.set_user(None)


def set_tag(key: str, value: str) -> None:
    """Set a tag on the current scope."""
    if not SENTRY_AVAILABLE:
        return

    sentry_sdk.set_tag(key, value)


def set_context(name: str, data: dict[str, Any]) -> None:
    """Set additional context data."""
    if not SENTRY_AVAILABLE:
        return

    sentry_sdk.set_context(name, data)


def capture_message(message: str, level: str = "info") -> str | None:
    """
    Capture a message as a Sentry event.

    Args:
        message: Message to capture
        level: Level (info/warning/error/fatal)

    Returns:
        Event ID if captured, None otherwise
    """
    if not SENTRY_AVAILABLE:
        return None

    return sentry_sdk.capture_message(message, level=level)


def capture_exception(exception: Exception | None = None) -> str | None:
    """
    Capture an exception as a Sentry event.

    Args:
        exception: Exception to capture (uses current if None)

    Returns:
        Event ID if captured, None otherwise
    """
    if not SENTRY_AVAILABLE:
        return None

    return sentry_sdk.capture_exception(exception)


def start_transaction(
    name: str,
    op: str = "function",
    description: str | None = None,
):
    """
    Start a performance transaction.

    Usage:
        with start_transaction("my_operation", op="task"):
            # Your code here
            pass
    """
    if not SENTRY_AVAILABLE:
        from contextlib import nullcontext
        return nullcontext()

    return sentry_sdk.start_transaction(
        name=name,
        op=op,
        description=description,
    )


def add_breadcrumb(
    message: str,
    category: str = "info",
    level: str = "info",
    data: dict | None = None,
) -> None:
    """Add a breadcrumb for debugging context."""
    if not SENTRY_AVAILABLE:
        return

    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data or {},
    )


class SentryMiddleware:
    """
    Middleware to add request context to Sentry.
    """

    async def __call__(self, request, call_next):
        # Set request context
        if SENTRY_AVAILABLE:
            with sentry_sdk.configure_scope() as scope:
                # Add request info
                scope.set_tag("request_id", getattr(request.state, "request_id", "unknown"))
                scope.set_tag("path", str(request.url.path))
                scope.set_tag("method", request.method)

        return await call_next(request)


def setup_sentry_for_celery() -> None:
    """
    Configure Sentry specifically for Celery workers.

    Call this in your Celery worker configuration.
    """
    if not SENTRY_AVAILABLE:
        return

    # The CeleryIntegration is already added in configure_sentry()
    # This function can be used for additional Celery-specific setup
    logger.info("Sentry configured for Celery workers")
