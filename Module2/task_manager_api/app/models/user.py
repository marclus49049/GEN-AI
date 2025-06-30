from beanie import Document, Indexed
from pydantic import EmailStr, Field
from datetime import datetime
from typing import Optional

class User(Document):
    username: Indexed(str, unique=True)
    email: Indexed(EmailStr, unique=True)
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"