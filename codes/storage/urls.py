from django.urls import include, path
from storage import views

urlpatterns = [
    path('deletefile/<int:fileid>', views.deletefile, name='deletefile'),
    path('fileupload/', views.fileupload, name='file_upload'),
    path('api/media/<int:media_id>/update/', views.update_file_upload, name='update_file_upload'),
    path('api/media/<int:media_id>/delete/', views.delete_file_upload, name='delete_file_upload'),


    path('add_view/<int:upload_id>', views.add_view, name='add-view'),
    path('stream', views.stream, name='stream'),
    path('add_comment/', views.add_comment, name='add_comment'),
    path('get-activity/', views.get_activity, name='get_activity'),
    path('getfiles/', views.getfiles, name='getfiles'),
    path('list_comments/<int:upload_id>',
         views.list_comments, name='list_comments'),
    path('get_media/', views.get_media, name="get_media"),
    path('downloaded-songs/', views.list_downloaded_songs,
         name='list_downloaded_songs'),
    path('stream_media', views.stream_video, name="stream_video"),
]
