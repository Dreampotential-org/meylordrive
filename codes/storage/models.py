from django.db import models
from django.contrib.auth import get_user_model
import uuid
import os
from django.contrib.auth.models import User
from ashe.models import Device, Upload


class Comment(models.Model):
    message = models.TextField(default="")
    upload = models.ForeignKey(
        Upload, on_delete=models.CASCADE,
        null=True, blank=True, default=None)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE,
        null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)


class View(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(),
                             on_delete=models.CASCADE,
                             null=True, blank=True,
                             default=None)
    upload = models.ForeignKey(
            Upload, on_delete=models.CASCADE,
            null=True, blank=True, default=None)
    exit_time = models.DateTimeField(null=True, blank=True)

def uuid_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join(filename)


class MediA(models.Model):
    soundfile = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=uuid_file_path)

    path = models.CharField(max_length=5128,
                            blank=True, null=True)
    name = models.CharField(max_length=5128,
                            blank=True, null=True)
    user = models.ForeignKey(to=get_user_model(),
                             on_delete=models.CASCADE,
                             default="", blank=True, null=True)

class ProfileInfo(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=17, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Channel(models.Model):
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    url = models.URLField()
    description = models.TextField(default="")
    subscribers = models.IntegerField(default=0)
    videos = models.IntegerField(default=0)


class YouTubeVideo(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField()
    description = models.TextField()


    channel = models.ForeignKey(
        to=Channel, on_delete=models.CASCADE,
        default=None, blank=True, null=True)

    mediA = models.ForeignKey(to=MediA,
                             on_delete=models.CASCADE,
                             default=None, blank=True, null=True)


    def __str__(self):
        return self.title
