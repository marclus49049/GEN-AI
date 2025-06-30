from beanie import Document, Link, Indexed
from datetime import datetime
from pydantic import Field
from app.models.user import User

class Session(Document):
    session_id: Indexed(str, unique=True)
    user: Link[User]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    ip_address: str
    user_agent: str

    class Settings:
        name = "sessions"
        
    @classmethod
    async def cleanup_expired(cls):
        """Delete all expired sessions"""
        await cls.find(cls.expires_at < datetime.utcnow()).delete()