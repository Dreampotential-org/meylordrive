# server_agent/routing.py
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from .consumers import ChatConsumer
from channels.db import database_sync_to_async
from django.core.asgi import get_asgi_application

websocket_urlpatterns = [
    path("ws/chat/", ChatConsumer.as_asgi()),  # Adjust the path as needed
]


application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})

# Wrap the application with `database_sync_to_async`
application = database_sync_to_async(get_asgi_application)(application)
