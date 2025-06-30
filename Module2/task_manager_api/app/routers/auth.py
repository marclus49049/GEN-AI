from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.errors import PyMongoError
from app.models.user import User
from app.models.session import Session
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.core.security import verify_password, get_password_hash, generate_session_id, get_session_expiry, COOKIE_NAME, SESSION_EXPIRE_HOURS
from app.core.exceptions import (
    ResourceAlreadyExistsException,
    InvalidCredentialsException,
    NotAuthenticatedException,
    DatabaseException,
    ServerException
)

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    try:
        # Check if username exists
        existing_user = await User.find_one(User.username == user.username)
        if existing_user:
            raise ResourceAlreadyExistsException("User", "username", user.username)
        
        # Check if email exists
        existing_email = await User.find_one(User.email == user.email)
        if existing_email:
            raise ResourceAlreadyExistsException("User", "email", user.email)
        
        # Create new user
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password
        )
        await db_user.create()
        return db_user
    except (ResourceAlreadyExistsException, HTTPException):
        raise
    except PyMongoError as e:
        raise DatabaseException(f"Failed to create user: Database error")
    except Exception as e:
        raise ServerException(f"Failed to register user")

@router.post("/login")
async def login(
    response: Response,
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    try:
        # Find user
        user = await User.find_one(User.username == form_data.username)
        if not user:
            raise InvalidCredentialsException()
        
        # Verify password
        if not verify_password(form_data.password, user.hashed_password):
            raise InvalidCredentialsException()
        
        # Clean up old sessions for this user
        try:
            # Query sessions by user ID
            await Session.find(Session.user.id == user.id).delete()
        except PyMongoError:
            # Continue even if cleanup fails
            pass
        
        # Create new session
        session_id = generate_session_id()
        session = Session(
            session_id=session_id,
            user=user.id,  # Use user ID for Link field
            expires_at=get_session_expiry(),
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("User-Agent", "Unknown")
        )
        await session.create()
        
        # Set cookie
        response.set_cookie(
            key=COOKIE_NAME,
            value=session_id,
            httponly=True,
            secure=False,  # Set to True for production with HTTPS
            samesite="lax",
            max_age=SESSION_EXPIRE_HOURS * 3600
        )
        
        return {"message": "Login successful", "username": user.username}
    except (InvalidCredentialsException, HTTPException):
        raise
    except PyMongoError as e:
        raise DatabaseException("Failed to process login: Database error")
    except Exception as e:
        raise ServerException("Login failed due to server error")

@router.post("/logout")
async def logout(request: Request, response: Response):
    """Logout the current user - uses middleware for authentication"""
    try:
        # The middleware ensures request.state.user is available
        # Get session from request state (populated by middleware)
        if hasattr(request.state, 'session') and request.state.session:
            try:
                await request.state.session.delete()
            except PyMongoError:
                # Continue even if session deletion fails
                pass
        
        # Clear cookie
        response.delete_cookie(key=COOKIE_NAME)
        
        return {"message": "Logout successful"}
    except Exception as e:
        # Always try to clear the cookie
        response.delete_cookie(key=COOKIE_NAME)
        # Log error but return success since user is effectively logged out
        return {"message": "Logout successful"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(request: Request):
    """Get current user info - uses middleware for authentication"""
    # The middleware ensures request.state.user is available
    if not hasattr(request.state, 'user') or request.state.user is None:
        raise NotAuthenticatedException("User not authenticated. Please login.")
    
    try:
        return request.state.user
    except Exception as e:
        raise ServerException("Failed to retrieve user information")