from beanie import Document, before_event, Replace, Update, PydanticObjectId
from datetime import datetime
from typing import Optional
from pydantic import Field
from app.models.user import User

class Task(Document):
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    owner: PydanticObjectId  # Store just the ObjectId, not a DBRef

    @before_event([Replace, Update])
    async def update_timestamp(self):
        self.updated_at = datetime.utcnow()

    class Settings:
        name = "tasks"