from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.rooms, name='home'),  # Add this URL pattern for the home view
    path('<str:slug>/', views.room, name='room'),
    path('ws/<str:room_name>/', views.websocket_connect, name='websocket_connect'),
    path('ws/<str:room_name>/disconnect/', views.websocket_disconnect, name='websocket_disconnect'),
    path('ws/<str:room_name>/receive/', views.websocket_receive, name='websocket_receive'),
    path('ws/<str:room_name>/send/', views.websocket_send, name='websocket_send'),
]
