"""
Standardized API Response Models and Utilities
Ensures all endpoints return consistent response format across the entire API.

Format:
{
    "success": true/false,
    "data": {...},           # Main response data (null if error)
    "message": "...",        # User-friendly message
    "error": null/string,    # Error details (null on success)
    "timestamp": "2026-01-22T...",  # ISO 8601 timestamp
    "path": "/api/v1x/auth/login"   # Request path
}
"""

from pydantic import BaseModel, Field
from typing import Any, Optional, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')


class StandardResponse(BaseModel, Generic[T]):
    """
    Standard response wrapper for all API endpoints.
    
    Attributes:
        success: Whether the request was successful
        data: The response payload (any type)
        message: Human-readable message for the client
        error: Error details (None if successful)
        timestamp: When the response was generated (ISO 8601)
        path: The API endpoint path
    
    Example successful response:
        {
            "success": true,
            "data": {"user_id": 1, "email": "user@example.com"},
            "message": "Login successful",
            "error": null,
            "timestamp": "2026-01-22T14:30:00Z",
            "path": "/api/v1x/auth/login"
        }
    
    Example error response:
        {
            "success": false,
            "data": null,
            "message": "Invalid credentials",
            "error": "InvalidCredentialsError: Email or password is incorrect",
            "timestamp": "2026-01-22T14:30:01Z",
            "path": "/api/v1x/auth/login"
        }
    """
    success: bool = Field(..., description="Whether request was successful")
    data: Optional[T] = Field(None, description="Response payload")
    message: str = Field(..., description="User-friendly message")
    error: Optional[str] = Field(None, description="Error details if failed")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z", 
                           description="ISO 8601 timestamp")
    path: Optional[str] = Field(None, description="Request path")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"id": 1, "name": "John"},
                "message": "Operation successful",
                "error": None,
                "timestamp": "2026-01-22T14:30:00Z",
                "path": "/api/v1x/resource"
            }
        }


class ErrorDetail(BaseModel):
    """Detailed error information"""
    code: str = Field(..., description="Error code (e.g., 'INVALID_EMAIL')")
    message: str = Field(..., description="Error message")
    field: Optional[str] = Field(None, description="Field that caused error (for validation)")


class ValidationError(BaseModel):
    """Validation error response"""
    success: bool = False
    data: None = None
    message: str = "Validation error"
    error: str
    details: list[ErrorDetail] = Field(default_factory=list)


# ============================================================================
# HTTP STATUS CODE REFERENCE
# ============================================================================

HTTP_STATUS_CODES = {
    # Success Codes
    200: "OK - Request successful",
    201: "Created - Resource created successfully",
    204: "No Content - Request successful with no body",
    
    # Client Error Codes
    400: "Bad Request - Invalid request format or data",
    401: "Unauthorized - Missing or invalid authentication",
    403: "Forbidden - User lacks permission for this resource",
    404: "Not Found - Resource does not exist",
    409: "Conflict - Request conflicts with current state",
    422: "Unprocessable Entity - Validation error",
    429: "Too Many Requests - Rate limit exceeded",
    
    # Server Error Codes
    500: "Internal Server Error - Unexpected server error",
    503: "Service Unavailable - Server temporarily unavailable",
}


# ============================================================================
# ERROR MESSAGE TEMPLATES
# ============================================================================

