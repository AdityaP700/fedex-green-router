import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import sys

print("Current working directory:", os.getcwd())
print("Python path:", sys.path)

# Load from .env.temp instead of .env
env_path = os.path.join(os.getcwd(), '.env.temp')
print("Looking for .env.temp at:", env_path)
load_dotenv(env_path)

MONGODB_URI = os.getenv("MONGODB_URI")
print("MONGODB_URI:", MONGODB_URI)

if not MONGODB_URI:
    raise ValueError("MONGODB_URI environment variable is not set")

client = AsyncIOMotorClient(MONGODB_URI)

# Get database
db = client.fedex_green_router

async def init_db():
    """Initialize the database by creating necessary collections."""
    collections = [
        "api_keys",
        "vehicles",
        "metrics",
        "errors",
        "routes",
        "user_preferences",
        "maintenance_records"
    ]
    
    existing_collections = await db.list_collection_names()
    
    for collection in collections:
        if collection not in existing_collections:
            await db.create_collection(collection)

# Add the init_db method to the db object
db.init_db = init_db