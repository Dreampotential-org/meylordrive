# # server_websocket/routing.py
# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.urls import path
# from server_agent.consumers import ServerAgentConsumer

# application = ProtocolTypeRouter({
#     "websocket": URLRouter([
#         path("ws/chat/", ServerAgentConsumer.as_asgi()),
#     ]),
# })

# server_websocket.py

from django.urls import re_path

from .consumers import ChatConsumer  # Import your WebSocket consumer

websocket_urlpatterns = [
    re_path(r'ws/chat/$', ChatConsumer.as_asgi()),  # Adjust the path as needed
]
