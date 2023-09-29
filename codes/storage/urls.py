from django.urls import include, path
from storage import views

urlpatterns = [
    path('video-upload/', views.video_upload, name='video_upload'),
    path('stream-video/', views.stream_video, name='stream-video'),
]
