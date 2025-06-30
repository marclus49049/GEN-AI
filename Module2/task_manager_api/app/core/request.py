from fastapi import Request as FastAPIRequest
from typing import Optional
from app.models.user import User
from app.models.session import Session

class Request(FastAPIRequest):
    """Custom Request class with user and session attributes"""
    
    @property
    def user(self) -> Optional[User]:
        """Get the authenticated user from request state"""
        return getattr(self.state, "user", None)
    
    @property
    def session(self) -> Optional[Session]:
        """Get the current session from request state"""
        return getattr(self.state, "session", None)