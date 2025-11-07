"""
Script to check if a user exists in the database.

Usage:
    python scripts/check_user.py anishadg@icloud.com
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import User
from app.auth.service import AuthService


def check_user(email: str):
    """
    Check if a user exists in the database.
    
    Args:
        email: User email address
    """
    db = SessionLocal()
    try:
        user = AuthService.get_user_by_email(db, email)
        
        if user:
            print(f"✅ User found!")
            print(f"   Email: {user.email}")
            print(f"   User ID: {user.id}")
            print(f"   Name: {user.first_name} {user.last_name}")
            print(f"   Active: {user.is_active}")
            print(f"   Verified: {user.is_verified}")
            print(f"   Created at: {user.created_at}")
            return user
        else:
            print(f"❌ User with email '{email}' not found in database!")
            return None
        
    except Exception as e:
        print(f"❌ Error checking user: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        email = "anishadg@icloud.com"
    
    check_user(email)

