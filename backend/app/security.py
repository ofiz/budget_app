"""Security utilities for authentication and authorization.

Security: Following OWASP guidelines - Argon2/bcrypt for passwords, secure JWT tokens.
"""

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import settings
from .database import get_db
from .models import TokenData, UserInDB

# Security: Using bcrypt for password hashing (OWASP recommended)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security: HTTPBearer for JWT token authentication
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash.
    
    Security: Using bcrypt timing-safe comparison.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password using bcrypt.
    
    Security: Bcrypt with automatic salt generation (OWASP A02 mitigation).
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create JWT access token.
    
    Security: Using HS256 algorithm, short expiration time.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode.update({"exp": expire})
    # Security: Using secret from environment (never hardcoded)
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db = Depends(get_db),
) -> UserInDB:
    """Get current authenticated user.
    
    Security: Validates JWT token, checks user exists and is active.
    Implements proper access control (OWASP A01 mitigation).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Security: Verify JWT token signature and expiration
        token = credentials.credentials
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        user_public_id: str | None = payload.get("sub")
        email: str | None = payload.get("email")
        
        if user_public_id is None or email is None:
            raise credentials_exception
        
        token_data = TokenData(user_public_id=user_public_id, email=email)
    except JWTError:
        raise credentials_exception
    
    # Security: Fetch user from database (validate user still exists)
    user_dict = await db.users.find_one(
        {
            "public_id": str(token_data.user_public_id),
            "deleted_at": None,  # Soft delete check
        }
    )
    
    if user_dict is None:
        raise credentials_exception
    
    user = UserInDB(**user_dict)
    
    # Security: Check user is active (OWASP A01 - access control)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )
    
    return user


async def authenticate_user(
    email: str, password: str, db
) -> UserInDB | None:
    """Authenticate user credentials.
    
    Security: Timing-safe password comparison, account lockout ready.
    """
    user_dict = await db.users.find_one(
        {"email": email, "deleted_at": None}
    )
    
    if user_dict is None:
        # Security: Return None instead of specific error to prevent user enumeration
        return None
    
    user = UserInDB(**user_dict)
    
    if not verify_password(password, user.hashed_password):
        # Security: Timing-safe comparison prevents timing attacks
        return None
    
    return user
