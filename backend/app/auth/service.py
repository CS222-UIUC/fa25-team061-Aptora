"""
Authentication Service

Handles authentication business logic including:
- Password hashing and verification
- JWT token generation and validation
- User authentication
- Password reset
- Email verification
"""

from datetime import datetime, timedelta
from typing import Optional
import secrets
from jose import JWTError, jwt as jose_jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..config import settings
from ..models import User

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication operations."""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password.
        
        Args:
            plain_password: The plain text password
            hashed_password: The hashed password to compare against
            
        Returns:
            True if passwords match, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        Hash a password.
        
        Args:
            password: The plain text password to hash
            
        Returns:
            The hashed password
        """
        # Bcrypt has a 72-byte limit, so truncate if necessary
        # Convert to bytes to check length properly
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
            password = password_bytes.decode('utf-8', errors='ignore')
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: The data to encode in the token (typically user ID and email)
            expires_delta: Optional custom expiration time
            
        Returns:
            The encoded JWT token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jose_jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """
        Verify and decode a JWT token.

        Args:
            token: The JWT token to verify

        Returns:
            The decoded token payload if valid, None otherwise
        """
        try:
            payload = jose_jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            return payload
        except JWTError as e:
            print(f"JWT Error: {e}")  # Debug logging
            return None

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email and password.
        
        Args:
            db: Database session
            email: User's email address
            password: Plain text password
            
        Returns:
            User object if authentication succeeds, None otherwise
        """
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        return user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Get a user by email address.
        
        Args:
            db: Database session
            email: User's email address
            
        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def create_user(db: Session, email: str, password: str, first_name: str, last_name: str) -> User:
        """
        Create a new user account.

        Args:
            db: Database session
            email: User's email address
            password: Plain text password (will be hashed)
            first_name: User's first name
            last_name: User's last name

        Returns:
            The created User object
        """
        # Check if user already exists
        existing_user = AuthService.get_user_by_email(db, email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create new user
        hashed_password = AuthService.get_password_hash(password)
        user = User(
            email=email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            is_active=True
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def generate_reset_token() -> str:
        """
        Generate a secure random token for password reset.

        Returns:
            A secure random token string
        """
        return secrets.token_urlsafe(32)

    @staticmethod
    def create_password_reset_token(db: Session, email: str) -> Optional[str]:
        """
        Create a password reset token for a user.

        Args:
            db: Database session
            email: User's email address

        Returns:
            Reset token if user found, None otherwise
        """
        user = AuthService.get_user_by_email(db, email)
        if not user:
            return None

        # Generate reset token
        reset_token = AuthService.generate_reset_token()
        user.reset_token = reset_token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)

        db.commit()

        return reset_token

    @staticmethod
    def reset_password_with_token(db: Session, token: str, new_password: str) -> bool:
        """
        Reset a user's password using a reset token.

        Args:
            db: Database session
            token: Password reset token
            new_password: New password (plain text, will be hashed)

        Returns:
            True if password reset successful, False otherwise
        """
        user = db.query(User).filter(User.reset_token == token).first()

        if not user:
            return False

        # Check if token is expired
        if not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
            return False

        # Reset password
        user.hashed_password = AuthService.get_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expires = None

        db.commit()

        return True

    @staticmethod
    def create_verification_token(db: Session, user_id: int) -> str:
        """
        Create an email verification token for a user.

        Args:
            db: Database session
            user_id: User's ID

        Returns:
            Verification token
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Generate verification token
        verification_token = AuthService.generate_reset_token()
        user.verification_token = verification_token
        user.verification_token_expires = datetime.utcnow() + timedelta(hours=24)

        db.commit()

        return verification_token

    @staticmethod
    def verify_email(db: Session, token: str) -> bool:
        """
        Verify a user's email using a verification token.

        Args:
            db: Database session
            token: Email verification token

        Returns:
            True if verification successful, False otherwise
        """
        user = db.query(User).filter(User.verification_token == token).first()

        if not user:
            return False

        # Check if token is expired
        if not user.verification_token_expires or user.verification_token_expires < datetime.utcnow():
            return False

        # Verify email
        user.is_verified = True
        user.verification_token = None
        user.verification_token_expires = None

        db.commit()

        return True

