from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.user import User
from app.models.task import Task
from app.models.session import Session
import os

# MongoDB connection URL
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "task_manager")

# MongoDB client
client = AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]

async def init_db():
    """Initialize database connection and Beanie ODM"""
    await init_beanie(
        database=database,
        document_models=[User, Task, Session]
    )