# # routing.py
# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.urls import path
# from server_agent.consumers import ServerAgentConsumer  # Replace with your WebSocket consumer
# from channels.auth import AuthMiddlewareStack

# # from urls import *
# application = ProtocolTypeRouter({
#     "websocket": AuthMiddlewareStack([
#         path("ws/some_path/", ServerAgentConsumer.as_asgi()),  # Define WebSocket paths and consumers here
#     ]),
# })

from django.urls import path , include,re_path
from server_websocket.consumers import ChatConsumer
 
# Here, "" is routing to the URL ChatConsumer which 
# will handle the chat functionality.
websocket_urlpatterns = [
    re_path(r'^ws/(?P<room_slug>[^/]+)/$', ChatConsumer.as_asgi()),
]