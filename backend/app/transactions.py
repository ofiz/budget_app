"""Transaction management routes.

Security: All routes protected by authentication, using parameterized queries.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from .database import get_db
from .models import (
    BalanceResponse,
    TransactionCreate,
    TransactionInDB,
    TransactionResponse,
    TransactionType,
    UserInDB,
)
from .security import get_current_user

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
) -> TransactionResponse:
    """Create a new transaction (expense or income).
    
    Security: Access control - user can only create their own transactions (OWASP A01).
    """
    transaction = TransactionInDB(
        **transaction_data.model_dump(),
        user_public_id=current_user.public_id,
    )
    
    # Security: Using MongoDB's native insert (parameterized, prevents injection)
    await db.transactions.insert_one(transaction.model_dump(mode="json"))
    
    return TransactionResponse(
        public_id=transaction.public_id,
        type=transaction.type,
        category=transaction.category,
        amount=transaction.amount,
        description=transaction.description,
        date=transaction.date,
        created_at=transaction.created_at,
    )


@router.get("", response_model=list[TransactionResponse])
async def get_transactions(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
) -> list[TransactionResponse]:
    """Get user's transactions with pagination.
    
    Security: Access control - users can only see their own transactions (OWASP A01).
    Using parameterized queries to prevent injection (OWASP A03).
    """
    # Security: Filter by user_public_id (deny by default access control)
    cursor = db.transactions.find(
        {
            "user_public_id": str(current_user.public_id),
            "deleted_at": None,  # Soft delete filter
        }
    ).sort("date", -1).skip(skip).limit(limit)
    
    transactions = []
    async for doc in cursor:
        transactions.append(TransactionResponse(
            public_id=UUID(doc["public_id"]),
            type=TransactionType(doc["type"]),
            category=doc["category"],
            amount=doc["amount"],
            description=doc["description"],
            date=doc["date"],
            created_at=doc["created_at"],
        ))
    
    return transactions


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: UUID,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
) -> TransactionResponse:
    """Get a specific transaction.
    
    Security: Access control - verify transaction belongs to user (OWASP A01).
    """
    # Security: Parameterized query with user ownership check
    transaction_dict = await db.transactions.find_one(
        {
            "public_id": str(transaction_id),
            "user_public_id": str(current_user.public_id),
            "deleted_at": None,
        }
    )
    
    if transaction_dict is None:
        # Security: Generic 404 prevents information leakage
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    
    return TransactionResponse(
        public_id=UUID(transaction_dict["public_id"]),
        type=TransactionType(transaction_dict["type"]),
        category=transaction_dict["category"],
        amount=transaction_dict["amount"],
        description=transaction_dict["description"],
        date=transaction_dict["date"],
        created_at=transaction_dict["created_at"],
    )


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: UUID,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
) -> None:
    """Soft delete a transaction.
    
    Security: Access control - verify transaction belongs to user (OWASP A01).
    Using soft delete pattern.
    """
    from datetime import datetime, timezone
    
    # Security: Verify ownership before deletion
    result = await db.transactions.update_one(
        {
            "public_id": str(transaction_id),
            "user_public_id": str(current_user.public_id),
            "deleted_at": None,
        },
        {"$set": {"deleted_at": datetime.now(timezone.utc)}},
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )


@router.get("/balance/current", response_model=BalanceResponse)
async def get_balance(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
) -> BalanceResponse:
    """Calculate user's current balance.
    
    Security: Access control - only user's own transactions (OWASP A01).
    """
    # Security: Aggregation pipeline with user filter
    pipeline = [
        {
            "$match": {
                "user_public_id": str(current_user.public_id),
                "deleted_at": None,
            }
        },
        {
            "$group": {
                "_id": "$type",
                "total": {"$sum": "$amount"},
                "count": {"$sum": 1},
            }
        },
    ]
    
    results = await db.transactions.aggregate(pipeline).to_list(length=10)
    
    total_income = 0.0
    total_expenses = 0.0
    transaction_count = 0
    
    for result in results:
        if result["_id"] == TransactionType.INCOME.value:
            total_income = result["total"]
            transaction_count += result["count"]
        elif result["_id"] == TransactionType.EXPENSE.value:
            total_expenses = result["total"]
            transaction_count += result["count"]
    
    current_balance = total_income - total_expenses
    
    return BalanceResponse(
        total_income=total_income,
        total_expenses=total_expenses,
        current_balance=current_balance,
        transaction_count=transaction_count,
    )
