from django.db import models
from django.contrib.auth import get_user_model


class View(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)


class Upload(models.Model):
    Url = models.CharField(max_length=500)
    path = models.CharField(max_length=500)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                             null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=500, default="")

    def __str__(self):
        return self.Url


class Comment(models.Model):
    message = models.TextField(default="")
    upload = models.ForeignKey(Upload(), on_delete=models.CASCADE,
                               null=True, blank=True, default=None)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                             null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)



