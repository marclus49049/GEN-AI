from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
from pymongo.errors import PyMongoError
import logging
from app.models.session import Session
from app.models.user import User
from app.core.security import COOKIE_NAME
from app.core.exceptions import (
    NotAuthenticatedException,
    SessionExpiredException,
    InactiveUserException,
    DatabaseException
)

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to validate session and attach user to request"""
    
    def __init__(self, app, excluded_paths: list = None):
        super().__init__(app)
        # Paths that don't require authentication
        # Use tuples: (path, exact_match) where exact_match is True for exact matching
        self.excluded_paths = excluded_paths or [
            ("/", True),
            ("/docs", False),  # Allow /docs/*
            ("/redoc", False),  # Allow /redoc/*
            ("/openapi.json", True),
            ("/api/auth/register", True),
            ("/api/auth/login", True),
            ("/api/public", False)  # Allow /api/public/*
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for excluded paths
        is_excluded = False
        for path, exact_match in self.excluded_paths:
            if exact_match:
                if request.url.path == path:
                    is_excluded = True
                    break
            else:
                if request.url.path.startswith(path):
                    is_excluded = True
                    break
        
        if is_excluded:
            request.state.user = None
            request.state.session = None
            response = await call_next(request)
            return response
        
        # Get session ID from cookie
        session_id = request.cookies.get(COOKIE_NAME)
        
        if not session_id:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Not authenticated", "error_code": "AUTH_REQUIRED"}
            )
        
        # Find session
        session = await Session.find_one(Session.session_id == session_id)
        
        if not session:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid session", "error_code": "INVALID_SESSION"}
            )
        
        # Check if session is expired
        if session.expires_at < datetime.utcnow():
            try:
                await session.delete()
            except PyMongoError:
                pass  # Continue even if deletion fails
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Session expired", "error_code": "SESSION_EXPIRED"}
            )
        
        # Get user with fetch_links
        try:
            # Fetch the linked user document
            await session.fetch_link(Session.user)
            user = session.user
            
            # Verify user exists and is properly loaded
            if not user or not hasattr(user, 'id'):
                logger.error(f"User not found for session {session_id}")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "User not found", "error_code": "USER_NOT_FOUND"}
                )
            
            logger.debug(f"User {user.username} (ID: {user.id}) authenticated via session {session_id}")
        except PyMongoError as e:
            logger.error(f"Database error loading user for session {session_id}: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Failed to load user information", "error_code": "DATABASE_ERROR"}
            )
        except Exception as e:
            logger.error(f"Unexpected error loading user for session {session_id}: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Failed to process user data", "error_code": "SERVER_ERROR"}
            )
        
        # Check if user is active
        if not user.is_active:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "User account is inactive", "error_code": "USER_INACTIVE"}
            )
        # Attach user to request state
        request.state.user = user
        request.state.session = session
        # Process request
        response = await call_next(request)
        return response