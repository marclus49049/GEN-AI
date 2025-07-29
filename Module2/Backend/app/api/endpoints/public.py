from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Todo, User
from app.schemas import PublicTodoCreate, PublicTodoResponse, TodoUpdate
from app.dependencies import get_current_user_optional

router = APIRouter()

@router.get("/", response_model=List[PublicTodoResponse])
async def get_public_todos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    todos = db.query(Todo).filter(Todo.is_public == True).offset(skip).limit(limit).all()
    # Map todos to response format with owner information
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
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        is_public=True,
        user_id=current_user.id if current_user else None
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
        "owner": current_user.username if current_user else None
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
    
    update_data = todo_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(todo, field, value)
    
    db.commit()
    db.refresh(todo)
    
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
    
    db.delete(todo)
    db.commit()
    return None