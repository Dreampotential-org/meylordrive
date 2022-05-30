from django.db import models


class Task(models.Model):
    unique = True
    status = models.CharField(max_length=64)
    command = models.CharField(max_length=4096, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    stdout = models.TextField(null=True)
    stderr = models.TextField(null=True)


class Server(models.Model):
    ip_address = models.CharField(max_length=64)
    username = models.CharField(max_length=4096, blank=True, null=True)
    password = models.CharField(max_length=4096, blank=True, null=True)
    error = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Pipeline(models.Model):
    repo = models.CharField(max_length=4096)
    task = models.ForeignKey(Task, on_delete=models.CASCADE,
                             blank=True, null=True)


class GithubHook(models.Model):
    repo = models.CharField(max_length=4096)
    error = models.BooleanField(default=False)
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE,
                                 blank=True, null=True)
