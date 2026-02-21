"""
MongoDB async client using Motor.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from settings import settings

_client: AsyncIOMotorClient = None


async def connect_db():
    """Initialize the MongoDB connection."""
    global _client
    _client = AsyncIOMotorClient(settings.MONGODB_URI)
    # Ping to verify connection
    await _client.admin.command("ping")
    print(f"✅ Connected to MongoDB at {settings.MONGODB_URI}")


async def close_db():
    """Close the MongoDB connection."""
    global _client
    if _client:
        _client.close()
        print("🔌 MongoDB connection closed")


def get_db():
    """Get the database instance."""
    return _client[settings.MONGODB_DB_NAME]


def get_collection(collection_name: str):
    """Get a collection from the database."""
    return get_db()[collection_name]
