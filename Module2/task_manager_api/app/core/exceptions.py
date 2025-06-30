from fastapi import HTTPException, status
from typing import Any, Dict, Optional

class APIException(HTTPException):
    """Base API Exception with consistent error format"""
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code or f"ERR_{status_code}"

# Authentication Errors
class NotAuthenticatedException(APIException):
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="AUTH_REQUIRED"
        )

class InvalidCredentialsException(APIException):
    def __init__(self, detail: str = "Invalid username or password"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="INVALID_CREDENTIALS"
        )

class SessionExpiredException(APIException):
    def __init__(self, detail: str = "Session has expired"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="SESSION_EXPIRED"
        )

class InactiveUserException(APIException):
    def __init__(self, detail: str = "User account is inactive"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="USER_INACTIVE"
        )

# Resource Errors
class ResourceNotFoundException(APIException):
    def __init__(self, resource: str, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail or f"{resource} not found",
            error_code="RESOURCE_NOT_FOUND"
        )

class ResourceAlreadyExistsException(APIException):
    def __init__(self, resource: str, field: str, value: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{resource} with {field} '{value}' already exists",
            error_code="RESOURCE_EXISTS"
        )

# Validation Errors
class ValidationException(APIException):
    def __init__(self, detail: str, field: Optional[str] = None):
        error_detail = f"Validation error: {detail}"
        if field:
            error_detail = f"Validation error in field '{field}': {detail}"
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error_detail,
            error_code="VALIDATION_ERROR"
        )

# Database Errors
class DatabaseException(APIException):
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="DATABASE_ERROR"
        )

# Generic Server Error
class ServerException(APIException):
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="SERVER_ERROR"
        )