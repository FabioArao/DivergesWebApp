from fastapi import Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Callable
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

def setup_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],  # Add your frontend URL
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

async def log_request_middleware(request: Request, call_next: Callable):
    start_time = time.time()
    response = None
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        logger.info(
            f"Path: {request.url.path} "
            f"Method: {request.method} "
            f"Status: {response.status_code} "
            f"Duration: {process_time:.3f}s"
        )
        
        return response
    except Exception as e:
        logger.error(
            f"Request failed: {str(e)} "
            f"Path: {request.url.path} "
            f"Method: {request.method}"
        )
        
        if response is None:
            raise HTTPException(
                status_code=500,
                detail="Internal server error"
            )
        return response

async def verify_token_middleware(request: Request, call_next: Callable):
    if request.url.path.startswith("/api/"):
        if "authorization" not in request.headers:
            raise HTTPException(
                status_code=401,
                detail="Authorization header missing"
            )
            
        # Token verification logic will be handled in the routes
        
    return await call_next(request)

def setup_middlewares(app):
    app.middleware("http")(log_request_middleware)
    app.middleware("http")(verify_token_middleware)
    setup_cors(app)
