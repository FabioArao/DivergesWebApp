from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .routes import auth
from .middleware.security import setup_middlewares
from .database import engine, Base
import logging
from typing import Union
import firebase_admin
from firebase_admin import credentials
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Firebase Admin
try:
    cred = credentials.Certificate(
        os.getenv(
            'FIREBASE_ADMIN_SDK_PATH',
            'divergesapp-firebase-adminsdk-1rnry-c91725b726.json'
        )
    )
    firebase_admin.initialize_app(cred)
except Exception as e:
    logger.error(f"Failed to initialize Firebase Admin: {str(e)}")
    raise

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    logger.error(f"Failed to create database tables: {str(e)}")
    raise

app = FastAPI(
    title="DivergesApp API",
    description="Backend API for DivergesApp",
    version="1.0.0"
)

# Setup middleware
setup_middlewares(app)

# Include routers
app.include_router(auth.router)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler caught: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "code": "INTERNAL_ERROR"
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected" if engine.connect() else "disconnected"
    }

# OpenAPI customization
app.swagger_ui_parameters = {
    "persistAuthorization": True,
    "displayRequestDuration": True,
    "filter": True
}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
