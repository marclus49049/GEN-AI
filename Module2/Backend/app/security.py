"""
Authentication and security utilities for JWT token management and password hashing.

This module implements JWT-based authentication using the OAuth2 Bearer token standard.
Security considerations:
- Uses bcrypt for password hashing with automatic salt generation
- JWT tokens include expiration times to limit exposure window
- Secret key should be cryptographically random in production
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-this-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Bcrypt context for secure password hashing with automatic salt generation
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate a bcrypt hash for a password with automatic salt."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token with user data and expiration.
    
    Tokens are signed with HS256 algorithm and include:
    - User identifier in 'sub' (subject) claim
    - Expiration time to limit token lifetime
    - Any additional data passed in the data dict
    
    Args:
        data: Dict containing user info (typically {"sub": str(user_id)})
        expires_delta: Optional custom expiration time, defaults to ACCESS_TOKEN_EXPIRE_MINUTES
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT token, returning user information.
    
    Validates token signature, expiration, and extracts user_id from 'sub' claim.
    Raises HTTP 401 Unauthorized for any validation failures.
    
    Args:
        token: The JWT token string from Authorization header
        
    Returns:
        Dict with user_id extracted from token
        
    Raises:
        HTTPException: 401 Unauthorized if token is invalid, expired, or malformed
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"user_id": int(user_id)}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )