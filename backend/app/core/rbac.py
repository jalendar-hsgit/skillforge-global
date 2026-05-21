"""
Role-based Access Control (RBAC) utilities
Provides decorators and dependencies for admin/mentor permission validation
"""

from fastapi import HTTPException, Depends, status
from app.core.security import get_current_user
from app.models.user import User, UserRole


def require_admin(user: User = Depends(get_current_user)) -> User:
    """
    Dependency to verify user is ADMIN or SUPERADMIN.
    
    Raises:
        HTTPException(403): If user doesn't have admin role
    
    Usage:
        @router.get("/admin-only")
        def admin_endpoint(user: User = Depends(require_admin)):
            ...
    """
    if user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


def require_superadmin(user: User = Depends(get_current_user)) -> User:
    """
    Dependency to verify user is SUPERADMIN only.
    
    Raises:
        HTTPException(403): If user is not SUPERADMIN
    
    Usage:
        @router.delete("/dangerous-operation")
        def superadmin_endpoint(user: User = Depends(require_superadmin)):
            ...
    """
    if user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superadmin access required"
        )
    return user


def require_mentor(user: User = Depends(get_current_user)) -> User:
    """
    Dependency to verify user is MENTOR (or above).
    
    Raises:
        HTTPException(403): If user doesn't have mentor role
    
    Usage:
        @router.post("/mentor-only")
        def mentor_endpoint(user: User = Depends(require_mentor)):
            ...
    """
    if user.role not in [UserRole.MENTOR, UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mentor access required"
        )
    return user


def require_authenticated(user: User = Depends(get_current_user)) -> User:
    """
    Dependency to verify user is authenticated.
    Always returns the current user.
    
    Usage:
        @router.get("/profile")
        def user_profile(user: User = Depends(require_authenticated)):
            ...
    """
    return user


# Role checking utilities
def is_admin(user: User) -> bool:
    """Check if user is ADMIN or SUPERADMIN"""
    return user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]


def is_superadmin(user: User) -> bool:
    """Check if user is SUPERADMIN"""
    return user.role == UserRole.SUPERADMIN


def is_mentor(user: User) -> bool:
    """Check if user is MENTOR or higher"""
    return user.role in [UserRole.MENTOR, UserRole.ADMIN, UserRole.SUPERADMIN]


def is_authenticated(user: User) -> bool:
    """Check if user is authenticated (always true if user object exists)"""
    return user is not None


def check_role(user: User, required_role: UserRole) -> bool:
    """Check if user has at least the required role"""
    role_hierarchy = {
        UserRole.USER: 0,
        UserRole.MENTOR: 1,
        UserRole.ADMIN: 2,
        UserRole.SUPERADMIN: 3,
    }
    return role_hierarchy.get(user.role, 0) >= role_hierarchy.get(required_role, 0)
