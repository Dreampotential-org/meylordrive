# WebSocket REST API Integration - Quick Start Guide

## 🎯Requirements Implementation

This guide shows you how to **send WebSocket messages from REST API endpoints** - exactly what was wanted:

> "Write to websocket from rest API from ashe/views.py to connected sockets, select specific ones (not broadcast to all), have the server keep doing push, and provide Python script examples."

## 🚀 Quick Start (3 Steps)

### Step 1: Start Both Servers

#### Terminal 1 - Django Server (Port 8021)

```powershell
cd C:\Users\user\techzone\emails\meylordrive\codes
python manage.py runserver 8021
```

#### Terminal 2 - WebSocket Server (Port 8022)

```powershell
cd C:\Users\user\techzone\emails\meylordrive\codes
daphne -p 8022 web.asgi:application
```

### Step 2: Get Your API Token

```powershell
cd C:\Users\user\techzone\emails\meylordrive\codes
python test\create_token.py
```

Copy the token that gets printed (e.g., `28491066c4854472c24d4c167cfdbc228a5b9aae`)

### Step 3: Test the Implementation

```powershell
cd C:\Users\user\techzone\emails\meylordrive
python websocket_rest_example.py
```

Choose option `1` for the main demo.

## ✅ What You'll See Working

```
🚀 Test Results Summary:
    ✅ Simple messaging: SUCCESS
    ✅ Targeted messaging: SUCCESS  
    ✅ Location updates: SUCCESS
    ✅ Live push service: SUCCESS (started & stopped)
    ✅ Multiple sequential messages: SUCCESS
```

## 📡 Available Endpoints

### 1. Send WebSocket Message from REST API

```http
POST http://localhost:8021/ashe/send-websocket/
Authorization: Token YOUR_TOKEN_HERE
Content-Type: application/json

{
    "room": "general",
    "message": "Hello from REST API!",
    "target_user": "123",  // Optional: send to specific user only
    "data": {"priority": "high"}
}
```

### 2. Push Location Updates

```http
POST http://localhost:8021/ashe/push-location/
Authorization: Token YOUR_TOKEN_HERE
Content-Type: application/json

{
    "latitude": 40.7128,
    "longitude": -74.0060,
    "device_id": "mobile_001"
}
```

### 3. Start Continuous Push (Server Keep Doing Push)

```http
POST http://localhost:8021/ashe/start-live-push/
Authorization: Token YOUR_TOKEN_HERE
Content-Type: application/json

{
    "room": "live_updates",
    "interval": 3
}
```

### 4. Stop Continuous Push

```http
POST http://localhost:8021/ashe/stop-live-push/
Authorization: Token YOUR_TOKEN_HERE
Content-Type: application/json
```

## 🧪 Testing Options

### Option A: PowerShell Commands

```powershell
# Test basic messaging
$headers = @{'Content-Type'='application/json'; 'Authorization'='Token YOUR_TOKEN'}
$body = '{"room": "general", "message": "Hello from PowerShell!"}'
Invoke-WebRequest -Uri "http://localhost:8021/ashe/send-websocket/" -Method POST -Headers $headers -Body $body
```

### Option B: Python Script (Recommended)

```python
# Run the complete test suite
python websocket_rest_example.py

# Options:
# 1. Main demo (all features)
# 2. Continuous location pusher  
# 3. Chat simulation
# 4. All demos
```

### Option C: HTML Test Interface

1. Open `websocket_test.html` in your browser
2. Enter your API token
3. Connect to WebSocket
4. Send messages via REST API buttons

### Option D: WebSocket Client Test

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8022/ws/test/general/');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received message:', data.message);
};
```

## 🔧 Customer Requirements Fulfilled

### ✅ 1. Write to WebSocket from REST API (ashe/views.py)

**Implementation**: `send_to_websocket()` function in `ashe/views.py`

```python
# From any REST API endpoint, you can now do:
from ashe.views import send_websocket_message

def your_api_view(request):
    # Send message to WebSocket clients
    send_websocket_message("general", {
        "content": "Order completed!",
        "order_id": 123
    })
```

### ✅ 2. Select Specific Connected Sockets (Not Broadcast to All)

**Implementation**: Use `target_user` parameter

```json
{
    "room": "notifications",
    "message": "Private notification",
    "target_user": "123"  // Only user ID 123 receives this
}
```

### ✅ 3. Server Keep Doing Push

**Implementation**: Background `WebSocketPusher` class

```python
# Automatically pushes live data every N seconds
# Start: POST /ashe/start-live-push/
# Stop:  POST /ashe/stop-live-push/
```

### ✅ 4. Python Script Examples

**Implementation**: `websocket_rest_example.py`

- Main demo with all features
- Continuous location pusher
- Chat simulation
- Multiple test scenarios

## 📝 Integration in Your Code

### Send Message from Any Django View

```python
from ashe.views import send_websocket_message

def your_business_logic(request):
    # Your business logic here...
    order = process_order(request.data)
  
    # Send real-time update to WebSocket clients
    send_websocket_message("orders", {
        "type": "order_update",
        "order_id": order.id,
        "status": "completed",
        "user_id": request.user.id
    }, user_id=request.user.id)  # Send only to this user
  
    return Response({"status": "success"})
```

### Background Live Updates

```python
from ashe.views import WebSocketPusher

# Start background pushing
pusher = WebSocketPusher("live_dashboard", interval=5)
pusher.start_pushing()  # Pushes system stats every 5 seconds

# Stop when needed
pusher.stop_pushing()
```

## 🛠️ Files Created/Modified

1. **`ashe/views.py`** - WebSocket messaging functions
2. **`ashe/urls.py`** - New endpoint routes
3. **`web/settings.py`** - Fixed authentication configuration
4. **`web/simple_consumers.py`** - Updated WebSocket consumer
5. **`websocket_rest_example.py`** - Complete Python test script
6. **`websocket_test.html`** - Web interface for testing
7. **`test/create_token.py`** - Token creation utility

## 🔍 Troubleshooting

### Issue: "Invalid token"

**Solution**: Make sure REST_FRAMEWORK uses TokenAuthentication:

```python
# In web/settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework.authentication.TokenAuthentication',),
}
```

### Issue: WebSocket connection failed

**Solution**: Ensure Daphne server is running on port 8022:

```powershell
cd codes
daphne -p 8022 web.asgi:application
```

### Issue: Messages not appearing

**Solution**:

1. Check both servers are running
2. Verify token is valid
3. Ensure WebSocket client is connected to correct room

## 📊 Success Indicators

When everything is working, you should see:

```json
// REST API Response
{
    "status": "success",
    "message": "Message sent to WebSocket",
    "room": "general",
    "sent_at": "2025-12-08T21:05:18.095182"
}

// WebSocket Client Receives
{
    "type": "api_message",
    "message": {
        "content": "Hello from REST API!",
        "sender": "username",
        "type": "api_message",
        "timestamp": "2025-12-08T21:05:18.095182"
    },
    "source": "rest_api"
}
```

## 🎉Done!

The WebSocket REST API integration is now complete and fully functional. You can:

- Send WebSocket messages from any REST API endpoint
- Target specific users or broadcast to rooms
- Have continuous background pushing
- Test with multiple provided tools

The requirements have been 100% implemented and tested successfully! 🚀
