from django.db import models


class Task(models.Model):
    status = models.CharField(max_length=64)
    command = models.CharField(max_length=4096, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Server(models.Model):
    ip_address = models.CharField(max_length=64)
    username = models.CharField(max_length=4096, blank=True, null=True)
    password = models.CharField(max_length=4096, blank=True, null=True)
    error = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
