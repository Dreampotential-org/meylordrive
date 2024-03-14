# new_youtube/urls.py
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import add_to_playlist, download_video, get_media, home, playlist_detail, register

urlpatterns = [
    path('', home, name='home'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),
    path('list_files/', get_media, name='get_media'),  # Updated URL pattern
    path('download/<int:video_id>/', download_video, name='download_video'),
    path('add_to_playlist/<int:profile_id>/', add_to_playlist, name='add_to_playlist'),
    path('playlist/<int:profile_id>/', playlist_detail, name='playlist_detail'),




]
