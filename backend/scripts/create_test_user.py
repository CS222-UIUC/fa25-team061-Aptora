"""
Script to create a test user account.

Usage:
    python scripts/create_test_user.py
    python scripts/create_test_user.py --email test@example.com --password testpass123
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import User
from app.auth.service import AuthService
import argparse


def create_test_user(email: str = "test@example.com", password: str = "testpass123", 
                     first_name: str = "Test", last_name: str = "User"):
    """
    Create a test user account.
    
    Args:
        email: User email address
        password: User password
        first_name: User first name
        last_name: User last name
    """
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"❌ User with email '{email}' already exists!")
            print(f"   User ID: {existing_user.id}")
            print(f"   Name: {existing_user.first_name} {existing_user.last_name}")
            return existing_user
        
        # Create new user
        # Ensure password is a string and not too long for bcrypt
        password_str = str(password)[:72]  # bcrypt has 72 byte limit
        hashed_password = AuthService.get_password_hash(password_str)
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
        
        print("✅ Test user created successfully!")
        print(f"   Email: {user.email}")
        print(f"   Password: {password}")
        print(f"   Name: {user.first_name} {user.last_name}")
        print(f"   User ID: {user.id}")
        print(f"   Active: {user.is_active}")
        print("\n📝 You can now use these credentials to login at /auth/login")
        
        return user
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating test user: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a test user account")
    parser.add_argument("--email", default="test@example.com", help="User email address")
    parser.add_argument("--password", default="testpass123", help="User password")
    parser.add_argument("--first-name", default="Test", dest="first_name", help="User first name")
    parser.add_argument("--last-name", default="User", dest="last_name", help="User last name")
    
    args = parser.parse_args()
    
    create_test_user(
        email=args.email,
        password=args.password,
        first_name=args.first_name,
        last_name=args.last_name
    )

