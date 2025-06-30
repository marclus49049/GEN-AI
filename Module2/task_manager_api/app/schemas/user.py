from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from beanie import PydanticObjectId

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: PydanticObjectId = Field(alias="_id")
    is_active: bool
    created_at: datetime

    class Config:
        populate_by_name = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None