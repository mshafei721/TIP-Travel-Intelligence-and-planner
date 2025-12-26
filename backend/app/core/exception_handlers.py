"""
Exception Handlers for TIP API

Centralized exception handling that converts all exceptions
to standardized ErrorResponse format.
"""

import logging
import traceback
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.errors import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    ErrorCode,
    ErrorDetail,
    ErrorResponse,
    ErrorWrapper,
    ExternalServiceError,
    InternalError,
    NotFoundError,
    RateLimitError,
    TIPException,
    ValidationError,
)

logger = logging.getLogger(__name__)


def get_request_id(request: Request) -> str:
    """Get or generate a request ID."""
    # Try to get from header (if set by reverse proxy)
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        # Generate a new one
        request_id = f"req-{uuid4().hex[:12]}"
    return request_id


def create_error_response(
    code: ErrorCode,
    message: str,
    status_code: int,
    request: Request,
    details: list[ErrorDetail] | None = None,
) -> JSONResponse:
    """Create a standardized error response."""
    request_id = get_request_id(request)

    error_response = ErrorWrapper(
        error=ErrorResponse(
            code=code,
            message=message,
            details=details,
            request_id=request_id,
            path=str(request.url.path),
        )
    )

    return JSONResponse(
        status_code=status_code,
        content=error_response.model_dump(mode="json"),
        headers={"X-Request-ID": request_id},
    )


async def tip_exception_handler(request: Request, exc: TIPException) -> JSONResponse:
    """Handle TIP application exceptions."""
    # Log the error
    logger.error(
        "TIP Exception",
        extra={
            "error_code": exc.code.value,
            "message": exc.message,
            "status_code": exc.status_code,
            "path": str(request.url.path),
            "method": request.method,
        }
    )

    return create_error_response(
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        request=request,
        details=exc.details,
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic/FastAPI validation errors."""
    details = []
    for error in exc.errors():
        field_path = ".".join(str(loc) for loc in error["loc"])
        details.append(
            ErrorDetail(
                field=field_path,
                message=error["msg"],
                code=error["type"],
            )
        )

    # Log validation errors
    logger.warning(
        "Validation error",
        extra={
            "path": str(request.url.path),
            "method": request.method,
            "errors": [d.model_dump() for d in details],
        }
    )

    return create_error_response(
        code=ErrorCode.VALIDATION_ERROR,
        message="Request validation failed",
        status_code=422,
        request=request,
        details=details,
    )


async def pydantic_validation_handler(
    request: Request,
    exc: PydanticValidationError
) -> JSONResponse:
    """Handle Pydantic model validation errors."""
    details = []
    for error in exc.errors():
        field_path = ".".join(str(loc) for loc in error["loc"])
        details.append(
            ErrorDetail(
                field=field_path,
                message=error["msg"],
                code=error["type"],
            )
        )

    return create_error_response(
        code=ErrorCode.VALIDATION_ERROR,
        message="Data validation failed",
        status_code=422,
        request=request,
        details=details,
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException
) -> JSONResponse:
    """Handle FastAPI/Starlette HTTP exceptions."""
    # Map HTTP status codes to error codes
    status_code_mapping = {
        400: ErrorCode.VALIDATION_ERROR,
        401: ErrorCode.AUTH_TOKEN_INVALID,
        403: ErrorCode.AUTH_FORBIDDEN,
        404: ErrorCode.NOT_FOUND_RESOURCE,
        409: ErrorCode.CONFLICT_RESOURCE_STATE,
        429: ErrorCode.RATE_LIMIT_EXCEEDED,
        500: ErrorCode.INTERNAL_ERROR,
        502: ErrorCode.EXTERNAL_SERVICE_ERROR,
        503: ErrorCode.EXTERNAL_API_UNAVAILABLE,
    }

    error_code = status_code_mapping.get(
        exc.status_code,
        ErrorCode.INTERNAL_ERROR
    )

    # Log based on status code
    if exc.status_code >= 500:
        logger.error(
            "HTTP Exception",
            extra={
                "status_code": exc.status_code,
                "detail": exc.detail,
                "path": str(request.url.path),
            }
        )
    else:
        logger.warning(
            "HTTP Exception",
            extra={
                "status_code": exc.status_code,
                "detail": exc.detail,
                "path": str(request.url.path),
            }
        )

    return create_error_response(
        code=error_code,
        message=str(exc.detail) if exc.detail else "An error occurred",
        status_code=exc.status_code,
        request=request,
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle any unhandled exceptions."""
    # Log full traceback for debugging
    logger.exception(
        "Unhandled exception",
        extra={
            "path": str(request.url.path),
            "method": request.method,
            "exception_type": type(exc).__name__,
        }
    )

    # In production, don't expose internal error details
    message = "An internal error occurred. Please try again later."

    # Capture in Sentry if configured
    try:
        import sentry_sdk
        sentry_sdk.capture_exception(exc)
    except ImportError:
        pass  # Sentry not configured

    return create_error_response(
        code=ErrorCode.INTERNAL_ERROR,
        message=message,
        status_code=500,
        request=request,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app."""
    # TIP custom exceptions
    app.add_exception_handler(TIPException, tip_exception_handler)
    app.add_exception_handler(ValidationError, tip_exception_handler)
    app.add_exception_handler(AuthenticationError, tip_exception_handler)
    app.add_exception_handler(AuthorizationError, tip_exception_handler)
    app.add_exception_handler(NotFoundError, tip_exception_handler)
    app.add_exception_handler(ConflictError, tip_exception_handler)
    app.add_exception_handler(RateLimitError, tip_exception_handler)
    app.add_exception_handler(InternalError, tip_exception_handler)
    app.add_exception_handler(ExternalServiceError, tip_exception_handler)

    # FastAPI/Starlette built-in exceptions
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(PydanticValidationError, pydantic_validation_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)

    # Catch-all for unhandled exceptions
    app.add_exception_handler(Exception, unhandled_exception_handler)

    logger.info("Exception handlers registered")
