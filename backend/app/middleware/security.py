from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)
        
        # Security Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy
        if settings.is_production:
            csp_directives = [
                "default-src 'self'",
                "img-src 'self' data: https:",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
                "style-src 'self' 'unsafe-inline'",
                "font-src 'self' data:",
                f"connect-src 'self' {' '.join(settings.allowed_origins_list)}",
                "frame-ancestors 'none'",
                "base-uri 'self'",
                "form-action 'self'"
            ]
            response.headers["Content-Security-Policy"] = "; ".join(csp_directives)
        
        # HSTS in production
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Cache Control
        if request.url.path.startswith(("/api/static/", "/api/media/")):
            response.headers["Cache-Control"] = "public, max-age=31536000"
        else:
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        
        return response

class UploadSizeMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.method == "POST" and request.headers.get("content-type", "").startswith("multipart/form-data"):
            content_length = request.headers.get("content-length")
            if content_length:
                content_length = int(content_length)
                if content_length > settings.MAX_UPLOAD_SIZE:
                    logger.warning(f"Upload size {content_length} exceeds maximum allowed size {settings.MAX_UPLOAD_SIZE}")
                    return Response(
                        content="File too large",
                        status_code=413,
                        media_type="text/plain"
                    )
        
        return await call_next(request)

class FileTypeValidationMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.method == "POST" and request.headers.get("content-type", "").startswith("multipart/form-data"):
            form = await request.form()
            for field_name, field_value in form.items():
                if hasattr(field_value, "content_type"):
                    if field_value.content_type not in settings.allowed_file_types_list:
                        logger.warning(f"Invalid file type: {field_value.content_type}")
                        return Response(
                            content="Invalid file type",
                            status_code=415,
                            media_type="text/plain"
                        )
        
        return await call_next(request)
