# server_websocket/routing.py
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from server_agent.consumers import ServerAgentConsumer

application = ProtocolTypeRouter({
    "websocket": URLRouter([
        path("ws/chat/", ServerAgentConsumer.as_asgi()),
    ]),
})
