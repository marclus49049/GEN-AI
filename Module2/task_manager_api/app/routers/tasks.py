from fastapi import APIRouter, HTTPException, status
from typing import List
from beanie import PydanticObjectId
from pymongo.errors import PyMongoError
from bson.errors import InvalidId
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, UserInTask
from app.core.request import Request
from app.core.exceptions import (
    ResourceNotFoundException,
    DatabaseException,
    ServerException,
    NotAuthenticatedException,
    ValidationException
)
from bson import ObjectId

router = APIRouter()

@router.post("/", response_model=TaskResponse)
async def create_task(request: Request, task: TaskCreate):
    """Create a new task - user is automatically available from middleware"""
    if not hasattr(request.state, 'user') or request.state.user is None:
        raise NotAuthenticatedException("User not authenticated")
    
    try:
        db_task = Task(
            **task.dict(),
            owner=request.state.user.id
        )
        await db_task.create()
        # Manually populate owner data for response
        return TaskResponse(
            id=db_task.id,
            title=db_task.title,
            description=db_task.description,
            completed=db_task.completed,
            created_at=db_task.created_at,
            updated_at=db_task.updated_at,
            owner=UserInTask(
                id=request.state.user.id,
                username=request.state.user.username,
                email=request.state.user.email,
                is_active=request.state.user.is_active,
                created_at=request.state.user.created_at
            )
        )
    except PyMongoError as e:
        raise DatabaseException("Failed to create task: Database error")
    except Exception as e:
        raise ServerException(f"Failed to create task: {str(e)}")

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(request: Request, skip: int = 0, limit: int = 100):
    """Get all tasks for the authenticated user"""
    if not hasattr(request.state, 'user') or request.state.user is None:
        raise NotAuthenticatedException("User not authenticated")
    
    try:
        if skip < 0:
            raise ValidationException("Skip value must be non-negative", "skip")
        if limit < 1 or limit > 1000:
            raise ValidationException("Limit must be between 1 and 1000", "limit")
        
        # Query tasks by owner ID
        tasks = await Task.find(
            Task.owner == request.state.user.id
        ).skip(skip).limit(limit).to_list()
        
        # Manually populate owner data for response
        return [
            TaskResponse(
                id=task.id,
                title=task.title,
                description=task.description,
                completed=task.completed,
                created_at=task.created_at,
                updated_at=task.updated_at,
                owner=UserInTask(
                    id=request.state.user.id,
                    username=request.state.user.username,
                    email=request.state.user.email,
                    is_active=request.state.user.is_active,
                    created_at=request.state.user.created_at
                )
            ) for task in tasks
        ]
    except ValidationException:
        raise
    except PyMongoError as e:
        raise DatabaseException("Failed to retrieve tasks: Database error")
    except Exception as e:
        raise ServerException("Failed to retrieve tasks")

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(request: Request, task_id: str):
    """Get a specific task"""
    if not hasattr(request.state, 'user') or request.state.user is None:
        raise NotAuthenticatedException("User not authenticated")
    
    try:
        # Validate ObjectId format
        try:
            obj_id = PydanticObjectId(task_id)
        except InvalidId:
            raise ValidationException(f"Invalid task ID format: {task_id}", "task_id")
        
        # Query task by ID and owner ID
        task = await Task.find_one(
            Task.id == obj_id, 
            Task.owner == request.state.user.id
        )
        if not task:
            raise ResourceNotFoundException("Task", f"Task with ID {task_id} not found or access denied")
        
        # Manually populate owner data for response
        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            created_at=task.created_at,
            updated_at=task.updated_at,
            owner=UserInTask(
                id=request.state.user.id,
                username=request.state.user.username,
                email=request.state.user.email,
                is_active=request.state.user.is_active,
                created_at=request.state.user.created_at
            )
        )
    except (ValidationException, ResourceNotFoundException):
        raise
    except PyMongoError as e:
        raise DatabaseException("Failed to retrieve task: Database error")
    except Exception as e:
        raise ServerException("Failed to retrieve task")

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    request: Request,
    task_id: str,
    task_update: TaskUpdate
):
    """Update a task"""
    if not hasattr(request.state, 'user') or request.state.user is None:
        raise NotAuthenticatedException("User not authenticated")
    
    try:
        # Validate ObjectId format
        try:
            obj_id = PydanticObjectId(task_id)
        except InvalidId:
            raise ValidationException(f"Invalid task ID format: {task_id}", "task_id")
        
        # Query task by ID and owner ID
        task = await Task.find_one(
            Task.id == obj_id, 
            Task.owner == request.state.user.id
        )
        if not task:
            raise ResourceNotFoundException("Task", f"Task with ID {task_id} not found or access denied")
        
        update_data = task_update.dict(exclude_unset=True)
        if update_data:
            await task.update({"$set": update_data})
        
        # Manually populate owner data for response
        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            created_at=task.created_at,
            updated_at=task.updated_at,
            owner=UserInTask(
                id=request.state.user.id,
                username=request.state.user.username,
                email=request.state.user.email,
                is_active=request.state.user.is_active,
                created_at=request.state.user.created_at
            )
        )
    except (ValidationException, ResourceNotFoundException):
        raise
    except PyMongoError as e:
        raise DatabaseException("Failed to update task: Database error")
    except Exception as e:
        raise ServerException("Failed to update task")

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(request: Request, task_id: str):
    """Delete a task"""
    if not hasattr(request.state, 'user') or request.state.user is None:
        raise NotAuthenticatedException("User not authenticated")
    
    try:
        # Validate ObjectId format
        try:
            obj_id = PydanticObjectId(task_id)
        except InvalidId:
            raise ValidationException(f"Invalid task ID format: {task_id}", "task_id")
        
        # Query task by ID and owner ID
        task = await Task.find_one(Task.id == obj_id, Task.owner == request.state.user.id)
        if not task:
            raise ResourceNotFoundException("Task", f"Task with ID {task_id} not found or access denied")
        
        await task.delete()
        return None
    except (ValidationException, ResourceNotFoundException):
        raise
    except PyMongoError as e:
        raise DatabaseException("Failed to delete task: Database error")
    except Exception as e:
        raise ServerException("Failed to delete task")

@router.get("/stats/summary")
async def get_task_stats(request: Request):
    """Get task statistics for the current user"""
    if not hasattr(request.state, 'user') or request.state.user is None:
        raise NotAuthenticatedException("User not authenticated")
    
    try:
        # Query task counts by owner ID
        total = await Task.find(Task.owner == request.state.user.id).count()
        completed = await Task.find(Task.owner == request.state.user.id, Task.completed == True).count()
        pending = await Task.find(Task.owner == request.state.user.id, Task.completed == False).count()
        
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "user": request.state.user.username,
            "session_info": {
                "expires_at": request.state.session.expires_at if hasattr(request.state, 'session') else None,
                "ip_address": request.state.session.ip_address if hasattr(request.state, 'session') else None
            }
        }
    except PyMongoError as e:
        raise DatabaseException("Failed to retrieve task statistics: Database error")
    except Exception as e:
        raise ServerException("Failed to retrieve task statistics")