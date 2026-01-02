import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.logging_config import setup_logging
from app.middleware.logging import LoggingMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.models.errors import ErrorDetail, ErrorResponse
from app.routes import ai, health

# Setup logging
setup_logging(log_level="DEBUG" if settings.DEBUG else "INFO")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    routes = []
    for route in app.routes:
        if hasattr(route, "path") and hasattr(route, "methods"):
            route_path = getattr(route, "path", "")
            route_methods = getattr(route, "methods", set())
            routes.append({"path": route_path, "methods": list(route_methods)})
    logger.info(f"Registered {len(routes)} routes", extra={"routes": routes})
    yield
    # Shutdown (if needed in the future)


app = FastAPI(
    title="Mnemos API",
    description="Second Brain for Receipts / Manuals / PDFs",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

logger.info(f"🚀 Starting Mnemos API (DEBUG={settings.DEBUG})")

# Middleware (order matters - last added is first executed)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)

# CORS (configured per environment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle validation errors with consistent format."""
    request_id = getattr(request.state, "request_id", None)
    errors = [
        ErrorDetail(
            field=".".join(str(loc) for loc in error["loc"]),
            message=error["msg"],
            type=error["type"],
        )
        for error in exc.errors()
    ]

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=ErrorResponse(
            error="Validation error",
            detail="Request validation failed",
            request_id=request_id,
            errors=errors,
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected errors."""
    request_id = getattr(request.state, "request_id", None)
    logger.error(
        f"Unhandled exception: {type(exc).__name__}",
        extra={"request_id": request_id, "path": request.url.path},
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal server error",
            detail="An unexpected error occurred" if not settings.DEBUG else str(exc),
            request_id=request_id,
            errors=None,
        ).model_dump(),
    )


# Include routers
app.include_router(health.router)
app.include_router(ai.router)


@app.get("/", tags=["Root"])
async def root():
    """API root endpoint."""
    return {
        "message": "Mnemos API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
