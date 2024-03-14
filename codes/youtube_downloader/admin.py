# admin.py
from django.contrib import admin
from .models import YouTubeProfile

class YouTubeProfileAdmin(admin.ModelAdmin):
    list_display = ('profile_name',)

admin.site.register(YouTubeProfile, YouTubeProfileAdmin)
