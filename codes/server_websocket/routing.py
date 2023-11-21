# server_websocket/routing.py
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from .consumers import ChatConsumer
from django.urls import path

application = ProtocolTypeRouter(
    {
        "websocket": AuthMiddlewareStack(
            URLRouter([
                path("ws/chat/", ChatConsumer.as_asgi()),
            ])
        ),
    }
)
