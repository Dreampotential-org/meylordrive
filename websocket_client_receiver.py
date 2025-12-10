#!/usr/bin/env python3
"""
WebSocket Client - Receives Push Messages from Server
This shows how the WebSocket client receives messages pushed from REST API
"""

import asyncio
import websockets
import json
from datetime import datetime

async def websocket_client_receiver():
    """
    WebSocket client that connects and listens for messages from the server
    This demonstrates receiving push messages sent from REST API
    """
    
    # Connect to the correct WebSocket endpoint
    uri = "ws://127.0.0.1:8022/ws/general/" 
    
    print(f"Connecting to WebSocket: {uri}")
    print("=" * 50)
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection opened successfully!")
            print("👂 Listening for messages from server...")
            print("💡 Now send messages via REST API to see them here!")
            print("-" * 50)
            
            # Send a test message to the server (optional)
            test_message = {
                "message_type": "chat",
                "message": "Hello from Python client!",
                "username": "python_client"
            }
            await websocket.send(json.dumps(test_message))
            print("📤 Sent test message to server")
            
            # Listen for messages from the server
            message_count = 0
            while True:
                try:
                    # This is where we receive messages pushed from REST API
                    response = await websocket.recv()
                    message_count += 1
                    
                    # Parse the JSON response
                    try:
                        data = json.loads(response)
                        print(f"\n📨 Message #{message_count} received:")
                        print(f"   ⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
                        
                        # Handle different message types
                        if data.get('type') == 'api_message':
                            # This is a message sent from REST API
                            msg_data = data.get('message', {})
                            print(f"   🔥 FROM REST API:")
                            print(f"   📝 Content: {msg_data.get('content', 'No content')}")
                            print(f"   👤 Sender: {msg_data.get('sender', 'Unknown')}")
                            print(f"   🏷️  Type: {msg_data.get('type', 'Unknown')}")
                            
                            if msg_data.get('type') == 'location_update':
                                print(f"   📍 Location: {msg_data.get('latitude')}, {msg_data.get('longitude')}")
                                print(f"   📱 Device: {msg_data.get('device_id')}")
                                
                            elif msg_data.get('type') == 'live_stats':
                                stats = msg_data.get('stats', {})
                                print(f"   📊 Live Stats:")
                                print(f"      - Devices: {stats.get('devices', 0)}")
                                print(f"      - Sessions: {stats.get('sessions', 0)}")
                                print(f"      - Dots: {stats.get('dots', 0)}")
                                
                        elif data.get('type') == 'chat_message':
                            # Regular chat message
                            print(f"   💬 CHAT MESSAGE:")
                            print(f"   📝 Message: {data.get('message', 'No message')}")
                            print(f"   👤 Username: {data.get('username', 'Unknown')}")
                            
                        elif data.get('type') == 'connection_status':
                            # Connection status message
                            print(f"   🔗 CONNECTION STATUS:")
                            print(f"   📝 Message: {data.get('message', 'No message')}")
                            print(f"   🏠 Room: {data.get('room', 'Unknown')}")
                            
                        else:
                            # Other message types
                            print(f"   📦 RAW DATA: {data}")
                            
                    except json.JSONDecodeError:
                        # Handle non-JSON messages
                        print(f"   📄 Raw message: {response}")
                        
                except websockets.exceptions.ConnectionClosedError as e:
                    print(f"\n❌ WebSocket connection closed: {e}")
                    break
                except Exception as e:
                    print(f"\n⚠️ Error receiving message: {e}")
                    continue
                    
    except Exception as e:
        print(f"❌ Failed to connect to WebSocket: {e}")
        print("💡 Make sure the WebSocket server is running on port 8022")

async def websocket_client_with_periodic_check():
    """
    Enhanced client that also sends periodic ping messages
    """
    uri = "ws://127.0.0.1:8022/ws/live_updates/"
    
    print(f"Connecting to WebSocket with periodic ping: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected! Sending periodic pings...")
            
            async def listen_for_messages():
                """Listen for incoming messages"""
                while True:
                    try:
                        response = await websocket.recv()
                        data = json.loads(response)
                        print(f"📨 Received: {data.get('type', 'unknown')} - {data.get('message', {}).get('content', 'No content')}")
                    except Exception as e:
                        print(f"Error: {e}")
                        break
            
            async def send_periodic_pings():
                """Send periodic ping messages"""
                ping_count = 0
                while True:
                    try:
                        await asyncio.sleep(10)  # Wait 10 seconds
                        ping_count += 1
                        ping_msg = {
                            "message_type": "ping",
                            "data": {"ping_number": ping_count}
                        }
                        await websocket.send(json.dumps(ping_msg))
                        print(f"📤 Sent ping #{ping_count}")
                    except Exception as e:
                        print(f"Ping error: {e}")
                        break
            
            # Run both tasks concurrently
            await asyncio.gather(
                listen_for_messages(),
                send_periodic_pings()
            )
            
    except Exception as e:
        print(f"Connection failed: {e}")

def main():
    """Main function to choose demo type"""
    print("🚀 WebSocket Client Receiver Demo")
    print("=" * 40)
    print("Choose demo type:")
    print("1. Basic receiver (recommended)")
    print("2. Receiver with periodic pings")
    print("3. Both demos")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        print("\n🎯 Starting basic WebSocket receiver...")
        print("💡 Now open another terminal and run:")
        print("   python websocket_rest_example.py")
        print("   Or send REST API calls to see messages here!")
        asyncio.get_event_loop().run_until_complete(websocket_client_receiver())
        
    elif choice == "2":
        print("\n🎯 Starting receiver with pings...")
        asyncio.get_event_loop().run_until_complete(websocket_client_with_periodic_check())
        
    elif choice == "3":
        print("\n🎯 Running basic demo first...")
        asyncio.get_event_loop().run_until_complete(websocket_client_receiver())
        print("\n🎯 Now running ping demo...")
        asyncio.get_event_loop().run_until_complete(websocket_client_with_periodic_check())
        
    else:
        print("Invalid choice, running basic demo...")
        asyncio.get_event_loop().run_until_complete(websocket_client_receiver())

if __name__ == "__main__":
    main()