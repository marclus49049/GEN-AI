from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User
from app.schemas import NotificationResponse, NotificationUpdate
from app.dependencies import get_current_user
from app.notification_service import NotificationService
from app.websocket_manager import websocket_manager

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
async def get_user_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """Get user's notifications"""
    notifications = NotificationService.get_user_notifications(db, current_user.id, limit)
    return notifications

@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications"""
    count = NotificationService.get_unread_count(db, current_user.id)
    return {"unread_count": count}

@router.put("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a notification as read"""
    success = NotificationService.mark_notification_as_read(db, notification_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    # Get updated notification data
    updated_notification = NotificationService.get_notification_with_details(db, notification_id)
    
    # Send WebSocket notification for real-time update
    if updated_notification:
        await websocket_manager.send_personal_message({
            "type": "notification_marked_read",
            "data": {
                "notification_id": notification_id,
                "notification": updated_notification.dict()
            }
        }, current_user.id)
    
    return {"success": True, "message": "Notification marked as read"}

@router.put("/mark-all-read")
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all user's notifications as read"""
    from app.models import Notification
    
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).all()
    
    # Store notification IDs before updating
    notification_ids = [n.id for n in notifications]
    
    count = 0
    for notification in notifications:
        notification.is_read = True
        count += 1
    
    db.commit()
    
    # Send WebSocket notification for real-time update
    await websocket_manager.send_personal_message({
        "type": "notifications_all_marked_read",
        "data": {
            "marked_count": count,
            "notification_ids": notification_ids,
            "new_unread_count": 0
        }
    }, current_user.id)
    
    return {"success": True, "message": f"Marked {count} notifications as read"}