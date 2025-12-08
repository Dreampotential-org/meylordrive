# WebSocket REST API Integration

This integration allows you to send WebSocket messages from REST API endpoints in Django. Based on your client's requirements, this implements:

1. **Sending WebSocket messages from REST API** (from `ashe/views.py`)
2. **Targeting specific connected sockets** (not broadcasting to all)
3. **Continuous server push** to WebSocket clients
4. **Python script examples** for testing

## Features Implemented

### 1. Basic WebSocket Messaging from REST API
- **Endpoint**: `POST /ashe/send-websocket/`
- **Purpose**: Send messages to WebSocket clients from REST API calls

### 2. Location Updates via WebSocket
- **Endpoint**: `POST /ashe/push-location/`
- **Purpose**: Push location updates to connected WebSocket clients

### 3. Continuous Live Push Service
- **Start**: `POST /ashe/start-live-push/`
- **Stop**: `POST /ashe/stop-live-push/`
- **Purpose**: Background service that continuously pushes data to WebSocket

## How to Use

### 1. Start Your Django Server
```bash
cd meylordrive/codes
python manage.py runserver
```

### 2. Start WebSocket Server (Daphne)
```bash
# In another terminal
cd meylordrive
daphne -p 8022 project.asgi:application
```

### 3. Get API Token
First, you need to get an authentication token:
```python
# In Django shell: python manage.py shell
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

user = User.objects.first()  # or create a user
token, created = Token.objects.get_or_create(user=user)
print(f"Your token: {token.key}")
```

### 4. Test with Python Script
```bash
# Edit the script to add your token
python websocket_rest_example.py
```

### 5. Test with HTML Interface
1. Open `websocket_test.html` in your browser
2. Enter your API token
3. Connect to WebSocket
4. Send messages via REST API

## API Endpoints

### Send WebSocket Message
```bash
curl -X POST http://localhost:8000/ashe/send-websocket/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "room": "general",
    "message": "Hello from REST API!",
    "target_user": null,
    "data": {"source": "curl"}
  }'
```

### Push Location Update
```bash
curl -X POST http://localhost:8000/ashe/push-location/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "latitude": 40.7128,
    "longitude": -74.0060,
    "device_id": "device_001"
  }'
```

### Start Continuous Push
```bash
curl -X POST http://localhost:8000/ashe/start-live-push/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "room": "live_updates",
    "interval": 5
  }'
```

### Stop Continuous Push
```bash
curl -X POST http://localhost:8000/ashe/stop-live-push/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN"
```

## WebSocket Connection

Connect to WebSocket at: `ws://localhost:8022/ws/test/{room_name}/`

Example JavaScript:
```javascript
const ws = new WebSocket('ws://localhost:8022/ws/test/general/');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data.message);
};
```

## Message Types

The WebSocket receives different types of messages:

### API Messages
```json
{
  "message": {
    "content": "Hello from REST API!",
    "sender": "username",
    "sender_id": 1,
    "type": "api_message",
    "timestamp": "2025-12-08T10:30:00"
  }
}
```

### Location Updates
```json
{
  "message": {
    "content": "Location update from device device_001",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "device_id": "device_001",
    "type": "location_update",
    "timestamp": "2025-12-08T10:30:00"
  }
}
```

### Live Statistics
```json
{
  "message": {
    "content": "Live system update",
    "type": "live_stats",
    "stats": {
      "devices": 5,
      "sessions": 12,
      "dots": 8,
      "timestamp": "2025-12-08T10:30:00",
      "formatted_time": "10:30:00"
    }
  }
}
```

## Client Requirements Implementation

✅ **Write to websocket from REST API**: Implemented in `ashe/views.py`
✅ **Select specific sockets, not broadcast to all**: Use `target_user` parameter
✅ **Python script example**: `websocket_rest_example.py`
✅ **Server keep doing push**: Background `WebSocketPusher` class
✅ **Easy to use from ashe/views.py**: All functions are in this file

## Files Modified/Created

1. **`ashe/views.py`**: Added WebSocket messaging functions
2. **`ashe/urls.py`**: Added new endpoint URLs
3. **`websocket_rest_example.py`**: Python script for testing
4. **`websocket_test.html`**: HTML interface for testing
5. **`websocket_rest_api_README.md`**: This documentation

## Troubleshooting

1. **Token Authentication Error**: Make sure you have a valid token
2. **WebSocket Connection Failed**: Check if Daphne is running on port 8022
3. **CORS Issues**: Add your domain to Django CORS settings
4. **Live Push Not Working**: Check Django logs for background thread errors

## Example Use Cases

1. **Real-time Notifications**: Send alerts to users via WebSocket
2. **Live Tracking**: Push location updates to dashboard
3. **System Status**: Continuous monitoring data
4. **Chat Integration**: REST API posts trigger WebSocket messages
5. **IoT Data**: Device data pushed to real-time dashboard