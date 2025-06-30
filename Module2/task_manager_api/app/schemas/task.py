from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, Union
from beanie import PydanticObjectId

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class UserInTask(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    username: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        populate_by_name = True

class TaskResponse(TaskBase):
    id: PydanticObjectId = Field(alias="_id")
    completed: bool
    created_at: datetime
    updated_at: datetime
    owner: UserInTask  # Always populated with user data

    class Config:
        populate_by_name = True
        
class TaskInDB(TaskBase):
    id: PydanticObjectId = Field(alias="_id")
    completed: bool
    created_at: datetime
    updated_at: datetime
    owner: PydanticObjectId  # Just the ID when not populated

    class Config:
        populate_by_name = True