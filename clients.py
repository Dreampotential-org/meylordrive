import asyncio
import websockets


async def main():
    uri = "ws://127.0.0.1:8022/ws/general/"  # Updated to correct URL
    async with websockets.connect(uri) as websocket:
        # WebSocket connection is open
        print("WebSocket connection opened")

        # Send a message to the server
        await websocket.send("some sample api key to web socket")

        # Receive and print messages from the server
        while True:
            try:
                response = await websocket.recv()
                print(f"Received message from server: {response}")
            except websockets.exceptions.ConnectionClosedError as e:
                print(f"WebSocket connection closed unexpectedly: {e}")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
