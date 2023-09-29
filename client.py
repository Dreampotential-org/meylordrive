import websocket
import thread
import time
import asyncio
import websockets

# Define a callback function to handle incoming messages from clients
async def handle_client(websocket, path):
    try:
        async for message in websocket:
            # When a message is received from the client, print it
            print(f"Received message: {message}")

            # Send a response back to the client
            response = f"Server received: {message}"
            await websocket.send(response)
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

# Create a WebSocket server that listens on a specific host and port
start_server = websockets.serve(handle_client, "localhost", 8000)

# Start the server and keep it running indefinitely
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

