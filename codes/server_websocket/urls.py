from django.urls import path

from . import views


urlpatterns = [
    path("", views.rooms, name="home"),
    path("d", views.rooms, name="rooms"),
    path("create_room/", views.create_room, name="create_room"),
    path("<str:slug>", views.room, name="room"),
]