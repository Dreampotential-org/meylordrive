# ashe/websocket_views.py
"""
Enhanced REST API views with WebSocket integration
These views can send messages to WebSocket clients
"""

import json
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from utils.websocket_bridge import websocket_bridge
from .models import Session, SessionPoint, Device, Dot


@api_view(['POST'])
def send_notification_to_user(request):
    """
    Send notification to specific user via WebSocket
    
    POST /api/notify-user/
    {
        "username": "user123",
        "title": "New Update",
        "message": "Your data has been updated",
        "data": {"key": "value"}
    }
    """
    try:
        username = request.data.get('username')
        title = request.data.get('title', 'Notification')
        message = request.data.get('message', '')
        extra_data = request.data.get('data', {})
        
        if not username:
            return Response(
                {'error': 'Username is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Send notification via WebSocket
        notification_data = {
            'title': title,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'extra_data': extra_data
        }
        
        success = websocket_bridge.send_to_user(
            username=username,
            message_type='notification',
            data=notification_data
        )
        
        if success:
            return Response({
                'status': 'success',
                'message': f'Notification sent to {username}',
                'data': notification_data
            })
        else:
            return Response({
                'status': 'warning',
                'message': 'WebSocket not configured or user not connected',
                'data': notification_data
            }, status=status.HTTP_202_ACCEPTED)
            
    except Exception as e:
        return Response(
            {'error': f'Failed to send notification: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def send_agent_command(request):
    """
    Send command to specific agent via WebSocket
    
    POST /api/agent-command/
    {
        "agent_id": "agent123",
        "command": "restart",
        "data": {"param1": "value1"}
    }
    """
    try:
        agent_id = request.data.get('agent_id')
        command = request.data.get('command')
        command_data = request.data.get('data', {})
        
        if not agent_id or not command:
            return Response(
                {'error': 'Both agent_id and command are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success = websocket_bridge.send_to_agent(
            agent_id=agent_id,
            command=command,
            data=command_data
        )
        
        if success:
            return Response({
                'status': 'success',
                'message': f'Command "{command}" sent to agent {agent_id}',
                'agent_id': agent_id,
                'command': command,
                'data': command_data
            })
        else:
            return Response({
                'status': 'warning',
                'message': 'WebSocket not configured or agent not connected'
            }, status=status.HTTP_202_ACCEPTED)
            
    except Exception as e:
        return Response(
            {'error': f'Failed to send command: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def broadcast_system_message(request):
    """
    Broadcast message to all connected WebSocket clients
    
    POST /api/broadcast/
    {
        "message": "System maintenance in 5 minutes",
        "type": "system_alert",
        "data": {"severity": "warning"}
    }
    """
    try:
        message = request.data.get('message')
        message_type = request.data.get('type', 'system_message')
        extra_data = request.data.get('data', {})
        
        if not message:
            return Response(
                {'error': 'Message is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        broadcast_data = {
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'extra_data': extra_data
        }
        
        success = websocket_bridge.broadcast_to_all(
            message_type=message_type,
            data=broadcast_data
        )
        
        if success:
            return Response({
                'status': 'success',
                'message': 'Broadcast sent to all connected clients',
                'broadcast_type': message_type,
                'data': broadcast_data
            })
        else:
            return Response({
                'status': 'warning',
                'message': 'WebSocket not configured'
            }, status=status.HTTP_202_ACCEPTED)
            
    except Exception as e:
        return Response(
            {'error': f'Failed to broadcast: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def enhanced_dot_create(request):
    """
    Enhanced dot creation with WebSocket notification
    
    This is your existing dot creation with added WebSocket notification
    """
    try:
        # Original dot creation logic
        dot = Dot()
        dot.latitude = request.data.get("latitude")
        dot.longitude = request.data.get("longitude")
        dot.save()
        
        # Send WebSocket notification about new dot
        dot_data = {
            'dot_id': dot.id,
            'latitude': dot.latitude,
            'longitude': dot.longitude,
            'created_at': datetime.now().isoformat()
        }
        
        # Broadcast to all clients about new dot
        websocket_bridge.broadcast_to_all(
            message_type='new_dot_created',
            data=dot_data
        )
        
        # If you want to notify specific user
        username = request.data.get('notify_user')
        if username:
            websocket_bridge.send_to_user(
                username=username,
                message_type='dot_created_notification',
                data={
                    'message': f'New dot created with ID {dot.id}',
                    'dot_data': dot_data
                }
            )
        
        return Response({
            'id': dot.id,
            'status': 'success',
            'websocket_notifications_sent': True,
            'data': dot_data
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to create dot: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def websocket_status(request):
    """
    Check WebSocket bridge status
    
    GET /api/websocket-status/
    """
    try:
        # Test if channel layer is working
        bridge = websocket_bridge
        channel_layer_available = bridge.channel_layer is not None
        
        return Response({
            'websocket_bridge_status': 'active',
            'channel_layer_available': channel_layer_available,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return Response({
            'websocket_bridge_status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def test_websocket_connection(request):
    """
    Test WebSocket connection by sending a test message
    
    POST /api/test-websocket/
    {
        "target_type": "user|broadcast|agent",
        "target": "username_or_agent_id",
        "test_message": "Hello WebSocket!"
    }
    """
    try:
        target_type = request.data.get('target_type', 'broadcast')
        target = request.data.get('target', '')
        test_message = request.data.get('test_message', 'Test message from REST API')
        
        test_data = {
            'message': test_message,
            'test': True,
            'timestamp': datetime.now().isoformat()
        }
        
        success = False
        
        if target_type == 'user' and target:
            success = websocket_bridge.send_to_user(
                username=target,
                message_type='test_message',
                data=test_data
            )
        elif target_type == 'agent' and target:
            success = websocket_bridge.send_to_agent(
                agent_id=target,
                command='test',
                data=test_data
            )
        elif target_type == 'broadcast':
            success = websocket_bridge.broadcast_to_all(
                message_type='test_message',
                data=test_data
            )
        
        return Response({
            'test_status': 'success' if success else 'failed',
            'target_type': target_type,
            'target': target,
            'message_sent': success,
            'test_data': test_data
        })
        
    except Exception as e:
        return Response({
            'test_status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)