"""
Error logging middleware and exception handlers for development and production.
"""
import logging
import traceback
from typing import Callable
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output
    ]
)

logger = logging.getLogger("app")


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to catch and log all unhandled exceptions.
    In development, returns detailed error information.
    In production, returns generic error messages.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            
            # Log 4xx and 5xx responses
            if response.status_code >= 400:
                logger.warning(
                    f"{request.method} {request.url.path} - Status: {response.status_code}"
                )
            
            return response
            
        except Exception as exc:
            # Log the full exception with stack trace
            logger.error(
                f"Unhandled exception on {request.method} {request.url.path}",
                exc_info=True
            )
            
            # Determine if we're in development mode
            is_dev = getattr(settings, "ENVIRONMENT", "production").lower() in ["development", "dev", "local"]
            
            # Build error response
            if is_dev:
                # In development, return detailed error information
                error_detail = {
                    "error": type(exc).__name__,
                    "message": str(exc),
                    "traceback": traceback.format_exc().split("\n"),
                    "path": str(request.url.path),
                    "method": request.method
                }
            else:
                # In production, return generic error message
                error_detail = {
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred. Please try again later."
                }
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=error_detail
            )


def setup_error_logging():
    """
    Setup file logging if configured in settings.
    Call this during app startup.
    """
    log_file = getattr(settings, "LOG_FILE", None)
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(file_handler)
        logger.info(f"File logging enabled: {log_file}")


def log_startup_info():
    """Log application startup information"""
    logger.info("=" * 50)
    logger.info("SkillForge Global API Starting")
    logger.info(f"Environment: {getattr(settings, 'ENVIRONMENT', 'production')}")
    logger.info(f"Database: {settings.DATABASE_URL}")
    logger.info(f"Frontend Origin: {settings.FRONTEND_ORIGIN}")
    logger.info("=" * 50)
