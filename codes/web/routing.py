from django.urls import path, re_path
from .simple_consumers import SimpleTestConsumer

websocket_urlpatterns = [
    # Simple test consumer (no dependencies)
    re_path(r'^ws/(?P<room_slug>[\w-]+)/$', SimpleTestConsumer.as_asgi()),
]
