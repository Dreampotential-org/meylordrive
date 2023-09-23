# asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import server_agent.routing  # Import your app's routing configuration

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            server_agent.routing.websocket_urlpatterns  # Use your app's WebSocket URL routing
        )
    ),
})
