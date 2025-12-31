"""
Standardized Error Handling for TIP API

This module provides a consistent error response format across all API endpoints.
All errors return the same structure for predictable frontend handling.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ErrorCode(str, Enum):
    """
    Standardized error codes for API responses.

    Grouped by category:
    - VALIDATION_*: Input validation errors (400)
    - AUTH_*: Authentication/authorization errors (401/403)
    - NOT_FOUND_*: Resource not found errors (404)
    - CONFLICT_*: State conflict errors (409)
    - RATE_LIMIT_*: Rate limiting errors (429)
    - INTERNAL_*: Server errors (500)
    - EXTERNAL_*: External service errors (502/503)
    """

    # Validation Errors (400)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    VALIDATION_MISSING_FIELD = "VALIDATION_MISSING_FIELD"
    VALIDATION_INVALID_FORMAT = "VALIDATION_INVALID_FORMAT"
    VALIDATION_OUT_OF_RANGE = "VALIDATION_OUT_OF_RANGE"

    # Authentication Errors (401)
    AUTH_TOKEN_MISSING = "AUTH_TOKEN_MISSING"
    AUTH_TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED"
    AUTH_TOKEN_INVALID = "AUTH_TOKEN_INVALID"

    # Authorization Errors (403)
    AUTH_FORBIDDEN = "AUTH_FORBIDDEN"
    AUTH_INSUFFICIENT_PERMISSIONS = "AUTH_INSUFFICIENT_PERMISSIONS"
    AUTH_RESOURCE_ACCESS_DENIED = "AUTH_RESOURCE_ACCESS_DENIED"

    # Not Found Errors (404)
    NOT_FOUND_TRIP = "NOT_FOUND_TRIP"
    NOT_FOUND_REPORT = "NOT_FOUND_REPORT"
    NOT_FOUND_TEMPLATE = "NOT_FOUND_TEMPLATE"
    NOT_FOUND_USER = "NOT_FOUND_USER"
    NOT_FOUND_DRAFT = "NOT_FOUND_DRAFT"
    NOT_FOUND_RESOURCE = "NOT_FOUND_RESOURCE"

    # Conflict Errors (409)
    CONFLICT_TRIP_STATUS = "CONFLICT_TRIP_STATUS"
    CONFLICT_DUPLICATE_REQUEST = "CONFLICT_DUPLICATE_REQUEST"
    CONFLICT_RESOURCE_STATE = "CONFLICT_RESOURCE_STATE"

    # Rate Limit Errors (429)
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    RATE_LIMIT_API_QUOTA = "RATE_LIMIT_API_QUOTA"

    # Internal Errors (500)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    INTERNAL_DATABASE_ERROR = "INTERNAL_DATABASE_ERROR"
    INTERNAL_AGENT_ERROR = "INTERNAL_AGENT_ERROR"
    INTERNAL_PDF_GENERATION_ERROR = "INTERNAL_PDF_GENERATION_ERROR"

    # External Service Errors (502/503)
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    EXTERNAL_API_TIMEOUT = "EXTERNAL_API_TIMEOUT"
    EXTERNAL_API_UNAVAILABLE = "EXTERNAL_API_UNAVAILABLE"


class ErrorDetail(BaseModel):
    """Details about a specific field error."""

    field: str = Field(..., description="Field name that has the error")
    message: str = Field(..., description="Human-readable error message")
    code: str | None = Field(None, description="Specific error code for this field")


class ErrorResponse(BaseModel):
    """
    Standardized error response format for all API errors.

    This format is consistent across all endpoints for predictable
    error handling on the frontend.

    Example:
        {
            "error": {
                "code": "NOT_FOUND_TRIP",
                "message": "Trip not found",
                "details": null,
                "timestamp": "2025-12-26T10:00:00Z",
                "request_id": "abc-123",
                "path": "/api/trips/invalid-id"
            }
        }
    """

    code: ErrorCode = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: list[ErrorDetail] | None = Field(
        None, description="Additional error details (field-level errors)"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="When the error occurred"
    )
    request_id: str | None = Field(None, description="Request ID for support/debugging")
    path: str | None = Field(None, description="API path that generated the error")

    class Config:
        json_schema_extra = {
            "example": {
                "code": "NOT_FOUND_TRIP",
                "message": "Trip not found",
                "details": None,
                "timestamp": "2025-12-26T10:00:00Z",
                "request_id": "req-abc123",
                "path": "/api/trips/invalid-uuid",
            }
        }


class ErrorWrapper(BaseModel):
    """Wrapper for error responses to maintain consistent structure."""

    error: ErrorResponse


# Application-specific exceptions
class TIPException(Exception):
    """Base exception for all TIP application errors."""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        status_code: int = 500,
        details: list[ErrorDetail] | None = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class ValidationError(TIPException):
    """Raised when input validation fails."""

    def __init__(self, message: str = "Validation error", details: list[ErrorDetail] | None = None):
        super().__init__(
            code=ErrorCode.VALIDATION_ERROR, message=message, status_code=400, details=details
        )


class AuthenticationError(TIPException):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication required",
        code: ErrorCode = ErrorCode.AUTH_TOKEN_INVALID,
    ):
        super().__init__(code=code, message=message, status_code=401)


class AuthorizationError(TIPException):
    """Raised when authorization fails."""

    def __init__(self, message: str = "Access denied", code: ErrorCode = ErrorCode.AUTH_FORBIDDEN):
        super().__init__(code=code, message=message, status_code=403)


class NotFoundError(TIPException):
    """Raised when a resource is not found."""

    def __init__(
        self, message: str = "Resource not found", code: ErrorCode = ErrorCode.NOT_FOUND_RESOURCE
    ):
        super().__init__(code=code, message=message, status_code=404)


class ConflictError(TIPException):
    """Raised when there's a resource state conflict."""

    def __init__(
        self,
        message: str = "Resource state conflict",
        code: ErrorCode = ErrorCode.CONFLICT_RESOURCE_STATE,
    ):
        super().__init__(code=code, message=message, status_code=409)


