from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.orm import Session
from .config import settings
from .database import get_db
from .models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create user database adapter
def get_user_db():
    db = next(get_db())
    yield SQLAlchemyUserDatabase(db, User)

# Create authentication backend
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.secret_key, lifetime_seconds=settings.access_token_expire_minutes * 60)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# Create FastAPI Users instance
fastapi_users = FastAPIUsers[User, int](get_user_db, [auth_backend])

# Get current user
current_active_user = fastapi_users.current_user(active=True)
