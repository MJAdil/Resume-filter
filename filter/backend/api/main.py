"""FastAPI main application with lifespan management"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging

from config import get_settings, log_configuration
from services.database import db_service
from services.embeddings import embedding_service
from utils.logging import setup_logging

# Import routers
from api.routes import candidates, jobs, matching, profiles

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown"""
    # Startup
    logger.info("=" * 60)
    logger.info("Starting FastAPI Application")
    logger.info("=" * 60)
    
    try:
        # Load settings
        settings = get_settings()
        log_configuration(settings)
        
        # Load embedding model
        logger.info("Loading embedding model...")
        embedding_service.load_model()
        
        # Connect to MongoDB
        logger.info("Connecting to MongoDB...")
        await db_service.connect(settings.mongodb_uri)
        
        # Create database indexes
        await db_service.create_indexes()
        
        logger.info("=" * 60)
        logger.info("✓ Application startup complete")
        logger.info("=" * 60)
        
        yield
        
    finally:
        # Shutdown
        logger.info("Shutting down application...")
        await db_service.disconnect()
        logger.info("✓ Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Resume Filter API",
    description="Production-ready resume filtering system with ML-based matching",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # React dev server
        "https://*.vercel.app",   # Vercel preview deployments
        # Add your production domain here
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    errors = exc.errors()
    logger.warning(f"Validation error on {request.url.path}: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Validation error",
            "detail": errors,
            "message": "Invalid request data. Please check the required fields."
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(f"Unhandled exception on {request.url.path}: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )


# Include routers
app.include_router(candidates.router)
app.include_router(jobs.router)
app.include_router(matching.router)
app.include_router(profiles.router)


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint
    
    Returns system status and database connectivity
    """
    try:
        # Check database connection
        db_healthy = await db_service.health_check()
        
        if db_healthy:
            return {
                "status": "ok",
                "database": "connected",
                "model": "bge-small-en-v1.5",
                "version": "2.0.0"
            }
        else:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "degraded",
                    "database": "disconnected",
                    "model": "bge-small-en-v1.5",
                    "version": "2.0.0"
                }
            )
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "degraded",
                "database": "error",
                "error": str(e),
                "model": "bge-small-en-v1.5",
                "version": "2.0.0"
            }
        )


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Resume Filter API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# For Vercel serverless deployment
handler = app
