from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    """
    User model representing authenticated users in the system.
    
    Users can create both private todos (visible only to them) and public todos
    (visible to all users). The notification system tracks when other users
    interact with their public todos.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # One-to-many: A user can have many todos
    todos = relationship("Todo", back_populates="owner")
    
    # One-to-many: A user can receive many notifications
    notifications = relationship("Notification", foreign_keys="Notification.user_id", back_populates="recipient")
    
    # One-to-many: A user can create notifications by acting on other users' todos
    created_notifications = relationship("Notification", foreign_keys="Notification.actor_id", back_populates="actor")

class Todo(Base):
    """
    Todo model supporting both private and public todos.
    
    Business logic:
    - is_public=False: Private todos visible only to the owner
    - is_public=True: Public todos visible to all users, others can modify/complete
    - user_id can be null for anonymous public todos (though current API requires auth)
    - updated_at automatically updates on any field changes
    """
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for anonymous todos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Many-to-one: Many todos belong to one user
    owner = relationship("User", back_populates="todos")

class Notification(Base):
    """
    Notification system for tracking interactions with public todos.
    
    Design rationale:
    - Only public todos generate notifications when modified by other users
    - Three-entity relationship: recipient (todo owner), actor (who acted), and todo
    - delivered_at tracks WebSocket delivery for real-time notifications
    - action_type enables different notification behaviors (updated/completed/deleted)
    
    Notification flow:
    1. User A creates public todo
    2. User B modifies/completes User A's public todo  
    3. Notification created with recipient=User A, actor=User B
    4. WebSocket delivers notification to User A if online
    """
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # recipient
    todo_id = Column(Integer, ForeignKey("todos.id"), nullable=True)   # related todo (null if deleted)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False) # who performed the action
    action_type = Column(String, nullable=False)  # 'updated', 'deleted', 'completed', 'uncompleted'
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    delivered_at = Column(DateTime(timezone=True), nullable=True)  # WebSocket delivery timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Many-to-one relationships with explicit foreign_keys to handle multiple User FKs
    recipient = relationship("User", foreign_keys=[user_id], back_populates="notifications")
    actor = relationship("User", foreign_keys=[actor_id], back_populates="created_notifications")
    todo = relationship("Todo")  # May be null if todo was deleted