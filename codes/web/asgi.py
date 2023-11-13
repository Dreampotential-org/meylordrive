# chat_project/asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import django
django.setup()
from server_websocket.routing import websocket_urlpatterns  # Update the import path based on your project structure
# from .consumers import ChatConsumer  # Import your WebSocket consumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
application = get_asgi_application()
from server_websocket.routing import application  # Update the import path based on your project structure

# import os
# import django

# django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        websocket_urlpatterns
    ),
})