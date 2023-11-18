# # routing.py
# from django.urls import re_path

# from server_websocket.consumers import ChatConsumer

# websocket_urlpatterns = [
#     re_path(r'ws/chat/$', ChatConsumer.as_asgi()),
# ]
from django.urls import path
from chat_websocket.consumers import ChatConsumer
from channels.routing import ProtocolTypeRouter,URLRouter
application=ProtocolTypeRouter({
    'websocket':URLRouter([
        path('ws/chat/', ChatConsumer)
    ])
})