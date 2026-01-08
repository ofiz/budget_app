"""Database connection and setup.

Security: Uses connection pooling and proper connection handling.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure

from .config import settings


class Database:
    """Database connection manager."""

    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None

    async def connect(self) -> None:
        """Establish database connection.
        
        Security: Uses parameterized connection string from environment.
        """
        try:
            self.client = AsyncIOMotorClient(settings.mongodb_url)
            self.db = self.client[settings.database_name]
            # Verify connection
            await self.client.admin.command("ping")
            print(f"✅ Connected to MongoDB: {settings.database_name}")
        except ConnectionFailure as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise

    async def disconnect(self) -> None:
        """Close database connection."""
        if self.client:
            self.client.close()
            print("✅ Disconnected from MongoDB")

    async def get_database(self) -> AsyncIOMotorDatabase:
        """Get database instance."""
        if self.db is None:
            await self.connect()
        return self.db  # type: ignore


# Global database instance
db = Database()


async def get_db() -> AsyncIOMotorDatabase:
    """Dependency for FastAPI routes."""
    return await db.get_database()
