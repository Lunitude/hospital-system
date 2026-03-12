from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = "hospital_system"

client: AsyncIOMotorClient = None
db = None


async def connect_db():
    global client, db
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    # Create indexes
    await db.doctors.create_index("name")
    await db.reviews.create_index("doctor_id")
    # Ensure admin exists
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    existing = await db.admins.find_one({"username": "admin"})
    if not existing:
        await db.admins.insert_one({
            "username": "admin",
            "password": pwd_context.hash("admin123")
        })
    print("✅ Connected to MongoDB")


async def close_db():
    global client
    if client:
        client.close()


def get_db():
    return db
