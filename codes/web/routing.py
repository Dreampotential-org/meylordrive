from django.urls import path , include,re_path
from web.consumers import ChatConsumer


websocket_urlpatterns = [
    path("ws/contact/<room_slug>/", ChatConsumer.as_asgi()),
    re_path(r'^ws/contact/$', ChatConsumer.as_asgi()),
]
