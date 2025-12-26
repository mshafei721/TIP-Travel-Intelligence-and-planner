"""
TIP - Travel Intelligence & Planner
FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import healthcheck, profile, recommendations, templates, trips
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging_config import RequestLogger, configure_logging
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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

# Add request logging middleware
app.middleware("http")(RequestLogger(app))

# Include routers
app.include_router(healthcheck.router, prefix="/api")
app.include_router(trips.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(templates.router, prefix="/api")


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
    logger.info(
        "Application starting",
        extra={
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "cors_origins": settings.cors_origins_list,
            "sentry_enabled": bool(settings.SENTRY_DSN),
        }
    )


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    import logging
    logger = logging.getLogger("app.startup")
    logger.info("Application shutting down")
