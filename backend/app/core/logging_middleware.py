"""
Error logging middleware and exception handlers for FastAPI.
Provides request IDs, detailed error logging in DEBUG mode, and structured exception handling.
"""
import logging
import traceback
import uuid
from typing import Callable
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all requests/responses with unique request IDs.
    In DEBUG mode, includes detailed error information.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log incoming request
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        try:
            response = await call_next(request)
            
            # Log response
            logger.info(
                f"[{request_id}] Response: {response.status_code}"
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as exc:
            # Log exception with full traceback in DEBUG mode
            if settings.DEBUG:
                logger.error(
                    f"[{request_id}] Unhandled exception:\n"
                    f"{traceback.format_exc()}"
                )
            else:
                logger.error(
                    f"[{request_id}] Unhandled exception: {type(exc).__name__}: {str(exc)}"
                )
            
            # Re-raise to let exception handlers deal with it
            raise


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle Pydantic validation errors with detailed field information.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.warning(f"[{request_id}] Validation error: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": str(exc),
            "request_id": request_id
        }
    )


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle HTTPException with proper status codes and messages.
    """
    from fastapi.exceptions import HTTPException
    
    request_id = getattr(request.state, "request_id", "unknown")
    
    if isinstance(exc, HTTPException):
        status_code = exc.status_code
        detail = exc.detail
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        detail = "Internal Server Error"
    
    logger.error(f"[{request_id}] HTTP {status_code}: {detail}")
    
    response_content = {
        "error": detail,
        "request_id": request_id
    }
    
    # In DEBUG mode, include additional context
    if settings.DEBUG and status_code >= 500:
        response_content["type"] = type(exc).__name__
        response_content["traceback"] = traceback.format_exc()
    
    return JSONResponse(
        status_code=status_code,
        content=response_content
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all handler for unexpected exceptions.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.error(
        f"[{request_id}] Unexpected error: {type(exc).__name__}: {str(exc)}"
    )
    
    if settings.DEBUG:
        logger.error(f"[{request_id}] Traceback:\n{traceback.format_exc()}")
    
    response_content = {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred",
        "request_id": request_id
    }
    
    # Only expose detailed error info in DEBUG mode
    if settings.DEBUG:
        response_content["detail"] = str(exc)
        response_content["type"] = type(exc).__name__
        response_content["traceback"] = traceback.format_exc().split("\n")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_content
    )


def setup_logging(app):
    """
    Configure logging middleware and exception handlers for the FastAPI app.
    Call this from main.py after app creation.
    """
    # Add middleware
    app.add_middleware(RequestLoggingMiddleware)
    
    # Add exception handlers
    from fastapi.exceptions import RequestValidationError, HTTPException
    
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info(f"Logging middleware configured (DEBUG={'ON' if settings.DEBUG else 'OFF'})")
