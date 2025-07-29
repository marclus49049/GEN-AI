"""
Authentication endpoints implementing OAuth2 password flow with JWT tokens.

OAuth2 Flow:
1. Registration: User provides username/email/password, gets UserResponse (no auto-login)
2. Login: Client sends form data (username/password), receives JWT Bearer token
3. Protected endpoints: Client includes "Authorization: Bearer <token>" header
4. Token validation: Dependencies decode JWT to extract user_id

Security features:
- Password hashing with bcrypt
- JWT tokens with configurable expiration
- Username and email uniqueness validation
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, Token
from app.security import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user with username, email, and password.
    
    Validates uniqueness of both username and email before creating user.
    Password is hashed with bcrypt before storage. Does not auto-login user
    after registration - they must call /login separately.
    """
    # Check for existing username or email
    db_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if db_user:
        # Provide specific error message to help user understand the issue
        if db_user.username == user.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Create user with hashed password
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT Bearer token.
    
    OAuth2 password flow: Client sends username/password in form data format.
    On success, returns JWT token that must be included in Authorization header
    for protected endpoints. Token contains user_id in 'sub' claim and expires
    after ACCESS_TOKEN_EXPIRE_MINUTES.
    
    Security note: Uses constant-time password verification to prevent timing attacks.
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # Use constant-time verification to prevent timing attacks
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create JWT token with user_id in 'sub' claim
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}