"""
Middleware to check maintenance mode and other platform settings.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.db import SessionLocal
from app.models.user import User
from app.core.security import get_current_user_optional
import logging

logger = logging.getLogger(__name__)


class MaintenanceModeMiddleware(BaseHTTPMiddleware):
    """
    Block non-admin users when maintenance mode is enabled.
    Allows admins/superadmins to access the site for testing.
    """
    
    # Endpoints that are always allowed even in maintenance mode
    ALLOWED_PATHS = [
        "/healthz",
        "/api/v1/auth/login",
        "/api/v1/auth/me",
        "/api/session/login",
        "/api/session/me",
        "/api/v1x/admin",  # All admin endpoints
    ]
    
    async def dispatch(self, request: Request, call_next):
        # Import here to avoid circular dependency
        from app.services.settings_service import is_maintenance_mode, get_platform_name, get_support_email
        
        # Check if maintenance mode is enabled
        if not is_maintenance_mode():
            # Not in maintenance, proceed normally
            return await call_next(request)
        
        # Check if path is allowed
        path = request.url.path
        for allowed in self.ALLOWED_PATHS:
            if path.startswith(allowed):
                return await call_next(request)
        
        # Check if user is admin
        try:
            db = SessionLocal()
            try:
                user = get_current_user_optional(request, db)
                if user and user.role in ["ADMIN", "SUPERADMIN"]:
                    # Admin can access during maintenance
                    return await call_next(request)
            finally:
                db.close()
        except Exception as e:
            logger.debug(f"Error checking user role in maintenance mode: {e}")
        
        # Block the request with maintenance message
        return JSONResponse(
            status_code=503,
            content={
                "error": "Service Unavailable",
                "message": f"{get_platform_name()} is currently undergoing maintenance. Please try again later.",
                "support": get_support_email(),
                "maintenance": True
            },
            headers={"Retry-After": "3600"}  # Suggest retry in 1 hour
        )
