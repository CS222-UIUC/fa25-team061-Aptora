from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_users import FastAPIUsers
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import UserCreate, User as UserSchema, Token
from ..auth import fastapi_users, auth_backend

router = APIRouter(prefix="/auth", tags=["authentication"])

# Include FastAPI Users routes
router.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/jwt")
router.include_router(fastapi_users.get_register_router(UserSchema, UserCreate), prefix="/register")
router.include_router(fastapi_users.get_reset_password_router(), prefix="/reset-password")
router.include_router(fastapi_users.get_verify_router(UserSchema), prefix="/verify")


@router.get("/me", response_model=UserSchema)
async def get_current_user(
    current_user: User = Depends(fastapi_users.current_user(active=True))
):
    """Get current user information."""
    return current_user


@router.patch("/me", response_model=UserSchema)
async def update_current_user(
    user_update: dict,
    current_user: User = Depends(fastapi_users.current_user(active=True)),
    db: Session = Depends(get_db)
):
    """Update current user information."""
    for field, value in user_update.items():
        if hasattr(current_user, field) and value is not None:
            setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user
