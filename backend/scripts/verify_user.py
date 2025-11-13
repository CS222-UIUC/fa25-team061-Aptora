"""
Script to verify a user's email in the database.

Usage:
    python scripts/verify_user.py anishadg@icloud.com
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import User
from app.auth.service import AuthService


def verify_user(email: str):
    """
    Verify a user's email in the database.
    
    Args:
        email: User email address
    """
    db = SessionLocal()
    try:
        user = AuthService.get_user_by_email(db, email)
        
        if not user:
            print(f"❌ User with email '{email}' not found in database!")
            return None
        
        if user.is_verified:
            print(f"✅ User '{email}' is already verified!")
            return user
        
        # Verify the user
        user.is_verified = True
        user.verification_token = None
        user.verification_token_expires = None
        
        db.commit()
        db.refresh(user)
        
        print(f"✅ User '{email}' has been verified successfully!")
        print(f"   Email: {user.email}")
        print(f"   User ID: {user.id}")
        print(f"   Name: {user.first_name} {user.last_name}")
        print(f"   Verified: {user.is_verified}")
        
        return user
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error verifying user: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        email = "anishadg@icloud.com"
    
    verify_user(email)

