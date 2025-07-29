from sqlalchemy.orm import Session
from app.models import Notification, User, Todo
from app.schemas import NotificationCreate, NotificationResponse
from app.websocket_manager import websocket_manager
from datetime import datetime
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def create_notification(db: Session, notification_data: NotificationCreate) -> Notification:
        """Create a new notification in the database"""
        db_notification = Notification(
            user_id=notification_data.user_id,
            todo_id=notification_data.todo_id,
            actor_id=notification_data.actor_id,
            action_type=notification_data.action_type,
            message=notification_data.message
        )
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        
        logger.info(f"Created notification {db_notification.id} for user {notification_data.user_id}")
        return db_notification
    
    @staticmethod
    async def create_and_send_notification(
        db: Session, 
        notification_data: NotificationCreate
    ) -> Optional[Notification]:
        """Create notification and send it via WebSocket if user is online"""
        # Create notification in database
        notification = NotificationService.create_notification(db, notification_data)
        
        # Get additional data for the notification
        notification_response = NotificationService.get_notification_with_details(db, notification.id)
        
        if notification_response:
            # Try to send via WebSocket
            delivered = await websocket_manager.send_notification(
                notification_response.dict(), 
                notification_data.user_id
            )
            
            # Update delivery status if sent successfully
            if delivered:
                notification.delivered_at = datetime.utcnow()
                db.commit()
                logger.info(f"Notification {notification.id} delivered via WebSocket")
            else:
                logger.info(f"Notification {notification.id} stored for offline user")
        
        return notification
    
    @staticmethod
    def get_notification_with_details(db: Session, notification_id: int) -> Optional[NotificationResponse]:
        """Get notification with actor username and todo title"""
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            return None
        
        # Get actor username
        actor = db.query(User).filter(User.id == notification.actor_id).first()
        actor_username = actor.username if actor else "Unknown user"
        
        # Get todo title if todo_id exists
        todo_title = None
        if notification.todo_id:
            todo = db.query(Todo).filter(Todo.id == notification.todo_id).first()
            todo_title = todo.title if todo else "Deleted todo"
        
        return NotificationResponse(
            id=notification.id,
            user_id=notification.user_id,
            todo_id=notification.todo_id,
            actor_id=notification.actor_id,
            action_type=notification.action_type,
            message=notification.message,
            is_read=notification.is_read,
            delivered_at=notification.delivered_at,
            created_at=notification.created_at,
            actor_username=actor_username,
            todo_title=todo_title
        )
    
    @staticmethod
    def get_user_notifications(db: Session, user_id: int, limit: int = 50) -> List[NotificationResponse]:
        """Get user's notifications with details"""
        notifications = db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(Notification.created_at.desc()).limit(limit).all()
        
        result = []
        for notification in notifications:
            notification_response = NotificationService.get_notification_with_details(db, notification.id)
            if notification_response:
                result.append(notification_response)
        
        return result
    
    @staticmethod
    def mark_notification_as_read(db: Session, notification_id: int, user_id: int) -> bool:
        """Mark a notification as read (only if it belongs to the user)"""
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification:
            notification.is_read = True
            db.commit()
            logger.info(f"Notification {notification_id} marked as read by user {user_id}")
            return True
        
        return False
    
    @staticmethod
    def get_unread_count(db: Session, user_id: int) -> int:
        """Get count of unread notifications for a user"""
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()
    
    @staticmethod
    async def notify_todo_updated(db: Session, todo: Todo, actor_id: int, changes: dict):
        """Send notification when someone updates a public todo"""
        if not todo.is_public or not todo.user_id or todo.user_id == actor_id:
            return  # Don't notify for private todos, anonymous todos, or self-updates
        
        # Build change description
        change_parts = []
        if 'title' in changes:
            change_parts.append("title")
        if 'description' in changes:
            change_parts.append("description")
        if 'completed' in changes:
            if changes['completed']:
                change_parts.append("marked as completed")
            else:
                change_parts.append("marked as incomplete")
        
        changes_text = ", ".join(change_parts) if change_parts else "updated"
        
        # Get actor username
        actor = db.query(User).filter(User.id == actor_id).first()
        actor_name = actor.username if actor else "Someone"
        
        message = f"{actor_name} {changes_text} your public todo '{todo.title}'"
        
        await NotificationService.create_and_send_notification(
            db,
            NotificationCreate(
                user_id=todo.user_id,
                todo_id=todo.id,
                actor_id=actor_id,
                action_type="updated",
                message=message
            )
        )
    
    @staticmethod
    async def notify_todo_deleted(db: Session, todo: Todo, actor_id: int):
        """Send notification when someone deletes a public todo"""
        if not todo.is_public or not todo.user_id or todo.user_id == actor_id:
            return  # Don't notify for private todos, anonymous todos, or self-deletions
        
        # Get actor username
        actor = db.query(User).filter(User.id == actor_id).first()
        actor_name = actor.username if actor else "Someone"
        
        message = f"{actor_name} deleted your public todo '{todo.title}'"
        
        await NotificationService.create_and_send_notification(
            db,
            NotificationCreate(
                user_id=todo.user_id,
                todo_id=None,  # Todo is deleted, so no todo_id
                actor_id=actor_id,
                action_type="deleted",
                message=message
            )
        )

# Helper function for easier importing
async def send_notification(
    user_id: int,
    actor_id: int,
    todo_id: Optional[int],
    action_type: str,
    message: str,
    db: Session
):
    """Helper function to send notifications"""
    notification_data = NotificationCreate(
        user_id=user_id,
        todo_id=todo_id,
        actor_id=actor_id,
        action_type=action_type,
        message=message
    )
    
    return await NotificationService.create_and_send_notification(db, notification_data)