from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('', views.rooms, name='home'),  # Add this URL pattern for the home view
    path("<str:slug>/", views.room, name="room"),


]