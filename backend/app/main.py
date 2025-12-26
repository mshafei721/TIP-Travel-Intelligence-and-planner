"""
TIP - Travel Intelligence & Planner
FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import analytics, healthcheck, history, itinerary, places, profile, recommendations, sharing, templates, trips
from app.api import settings as settings_router
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging_config import RequestLogger, configure_logging
from app.core.security import check_security_on_startup, register_security_middleware
from app.core.sentry import configure_sentry

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered travel intelligence platform providing accurate visa requirements, destination insights, and personalized itineraries",
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Configure CORS with restricted methods and headers (security hardening)
ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
ALLOWED_HEADERS = [
    "Authorization",
    "Content-Type",
    "X-Request-ID",
    "X-Idempotency-Key",
    "Accept",
    "Accept-Language",
    "Origin",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
    expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"],
)

# Configure structured logging
configure_logging(
    environment=settings.ENVIRONMENT,
    log_level=settings.LOG_LEVEL,
)

# Configure Sentry (if DSN is provided)
if settings.SENTRY_ENABLED and settings.SENTRY_DSN:
    configure_sentry(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        release=f"tip@{settings.APP_VERSION}",
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE,
    )

# Register exception handlers (must be before routers)
register_exception_handlers(app)

# Register security middleware (rate limiting, security headers)
register_security_middleware(app)

# Add request logging middleware
app.middleware("http")(RequestLogger(app))

# Include routers
app.include_router(healthcheck.router, prefix="/api")
app.include_router(trips.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(templates.router, prefix="/api")
app.include_router(itinerary.router, prefix="/api")
app.include_router(places.router, prefix="/api")
app.include_router(sharing.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(settings_router.router, prefix="/api")


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint - redirects to API docs"""
    return JSONResponse(
        {
            "message": f"Welcome to {settings.APP_NAME} API",
            "version": settings.APP_VERSION,
            "docs": "/api/docs",
            "health": "/api/health",
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    import logging
    logger = logging.getLogger("app.startup")

    # Run security validation (fails on critical issues in production)
    check_security_on_startup(app, fail_on_critical=True)

    logger.info(
        "Application starting",
        extra={
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "cors_origins": settings.cors_origins_list,
            "sentry_enabled": bool(settings.SENTRY_DSN),
            "rate_limit": settings.RATE_LIMIT_PER_MINUTE,
        }
    )


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    import logging
    logger = logging.getLogger("app.startup")
    logger.info("Application shutting down")
