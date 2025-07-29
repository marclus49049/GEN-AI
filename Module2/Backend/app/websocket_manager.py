from typing import Dict, List, Optional
from fastapi import WebSocket
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class WebSocketManager:
    def __init__(self):
        # Dictionary to store active connections by user_id
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept a new WebSocket connection for a user"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        logger.info(f"User {user_id} connected. Total connections: {len(self.active_connections[user_id])}")
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Remove a WebSocket connection for a user"""
        if user_id in self.active_connections:
            try:
                self.active_connections[user_id].remove(websocket)
                logger.info(f"User {user_id} disconnected. Remaining connections: {len(self.active_connections[user_id])}")
                
                # Clean up empty connection lists
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            except ValueError:
                # Connection not in list (already removed)
                pass
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Send a message to all connections of a specific user"""
        if user_id not in self.active_connections:
            logger.info(f"No active connections for user {user_id}")
            return False
        
        message_json = json.dumps(message, cls=DateTimeEncoder)
        disconnected_connections = []
        
        for connection in self.active_connections[user_id]:
            try:
                await connection.send_text(message_json)
                logger.info(f"Message sent to user {user_id}")
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {e}")
                disconnected_connections.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected_connections:
            self.disconnect(connection, user_id)
        
        return len(disconnected_connections) < len(self.active_connections.get(user_id, []))
    
    async def broadcast_to_all(self, message: dict):
        """Send a message to all connected users"""
        message_json = json.dumps(message, cls=DateTimeEncoder)
        
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_text(message_json)
                except Exception as e:
                    logger.error(f"Error broadcasting to user {user_id}: {e}")
    
    def get_connected_users(self) -> List[int]:
        """Get list of currently connected user IDs"""
        return list(self.active_connections.keys())
    
    def is_user_connected(self, user_id: int) -> bool:
        """Check if a user has any active connections"""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0
    
    async def send_notification(self, notification_data: dict, user_id: int):
        """Send a notification to a specific user"""
        message = {
            "type": "new_notification",
            "data": notification_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        delivered = await self.send_personal_message(message, user_id)
        return delivered

# Global WebSocket manager instance
websocket_manager = WebSocketManager()