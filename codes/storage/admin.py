# admin.py
from django.contrib import admin
from .models import Comment, View, MediA, ProfileInfo, YouTubeVideo
from ashe.models import Upload

@admin.register(Upload)
class UploadAdmin(admin.ModelAdmin):
    list_display = ['Url', 'file_type', 'filename', 'path', 'user', 'uploaded_at', 'source']
    search_fields = ['Url', 'filename', 'user__username']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['message', 'upload', 'user', 'created_at']
    search_fields = ['message', 'upload__Url', 'user__username']

@admin.register(View)
class ViewAdmin(admin.ModelAdmin):
    list_display = ['user', 'upload', 'created_at', 'exit_time']
    search_fields = ['user__username', 'upload__Url']

@admin.register(MediA)
class MediAAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'file', 'path', 'name', 'user']
    search_fields = ['name', 'user__username']

@admin.register(ProfileInfo)
class ProfileInfoAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'created_at']
    search_fields = ['user__username', 'name']

@admin.register(YouTubeVideo)
class YouTubeVideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'url', 'description']
    search_fields = ['title', 'url']
