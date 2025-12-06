# utils/websocket_bridge.py
"""
WebSocket Bridge - Connects REST API to WebSocket consumers
This utility allows REST API views to send messages to WebSocket clients
"""

import json
import asyncio
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class WebSocketBridge:
    """Bridge class to send messages from REST API to WebSocket clients"""
    
    def __init__(self):
        self.channel_layer = get_channel_layer()
    
    def send_to_user(self, username, message_type, data):
        """
        Send message to a specific user's WebSocket connection
        
        Args:
            username (str): Target user's username
            message_type (str): Type of message (e.g., 'notification', 'update', 'command')
            data (dict): Message data to send
        """
        if not self.channel_layer:
            print("Warning: No channel layer configured. WebSocket message not sent.")
            return False
            
        try:
            async_to_sync(self.channel_layer.group_send)(
                f"user_{username}",  # Group name for the user
                {
                    "type": "send_message_to_client",
                    "message_type": message_type,
                    "data": data
                }
            )
            print(f"Message sent to user {username}: {message_type}")
            return True
        except Exception as e:
            print(f"Failed to send WebSocket message: {e}")
            return False
    
    def send_to_room(self, room_name, message_type, data):
        """
        Send message to all clients in a specific room
        
        Args:
            room_name (str): Target room name
            message_type (str): Type of message
            data (dict): Message data to send
        """
        if not self.channel_layer:
            print("Warning: No channel layer configured. WebSocket message not sent.")
            return False
            
        try:
            async_to_sync(self.channel_layer.group_send)(
                f"room_{room_name}",
                {
                    "type": "send_message_to_client",
                    "message_type": message_type,
                    "data": data
                }
            )
            print(f"Message sent to room {room_name}: {message_type}")
            return True
        except Exception as e:
            print(f"Failed to send WebSocket message: {e}")
            return False
    
    def broadcast_to_all(self, message_type, data):
        """
        Broadcast message to all connected WebSocket clients
        
        Args:
            message_type (str): Type of message
            data (dict): Message data to send
        """
        if not self.channel_layer:
            print("Warning: No channel layer configured. WebSocket message not sent.")
            return False
            
        try:
            async_to_sync(self.channel_layer.group_send)(
                "broadcast_group",
                {
                    "type": "send_message_to_client",
                    "message_type": message_type,
                    "data": data
                }
            )
            print(f"Broadcast message sent: {message_type}")
            return True
        except Exception as e:
            print(f"Failed to broadcast WebSocket message: {e}")
            return False

    def send_to_agent(self, agent_id, command, data=None):
        """
        Send command to a specific agent
        
        Args:
            agent_id (str): Target agent ID
            command (str): Command to execute
            data (dict): Additional command data
        """
        if not self.channel_layer:
            print("Warning: No channel layer configured. Agent command not sent.")
            return False
            
        message_data = {
            "command": command,
            "agent_id": agent_id,
            "data": data or {}
        }
        
        try:
            async_to_sync(self.channel_layer.group_send)(
                f"agent_{agent_id}",
                {
                    "type": "send_agent_command",
                    "command_data": message_data
                }
            )
            print(f"Command sent to agent {agent_id}: {command}")
            return True
        except Exception as e:
            print(f"Failed to send agent command: {e}")
            return False


# Global instance for easy import
websocket_bridge = WebSocketBridge()