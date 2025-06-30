from datetime import datetime, timedelta
from typing import Optional
import secrets
from passlib.context import CryptContext

SESSION_EXPIRE_HOURS = 24
COOKIE_NAME = "session_id"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def generate_session_id() -> str:
    """Generate a secure random session ID"""
    return secrets.token_urlsafe(32)

def get_session_expiry() -> datetime:
    """Get the expiry time for a new session"""
    return datetime.utcnow() + timedelta(hours=SESSION_EXPIRE_HOURS)