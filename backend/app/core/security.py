"""
Security Middleware and Utilities for TIP API

Implements security best practices:
- Rate limiting
- Security headers
- Request validation
- Production environment checks
"""

import logging
import time
from collections import defaultdict
from datetime import datetime, timezone
from functools import wraps
from typing import Callable
from uuid import UUID

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.errors import ErrorCode, RateLimitError

logger = logging.getLogger(__name__)


# =============================================================================
# Security Headers Middleware
# =============================================================================

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    "Cache-Control": "no-store, no-cache, must-revalidate",
}

# HSTS should only be enabled in production with HTTPS
PRODUCTION_HEADERS = {
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Add base security headers
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value

        # Add HSTS only in production
        if settings.ENVIRONMENT == "production":
            for header, value in PRODUCTION_HEADERS.items():
                response.headers[header] = value

        return response


# =============================================================================
# Rate Limiting
# =============================================================================

class RateLimiter:
    """
    Simple in-memory rate limiter using sliding window.

    For production, consider Redis-based rate limiting for distributed systems.
    """

    def __init__(
        self,
        requests_per_minute: int = 60,
        burst_multiplier: float = 1.5,
    ):
        self.requests_per_minute = requests_per_minute
        self.burst_limit = int(requests_per_minute * burst_multiplier)
        self.window_size = 60  # seconds
        self.requests: dict[str, list[float]] = defaultdict(list)

    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier."""
        # Try to get user_id from request state (set by auth)
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"

        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"

        return f"ip:{ip}"

    def _clean_old_requests(self, client_id: str, current_time: float) -> None:
        """Remove requests outside the current window."""
        cutoff = current_time - self.window_size
        self.requests[client_id] = [
            t for t in self.requests[client_id] if t > cutoff
        ]

    def is_rate_limited(self, request: Request) -> tuple[bool, dict]:
        """
        Check if request should be rate limited.

        Returns:
            tuple: (is_limited, headers_dict)
        """
        client_id = self._get_client_id(request)
        current_time = time.time()

        # Clean old requests
        self._clean_old_requests(client_id, current_time)

        # Count requests in current window
        request_count = len(self.requests[client_id])

        # Calculate rate limit headers
        remaining = max(0, self.requests_per_minute - request_count)
        reset_time = int(current_time) + self.window_size

        headers = {
            "X-RateLimit-Limit": str(self.requests_per_minute),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_time),
        }

        # Check if rate limited
        if request_count >= self.burst_limit:
            retry_after = self.window_size - int(current_time - min(self.requests[client_id]))
            headers["Retry-After"] = str(max(1, retry_after))
            return True, headers

        # Record this request
        self.requests[client_id].append(current_time)

        return False, headers


# Global rate limiter instance
_rate_limiter: RateLimiter | None = None


def get_rate_limiter() -> RateLimiter:
    """Get or create the global rate limiter."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter(
            requests_per_minute=settings.RATE_LIMIT_PER_MINUTE
        )
    return _rate_limiter


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""

    # Endpoints exempt from rate limiting
    EXEMPT_PATHS = {
        "/api/health",
        "/api/docs",
        "/api/redoc",
        "/api/openapi.json",
        "/",
    }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for exempt paths
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        rate_limiter = get_rate_limiter()
        is_limited, headers = rate_limiter.is_rate_limited(request)

        if is_limited:
            logger.warning(
                "Rate limit exceeded",
                extra={
                    "path": str(request.url.path),
                    "client": headers.get("X-RateLimit-Limit"),
                }
            )

            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": ErrorCode.RATE_LIMIT_EXCEEDED.value,
                        "message": "Too many requests. Please try again later.",
                        "details": None,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "path": str(request.url.path),
                    }
                },
                headers=headers,
            )

        # Process request and add rate limit headers
        response = await call_next(request)
        for header, value in headers.items():
            response.headers[header] = value

        return response


# =============================================================================
# Production Environment Validation
# =============================================================================

class SecurityValidationError(Exception):
    """Raised when security validation fails."""

    pass


