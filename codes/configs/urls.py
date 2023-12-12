from django.urls import path

from . import views

urlpatterns = [
    path('list_media', views.get_mediA, name="list_media"),
    path('stream_media', views.stream_video, name="stream_video"),
    path('create-user', views.create_user, name="create_user"),
    path('login-user', views.login_user, name="login_user"),
]
