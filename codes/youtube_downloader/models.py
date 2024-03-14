# storage/models.py
from django.db import models
from django.contrib.auth.models import User

class YouTubeVideo(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title

class YouTubeProfile(models.Model):
    profile_name = models.CharField(max_length=255, default='default_profile_name')
    videos = models.ManyToManyField('YouTubeVideo', blank=True)

    def __str__(self):
        return self.profile_name

class YProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    playlist = models.ManyToManyField('YouTubeProfile', blank=True)
