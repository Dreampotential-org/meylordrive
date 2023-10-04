# chat_project/asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from server_websocket import routing  # Import your app's routing configuration

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        routing.websocket_urlpatterns
    ),
})