def validate_production_security() -> list[str]:
    """
    Validate security configuration for production environment.

    Returns:
        list: List of security warnings/errors
    """
    issues = []

    # Check environment
    if settings.ENVIRONMENT not in ("development", "staging", "production"):
        issues.append(f"Unknown environment: {settings.ENVIRONMENT}")

    # Production-specific checks
    if settings.ENVIRONMENT == "production":
        # Check for default/weak secrets
        if settings.SECRET_KEY == "test-secret-key-change-in-production":
            issues.append("CRITICAL: Using default SECRET_KEY in production!")

        if len(settings.SECRET_KEY) < 32:
            issues.append("WARNING: SECRET_KEY should be at least 32 characters")

        # Check Supabase configuration
        if not settings.SUPABASE_URL:
            issues.append("CRITICAL: SUPABASE_URL is not configured")

        if not settings.SUPABASE_JWT_SECRET:
            issues.append("CRITICAL: SUPABASE_JWT_SECRET is not configured")

        if not settings.SUPABASE_SERVICE_ROLE_KEY:
            issues.append("CRITICAL: SUPABASE_SERVICE_ROLE_KEY is not configured")

        # Check for development URLs in production
        if "localhost" in settings.FRONTEND_URL:
            issues.append("WARNING: FRONTEND_URL contains localhost in production")

        if "localhost" in settings.BACKEND_URL:
            issues.append("WARNING: BACKEND_URL contains localhost in production")

        # Check CORS origins
        for origin in settings.cors_origins_list:
            if "localhost" in origin or "127.0.0.1" in origin:
                issues.append(f"WARNING: CORS allows localhost origin: {origin}")

        # Check Redis URL (should not be localhost in production)
        if "localhost" in settings.REDIS_URL or "127.0.0.1" in settings.REDIS_URL:
            issues.append("WARNING: REDIS_URL contains localhost in production")

        if "localhost" in settings.CELERY_BROKER_URL or "127.0.0.1" in settings.CELERY_BROKER_URL:
            issues.append("WARNING: CELERY_BROKER_URL contains localhost in production")

        # Check Sentry configuration
        if not settings.SENTRY_DSN:
            issues.append("INFO: SENTRY_DSN not configured - errors won't be tracked")

    return issues


def check_security_on_startup(app: FastAPI, fail_on_critical: bool = True) -> None:
    """
    Run security checks on application startup.

    Args:
        app: FastAPI application
        fail_on_critical: If True, raise exception on critical issues in production
    """
    issues = validate_production_security()

    if not issues:
        logger.info("Security validation passed")
        return

    # Log all issues
    critical_found = False
    for issue in issues:
        if issue.startswith("CRITICAL"):
            logger.critical(issue)
            critical_found = True
        elif issue.startswith("WARNING"):
            logger.warning(issue)
        else:
            logger.info(issue)

    # Fail on critical issues in production
    if critical_found and fail_on_critical and settings.ENVIRONMENT == "production":
        raise SecurityValidationError(
            "Critical security issues found. Cannot start in production mode."
        )


# =============================================================================
# UUID Validation
# =============================================================================

def validate_uuid(value: str) -> UUID | None:
    """
    Validate and parse UUID string.

    Returns:
        UUID object if valid, None if invalid
    """
    try:
        return UUID(value)
    except (ValueError, AttributeError):
        return None


def is_valid_uuid(value: str) -> bool:
    """Check if string is a valid UUID."""
    return validate_uuid(value) is not None


# =============================================================================
# Input Sanitization
# =============================================================================

def sanitize_log_input(value: str, max_length: int = 200) -> str:
    """
    Sanitize input for safe logging.

    - Truncates long strings
    - Removes newlines and control characters
    - Escapes special characters
    """
    if not isinstance(value, str):
        value = str(value)

    # Truncate
    if len(value) > max_length:
        value = value[:max_length] + "..."

    # Remove control characters
    value = "".join(char for char in value if ord(char) >= 32 or char in "\t")

    # Replace newlines
    value = value.replace("\n", "\\n").replace("\r", "\\r")

    return value


# =============================================================================
# Secure Error Messages
# =============================================================================

def get_safe_error_message(exception: Exception, include_details: bool = False) -> str:
    """
    Get a safe error message that doesn't leak sensitive information.

    Args:
        exception: The exception to get message from
        include_details: If True, include exception details (for development only)

    Returns:
        Safe error message string
    """
    # Generic messages for common exceptions
    generic_messages = {
        "JWTError": "Token validation failed",
        "ExpiredSignatureError": "Token has expired",
        "JWTClaimsError": "Invalid token claims",
        "DecodeError": "Invalid token format",
        "ValidationError": "Request validation failed",
        "DatabaseError": "Database operation failed",
        "ConnectionError": "Service connection failed",
        "TimeoutError": "Request timed out",
    }

    exception_type = type(exception).__name__

    # In development, include details
    if include_details and settings.ENVIRONMENT == "development":
        return f"{exception_type}: {str(exception)}"

    # In production, use generic messages
    return generic_messages.get(exception_type, "An error occurred")


# =============================================================================
# Security Middleware Registration
# =============================================================================

def register_security_middleware(app: FastAPI) -> None:
    """Register all security middleware with the FastAPI app."""
    # Add security headers (must be first to ensure headers on all responses)
    app.add_middleware(SecurityHeadersMiddleware)

    # Add rate limiting
    app.add_middleware(RateLimitMiddleware)

    logger.info(
        "Security middleware registered",
        extra={
            "rate_limit": settings.RATE_LIMIT_PER_MINUTE,
            "environment": settings.ENVIRONMENT,
        }
    )
