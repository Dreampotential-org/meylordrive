# web/asgi.py
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter

# web/asgi.py
from django.core.asgi import get_asgi_application
from server_websocket.routing import application as websocket_application

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": websocket_application,
    }
)
