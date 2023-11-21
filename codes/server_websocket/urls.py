from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('', views.rooms, name='home'),  # Add this URL pattern for the home view
    path("<str:slug>/", views.room, name="room"),
    path('create_room/', views.create_room, name='create_room'),

    # path('room/<slug:slug>/', views.room, name='room'),


]