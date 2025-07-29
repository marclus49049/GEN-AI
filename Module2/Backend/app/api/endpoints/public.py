"""
Public todo endpoints with cross-user collaboration and notification system.

Key features:
- Public todos visible to all users (authenticated or not)
- Any authenticated user can modify/complete any public todo
- Notification system alerts todo owners when others interact with their todos
- Action types: 'updated', 'completed', 'uncompleted', 'deleted'

Business logic:
- GET /: No authentication required, shows all public todos
- POST, PUT, DELETE: Authentication required to prevent anonymous abuse
- Notifications only sent when actor != owner (users don't get notified of own actions)
- Custom response format includes owner username for better UX
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Todo, User
from app.schemas import PublicTodoCreate, PublicTodoResponse, TodoUpdate
from app.dependencies import get_current_user_optional, get_current_user
from app.notification_service import send_notification

router = APIRouter()

@router.get("/", response_model=List[PublicTodoResponse])
async def get_public_todos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all public todos - no authentication required.
    
    Includes owner username for better user experience. This allows
    users to see who created each todo before deciding to interact.
    Manual response mapping is used instead of Pydantic to include
    the computed owner field.
    """
    todos = db.query(Todo).filter(Todo.is_public == True).offset(skip).limit(limit).all()
    
    # Custom response mapping to include owner username
    result = []
    for todo in todos:
        todo_dict = {
            "id": todo.id,
            "title": todo.title,
            "description": todo.description,
            "completed": todo.completed,
            "is_public": True,
            "created_at": todo.created_at,
            "user_id": todo.user_id,
            "owner": todo.owner.username if todo.owner else None
        }
        result.append(todo_dict)
    return result

@router.post("/", response_model=PublicTodoResponse)
async def create_public_todo(
    todo: PublicTodoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        is_public=True,
        user_id=current_user.id
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    
    return {
        "id": db_todo.id,
        "title": db_todo.title,
        "description": db_todo.description,
        "completed": db_todo.completed,
        "is_public": True,
        "created_at": db_todo.created_at,
        "user_id": db_todo.user_id,
        "owner": current_user.username
    }

@router.get("/{todo_id}", response_model=PublicTodoResponse)
async def get_public_todo(
    todo_id: int,
    db: Session = Depends(get_db)
):
    todo = db.query(Todo).filter(
        Todo.id == todo_id,
        Todo.is_public == True
    ).first()
    
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public todo not found"
        )
    
    return {
        "id": todo.id,
        "title": todo.title,
        "description": todo.description,
        "completed": todo.completed,
        "is_public": True,
        "created_at": todo.created_at,
        "user_id": todo.user_id,
        "owner": todo.owner.username if todo.owner else None
    }

@router.put("/{todo_id}", response_model=PublicTodoResponse)
async def update_public_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a public todo with intelligent notification system.
    
    Notification logic:
    - Stores original values to detect what changed
    - Determines action_type: 'updated', 'completed', or 'uncompleted'
    - Only notifies if actor != owner (users don't get notified of own actions)
    - Creates contextual messages based on the type of change
    
    This enables collaborative todo management while keeping owners informed.
    """
    todo = db.query(Todo).filter(
        Todo.id == todo_id,
        Todo.is_public == True
    ).first()
    
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public todo not found"
        )
    
    # Store original values to detect changes for notifications
    original_title = todo.title
    original_completed = todo.completed
    
    # Apply partial update
    update_data = todo_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(todo, field, value)
    
    db.commit()
    db.refresh(todo)
    
    # Notification system: only notify if someone else modified the todo
    if todo.user_id != current_user.id:
        # Determine specific action type for better notification context
        action_type = "updated"
        if "completed" in update_data and update_data["completed"] != original_completed:
            action_type = "completed" if update_data["completed"] else "uncompleted"
        
        # Create contextual notification message
        if action_type == "completed":
            message = f"{current_user.username} marked your public todo '{todo.title}' as completed"
        elif action_type == "uncompleted":
            message = f"{current_user.username} marked your public todo '{todo.title}' as incomplete"
        else:
            message = f"{current_user.username} updated your public todo '{todo.title}'"
        
        # Send notification via WebSocket and store in database
        await send_notification(
            user_id=todo.user_id,
            actor_id=current_user.id,
            todo_id=todo.id,
            action_type=action_type,
            message=message,
            db=db
        )
    
    return {
        "id": todo.id,
        "title": todo.title,
        "description": todo.description,
        "completed": todo.completed,
        "is_public": True,
        "created_at": todo.created_at,
        "user_id": todo.user_id,
        "owner": todo.owner.username if todo.owner else None
    }

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_public_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a public todo with pre-deletion notification.
    
    Critical timing: Notification must be sent BEFORE deletion because:
    1. We need todo data (title, owner_id) for the notification message
    2. The todo_id becomes invalid after deletion
    3. The notification record references the deleted todo
    
    This ensures owners are always notified when their public todos are deleted.
    """
    todo = db.query(Todo).filter(
        Todo.id == todo_id,
        Todo.is_public == True
    ).first()
    
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public todo not found"
        )
    
    # Extract data needed for notification before deletion
    todo_title = todo.title
    todo_owner_id = todo.user_id
    
    # Send notification before deletion (if someone else is deleting)
    if todo.user_id != current_user.id:
        message = f"{current_user.username} deleted your public todo '{todo_title}'"
        
        await send_notification(
            user_id=todo_owner_id,
            actor_id=current_user.id,
            todo_id=todo.id,  # Still valid since we haven't deleted yet
            action_type="deleted",
            message=message,
            db=db
        )
    
    # Now safe to delete the todo
    db.delete(todo)
    db.commit()
    return None