"""
Structured Logging Configuration for TIP API

Provides JSON-formatted logging for production environments
with context enrichment and performance tracking.
"""

import logging
import sys
import time
from contextlib import asynccontextmanager
from datetime import datetime
from functools import wraps
from typing import Any, Callable
from uuid import uuid4

from fastapi import FastAPI, Request

# Try to import structlog for advanced structured logging
try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False

# Try to import orjson for faster JSON serialization
try:
    import orjson

    def json_serializer(obj: Any) -> str:
        return orjson.dumps(obj).decode()
except ImportError:
    import json

    def json_serializer(obj: Any) -> str:
        return json.dumps(obj, default=str)


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.

    Outputs logs in JSON format with standardized fields for
    easy parsing by log aggregation services (ELK, CloudWatch, etc.)
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }

        # Add extra fields from record
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in {
                "name", "msg", "args", "created", "filename",
                "funcName", "levelname", "levelno", "lineno",
                "module", "msecs", "pathname", "process",
                "processName", "relativeCreated", "stack_info",
                "exc_info", "exc_text", "message", "thread",
                "threadName", "taskName",
            }:
                extra_fields[key] = value

        if extra_fields:
            log_data["extra"] = extra_fields

        return json_serializer(log_data)


class ConsoleFormatter(logging.Formatter):
    """
    Colored console formatter for development.
    """

    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, "")
        record.levelname = f"{color}{record.levelname}{self.RESET}"

        # Format extra fields nicely
        extra = ""
        for key, value in record.__dict__.items():
            if key.startswith("_") or key in {
                "name", "msg", "args", "created", "filename",
                "funcName", "levelname", "levelno", "lineno",
                "module", "msecs", "pathname", "process",
                "processName", "relativeCreated", "stack_info",
                "exc_info", "exc_text", "message", "thread",
                "threadName", "taskName",
            }:
                continue
            extra += f" | {key}={value}"

        return f"[{record.name}] {record.levelname}: {record.getMessage()}{extra}"


def configure_logging(
    environment: str = "development",
    log_level: str = "INFO",
    enable_json: bool | None = None,
) -> None:
    """
    Configure logging for the application.

    Args:
        environment: Current environment (development/staging/production)
        log_level: Minimum log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)
        enable_json: Force JSON format (auto-detected based on environment if None)
    """
    # Determine if we should use JSON format
    use_json = enable_json if enable_json is not None else (
        environment in ("production", "staging")
    )

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level.upper()))

    # Set formatter based on environment
    if use_json:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(ConsoleFormatter())

    root_logger.addHandler(handler)

    # Configure specific loggers
    # Reduce noise from external libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("supabase").setLevel(logging.WARNING)

    # TIP loggers
    logging.getLogger("app").setLevel(getattr(logging, log_level.upper()))

    logger = logging.getLogger(__name__)
    logger.info(
        "Logging configured",
        extra={
            "environment": environment,
            "log_level": log_level,
            "format": "json" if use_json else "console",
        }
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    return logging.getLogger(name)


class RequestLogger:
    """
    Middleware for logging HTTP requests and responses.
    """

    def __init__(self, app: FastAPI):
        self.app = app
        self.logger = logging.getLogger("app.requests")

    async def __call__(self, request: Request, call_next):
        # Generate request ID
        request_id = request.headers.get("X-Request-ID", f"req-{uuid4().hex[:12]}")

        # Store request ID in state for use in handlers
        request.state.request_id = request_id

        # Log request start
        start_time = time.time()
        self.logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": str(request.url.path),
                "query": str(request.query_params),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log error
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": str(request.url.path),
                    "duration_ms": round(duration_ms, 2),
                    "error": str(e),
                    "error_type": type(e).__name__,
                }
            )
            raise

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Log request completion
        log_level = logging.INFO if response.status_code < 400 else logging.WARNING
        self.logger.log(
            log_level,
            "Request completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": str(request.url.path),
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
            }
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response


def log_execution_time(logger_name: str = "app.performance"):
    """
    Decorator to log function execution time.

    Usage:
        @log_execution_time()
        async def my_function():
            ...
    """
    def decorator(func: Callable):
        logger = logging.getLogger(logger_name)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start) * 1000
                logger.debug(
                    "Function completed",
                    extra={
                        "function": func.__name__,
                        "duration_ms": round(duration_ms, 2),
                    }
                )
                return result
            except Exception as e:
                duration_ms = (time.time() - start) * 1000
                logger.error(
                    "Function failed",
                    extra={
                        "function": func.__name__,
                        "duration_ms": round(duration_ms, 2),
                        "error": str(e),
                    }
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start) * 1000
                logger.debug(
                    "Function completed",
                    extra={
                        "function": func.__name__,
                        "duration_ms": round(duration_ms, 2),
                    }
                )
                return result
            except Exception as e:
                duration_ms = (time.time() - start) * 1000
                logger.error(
                    "Function failed",
                    extra={
                        "function": func.__name__,
                        "duration_ms": round(duration_ms, 2),
                        "error": str(e),
                    }
                )
                raise

        if asyncio_iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def asyncio_iscoroutinefunction(func: Callable) -> bool:
    """Check if function is async."""
    import asyncio
    return asyncio.iscoroutinefunction(func)


# Logging utilities for agents
class AgentLogger:
    """
    Specialized logger for AI agents with context tracking.
    """

    def __init__(self, agent_type: str, trip_id: str | None = None):
        self.agent_type = agent_type
        self.trip_id = trip_id
        self.logger = logging.getLogger(f"app.agents.{agent_type}")
        self.start_time: float | None = None

    def start(self, message: str = "Agent started"):
        """Log agent start."""
        self.start_time = time.time()
        self.logger.info(
            message,
            extra={
                "agent_type": self.agent_type,
                "trip_id": self.trip_id,
                "phase": "start",
            }
        )

    def progress(self, message: str, step: int | None = None, total: int | None = None):
        """Log agent progress."""
        extra = {
            "agent_type": self.agent_type,
            "trip_id": self.trip_id,
            "phase": "progress",
        }
        if step is not None:
            extra["step"] = step
        if total is not None:
            extra["total_steps"] = total
            extra["progress_pct"] = round((step / total) * 100, 1) if step else 0

        self.logger.info(message, extra=extra)

    def complete(self, message: str = "Agent completed", confidence: float | None = None):
        """Log agent completion."""
        duration_ms = None
        if self.start_time:
            duration_ms = (time.time() - self.start_time) * 1000

        extra = {
            "agent_type": self.agent_type,
            "trip_id": self.trip_id,
            "phase": "complete",
        }
        if duration_ms:
            extra["duration_ms"] = round(duration_ms, 2)
        if confidence is not None:
            extra["confidence"] = round(confidence, 3)

        self.logger.info(message, extra=extra)

    def error(self, message: str, error: Exception | None = None):
        """Log agent error."""
        duration_ms = None
        if self.start_time:
            duration_ms = (time.time() - self.start_time) * 1000

        extra = {
            "agent_type": self.agent_type,
            "trip_id": self.trip_id,
            "phase": "error",
        }
        if duration_ms:
            extra["duration_ms"] = round(duration_ms, 2)
        if error:
            extra["error_type"] = type(error).__name__
            extra["error_message"] = str(error)

        self.logger.error(message, extra=extra, exc_info=error is not None)