class RateLimitError(TIPException):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: int | None = None):
        super().__init__(code=ErrorCode.RATE_LIMIT_EXCEEDED, message=message, status_code=429)
        self.retry_after = retry_after


class InternalError(TIPException):
    """Raised for internal server errors."""

    def __init__(
        self, message: str = "Internal server error", code: ErrorCode = ErrorCode.INTERNAL_ERROR
    ):
        super().__init__(code=code, message=message, status_code=500)


class ExternalServiceError(TIPException):
    """Raised when an external service fails."""

    def __init__(
        self,
        message: str = "External service error",
        code: ErrorCode = ErrorCode.EXTERNAL_SERVICE_ERROR,
        service_name: str | None = None,
    ):
        super().__init__(code=code, message=message, status_code=502)
        self.service_name = service_name


# Error message templates
ERROR_MESSAGES = {
    ErrorCode.VALIDATION_ERROR: "Request validation failed",
    ErrorCode.VALIDATION_MISSING_FIELD: "Required field is missing: {field}",
    ErrorCode.VALIDATION_INVALID_FORMAT: "Invalid format for field: {field}",
    ErrorCode.VALIDATION_OUT_OF_RANGE: "Value out of valid range for field: {field}",
    ErrorCode.AUTH_TOKEN_MISSING: "Authentication token is required",
    ErrorCode.AUTH_TOKEN_EXPIRED: "Authentication token has expired",
    ErrorCode.AUTH_TOKEN_INVALID: "Invalid authentication token",
    ErrorCode.AUTH_FORBIDDEN: "Access to this resource is forbidden",
    ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS: "Insufficient permissions for this action",
    ErrorCode.AUTH_RESOURCE_ACCESS_DENIED: "You do not have access to this resource",
    ErrorCode.NOT_FOUND_TRIP: "Trip not found",
    ErrorCode.NOT_FOUND_REPORT: "Report not found for this trip. Generate the report first.",
    ErrorCode.NOT_FOUND_TEMPLATE: "Template not found",
    ErrorCode.NOT_FOUND_USER: "User not found",
    ErrorCode.NOT_FOUND_DRAFT: "Draft not found",
    ErrorCode.NOT_FOUND_RESOURCE: "Requested resource not found",
    ErrorCode.CONFLICT_TRIP_STATUS: "Cannot perform this action on a trip with status: {status}",
    ErrorCode.CONFLICT_DUPLICATE_REQUEST: "A duplicate request was detected",
    ErrorCode.CONFLICT_RESOURCE_STATE: "Resource is in an invalid state for this operation",
    ErrorCode.RATE_LIMIT_EXCEEDED: "Too many requests. Please try again later.",
    ErrorCode.RATE_LIMIT_API_QUOTA: "API quota exceeded for this period",
    ErrorCode.INTERNAL_ERROR: "An internal error occurred. Please try again later.",
    ErrorCode.INTERNAL_DATABASE_ERROR: "Database operation failed",
    ErrorCode.INTERNAL_AGENT_ERROR: "AI agent execution failed",
    ErrorCode.INTERNAL_PDF_GENERATION_ERROR: "PDF generation failed",
    ErrorCode.EXTERNAL_SERVICE_ERROR: "External service error: {service}",
    ErrorCode.EXTERNAL_API_TIMEOUT: "External API request timed out",
    ErrorCode.EXTERNAL_API_UNAVAILABLE: "External API is currently unavailable",
}


