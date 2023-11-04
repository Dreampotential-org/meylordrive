# routing.py
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from server_agent.consumers import ServerAgentConsumer  # Replace with your WebSocket consumer

application = ProtocolTypeRouter({
    "websocket": URLRouter([
        path("ws/some_path/", YourConsumer.as_asgi()),  # Define WebSocket paths and consumers here
    ]),
})
