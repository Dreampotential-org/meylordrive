import uuid
import os
from django.db import models
from django.contrib.auth import get_user_model


def uuid_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join(filename)


class Upload(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=uuid_file_path)


class AdminFeedback(models.Model):
    user = models.ForeignKey(
        to=get_user_model(), on_delete=models.CASCADE, default="")
    message = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)


class Profile(models.Model):
    user = models.ForeignKey(to=get_user_model(),
                             on_delete=models.CASCADE,
                             blank=True, null=True)
    phone = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=128, blank=True, null=True)
    bio = models.CharField(max_length=255, blank=True, null=True)
    photo = models.CharField(max_length=255, blank=True, null=True)
    code_2fa = models.CharField(max_length=20, blank=True, null=True)
    has_verified_phone = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    question_answers = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('phone',)


class UserEventNotify(models.Model):
    user = models.ForeignKey(to=get_user_model(),
                             on_delete=models.CASCADE,
                             default="", blank=True, null=True)
    notify_email = models.EmailField(
        max_length=512, blank=True, null=True)


class Device(models.Model):
    key = models.CharField(max_length=2000, default='')


class GpsC(models.Model):
    msg = models.CharField(max_length=2000, default='')
    device = models.CharField(max_length=2000, default='')
    lat = models.CharField(max_length=500, default='')
    lng = models.CharField(max_length=500, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    admin_feedback = models.ManyToManyField(AdminFeedback)
    user = models.ForeignKey(to=get_user_model(),
                             on_delete=models.CASCADE,
                             default="", blank=True, null=True)


class VideoCU(models.Model):
    videoUrl = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=500, default="")
    video_uuid = models.CharField(max_length=500, default='')
    admin_feedback = models.ManyToManyField(AdminFeedback)
    user = models.ForeignKey(to=get_user_model(),
                             on_delete=models.CASCADE,
                             default="", blank=True, null=True)


class MyMed(models.Model):
    name = models.CharField(max_length=2000, default='')
    dosage = models.CharField(max_length=2000, default='')
    user = models.ForeignKey(to=get_user_model(),
                             on_delete=models.CASCADE,
                             default="", blank=True, null=True)


class Question(models.Model):
    question_text = models.CharField(max_length=4000)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=400)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.choice_text or ''


class Token(models.Model):
    token = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(to=get_user_model(),
                             on_delete=models.CASCADE,
                             default="", blank=True, null=True)


class Service(models.Model):
    title = models.CharField(max_length=512)
    url = models.CharField(max_length=4096, blank=True, null=True,
                           unique=True)
    description = models.TextField()
    services_list = models.TextField(blank=True, null=True)
    population_list = models.TextField(blank=True, null=True)
    description = models.TextField()
    services = models.TextField(blank=True, null=True)
    other_info = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=1024, blank=True, null=True)
    address = models.CharField(max_length=512, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6,
                                   blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6,
                                    blank=True, null=True)


class UserSession(models.Model):
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(to=get_user_model(),
                             on_delete=models.CASCADE,
                             default="", blank=True, null=True)


class Session(models.Model):
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    device = models.ForeignKey(Device,
                               on_delete=models.CASCADE,
                               blank=True, null=True)


class SessionPoint(models.Model):
    # user = models.ForeignKey(to=get_user_model(),
    #                         on_delete=models.CASCADE,
    #                         default="", blank=True, null=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6,
                                   blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6,
                                    blank=True, null=True)
    device_timestamp = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE,
                                blank=True, null=True)
    device = models.ForeignKey(Device,
                               on_delete=models.CASCADE,
                               blank=True, null=True)


class Dot(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()


class GXYZPoint(models.Model):
    g = models.FloatField()
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    device_timestamp = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    device = models.ForeignKey(Device,
                               on_delete=models.CASCADE,
                               blank=True, null=True)