ERROR_MESSAGES = {
    # Authentication Errors
    "INVALID_CREDENTIALS": "Email or password is incorrect",
    "INVALID_EMAIL": "Invalid email format",
    "INVALID_PASSWORD": "Password must be at least 8 characters",
    "EMAIL_ALREADY_EXISTS": "Email address is already registered",
    "USER_NOT_FOUND": "User account does not exist",
    "ACCOUNT_DISABLED": "Account has been disabled",
    "INVALID_TOKEN": "Token is invalid or expired",
    "TOKEN_EXPIRED": "Token has expired. Please login again",
    
    # Authorization Errors
    "PERMISSION_DENIED": "You do not have permission to perform this action",
    "ADMIN_ONLY": "This action requires administrator privileges",
    "OWNER_ONLY": "You can only access your own resources",
    
    # Validation Errors
    "INVALID_INPUT": "Invalid input data provided",
    "MISSING_REQUIRED_FIELD": "Required field is missing",
    "INVALID_ENUM_VALUE": "Invalid value for field",
    "EMAIL_REQUIRED": "Email address is required",
    "PASSWORD_REQUIRED": "Password is required",
    
    # Resource Errors
    "RESOURCE_NOT_FOUND": "Requested resource does not exist",
    "RESOURCE_ALREADY_EXISTS": "Resource already exists",
    "RESOURCE_IN_USE": "Resource is in use and cannot be deleted",
    
    # Rate Limiting
    "RATE_LIMIT_EXCEEDED": "Too many requests. Please try again later",
    
    # Server Errors
    "INTERNAL_ERROR": "An unexpected error occurred. Please try again later",
    "DATABASE_ERROR": "Database operation failed",
    "EXTERNAL_SERVICE_ERROR": "External service is temporarily unavailable",
    
    # Business Logic Errors
    "INSUFFICIENT_BALANCE": "Insufficient balance for this transaction",
    "INVALID_STATUS_TRANSITION": "Cannot transition to this status",
    "OPERATION_ALREADY_COMPLETED": "This operation has already been completed",
    "OPERATION_NOT_ALLOWED": "This operation is not allowed at this time",
}


# ============================================================================
# SUCCESS MESSAGE TEMPLATES
# ============================================================================

SUCCESS_MESSAGES = {
    "LOGIN": "Login successful",
    "LOGOUT": "Logout successful",
    "REGISTER": "Registration successful. Please check your email",
    "PASSWORD_RESET": "Password reset successful",
    "EMAIL_VERIFIED": "Email verified successfully",
    "PROFILE_UPDATED": "Profile updated successfully",
    "RESOURCE_CREATED": "Resource created successfully",
    "RESOURCE_UPDATED": "Resource updated successfully",
    "RESOURCE_DELETED": "Resource deleted successfully",
    "ACTION_COMPLETED": "Action completed successfully",
}


# ============================================================================
# RESPONSE BUILDER UTILITIES
# ============================================================================

def success_response(
    data: Any = None,
    message: str = "Success",
    path: str = None,
    timestamp: str = None
) -> dict:
    """
    Build a successful response.
    
    Args:
        data: Response payload
        message: User-friendly message
        path: API endpoint path
        timestamp: ISO 8601 timestamp (auto-generated if not provided)
    
    Returns:
        Standardized success response dict
    """
    if timestamp is None:
        timestamp = datetime.utcnow().isoformat() + "Z"
    
    return {
        "success": True,
        "data": data,
        "message": message,
        "error": None,
        "timestamp": timestamp,
        "path": path
    }


def error_response(
    message: str = "An error occurred",
    error: str = None,
    data: Any = None,
    path: str = None,
    timestamp: str = None
) -> dict:
    """
    Build an error response.
    
    Args:
        message: User-friendly message
        error: Error details/exception message
        data: Additional data (usually None)
        path: API endpoint path
        timestamp: ISO 8601 timestamp (auto-generated if not provided)
    
    Returns:
        Standardized error response dict
    """
    if timestamp is None:
        timestamp = datetime.utcnow().isoformat() + "Z"
    
    return {
        "success": False,
        "data": data,
        "message": message,
        "error": error or message,
        "timestamp": timestamp,
        "path": path
    }


def validation_error_response(
    details: list[dict] = None,
    path: str = None,
    timestamp: str = None
) -> dict:
    """
    Build a validation error response with field details.
    
    Args:
        details: List of validation errors with field info
        path: API endpoint path
        timestamp: ISO 8601 timestamp
    
    Returns:
        Validation error response dict
    """
    if timestamp is None:
        timestamp = datetime.utcnow().isoformat() + "Z"
    
    return {
        "success": False,
        "data": None,
        "message": "Validation error",
        "error": "VALIDATION_ERROR",
        "details": details or [],
        "timestamp": timestamp,
        "path": path
    }
