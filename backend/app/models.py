"""Data models for the Budget App.

Following backend-development skill: UUIDs for public IDs, soft deletes, timestamps.
Security: Pydantic validation prevents injection attacks.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Annotated
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field, field_validator


class TransactionType(str, Enum):
    """Transaction type enumeration."""

    INCOME = "income"
    EXPENSE = "expense"


class TransactionCategory(str, Enum):
    """Common expense/income categories."""

    # Income categories
    SALARY = "salary"
    FREELANCE = "freelance"
    INVESTMENT = "investment"
    OTHER_INCOME = "other_income"

    # Expense categories
    HOUSING = "housing"
    TRANSPORTATION = "transportation"
    FOOD = "food"
    UTILITIES = "utilities"
    HEALTHCARE = "healthcare"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    OTHER_EXPENSE = "other_expense"


class UserBase(BaseModel):
    """Base user model."""

    email: EmailStr
    full_name: str = Field(min_length=1, max_length=100)


class UserCreate(UserBase):
    """User registration model.
    
    Security: Password validation enforced.
    """

    password: str = Field(min_length=8, max_length=100)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength.
        
        Security: Enforce minimum complexity requirements.
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserInDB(UserBase):
    """User model as stored in database.
    
    Following backend-development skill: UUID public ID, timestamps, soft deletes.
    """

    public_id: UUID = Field(default_factory=uuid4)
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: datetime | None = None
    is_active: bool = True


class UserResponse(BaseModel):
    """User response model (public data only).
    
    Security: Never expose hashed_password or internal IDs.
    """

    public_id: UUID
    email: EmailStr
    full_name: str
    created_at: datetime


class TransactionBase(BaseModel):
    """Base transaction model."""

    type: TransactionType
    category: TransactionCategory
    amount: Annotated[float, Field(gt=0, description="Amount must be positive")]
    description: str = Field(max_length=500, default="")
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TransactionCreate(TransactionBase):
    """Transaction creation model."""

    pass


class TransactionInDB(TransactionBase):
    """Transaction model as stored in database.
    
    Following backend-development skill: UUID public ID, timestamps, soft deletes.
    """

    public_id: UUID = Field(default_factory=uuid4)
    user_public_id: UUID
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: datetime | None = None


class TransactionResponse(BaseModel):
    """Transaction response model."""

    public_id: UUID
    type: TransactionType
    category: TransactionCategory
    amount: float
    description: str
    date: datetime
    created_at: datetime


class BalanceResponse(BaseModel):
    """Balance response model."""

    total_income: float
    total_expenses: float
    current_balance: float
    transaction_count: int


class Token(BaseModel):
    """Token response model."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""

    user_public_id: UUID
    email: str
