from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json
import logging
from app.database import get_db
from app.models import User
from app.security import verify_token
from app.websocket_manager import websocket_manager

router = APIRouter()
logger = logging.getLogger(__name__)

async def get_user_from_token(token: str, db: Session) -> User:
    """Verify WebSocket token and get user"""
    try:
        token_data = verify_token(token)
        user = db.query(User).filter(User.id == token_data["user_id"]).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@router.websocket("/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time notifications"""
    try:
        # Verify token and get user
        user = await get_user_from_token(token, db)
        user_id = user.id
        
        # Connect to WebSocket manager
        await websocket_manager.connect(websocket, user_id)
        
        # Send connection acknowledgment
        await websocket.send_text(json.dumps({
            "type": "connection_ack",
            "data": {
                "user_id": user_id,
                "username": user.username,
                "message": "Connected to notifications"
            }
        }))
        
        logger.info(f"WebSocket connected for user {user_id} ({user.username})")
        
        try:
            while True:
                # Listen for messages from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "mark_read":
                    notification_id = message.get("notification_id")
                    if notification_id:
                        # TODO: Update notification as read in database
                        logger.info(f"User {user_id} marked notification {notification_id} as read")
                        
                        # Send acknowledgment
                        await websocket.send_text(json.dumps({
                            "type": "mark_read_ack",
                            "data": {
                                "notification_id": notification_id,
                                "success": True
                            }
                        }))
                
                elif message.get("type") == "ping":
                    # Respond to ping with pong
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "data": {"timestamp": message.get("timestamp")}
                    }))
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for user {user_id}")
        
    except HTTPException as e:
        # Authentication failed
        logger.error(f"WebSocket authentication failed: {e.detail}")
        await websocket.close(code=1008, reason="Authentication failed")
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=1011, reason="Internal server error")
    
    finally:
        # Clean up connection
        if 'user_id' in locals():
            websocket_manager.disconnect(websocket, user_id)