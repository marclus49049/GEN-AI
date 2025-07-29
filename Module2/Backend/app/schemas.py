from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# User schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

# Todo schemas
class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None

class TodoCreate(TodoBase):
    is_public: bool = False

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class TodoResponse(TodoBase):
    id: int
    completed: bool
    is_public: bool
    user_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class PublicTodoCreate(TodoBase):
    pass

class PublicTodoResponse(TodoBase):
    id: int
    completed: bool
    is_public: bool = True  # Always true for public todos
    created_at: datetime
    user_id: Optional[int] = None
    owner: Optional[str] = None  # username of the owner
    
    class Config:
        from_attributes = True

# Notification schemas
class NotificationBase(BaseModel):
    message: str
    action_type: str

class NotificationCreate(NotificationBase):
    user_id: int
    todo_id: Optional[int] = None
    actor_id: int

class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    todo_id: Optional[int]
    actor_id: int
    is_read: bool
    delivered_at: Optional[datetime]
    created_at: datetime
    actor_username: Optional[str] = None  # username of the person who did the action
    todo_title: Optional[str] = None      # title of the related todo
    
    class Config:
        from_attributes = True

class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None