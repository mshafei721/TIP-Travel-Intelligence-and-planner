"""
TIP - Travel Intelligence & Planner
FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api import healthcheck

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

# Include routers
app.include_router(healthcheck.router, prefix="/api")


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint - redirects to API docs"""
    return JSONResponse({
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
        "health": "/api/health"
    })


# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    print(f"[STARTUP] {settings.APP_NAME} v{settings.APP_VERSION} starting...")
    print(f"[STARTUP] Environment: {settings.ENVIRONMENT}")
    print(f"[STARTUP] CORS enabled for: {settings.cors_origins_list}")
    print(f"[STARTUP] API docs available at: /api/docs")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    print(f"[SHUTDOWN] {settings.APP_NAME} shutting down...")
