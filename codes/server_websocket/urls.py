from django.urls import path

from . import views


urlpatterns = [
    path("d", views.rooms, name="rooms"),
    path("<str:slug>", views.room, name="room"),
]