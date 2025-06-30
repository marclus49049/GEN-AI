from fastapi import APIRouter
from pymongo.errors import PyMongoError
from app.core.request import Request
from app.models.user import User
from app.models.task import Task
from app.core.exceptions import DatabaseException, ServerException

router = APIRouter()

@router.get("/stats")
async def get_public_stats():
    """Public endpoint - no authentication required"""
    try:
        total_users = await User.find_all().count()
        total_tasks = await Task.find_all().count()
        
        return {
            "total_users": total_users,
            "total_tasks": total_tasks,
            "api_version": "1.0.0",
            "status": "operational"
        }
    except PyMongoError as e:
        raise DatabaseException("Failed to retrieve statistics: Database connection error")
    except Exception as e:
        raise ServerException("Failed to retrieve public statistics")