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
