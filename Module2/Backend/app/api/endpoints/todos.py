"""
Private todo endpoints with strict ownership validation.

Security model:
- All endpoints require JWT authentication via get_current_user dependency
- Users can only access/modify todos they own (todo.user_id == current_user.id)
- Supports both private (is_public=False) and public (is_public=True) todos
- Public todos created here are visible in public endpoints but ownership is maintained

Ownership validation ensures users cannot access or modify other users' todos,
even if they know the todo ID.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Todo, User
from app.schemas import TodoCreate, TodoResponse, TodoUpdate
from app.dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[TodoResponse])
async def get_user_todos(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all todos owned by the authenticated user.
    
    Returns both private and public todos created by the user.
    Other users' todos are never included, ensuring data isolation.
    Supports pagination via skip/limit parameters.
    """
    # Ownership filter: only todos belonging to current user
    todos = db.query(Todo).filter(
        Todo.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return todos

@router.post("/", response_model=TodoResponse)
async def create_todo(
    todo: TodoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        is_public=todo.is_public,
        user_id=current_user.id
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific todo by ID, with ownership validation.
    
    Critical security: Uses compound filter (id AND user_id) to prevent
    users from accessing other users' todos even if they know the ID.
    Returns 404 for both non-existent todos and unauthorized access.
    """
    todo = db.query(Todo).filter(
        Todo.id == todo_id,
        Todo.user_id == current_user.id  # Ownership validation
    ).first()
    
    if todo is None:
        # Don't distinguish between "doesn't exist" and "not authorized" for security
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    return todo

@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a todo with ownership validation.
    
    Uses partial update pattern: only fields provided in todo_update are modified.
    The exclude_unset=True ensures None values don't overwrite existing data.
    All the same security principles as get_todo apply here.
    """
    todo = db.query(Todo).filter(
        Todo.id == todo_id,
        Todo.user_id == current_user.id  # Ownership validation
    ).first()
    
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    
    # Partial update: only modify provided fields
    update_data = todo_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(todo, field, value)
    
    db.commit()
    db.refresh(todo)
    return todo

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a todo with ownership validation.
    
    Returns 204 No Content on successful deletion per REST conventions.
    Same ownership validation as other endpoints prevents unauthorized deletion.
    Note: If this was a public todo, it will also be removed from public view.
    """
    todo = db.query(Todo).filter(
        Todo.id == todo_id,
        Todo.user_id == current_user.id  # Ownership validation
    ).first()
    
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    
    db.delete(todo)
    db.commit()
    return None