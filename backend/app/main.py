"""
LeadForge AI - FastAPI Application
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.api.v1.router import api_router
import time

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("Starting LeadForge AI backend...")
    # Create SQLite tables on startup (for dev without Alembic)
    if settings.DATABASE_URL.startswith("sqlite"):
        from app.db.database import create_tables
        import app.models  # noqa - ensure all models are registered
        create_tables()
        logger.info("SQLite tables initialized")
    yield
    logger.info("LeadForge AI backend shutting down")


app = FastAPI(
    title="LeadForge AI",
    description="""
## LeadForge AI - CRM & Sales Pipeline Management

A production-style SaaS CRM platform with AI-powered lead scoring and insights.

### Features
- 🔐 JWT Authentication with Role-Based Access Control
- 📊 Real-time analytics dashboard
- 🤖 AI lead scoring, summaries, and email generation
- 📋 Kanban-style sales pipeline
- 👥 Lead, company, and contact management
- ✅ Task and activity tracking

### AI Providers
Configure via `AI_PROVIDER` env var: `gemini`, `openai`, or `fallback` (default, no API key required)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    logger.info(
        f"{request.method} {request.url.path} -> {response.status_code} ({duration:.1f}ms)"
    )
    return response


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({"field": field, "message": error["msg"]})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": errors},
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A database error occurred. Please try again."},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred."},
    )


# Mount API routes
app.include_router(api_router)


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "LeadForge AI",
        "version": "1.0.0",
        "environment": settings.APP_ENV,
        "ai_provider": settings.AI_PROVIDER,
    }


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "LeadForge AI API",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }
