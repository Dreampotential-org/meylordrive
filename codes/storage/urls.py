from django.urls import include, path
from storage import views

urlpatterns = [
    path('file-upload/', views.file_upload, name='file_upload'),
    path('add_view/<int:upload_id>', views.add_view, name='add-view'),
    path('stream-video/<int:video_id>', views.stream_video, name='stream-video'),
    path('add_comment/', views.add_comment, name='add_comment'),
    path('get-activity/', views.get_activity, name='get_activity'),
    path('list_files/', views.list_files, name='list_files'),
    path('list_comments/<int:upload_id>',
         views.list_comments, name='list_comments'),
    path('get_media/', views.get_media, name="get_media"),
    path('stream_media', views.stream_video, name="stream_video"),
]