def get_error_message(code: ErrorCode, **kwargs: Any) -> str:
    """Get formatted error message for an error code."""
    template = ERROR_MESSAGES.get(code, "An error occurred")
    try:
        return template.format(**kwargs)
    except KeyError:
        return template


# Secure error handling utilities
import logging

_logger = logging.getLogger(__name__)


def raise_internal_error(
    operation: str,
    exception: Exception,
    user_message: str | None = None,
    error_code: ErrorCode = ErrorCode.INTERNAL_ERROR,
) -> None:
    """
    Securely handle an internal error.

    Logs the full error details server-side for debugging,
    but raises an exception with a generic user-facing message
    that doesn't expose internal details.

    Args:
        operation: Description of what operation failed (for logging)
        exception: The actual exception that occurred
        user_message: Optional custom user-facing message
        error_code: The error code to use

    Raises:
        InternalError: Always raises with secure message

    Example:
        try:
            result = database.query(...)
        except Exception as e:
            raise_internal_error("database query", e, "Failed to fetch data")
    """
    # Log full details server-side
    _logger.error(
        f"Internal error during {operation}: {type(exception).__name__}: {str(exception)}",
        exc_info=True,
        extra={
            "operation": operation,
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
        },
    )

    # Raise with secure message
    message = user_message or ERROR_MESSAGES.get(error_code, "An internal error occurred")
    raise InternalError(message=message, code=error_code)


def raise_database_error(operation: str, exception: Exception) -> None:
    """
    Securely handle a database error.

    Args:
        operation: What database operation failed
        exception: The actual exception

    Raises:
        InternalError with DATABASE_ERROR code
    """
    raise_internal_error(
        operation=f"database {operation}",
        exception=exception,
        error_code=ErrorCode.INTERNAL_DATABASE_ERROR,
    )


def raise_external_service_error(
    service_name: str,
    exception: Exception,
    error_code: ErrorCode = ErrorCode.EXTERNAL_SERVICE_ERROR,
) -> None:
    """
    Securely handle an external service error.

    Args:
        service_name: Name of the external service
        exception: The actual exception
        error_code: The error code to use

    Raises:
        ExternalServiceError with secure message
    """
    _logger.error(
        f"External service error ({service_name}): {type(exception).__name__}: {str(exception)}",
        exc_info=True,
        extra={
            "service_name": service_name,
            "exception_type": type(exception).__name__,
        },
    )

    message = get_error_message(error_code, service=service_name)
    raise ExternalServiceError(message=message, code=error_code, service_name=service_name)


def raise_not_found_error(
    resource_type: str,
    resource_id: str | None = None,
    error_code: ErrorCode = ErrorCode.NOT_FOUND_RESOURCE,
) -> None:
    """
    Raise a not found error with a safe message.

    Args:
        resource_type: Type of resource (trip, template, etc.)
        resource_id: Optional ID of the resource
        error_code: The error code to use

    Raises:
        NotFoundError with secure message
    """
    message = get_error_message(error_code)
    _logger.warning(
        f"Resource not found: {resource_type}",
        extra={
            "resource_type": resource_type,
            "resource_id": resource_id,
        },
    )
    raise NotFoundError(message=message, code=error_code)


def log_and_raise_http_error(
    operation: str,
    exception: Exception,
    user_message: str,
) -> None:
    """
    Log error details and raise HTTPException with safe message.

    This is a transitional helper for code still using HTTPException.
    New code should use raise_internal_error instead.

    Args:
        operation: What operation failed
        exception: The actual exception
        user_message: Safe message to show users

    Raises:
        HTTPException with safe message
    """
    from fastapi import HTTPException, status

    _logger.error(
        f"Error during {operation}: {type(exception).__name__}: {str(exception)}",
        exc_info=True,
    )

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=user_message,
    )
