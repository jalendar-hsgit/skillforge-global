"""
Global error handling middleware and exception handlers
Ensures all responses follow the standardized format.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import logging
from datetime import datetime

from app.core.responses import error_response, ERROR_MESSAGES

logger = logging.getLogger(__name__)


class StandardizedErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to catch unhandled exceptions and return standardized error responses.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        """Process request and catch any unhandled exceptions."""
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            logger.error(f"[ERROR] Unhandled exception in {request.method} {request.url.path}")
            logger.error(f"  Error type: {type(exc).__name__}")
            logger.error(f"  Error message: {str(exc)}")
            
            # Database errors
            if "database" in str(exc).lower() or "locked" in str(exc).lower():
                return JSONResponse(
                    status_code=503,
                    content=error_response(
                        message=ERROR_MESSAGES.get("DATABASE_ERROR", "Database error occurred"),
                        error=str(exc),
                        path=request.url.path
                    )
                )
            
            # Generic server error
            return JSONResponse(
                status_code=500,
                content=error_response(
                    message=ERROR_MESSAGES.get("INTERNAL_ERROR", "An unexpected error occurred"),
                    error=str(exc),
                    path=request.url.path
                )
            )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors with standardized response.
    """
    logger.warning(f"[VALIDATION] Request validation failed for {request.method} {request.url.path}")
    
    # Extract field errors
    details = []
    for error in exc.errors():
        field = ".".join(str(x) for x in error["loc"][1:]) if len(error["loc"]) > 1 else "unknown"
        details.append({
            "code": error["type"].upper(),
            "message": error["msg"],
            "field": field
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "data": None,
            "message": "Validation error",
            "error": "VALIDATION_ERROR",
            "details": details,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "path": request.url.path
        }
    )


async def http_exception_handler(request: Request, exc):
    """
    Handle FastAPI HTTPException with standardized response.
    """
    logger.warning(
        f"[HTTP_ERROR] {exc.status_code} in {request.method} {request.url.path}: {exc.detail}"
    )
    
    # Map HTTP status code to user message
    status_to_message = {
        400: ERROR_MESSAGES.get("INVALID_INPUT", "Invalid request"),
        401: ERROR_MESSAGES.get("INVALID_CREDENTIALS", "Authentication failed"),
        403: ERROR_MESSAGES.get("PERMISSION_DENIED", "Permission denied"),
        404: ERROR_MESSAGES.get("RESOURCE_NOT_FOUND", "Resource not found"),
        409: ERROR_MESSAGES.get("RESOURCE_ALREADY_EXISTS", "Resource already exists"),
        429: ERROR_MESSAGES.get("RATE_LIMIT_EXCEEDED", "Too many requests"),
        500: ERROR_MESSAGES.get("INTERNAL_ERROR", "Server error"),
        503: ERROR_MESSAGES.get("EXTERNAL_SERVICE_ERROR", "Service unavailable"),
    }
    
    message = status_to_message.get(exc.status_code, "An error occurred")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            message=message,
            error=str(exc.detail),
            path=request.url.path
        )
    )
