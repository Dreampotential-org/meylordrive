# chat_websocket/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/room/(?P<room_name>\w+)/$", consumers.ChatRoomConsumer.as_asgi()),
    # re_path(r"ws/chat/room_list/$", consumers.RoomListConsumer.as_asgi()),
    # Add URLs for other room-related functionalities
]
