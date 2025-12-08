#!/usr/bin/env python3
"""
WebSocket REST API Integration Example
This script shows how to send WebSocket messages from REST API calls
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8021"  # Your Django server URL
API_TOKEN = "28491066c4854472c24d4c167cfdbc228a5b9aae"  # Your actual token

# Headers for authentication
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Token {API_TOKEN}"  # Use your actual token
}


class WebSocketRESTClient:
    """Client for sending WebSocket messages via REST API"""
    
    def __init__(self, base_url=BASE_URL, token=API_TOKEN):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {token}"
        }
    
    def send_websocket_message(self, room, message, target_user=None, data=None):
        """Send a message to WebSocket via REST API"""
        url = f"{self.base_url}/ashe/send-websocket/"
        
        payload = {
            "room": room,
            "message": message,
            "target_user": target_user,
            "data": data or {}
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def push_location_update(self, latitude, longitude, device_id):
        """Push location update to WebSocket"""
        url = f"{self.base_url}/ashe/push-location/"
        
        payload = {
            "latitude": latitude,
            "longitude": longitude,
            "device_id": device_id
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def start_live_push(self, room="live_updates", interval=5):
        """Start continuous WebSocket pushing"""
        url = f"{self.base_url}/ashe/start-live-push/"
        
        payload = {
            "room": room,
            "interval": interval
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def stop_live_push(self):
        """Stop continuous WebSocket pushing"""
        url = f"{self.base_url}/ashe/stop-live-push/"
        
        try:
            response = requests.post(url, headers=self.headers)
            return response.json()
        except Exception as e:
            return {"error": str(e)}


def main():
    """Main demonstration function"""
    print("WebSocket REST API Integration Demo")
    print("=" * 50)
    
    # Initialize client
    client = WebSocketRESTClient()
    
    # Example 1: Send a simple message to WebSocket
    print("\n1. Sending simple message to WebSocket...")
    result = client.send_websocket_message(
        room="general",
        message="Hello from REST API!",
        data={"source": "python_script", "priority": "normal"}
    )
    print(f"Result: {result}")
    
    # Example 2: Send targeted message to specific user
    print("\n2. Sending targeted message...")
    result = client.send_websocket_message(
        room="private",
        message="This is a private message",
        target_user="1",  # User ID 1
        data={"type": "private", "encrypted": False}
    )
    print(f"Result: {result}")
    
    # Example 3: Push location update
    print("\n3. Pushing location update...")
    result = client.push_location_update(
        latitude=40.7128,
        longitude=-74.0060,
        device_id="device_001"
    )
    print(f"Result: {result}")
    
    # Example 4: Start continuous pushing
    print("\n4. Starting live push service...")
    result = client.start_live_push(room="live_stats", interval=3)
    print(f"Result: {result}")
    
    # Let it run for 15 seconds
    print("Live pushing for 15 seconds...")
    time.sleep(15)
    
    # Example 5: Stop continuous pushing
    print("\n5. Stopping live push service...")
    result = client.stop_live_push()
    print(f"Result: {result}")
    
    # Example 6: Send multiple messages in sequence
    print("\n6. Sending multiple messages...")
    messages = [
        "System starting up...",
        "Loading user data...",
        "Connecting to database...",
        "System ready!"
    ]
    
    for i, msg in enumerate(messages, 1):
        result = client.send_websocket_message(
            room="system_status",
            message=msg,
            data={"step": i, "total": len(messages)}
        )
        print(f"Step {i}: {result}")
        time.sleep(1)


def continuous_location_pusher():
    """
    Simulate a device continuously sending location updates
    This is what your client wants - "server keep doing push"
    """
    print("\nContinuous Location Pusher Demo")
    print("=" * 40)
    
    client = WebSocketRESTClient()
    
    # Simulate movement (in a small area)
    base_lat = 40.7128
    base_lng = -74.0060
    
    for i in range(20):  # Send 20 updates
        # Simulate slight movement
        lat = base_lat + (i * 0.0001)
        lng = base_lng + (i * 0.0001)
        
        result = client.push_location_update(
            latitude=lat,
            longitude=lng,
            device_id=f"mobile_device_{i % 3 + 1}"
        )
        
        print(f"Update {i+1}: Lat {lat:.6f}, Lng {lng:.6f} - {result.get('status', 'unknown')}")
        time.sleep(2)  # Wait 2 seconds between updates


def websocket_chat_simulation():
    """
    Simulate a chat system using REST API to WebSocket
    """
    print("\nWebSocket Chat Simulation")
    print("=" * 30)
    
    client = WebSocketRESTClient()
    
    # Simulate multiple users chatting
    chat_messages = [
        {"user": "user1", "message": "Hello everyone!", "room": "general"},
        {"user": "user2", "message": "Hi there! How's everyone doing?", "room": "general"},
        {"user": "user1", "message": "Great! Just testing the WebSocket integration", "room": "general"},
        {"user": "user3", "message": "This is amazing! Real-time from REST API", "room": "general"},
        {"user": "user2", "message": "The integration is working perfectly", "room": "general"},
    ]
    
    for msg_data in chat_messages:
        result = client.send_websocket_message(
            room=msg_data["room"],
            message=msg_data["message"],
            data={
                "simulated_user": msg_data["user"],
                "timestamp": datetime.now().isoformat()
            }
        )
        print(f"{msg_data['user']}: {msg_data['message']} -> {result.get('status', 'unknown')}")
        time.sleep(1.5)


if __name__ == "__main__":
    print("Choose a demo:")
    print("1. Main demo (all features)")
    print("2. Continuous location pusher")
    print("3. Chat simulation")
    print("4. All demos")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        main()
    elif choice == "2":
        continuous_location_pusher()
    elif choice == "3":
        websocket_chat_simulation()
    elif choice == "4":
        main()
        continuous_location_pusher()
        websocket_chat_simulation()
    else:
        print("Invalid choice. Running main demo...")
        main()