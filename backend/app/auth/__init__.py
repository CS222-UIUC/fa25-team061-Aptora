"""
Authentication Module

Handles user authentication, registration, and account management.
"""

from .router import router as auth_router
from .service import AuthService
from .dependencies import get_current_user, get_current_active_user

# Alias for backward compatibility with existing routers
current_active_user = get_current_active_user

__all__ = [
    "auth_router",
    "AuthService",
    "get_current_user",
    "get_current_active_user",
    "current_active_user",  # For backward compatibility
]
