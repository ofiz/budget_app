"""Authentication routes.

Security: Implements secure login/registration with OWASP best practices.
"""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Form
from motor.motor_asyncio import AsyncIOMotorDatabase

from .config import settings
from .database import get_db
from .models import Token, UserCreate, UserInDB, UserResponse
from .security import (
    authenticate_user,
    create_access_token,
    get_password_hash,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
) -> UserResponse:
    """Register a new user.
    
    Security: 
    - Password validated for strength in model
    - Password hashed with bcrypt before storage (OWASP A02)
    - Email uniqueness enforced
    """
    # Security: Check if user already exists (prevent account enumeration via timing?)
    existing_user = await db.users.find_one(
        {"email": user_data.email, "deleted_at": None}
    )
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Security: Hash password with bcrypt (OWASP A02 - Cryptographic Failures mitigation)
    hashed_password = get_password_hash(user_data.password)
    
    user = UserInDB(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
    )
    
    # Security: Store user with UUID public ID
    await db.users.insert_one(user.model_dump(mode="json"))
    
    return UserResponse(
        public_id=user.public_id,
        email=user.email,
        full_name=user.full_name,
        created_at=user.created_at,
    )


@router.post("/login", response_model=Token)
async def login(
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
) -> Token:
    """Login user and return JWT token.
    
    Security:
    - Accepts credentials as form data (not query params) - OWASP A02
    - Timing-safe password verification (OWASP A07)
    - JWT tokens with short expiration
    - Generic error message to prevent user enumeration
    """
    user = await authenticate_user(email, password, db)
    
    if not user:
        # Security: Generic error message prevents user enumeration (OWASP A07)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Security: Create JWT token with short expiration
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.public_id), "email": user.email},
        expires_delta=access_token_expires,
    )
    
    return Token(access_token=access_token, token_type="bearer")
