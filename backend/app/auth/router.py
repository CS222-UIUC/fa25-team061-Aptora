"""
Authentication Router

API endpoints for authentication including:
- User registration
- User login
- Token refresh
- Password change
- User profile management
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..config import settings
from .schemas import (
    UserLogin,
    UserRegister,
    TokenResponse,
    UserResponse,
    UserUpdate,
    PasswordChange,
    PasswordResetRequest,
    PasswordReset,
    MessageResponse,
)
from .service import AuthService
from .dependencies import get_current_active_user
from .email_service import EmailService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    Args:
        user_data: User registration data (email, password, first_name, last_name)
        db: Database session
        
    Returns:
        The created user information
        
    Raises:
        HTTPException: If email already exists or validation fails
    """
    try:
        user = AuthService.create_user(
            db=db,
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        
        # Create verification token and send verification email
        verification_token = AuthService.create_verification_token(db, user.id)
        EmailService.send_verification_email(user_data.email, verification_token)
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate a user and return an access token.
    
    Args:
        credentials: User login credentials (email and password)
        db: Database session
        
    Returns:
        Access token and token metadata
        
    Raises:
        HTTPException: If authentication fails
    """
    user = AuthService.authenticate_user(
        db=db,
        email=credentials.email,
        password=credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if email is verified
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email address before logging in.",
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": int(access_token_expires.total_seconds())
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the current authenticated user's information.
    
    Args:
        current_user: The current authenticated user (from dependency)
        
    Returns:
        Current user information
    """
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update the current user's information.
    
    Args:
        user_update: Fields to update (email, first_name, last_name)
        current_user: The current authenticated user
        db: Database session
        
    Returns:
        Updated user information
        
    Raises:
        HTTPException: If email already exists or validation fails
    """
    # Check if email is being updated and if it's already taken
    if user_update.email and user_update.email != current_user.email:
        existing_user = AuthService.get_user_by_email(db, user_update.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = user_update.email
    
    # Update other fields
    if user_update.first_name is not None:
        current_user.first_name = user_update.first_name
    if user_update.last_name is not None:
        current_user.last_name = user_update.last_name
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change the current user's password.
    
    Args:
        password_data: Current password and new password
        current_user: The current authenticated user
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If current password is incorrect
    """
    # Verify current password
    if not AuthService.verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.hashed_password = AuthService.get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout endpoint (client-side token removal).

    Note: With JWT tokens, logout is typically handled client-side by removing the token.
    This endpoint exists for consistency and can be extended for token blacklisting if needed.

    Args:
        current_user: The current authenticated user

    Returns:
        Success message
    """
    return {"message": "Logged out successfully"}


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request a password reset email.

    Args:
        request: Email address to send reset link to
        db: Database session

    Returns:
        Success message (always returns success to prevent email enumeration)
    """
    # Generate reset token
    reset_token = AuthService.create_password_reset_token(db, request.email)

    # Send reset email if user exists (always return success to prevent email enumeration)
    if reset_token:
        EmailService.send_password_reset_email(request.email, reset_token)

    return {
        "message": "If an account with that email exists, a password reset link has been sent"
    }


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
):
    """
    Reset password using a reset token.

    Args:
        reset_data: Reset token and new password
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If token is invalid or expired
    """
    success = AuthService.reset_password_with_token(
        db=db,
        token=reset_data.token,
        new_password=reset_data.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    return {"message": "Password has been reset successfully"}


@router.post("/request-verification", response_model=MessageResponse)
async def request_verification(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request email verification link (for unauthenticated users).

    Args:
        request: Email address to send verification link to
        db: Database session

    Returns:
        Success message (always returns success to prevent email enumeration)
    """
    user = AuthService.get_user_by_email(db, request.email)
    
    # Only send verification email if user exists and is not verified
    if user and not user.is_verified:
        verification_token = AuthService.create_verification_token(db, user.id)
        EmailService.send_verification_email(request.email, verification_token)
    
    # Always return success to prevent email enumeration
    return {
        "message": "If an account with that email exists and is not verified, a verification link has been sent"
    }


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Resend email verification link (for authenticated users).

    Args:
        current_user: The current authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If user is already verified
    """
    if current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )

    # Generate new verification token
    verification_token = AuthService.create_verification_token(db, current_user.id)

    # Send verification email
    EmailService.send_verification_email(current_user.email, verification_token)

    return {"message": "Verification email sent"}


@router.get("/verify-email/{token}", response_model=MessageResponse)
async def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Verify email address using verification token.

    Args:
        token: Email verification token
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If token is invalid or expired
    """
    success = AuthService.verify_email(db, token)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )

    return {"message": "Email verified successfully"}

