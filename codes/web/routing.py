# routing.py
from django.urls import path, re_path
from .consumers import ChatConsumer, CreateRoomConsumer
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

websocket_urlpatterns = [
    re_path(r'^ws/(?P<room_slug>[^/]+)/$', ChatConsumer.as_asgi()),
    re_path(r'^ws/create_room/$', CreateRoomConsumer.as_asgi()),  # Add this line
]

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": URLRouter(websocket_urlpatterns),
    }
)