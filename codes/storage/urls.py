from django.urls import include, path
from storage import views

urlpatterns = [
    path('file-upload/', views.file_upload, name='file_upload'),
    path('stream-video/<int:video_id>', views.stream_video, name='stream-video'),
    path('add_comment/', views.add_comment, name='add_comment'),
    path('list_files/', views.list_files, name='list_files'),
    path('list_comments/<int:upload_id>',
         views.list_comments, name='list_comments'),
]
