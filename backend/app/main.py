import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import init_db
from app.config.firebase import init_firebase
from app.routes import auth, content
from app.middleware.security import (
    SecurityMiddleware, 
    UploadSizeMiddleware, 
    FileTypeValidationMiddleware
)
from app.config.settings import settings, validate_settings
import time
from typing import Callable
import uvicorn
import os

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO if settings.is_development else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/app.log')
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DivergesWebApp API",
    description="Backend API for DivergesWebApp - Education Portal",
    version="1.0.0",
    docs_url="/api/docs" if settings.is_development else None,
    redoc_url="/api/redoc" if settings.is_development else None
)

# Static file serving
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Security Middlewares
app.add_middleware(SecurityMiddleware)
app.add_middleware(UploadSizeMiddleware)
app.add_middleware(FileTypeValidationMiddleware)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Trusted Host Middleware
allowed_hosts = ["localhost", "127.0.0.1"]
if settings.is_production:
    # Add production domain
    allowed_hosts.extend(["your-domain.com"])

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=allowed_hosts
)

# Request ID Middleware
@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next: Callable):
    request_id = request.headers.get("X-Request-ID", str(time.time()))
    logger.info(f"Processing request {request_id}: {request.method} {request.url}")
    
    try:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        logger.info(f"Request {request_id} completed in {process_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Request {request_id} failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "code": "INTERNAL_ERROR",
                "request_id": request_id
            }
        )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = request.headers.get("X-Request-ID", str(time.time()))
    logger.error(f"Global exception handler caught: {str(exc)}", extra={"request_id": request_id})
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "code": "INTERNAL_ERROR",
            "request_id": request_id
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = request.headers.get("X-Request-ID", str(time.time()))
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "code": getattr(exc, "code", "HTTP_ERROR"),
            "request_id": request_id
        }
    )

# Initialize services on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Application startup: Initializing services")
    try:
        # Validate settings
        validate_settings()
        logger.info("Settings validated successfully")
        
        # Initialize database
        init_db()
        logger.info("Database initialized successfully")
        
        # Initialize Firebase
        init_firebase()
        logger.info("Firebase initialized successfully")
        
        # Create required directories
        os.makedirs("uploads", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        logger.info("Required directories created/verified")
        
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.critical(f"Failed to initialize services: {str(e)}")
        raise
    
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown: Cleaning up resources")
    # Add cleanup tasks here

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(content.router, prefix="/api")

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        log_level="info" if settings.is_development else "warning",
        workers=4
    )
