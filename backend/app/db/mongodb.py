from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db = MongoDB()

async def connect_to_mongo():
    """Connect to MongoDB."""
    db.client = AsyncIOMotorClient(settings.MONGO_CONNECTION_STRING)
    db.db = db.client[settings.MONGO_DB]
    print(f"Connected to MongoDB at {settings.MONGO_HOST}:{settings.MONGO_PORT}")

async def close_mongo_connection():
    """Close MongoDB connection."""
    if db.client:
        db.client.close()
        print("Closed MongoDB connection")
